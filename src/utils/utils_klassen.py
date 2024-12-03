from typing import Type, TypeVar
import gc

T = TypeVar('T')


def suche_subklasse_by_klassenname(klasse: Type[T], klassenname: str) -> Type[T] | None:
    # Erstelle Generator und liefer mit next(genr, None) das 1. Element oder None
    return next((klasse for klasse in klasse.__subclasses__() if klasse.__name__ == klassenname), None)


def suche_alle_instanzen_einer_klasse(klasse: Type[T]) -> list[T]:
    return [objekt for objekt in gc.get_objects() if isinstance(objekt, klasse)]
