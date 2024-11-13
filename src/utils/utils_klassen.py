from typing import Type, TypeVar


T = TypeVar('T')


def suche_subklasse_by_klassenname(klasse: Type[T], klassenname: str) -> Type[T] | None:
    # TODO Test
    # Erstelle Generator und liefer mit next(genr, None) das 1. Element oder None
    return next((klasse for klasse in klasse.__subclasses__() if klasse.__name__ == klassenname), None)
