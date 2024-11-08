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
