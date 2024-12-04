from unittest import TestCase
from src.utils.utils_enum import name_zu_enum, enum_zu_dict

from src.classes.lernuhr import UhrStatus


class test_UtilsEnum(TestCase):

    def test_name_zu_enum(self):
        self.assertEqual(UhrStatus.PAUSE, name_zu_enum('PAUSE', UhrStatus))

    def test_enum_zu_dict(self):
        self.assertEqual('PAUSE', enum_zu_dict(UhrStatus.PAUSE))
