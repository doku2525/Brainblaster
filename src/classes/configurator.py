from __future__ import annotations
from dataclasses import dataclass, field, asdict
import src.utils.utils_io as u_io


@dataclass(frozen=True)
class Configurator:
    daten_pfad: str = "daten/data/"
    backup_pfad: str = "daten/data/backups/"
    log_pfad: str = "daten/log/"
    config_dateiname: str = "config.JSON"
    uhr_dateiname: str = "uhrzeit.JSON"
    vokabelkarten_dateiname: str = "vokabelkarten.JSON"
    vokabelboxen_dateiname: str = "vokabelboxen.JSON"

    def speicher(self) -> None:
        u_io.speicher_in_jsondatei(asdict(self), self.daten_pfad + self.config_dateiname)

    def laden(self) -> Configurator:
        return Configurator(**u_io.lese_aus_jsondatei(self.daten_pfad + self.config_dateiname))


config = Configurator().laden()
