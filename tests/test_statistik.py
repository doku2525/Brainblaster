from unittest import TestCase
from dataclasses import replace
from src.classes.antwort import Antwort
from src.classes.statistik import Statistik, StatModus, StatistikCalculations
from src.classes.lernuhr import Lernuhr


class test_Statistik(TestCase):

    def setUp(self):
        self.stat = Statistik(StatModus.NEU, [])
        self.ant1 = Antwort(5, 2000)
        self.ant2 = Antwort(3, 3000)
        self.ant3 = Antwort(7, 3000)
        self.ant4 = Antwort(0, 3000)

    def test_erzeugung_mit_standardwerten(self):
        obj = Statistik()
        self.assertEquals(obj.modus, StatModus.NEU)
        self.assertEquals(obj.antworten, [])
        self.assertFalse(obj.antworten)

    def test_add_neue_antwort(self):
        self.assertEquals(StatModus.NEU, self.stat.modus, "Modus = Neu")

        # ## Hinzufuegen zu Statistik im Modus NEU
        # falsche Antwort
        obj_falsch = self.stat.add_neue_antwort(Antwort(1, Lernuhr.echte_zeit()))
        self.assertEquals(StatModus.NEU, obj_falsch.modus, "(1) -> Modus = Neu")
        self.assertEquals([], obj_falsch.antworten, "() = []")
        # richtige Antwort
        obj_richtig = self.stat.add_neue_antwort(Antwort(5, Lernuhr.echte_zeit()))
        self.assertEquals(StatModus.PRUEFEN, obj_richtig.modus, "(5) Modus = Pruefen")
        self.assertEquals(5, obj_richtig.antworten[-1].antwort, "(5) last = 5")

        # ## Hinzufuegen zu  Statistik im Modus PRUEFEN
        # richtige Antwort
        obj_r = obj_richtig.add_neue_antwort(Antwort(5, Lernuhr.echte_zeit()))
        self.assertEquals(StatModus.PRUEFEN, obj_r.modus, "(5) -> Modus = Pruefen")
        self.assertEquals(5, obj_r.antworten[-1].antwort, "(5,5) last = 5")
        # falsche Antwort
        obj_falsch = obj_richtig.add_neue_antwort(Antwort(1, Lernuhr.echte_zeit()))
        self.assertEquals(1, obj_falsch.antworten[-1].antwort, "(5,1) last = 1")
        self.assertEquals(StatModus.LERNEN, obj_falsch.modus, "(5,1) -> Modus = Lernen")

        # ## Hinzufuegen zu Statistik im Modus LERNEN
        # richtige Vokabel
        obj_r = obj_falsch.add_neue_antwort(Antwort(5, Lernuhr.echte_zeit()))
        self.assertEquals(StatModus.LERNEN, obj_r.modus, "(5,1,7) -> Modus = Lernen")
        self.assertEquals(7, obj_r.antworten[-1].antwort, "(5,1,7) last = 7")
        obj_r = obj_r.add_neue_antwort(Antwort(5, Lernuhr.echte_zeit()))
        self.assertEquals(StatModus.PRUEFEN, obj_r.modus, "(5,1,7,7) -> Modus = Pruefen")
        self.assertEquals(7, obj_r.antworten[-1].antwort, "(5,1,7,7) last = 7")
        obj_r = obj_r.add_neue_antwort(Antwort(5, Lernuhr.echte_zeit()))
        self.assertEquals(StatModus.PRUEFEN, obj_r.modus, "(5,1,7,7,5) -> Modus = Pruefen")
        self.assertEquals(5, obj_r.antworten[-1].antwort, "(5,1,7,7,5) last = 5")
        # falsche Vokabel
        obj_f = obj_falsch.add_neue_antwort(Antwort(1, Lernuhr.echte_zeit()))
        self.assertEquals(StatModus.LERNEN, obj_f.modus, "(5,1,0) -> Modus = Lernen")
        self.assertEquals(0, obj_f.antworten[-1].antwort, "(5,1,0) last = 0")
        obj_r = obj_f.add_neue_antwort(Antwort(5, Lernuhr.echte_zeit()))
        self.assertEquals(StatModus.LERNEN, obj_r.modus, "(5,1,0,7) -> Modus = Lernen")
        self.assertEquals(7, obj_r.antworten[-1].antwort, "(5,1,0,7) last = 7")
        obj_r = obj_r.add_neue_antwort(Antwort(5, Lernuhr.echte_zeit()))
        self.assertEquals(StatModus.LERNEN, obj_r.modus, "(5,1,0,7,7) -> Modus = Lernen")
        self.assertEquals(7, obj_r.antworten[-1].antwort, "(5,1,0,7,7) last = 7")
        obj_r = obj_r.add_neue_antwort(Antwort(5, Lernuhr.echte_zeit()))
        self.assertEquals(StatModus.PRUEFEN, obj_r.modus, "(5,1,0,7,7,7) -> Modus = Pruefen")
        self.assertEquals(7, obj_r.antworten[-1].antwort, "(5,1,0,7,7,7) last = 7")
        obj_r = obj_r.add_neue_antwort(Antwort(5, Lernuhr.echte_zeit()))
        self.assertEquals(StatModus.PRUEFEN, obj_r.modus, "(5,1,0,7,7,7,5) -> Modus = Pruefen")
        self.assertEquals(5, obj_r.antworten[-1].antwort, "(5,1,0,7,7,7,5) last = 5")
        obj_f = obj_f.add_neue_antwort(Antwort(1, Lernuhr.echte_zeit()))
        self.assertEquals(StatModus.LERNEN, obj_f.modus, "(5,1,0,0) -> Modus = Lernen")
        self.assertEquals(0, obj_f.antworten[-1].antwort, "(5,1,0,0) last = 0")

    def test_ef(self):
        self.assertEquals(2.5, StatistikCalculations.ef(self.stat), "() = ef 2.5")
        self.stat = replace(self.stat, antworten=[Antwort(4, Lernuhr.echte_zeit())])
        self.assertGreater(StatistikCalculations.ef(self.stat), 2.5, "(4) = ef > 2.5")
        self.stat = replace(self.stat, antworten=[Antwort(3, Lernuhr.echte_zeit())])
        self.assertLess(StatistikCalculations.ef(self.stat), 2.5, "(3) = ef > 2.5")
        kleiner = Statistik(StatModus.NEU, [])
        groesser = Statistik(StatModus.NEU, [])
        kleiner = replace(kleiner, antworten=[Antwort(4, Lernuhr.echte_zeit())])
        groesser = replace(groesser, antworten=[Antwort(5, Lernuhr.echte_zeit())])
        self.assertLess(StatistikCalculations.ef(kleiner), StatistikCalculations.ef(groesser), "ef 4 < ef 5")
        kleiner = replace(kleiner, antworten=[Antwort(5, Lernuhr.echte_zeit())])
        groesser = replace(groesser, antworten=[Antwort(6, Lernuhr.echte_zeit())])
        self.assertLess(StatistikCalculations.ef(kleiner), StatistikCalculations.ef(groesser), "ef 5 < ef 6")
        kleiner = replace(kleiner, antworten=[Antwort(2, Lernuhr.echte_zeit())])
        groesser = replace(groesser, antworten=[Antwort(3, Lernuhr.echte_zeit())])
        self.assertGreater(StatistikCalculations.ef(groesser), StatistikCalculations.ef(kleiner), "ef 3 > ef 2")
        kleiner = replace(kleiner, antworten=[Antwort(1, Lernuhr.echte_zeit())])
        groesser = replace(groesser, antworten=[Antwort(2, Lernuhr.echte_zeit())])
        self.assertGreater(StatistikCalculations.ef(groesser), StatistikCalculations.ef(kleiner), "ef 2 > ef 1")

    def test_berechne_lernindex(self):
        self.assertEquals(1, StatistikCalculations.berechne_lernindex(self.stat), "Lernindex () = 1")
        self.assertEquals(1,
                          StatistikCalculations.berechne_lernindex(self.stat.add_neue_antwort(Antwort(5, 0))),
                          "Lernindex (5) = 2")
        obj = self.stat.add_neue_antwort(Antwort(5, 0))
        obj = obj.add_neue_antwort(Antwort(1, 0))
        self.assertEquals(0, StatistikCalculations.berechne_lernindex(obj), "(2) = 0")
        obj = obj.add_neue_antwort(Antwort(1, 0))
        self.assertEquals(-1, StatistikCalculations.berechne_lernindex(obj), "(2,2) = -1")
        obj = obj.add_neue_antwort(Antwort(5, 0))
        self.assertEquals(0, StatistikCalculations.berechne_lernindex(obj), "(2,2,5) = 0")
        obj = obj.add_neue_antwort(Antwort(5, 0))
        self.assertEquals(1, StatistikCalculations.berechne_lernindex(obj), "(2,2,5,5) = 1")
        obj = obj.add_neue_antwort(Antwort(5, 0))
        self.assertEquals(1, StatistikCalculations.berechne_lernindex(obj), "(2,2,5,5,6) = 1")
        obj = obj.add_neue_antwort(Antwort(2, 0))
        self.assertEquals(0, StatistikCalculations.berechne_lernindex(obj), "(2,2,5,5,6,2) = 0")

    def test_add_neue_antworten(self):
        self.assertFalse(self.stat.add_neue_antworten([]).antworten, "() ist leer")
        obj = self.stat.add_neue_antworten([Antwort(5, 0), Antwort(4, 0)])
        self.assertEquals(2, len(obj.antworten), "(5,4) sind 2 Elemente")
        self.assertEquals(5, [x.antwort for x in obj.antworten][0], "(5,4) 1. Element = 5")
        self.assertEquals(StatModus.PRUEFEN, obj.modus, "(5,4) Modus = PRUEFEN")
        obj = obj.add_neue_antworten([Antwort(6, 0), Antwort(1, 0), Antwort(2, 0)])
        self.assertEquals(5, len(obj.antworten), "(5,4)+(6,1,2) sind 5 Elemente")
        self.assertEquals(5, [x.antwort for x in obj.antworten][0], "(5,4)+(6,1,2) 1. Element = 5")
        self.assertEquals(0, [x.antwort for x in obj.antworten][-1], "(5,4)+(6,1,2) Letztes Element = 0")
        self.assertEquals(StatModus.LERNEN, obj.modus, "(5,4)+(6,1,2) Modus = LERNEN")
        obj = obj.add_neue_antworten([Antwort(6, 0)])
        self.assertEquals(7, [x.antwort for x in obj.antworten][-1], "(5,4)+(6,1,2)+(6) Letztes Element = 0")
        self.assertEquals(StatModus.LERNEN, obj.modus, "(5,4)+(6,1,2) Modus = LERNEN")

    def test_add_neue_antworten_aus_int(self):
        self.assertEquals([], self.stat.add_neue_antworten_aus_int([]).antworten, "Leere Liste")
        self.assertEquals([5, 2, 7, 7, 6],
                          [x.antwort for x in self.stat.add_neue_antworten_aus_int([5, 2, 6, 6, 6]).antworten],
                          "Liste mit falsch und lernen")
        self.assertEquals([6, 6, 6, 6],
                          [x.antwort for x in self.stat.add_neue_antworten_aus_int([1, 1, 6, 6, 6, 6]).antworten],
                          "Liste mit falsch und lernen")
        self.assertEquals([5, 1, 0, 7, 7, 7, 6],
                          [x.antwort for x in self.stat.add_neue_antworten_aus_int([5, 1, 1, 6, 6, 6, 6]).antworten],
                          "Liste mit falsch und lernen")
        self.assertEquals([5, 2, 0, 7, 7, 7, 6],
                          [x.antwort for x in self.stat.add_neue_antworten_aus_int([5, 2, 2, 6, 6, 6, 6]).antworten],
                          "Liste mit falsch und lernen")
        self.assertEquals([5, 2, 0, 7, 7, 7, 6],
                          [x.antwort for x in self.stat.add_neue_antworten_aus_int([5, 2, 1, 6, 6, 6, 6]).antworten],
                          "Liste mit falsch und lernen")
        self.assertEquals([5, 2],
                          [x.antwort for x in self.stat.add_neue_antworten_aus_int([5, 2]).antworten],
                          "Liste an Statistik mit Antworten")

    def test_berechne_millisekunden(self):
        for i in range(1, 7):
            if i < 5:
                self.assertGreater(StatistikCalculations.berechne_millisekunden(
                    self.stat.add_neue_antworten_aus_int([6] * i)), 0)
                self.assertEquals(
                    StatistikCalculations.berechne_millisekunden(
                        self.stat.add_neue_antworten_aus_int([6] * i)),
                    StatistikCalculations.berechne_millisekunden(
                        self.stat.add_neue_antworten_aus_int([5] * i)),
                    f"Teste mit {i} Antwort(en)")
            else:
                self.assertGreater(
                    StatistikCalculations.berechne_millisekunden(
                        self.stat.add_neue_antworten_aus_int([6] * i)),
                    0)
                self.assertGreater(
                    StatistikCalculations.berechne_millisekunden(
                        self.stat.add_neue_antworten_aus_int([6] * i)),
                    StatistikCalculations.berechne_millisekunden(
                        self.stat.add_neue_antworten_aus_int([5] * i)),
                    f"Teste mit {i} Antwort(en)")

    def test_erstes_datum(self):
        obj = self.stat.add_neue_antworten([Antwort(5, 0), Antwort(4, 20000)])
        self.assertEquals(0, obj.erstes_datum())

    def test_letztes_datum(self):
        obj = self.stat.add_neue_antworten([Antwort(5, 0), Antwort(4, 10000)])
        self.assertEquals(10000, obj.letztes_datum())

    def test_naechstes_datum(self):
        obj = self.stat.add_neue_antworten([Antwort(5, 0), Antwort(4, 0)])
        self.assertGreater(obj.naechstes_datum(), 0)

    def test_ist_abzufragen(self):
        # Fuer 2 richtige Antworten sollte der Wert bei 2 tagen liegen
        # Um mit int zu rechnen, liefert Uhr die Werte nicht in Sekunden, sondern in Millis
        sek_pro_tag = 86400*1000    # Umrechnung in Milis
        obj = self.stat.add_neue_antworten([Antwort(5, 0), Antwort(4, 0)])
        self.assertTrue(obj.ist_abzufragen(StatModus.PRUEFEN, int(sek_pro_tag * 2.8)))
        self.assertFalse(obj.ist_abzufragen(StatModus.PRUEFEN, int(sek_pro_tag * 1.8)))
        obj = self.stat.add_neue_antworten([Antwort(5, 0), Antwort(1, 0)])
        self.assertFalse(obj.ist_abzufragen(StatModus.PRUEFEN, 0))
        obj = self.stat.add_neue_antworten([Antwort(6, 0), Antwort(1, 0), Antwort(2, 0)])
        # Der Wert sollte bei etwa einem Halben Tag liegen
        self.assertTrue(obj.ist_abzufragen(StatModus.LERNEN, int(sek_pro_tag * 0.55)))
        self.assertFalse(obj.ist_abzufragen(StatModus.LERNEN, int(sek_pro_tag * 0.45)))
        obj = self.stat.add_neue_antworten([Antwort(6, 0), Antwort(1, 0), Antwort(2, 0), Antwort(2, 0)])
        # Der Wert sollte bei etwa einem Viertel Tag liegen
        self.assertTrue(obj.ist_abzufragen(StatModus.LERNEN, int(sek_pro_tag * 0.3)))
        self.assertFalse(obj.ist_abzufragen(StatModus.LERNEN, int(sek_pro_tag * 0.2)))
