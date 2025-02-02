from __future__ import annotations
from dataclasses import dataclass, field
from typing import Type, TYPE_CHECKING
from src.kommandos.kommando import Kommando

if TYPE_CHECKING:
    from src.classes.vokabeltrainercontroller import VokabeltrainerController


@dataclass(frozen=True)
class KommandoInterpreter:
    cmds: dict[str: Type[Kommando]] = field(default_factory=Kommando)

    def __post_init__(self):
        object.__setattr__(self, 'cmds', self.build_cmds_mapping(Kommando))

    @staticmethod
    def build_cmds_mapping(cmd_klasse: Type[Kommando]) -> dict[str, Type[Kommando]]:
        """Erstellt ein Dictionary aus allen SubKlassen der Klasse cmd_klasse.
           Im Normalfall sollte cmd_klasse eine abstracte Klasse sein."""
        return {sub_klasse.__name__: sub_klasse for sub_klasse in cmd_klasse.__subclasses__()}

    def execute(self, cmd: str, controller: VokabeltrainerController, args) -> VokabeltrainerController:
        kommando = self.cmds.get(cmd, False)
        print(f" KommandoInterpreter: {cmd = }  -  {kommando = }")
        return kommando().execute(controller)(*args) if kommando else controller
