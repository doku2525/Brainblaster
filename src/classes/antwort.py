from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Antwort:
    antwort: int = 0
    erzeugt: int = 0

    @classmethod
    def fromdict(cls, source_dict: dict) -> cls:
        return cls(antwort=source_dict['antwort'],
                   erzeugt=source_dict['erzeugt'])

    def ist_richtig(self) -> bool: return self.antwort in range(4, 7)
    def ist_falsch(self) -> bool: return self.antwort in range(1, 4)
    def ist_richtig_gelernt(self) -> bool: return self.antwort == 7
    def ist_falsch_gelernt(self) -> bool: return self.antwort == 0
    def ist_lernen(self) -> bool: return self.ist_richtig_gelernt() or self.ist_falsch_gelernt()
