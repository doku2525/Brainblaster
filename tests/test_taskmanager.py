from unittest import TestCase
import time

from src.classes.taskmanager import Task, TaskManager
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Foo:
    liste: list = field(default_factory=list)


class test_Task(TestCase):

    def setUp(self):
        self.task = Task([])
        self.test_foo = Foo([])

    def test_initialize(self):
        self.assertEqual([], self.task.value)
        self.assertEqual([], self.task.auftraege)
        self.assertEqual(None, self.task.arbeits_thread)
        self.assertEqual(0, self.task.leerlaufzeit.value)

    def test_registriere_funktion(self):
        self.task.registriere_funktion(lambda x: x + x)
        self.assertEqual(1, len(self.task.auftraege))

    def test_start(self):
        self.task.start()
        self.assertFalse(self.task.is_running())
        self.assertTrue(self.task.is_alive())
        self.task.stop()

    def test_stop(self):
        self.task.start()
        self.assertTrue(self.task.is_alive())
        self.task.stop()
        time.sleep(0.001)     # Pause, um den Thread Zeit zum Beenden zu geben
        self.assertFalse(self.task.is_alive())

    def test_is_running(self):
        def dummy(liste: list) -> list:
            time.sleep(0.1)
            return liste + [len(liste)]

        for _ in range(5):
            self.task.registriere_funktion(lambda x: dummy(x))
        self.assertTrue(5, self.task.auftraege)
        self.task.start()
        time.sleep(0.1)
        self.assertTrue(self.task.is_running())
        while self.task.is_running():
            self.assertTrue(self.task.is_running())
            time.sleep(0.1)
        self.assertFalse(self.task.is_running())
        self.assertTrue(self.task.is_alive())
        self.task.stop()

    def test_is_alive(self):
        self.assertFalse(self.task.is_alive())
        time.sleep(0.01)
        self.task.start()
        time.sleep(0.01)
        self.assertTrue(self.task.is_alive())
        time.sleep(0.01)
        self.task.stop()
        time.sleep(0.01)
        self.assertFalse(self.task.is_alive())

    def test_werte_zuweisung(self):
        def dummy(liste: list) -> list:
            return liste + [len(liste)]

        for _ in range(5):
            self.task.registriere_funktion(lambda x: dummy(x))
        self.task.start()
        self.task.join(0.2)
        self.task.stop()
        self.assertEqual(list(range(5)), self.task.value)

    def test_werte_zuweisung_registriere_waehrend_ausfuehrung(self):
        def dummy(liste: list) -> list:
            time.sleep(0.05)
            return liste + [len(liste)]

        for _ in range(5):
            self.task.registriere_funktion(lambda x: dummy(x))
        self.task.start()
        index = 0
        while self.task.is_running():
            if index in [3, 4]:
                self.task.registriere_funktion(lambda x: dummy(x))
            time.sleep(0.05)
            index += 1
        self.task.stop()
        self.assertEqual(5 + 2, len(self.task.value))

    def test_werte_zuweisung_registriere_nach_ausfuehrung(self):
        def dummy(liste: list) -> list:
            time.sleep(0.05)
            return liste + [len(liste)]

        for _ in range(5):
            self.task.registriere_funktion(lambda x: dummy(x))
        self.task.start()
        self.task.join(0.2)
        self.assertEqual(5, len(self.task.value))
        self.assertTrue(self.task.is_alive())
        self.assertFalse(self.task.is_running())
        self.task.registriere_funktion(lambda x: dummy(x))
        self.task.join()
        self.assertEqual(5 + 1, len(self.task.value))
        self.task.stop()

    def test_task_auf_klassen_attribut_anwenden(self):
        def dummy(x):
            self.test_foo = Foo(x.liste + [1, 2, 3])
            return Foo(x.liste + [1, 2, 3])

        self.task.value = self.test_foo
        self.assertIsInstance(self.task.value, Foo)
        self.task.registriere_funktion(lambda x: dummy(x))
        self.task.start()
        self.task.join(0.2)
        self.task.stop()
        self.assertEqual([1, 2, 3], self.task.value.liste)
        self.assertEqual([1, 2, 3], self.test_foo.liste)


class test_TaskManager(TestCase):

    def setUp(self):
        self.tm = TaskManager()

    def test_initialize(self):
        self.assertEqual({}, self.tm.tasks)

    def test_registriere_task_hole_task(self):
        result = self.tm.registriere_task('TEST', Task(1))
        self.assertIsNone(result)
        self.assertNotEqual({}, self.tm.tasks)
        self.assertEqual(1, len(self.tm.tasks))
        self.assertEqual('TEST', list(self.tm.tasks.keys())[0])
        result = self.tm.registriere_task('TEST', Task(2))
        self.assertIsNotNone(result)
        self.assertNotEqual({}, self.tm.tasks)
        self.assertEqual(1, len(self.tm.tasks))
        self.assertEqual('TEST', list(self.tm.tasks.keys())[0])
        self.assertEqual(1, result.value)
        self.assertEqual(2, self.tm.task('TEST').value)

    def test_mehrere_tasks_verwalten(self):
        def dummy(liste: list) -> list:
            time.sleep(0.1)
            return liste + [len(liste)]

        task1 = Task([])
        for _ in range(5):
            task1.registriere_funktion(lambda x: dummy(x))
        task2 = Task([])
        for _ in range(5):
            task2.registriere_funktion(lambda x: dummy(x * 2))
        self.tm.registriere_task('TASK1', task1)
        self.tm.registriere_task('TASK2', task2)
        self.tm.tasks['TASK1'].start()
        self.tm.tasks['TASK2'].start()
        while self.tm.tasks['TASK1'].is_running() or self.tm.tasks['TASK2'].is_running():
            time.sleep(0.1)
        self.tm.tasks['TASK1'].stop()
        self.tm.tasks['TASK2'].stop()
        self.assertEqual(5, len(self.tm.tasks['TASK1'].value))
        self.assertEqual(pow(2, 5) - 1, len(self.tm.tasks['TASK2'].value))
