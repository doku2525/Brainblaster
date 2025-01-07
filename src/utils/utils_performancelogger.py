from __future__ import annotations
from dataclasses import dataclass
import logging
import time
from typing import Any, Callable

# Definieren einer neuen Log-Stufe
TIME_LEVEL = 25
logging.addLevelName(TIME_LEVEL, "TIME")


# Verwenden der neuen Stufe, um die log-Funktion zu definieren, die im Logger registriert wird
def time_log(self, message, *args, **kwargs):
    if self.isEnabledFor(TIME_LEVEL):
        self._log(TIME_LEVEL, message, args, **kwargs)


def create_zeit_logger(filename: str, logger_name: str) -> logging.Logger:
    # Registrieren der log-Funktion im Logger. Der Name muss nicht identisch mit dem Namen der log-Funktion sein.
    logging.Logger.zeit = time_log

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # Mit 25 liegt der eigene Logger zwischen INFO und WARNING
    fh = logging.FileHandler(filename)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    return logger


@dataclass
class ZeitLogger:
    logger: logging.Logger
    start_zeit: float = 0
    end_zeit: float = 0

    def name(self, name: str) -> None:
        """Anedert den Namen der im log-File zweiter Stelle steht. Im Normalfall sollte es obj.name(__name__) sein"""
        self.logger.name = name

    def starte_logging(self) -> None:
        """Kann aufgerufen werden, um eine im log-File deutlich erkennbare Marke zu setzen."""
        self.logger.zeit(f"*****  Beginne neue Session  *****")

    def start(self, msg: str = None) -> None:
        """Wird vor dem zu messenden Block aufgerufen."""
        self.start_zeit = time.perf_counter()
        if msg:
            self.logger.zeit(f"{'_' * 11}   START {msg}")

    def fertig(self, msg: str) -> None:
        """Wird nach dem zu messenden Block aufgerufen."""
        self.end_zeit = time.perf_counter()
        self.logger.zeit(f"{self.end_zeit - self.start_zeit:.5f} sek = {msg}")

    @classmethod
    def create(cls, log_file: str, logger_name: str) -> ZeitLogger:
        """Erzeuge eine Instanze der Klasse"""
        return ZeitLogger(create_zeit_logger(log_file, logger_name))

    def execute(self, func: Callable, msg: str) -> Any:
        """Fuehre func aus und liefer das Ergebnis der func(). Eine Funktion mit allen Argumenten in einem lambda"""
        self.start()
        result = func()
        self.fertig(msg)
        return result
