from unittest import TestCase
import copy

import lerneinheit
from vokabeltrainer import Vokabeltrainer
from vokabelbox import Vokabelbox

class test_vokabeltrainer(TestCase):

    def setUp(self):
        self.obj = Vokabeltrainer.neu()

    def test_addVokabelkarte(self):
        self.assertFalse(Vokabeltrainer.vokabelkarten)
        self.assertFalse(self.obj.vokabelboxen)
        Vokabeltrainer.addBeispiele(20, "Japanisch")
        self.assertEquals(len(Vokabeltrainer.vokabelkarten), 20)
        self.assertFalse(self.obj.vokabelboxen)
        Vokabeltrainer.addBeispiele(80, "Chinesisch")
        self.assertEquals(len(Vokabeltrainer.vokabelkarten), 100)

    def test_speicherVokabelkartenInDatei(self):
        # TODO
        Vokabeltrainer.addBeispiele(5, "Japanisch")
        Vokabeltrainer.speicherVokabelkartenInDatei()
        Vokabeltrainer.speicherVokabelkartenInJSON()

    def test_addVokabelbox(self):
        self.assertEquals(len(self.obj.vokabelboxen), 0)
        objA = copy.deepcopy(self.obj.addVokabelbox(Vokabelbox("Titel 1", lerneinheit.LerneinheitJapanisch, [])))
        objAA = copy.deepcopy(self.obj.addVokabelbox(Vokabelbox("Titel 2", lerneinheit.LerneinheitJapanisch, [])))
        objAAA = copy.deepcopy(self.obj.addVokabelbox(Vokabelbox("Titel 3", lerneinheit.LerneinheitJapanisch, [])))
        self.assertEquals(len(objA.vokabelboxen), 1)
        self.assertEquals(len(objAA.vokabelboxen), 2)
        self.assertEquals(len(objAAA.vokabelboxen), 3)

    def test_existsBoxtitel(self):
        obj = self.obj.addVokabelbox(Vokabelbox("Titel 1", lerneinheit.LerneinheitJapanisch, []))
        obj = obj.addVokabelbox(Vokabelbox("Titel 2", lerneinheit.LerneinheitJapanisch, []))
        self.assertTrue(obj.existsBoxtitel('Titel 1'))
        self.assertTrue(obj.existsBoxtitel('Titel 2'))
        self.assertFalse(obj.existsBoxtitel('Titel 3'))
        self.assertFalse(obj.existsBoxtitel(''))

    def test_addBoxMitExistierendeTitel(self):
        obj = self.obj.addVokabelbox(Vokabelbox("Titel 1", lerneinheit.LerneinheitJapanisch, []))
        objA = obj.addVokabelbox(Vokabelbox("Titel 1", lerneinheit.LerneinheitJapanisch, []))
        self.assertEquals(len(obj.vokabelboxen), len(objA.vokabelboxen))

    def test_titelAllerVokabelboxen(self):
        # TODO
        objA = self.obj.addVokabelbox(Vokabelbox("Titel 1", lerneinheit.LerneinheitJapanisch, []))
        objAA = objA.addVokabelbox(Vokabelbox("Titel 2", lerneinheit.LerneinheitJapanisch, []))
        objAAA = objAA.addVokabelbox(Vokabelbox("Titel 3", lerneinheit.LerneinheitJapanisch, []))
        self.assertEquals(1, len(objA.vokabelboxen))
        self.assertEquals(2, len(objAA.vokabelboxen))
        self.assertEquals(3, len(objAAA.vokabelboxen))
        self.assertEquals("Titel 1", objAA.vokabelboxen[0].titel)
        self.assertEquals("Titel 2", objAA.vokabelboxen[1].titel)
        self.assertEquals("Titel 3", objAAA.vokabelboxen[2].titel)

    def test_renameBox(self):
        # TODO
        obj = self.obj.addVokabelbox(Vokabelbox("Titel 1", lerneinheit.LerneinheitJapanisch, []))
        obj = obj.addVokabelbox(Vokabelbox("Titel 2", lerneinheit.LerneinheitJapanisch, []))
        objA = obj.renameBox('Titel 1', 'Titel 2')
        objB = obj.renameBox('Titel 4', 'Titel 5')
        objC = obj.renameBox('Titel 1', 'Titel 3')
        self.assertEquals(obj.titelAllerVokabelboxen(), objA.titelAllerVokabelboxen())
        self.assertEquals(obj.titelAllerVokabelboxen(), objB.titelAllerVokabelboxen())
        self.assertEquals("Titel 3", objC.titelAllerVokabelboxen()[-1])
        self.assertEquals("Titel 2", objC.titelAllerVokabelboxen()[0])

    def test_loescheBox(self):
        # TODO
        obj = self.obj.addVokabelbox(Vokabelbox("Titel 1", lerneinheit.LerneinheitJapanisch, []))
        obj = obj.addVokabelbox(Vokabelbox("Titel 2", lerneinheit.LerneinheitJapanisch, []))
        objA = obj.loescheBox("Titel 3")
        objB = obj.loescheBox("Titel 2")
        objC = obj.loescheBox("Titel 1")
        objD = objB.loescheBox("Titel 1")
        self.assertEquals(2, len(objA.vokabelboxen))
        self.assertEquals(1, len(objB.vokabelboxen))
        self.assertEquals(1, len(objC.vokabelboxen))
        self.assertEquals(0, len(objD.vokabelboxen))