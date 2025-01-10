"""Maypy package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # metadata are missing
    __version__ = "undefined"

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
    "predicates",
]
