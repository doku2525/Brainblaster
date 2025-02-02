from unittest import TestCase

from src.zustaende.zustandsfactory import ZustandsFactory


class MockFactory(ZustandsFactory):
    def buildMock(self, zustand):
        return 10


class Mock:
    pass


class test_ZustandsFactory(TestCase):

    def setUp(self):
        self.factory = ZustandsFactory(None, None, None)
        self.mock = MockFactory(None, None, None)

    def test_suche_build_funktion(self):
        from src.zustaende.zustandstart import ZustandStart

        self.assertIsNotNone(self.factory.suche_build_funktion(ZustandStart))
        self.assertIsNone(self.factory.suche_build_funktion(Mock))
        self.assertIsNotNone(self.mock.suche_build_funktion(Mock))
        funktion = self.mock.suche_build_funktion(Mock)
        self.assertEqual(10, funktion(Mock()))
