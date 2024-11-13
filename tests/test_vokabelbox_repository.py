from unittest import TestCase
import copy

from libs.repository.vokabelbox_repository import (InMemeoryVokabelboxRepository, VokabelboxRepository,
                                                   DateiformatVokabelbox, BINARYDateiformatVokabelbox,
                                                   JSONDateiformatVokabelbox)
from vokabelbox import Vokabelbox
from lerneinheit import LerneinheitJapanisch


class test_VokabelboxRepository(TestCase):

    def setUp(self):
        self.obj = InMemeoryVokabelboxRepository(dateiname='__vokabelbox.data',
                                                 speicher_methode=BINARYDateiformatVokabelbox)
        self.assertIsInstance(self.obj, VokabelboxRepository)
        self.assertIsInstance(self.obj, InMemeoryVokabelboxRepository)
        self.assertIsInstance(self.obj.speicher_methode(), BINARYDateiformatVokabelbox)
        self.assertIsInstance(self.obj.speicher_methode(), DateiformatVokabelbox)

    def test_speichern(self):
        self.obj.speichern()

    def test_laden(self):
        self.assertEqual([], self.obj.vokabelboxen)
        self.obj.laden()
        self.assertEqual([], self.obj.vokabelboxen)
        self.obj.vokabelboxen = [1, 2, 3]
        self.obj.laden()
        self.assertEqual([1, 2, 3], self.obj.vokabelboxen)
        self.obj.vokabelboxen = []
        self.obj.add_box(Vokabelbox("Titel 1", LerneinheitJapanisch, []))

    def test_erneut_laden(self):
        self.assertEqual([], self.obj.vokabelboxen)
        self.obj.erneut_laden()
        self.assertEqual([], self.obj.vokabelboxen)
        self.obj.vokabelboxen = [1, 2, 3]
        self.obj.erneut_laden()
        self.assertEqual([], self.obj.vokabelboxen)

    def test_laden_und_speichern(self):
        self.obj.vokabelboxen = [1, 2, 3]
        self.obj.speichern()
        self.obj.vokabelboxen = None
        self.obj.laden()
        self.assertEqual([1, 2, 3], self.obj.vokabelboxen)
        self.obj.vokabelboxen = [1]
        self.obj.laden()
        self.assertEqual([1], self.obj.vokabelboxen)
        self.obj.erneut_laden()
        self.assertEqual([1, 2, 3], self.obj.vokabelboxen)
        self.obj.vokabelboxen = []
        self.obj.add_box(Vokabelbox("Titel 1", LerneinheitJapanisch, []))
        self.obj.add_box(Vokabelbox("Titel 2", LerneinheitJapanisch, []))
        self.obj.add_box(Vokabelbox("Titel 3", LerneinheitJapanisch, []))
        self.obj.speichern()
        self.obj.vokabelboxen = []
        self.obj.laden()
        self.assertEquals("Titel 1", self.obj.vokabelboxen[0].titel)
        self.assertEquals("Titel 2", self.obj.vokabelboxen[1].titel)
        self.assertEquals("Titel 3", self.obj.vokabelboxen[2].titel)
        self.obj.vokabelboxen = []
        self.obj.speichern()


    def test_add_box(self):
        obj = copy.deepcopy(self.obj)
        obj.add_box(Vokabelbox("Titel 1", LerneinheitJapanisch, []))
        self.assertEquals(len(obj.vokabelboxen), 1)
        self.assertEquals(len(self.obj.vokabelboxen), 0)
        self.assertIsInstance(obj.vokabelboxen[0], Vokabelbox)
        obj.add_box(Vokabelbox("Titel 2", LerneinheitJapanisch, []))
        self.assertEquals(len(obj.vokabelboxen), 2)
        obj.add_box(Vokabelbox("Titel 1", LerneinheitJapanisch, []))
        self.assertEquals(len(obj.vokabelboxen), 2)

    def test_remove_box(self):
        self.obj.add_box(Vokabelbox("Titel 1", LerneinheitJapanisch, []))
        self.obj.add_box(Vokabelbox("Titel 2", LerneinheitJapanisch, []))
        self.obj.remove_box("Titel 3")
        self.assertEquals(2, len(self.obj.vokabelboxen))
        self.obj.remove_box("Titel 2")
        self.assertEquals(1, len(self.obj.vokabelboxen))
        self.obj.remove_box("Titel 2")
        self.assertEquals(1, len(self.obj.vokabelboxen))
        self.obj.remove_box("Titel 1")
        self.assertEquals(0, len(self.obj.vokabelboxen))
        self.obj.remove_box("Titel 1")
        self.assertEquals(0, len(self.obj.vokabelboxen))

    def test_rename_box(self):
        self.obj.add_box(Vokabelbox("Titel 1", LerneinheitJapanisch, []))
        self.obj.add_box(Vokabelbox("Titel 2", LerneinheitJapanisch, []))
        self.obj.rename_box('Titel 1', 'Titel 2')
        self.obj.rename_box('Titel 4', 'Titel 5')
        self.obj.rename_box('Titel 1', 'Titel 3')
        self.assertEquals(self.obj.titel_aller_vokabelboxen(), self.obj.titel_aller_vokabelboxen())
        self.assertEquals(self.obj.titel_aller_vokabelboxen(), self.obj.titel_aller_vokabelboxen())
        self.assertEquals("Titel 3", self.obj.titel_aller_vokabelboxen()[-1])
        self.assertEquals("Titel 2", self.obj.titel_aller_vokabelboxen()[0])

    def test_titel_aller_vokabelboxen(self):
        self.obj.add_box(Vokabelbox("Titel 1", LerneinheitJapanisch, []))
        self.obj.add_box(Vokabelbox("Titel 2", LerneinheitJapanisch, []))
        self.obj.add_box(Vokabelbox("Titel 3", LerneinheitJapanisch, []))
        self.assertEquals(3, len(self.obj.vokabelboxen))
        self.assertEquals("Titel 1", self.obj.vokabelboxen[0].titel)
        self.assertEquals("Titel 2", self.obj.vokabelboxen[1].titel)
        self.assertEquals("Titel 3", self.obj.vokabelboxen[2].titel)
        self.assertEquals(["Titel 1", "Titel 2", "Titel 3"], self.obj.titel_aller_vokabelboxen())

    def test_exists_boxtitel(self):
        self.obj.add_box(Vokabelbox("Titel 1", LerneinheitJapanisch, []))
        self.obj.add_box(Vokabelbox("Titel 2", LerneinheitJapanisch, []))
        self.assertTrue(self.obj.exists_boxtitel('Titel 1'))
        self.assertTrue(self.obj.exists_boxtitel('Titel 2'))
        self.assertFalse(self.obj.exists_boxtitel('Titel 3'))
        self.assertFalse(self.obj.exists_boxtitel(''))
