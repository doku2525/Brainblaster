from unittest import TestCase
from libs.repository.vokabelbox_repository import VokabelboxRepository

class test_VokabelboxRepository(TestCase):

    def setUp(self):
        self.obj = VokabelboxRepository('__vokabelbox.data')

    def test_speichern(self):
        self.obj.speichern()

    def test_laden(self):
        self.assertIsNone(self.obj.vokabelboxen)
        self.obj.laden()
        self.assertIsNone(self.obj.vokabelboxen)

    def test_erneut_laden(self):
        self.assertIsNone(self.obj.vokabelboxen)
        self.obj.erneut_laden()
        self.assertIsNone(self.obj.vokabelboxen)

    def test_laden_und_speichern(self):
        self.assertIsNone(self.obj.vokabelboxen)
        self.obj.vokabelboxen = [1,2,3]
        self.obj.speichern()
        self.obj.vokabelboxen = None
        self.obj.laden()
        self.assertEqual([1,2,3], self.obj.vokabelboxen)
        self.obj.vokabelboxen = [1]
        self.obj.laden()
        self.assertEqual([1], self.obj.vokabelboxen)
        self.obj.erneut_laden()
        self.assertEqual([1,2,3], self.obj.vokabelboxen)
        self.obj.vokabelboxen = None
        self.obj.speichern()

    def test_add_box(self):
        assert False

    def test_remove_box(self):
        assert False

    def test_rename_box(self):
        assert False

    def test_titel_aller_vokabelboxen(self):
        assert False

    def test_exists_boxtitel(self):
        assert False
