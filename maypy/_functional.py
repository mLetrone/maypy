from typing import Callable, TypeVar

T = TypeVar("T", contravariant=True)
V = TypeVar("V", covariant=True)

Predicate = Callable[[T], bool]
Mapper = Callable[[T], V]
Supplier = Callable[[], T]
