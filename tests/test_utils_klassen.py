from unittest import TestCase
from src.classes.antwort import Antwort
from src.utils.utils_klassen import suche_alle_instanzen_einer_klasse, suche_subklasse_by_klassenname


class test_UtilsKlassen(TestCase):

    def test_suche_subklasse_by_klassenname(self):
        class A:
            x = 1

        class AA(A):
            x = 2

        class AB(A):
            x = 3

        result = suche_subklasse_by_klassenname(A, "AB")
        self.assertEqual(AB, result)
        self.assertNotEqual(AA, result)
        self.assertEqual(3, result.x)

    def test_suche_alle_instanzen_einer_klasse(self):
        from types import GeneratorType

        self.assertEqual(0, len(suche_alle_instanzen_einer_klasse(Antwort)))
        liste = (Antwort(),)
        self.assertIsInstance(liste, tuple)
        self.assertEqual(1, len(liste))
        self.assertEqual(1, len(suche_alle_instanzen_einer_klasse(Antwort)))
        liste = (Antwort(),) * 5
        self.assertIsInstance(liste, tuple)
        self.assertEqual(5, len(liste))
        self.assertEqual(1, len(suche_alle_instanzen_einer_klasse(Antwort)))
        liste = (Antwort(x, x) for x in range(10))
        self.assertIsInstance(liste, GeneratorType)
        self.assertEqual(0, len(suche_alle_instanzen_einer_klasse(Antwort)))
        liste = list((Antwort(x, x) for x in range(10)))
        self.assertEqual(10, len(suche_alle_instanzen_einer_klasse(Antwort)))
        self.assertIsInstance(liste, list)
        liste = [Antwort(x, x) for x in range(10)]
        self.assertIsInstance(liste, list)
        self.assertEqual(10, len(suche_alle_instanzen_einer_klasse(Antwort)))
