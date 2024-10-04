"""Maypy package."""

from importlib.metadata import version

__version__ = version(__name__)

from ._exceptions import EmptyMaybeException, MaybeException
from ._functional import Mapper, Predicate, Supplier
from ._maybe import Empty, Maybe

__all__ = [
    "Maybe",
    "Mapper",
    "Supplier",
    "Predicate",
    "EmptyMaybeException",
    "MaybeException",
    "Empty",
    "predicates"
]
