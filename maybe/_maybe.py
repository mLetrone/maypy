from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Optional, TypeVar, Union

from ._exceptions import EmptyMaybeException
from ._functional import Mapper, Predicate, Supplier

VALUE = TypeVar("VALUE")
OUTPUT = TypeVar("OUTPUT")


class Maybe(ABC, Generic[VALUE]):
    """Wrapper class inspired by the well-known Optional API from Java.

    A Maybe is container, a non-none value may be inside or may be not
    (hence the name Maybe as an alternative to Optional, which is already used by Python).

    If a value is present: `is_present` will return True and `get` will return the value.


    It useful when working with data that can be none.

    Examples:
        >>> import json
        >>> beer = json.loads(json_beer)
        >>> # Without maybe
        >>> price = beer.get("BeerPrice")
        >>> if price:
        >>>     if price > 0:
        >>>         price = convertDollarsToEuro(price)
        >>> else:
        >>>     raise MyCustomException()
        >>> #  with Maybe
        >>> Maybe.of(beer.get("BeerPrice")).
        >>>     filter(lambda price: price > 0).
        >>>     map(convertDollarsToEuro).
        >>>     or_else_raise(MyCustomException())
        >>>
    """

    @staticmethod
    def empty() -> "Maybe[Any]":
        """Returns a empty `Maybe` instance."""
        return _EmptyMaybe[Any]()

    @staticmethod
    def of(val: Optional[VALUE]) -> "Maybe[VALUE]":
        """Returns a `Maybe` instance depends on the value provided.

        If it's a none value, an empty `Maybe` will be returned.

        Params:
            val: the provided value to wrap.
        """
        if val is None:
            return _EmptyMaybe[VALUE]()
        return _ValuedMaybe[VALUE](val)

    @abstractmethod
    def get(self) -> VALUE:
        """Return the value if present, else raise EmptyElementException.

        Raises:
            EmptyElementException
        """

    @abstractmethod
    def filter(self, predicate: Predicate[VALUE]) -> "Maybe[VALUE]":
        """Filter the wrapped value (if present).

        If it matches the predicate, returns a Maybe describing the value,
        otherwise return an empty Maybe.
        """

    @abstractmethod
    def map(self, mapper: Mapper[VALUE, OUTPUT]) -> "Maybe[OUTPUT]":
        """Map the wrapped value (if present).

        Apply the given mapping function to the value.
        :return:
        """

    @abstractmethod
    def or_else(self, other: Union[VALUE, Supplier[VALUE]]) -> VALUE:
        """Returns the value if present, else return other.

        If other is a supplier, it returns the result of the invocation.
        """

    @abstractmethod
    def or_none(self) -> Optional[VALUE]:
        """Returns the value if present, else return other.

        If other is a supplier, it returns the result of the invocation.
        """

    @abstractmethod
    def or_else_raise(self, exception: Exception) -> VALUE:
        """Returns the value if present, otherwise raise the given exception."""

    @abstractmethod
    def is_present(self) -> bool:
        """Returns True if value is present, otherwise False."""

    @abstractmethod
    def is_empty(self) -> bool:
        """Returns True if value is not present, otherwise False."""

    @abstractmethod
    def if_present(self, consumer: Callable[[VALUE], None]) -> None:
        """Invoke the given consumer with the value if present, do nothing otherwise."""


class _ValuedMaybe(Maybe[VALUE]):
    """Private class defining the behavior of a valuated Maybe.

    Warnings:
        It should not be used outside of this file.
    """

    def __init__(self, value: VALUE) -> None:
        self.__value = value

    def get(self) -> VALUE:
        return self.__value

    def filter(self, predicate: Predicate[VALUE]) -> "Maybe[VALUE]":
        if predicate(self.__value):
            return self

        return Maybe.empty()

    def map(self, mapper: Mapper[VALUE, OUTPUT]) -> "Maybe[OUTPUT]":
        return Maybe.of(mapper(self.__value))

    def or_else(self, other: Union[VALUE, Supplier[VALUE]]) -> VALUE:
        return self.__value

    def or_none(self) -> Optional[VALUE]:
        return self.__value

    def or_else_raise(self, exception: Exception) -> VALUE:
        return self.__value

    def is_present(self) -> bool:
        return True

    def is_empty(self) -> bool:
        return False

    def if_present(self, consumer: Callable[[VALUE], None]) -> None:
        consumer(self.__value)

    def __bool__(self) -> bool:
        return True

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Maybe):
            return other.get().__eq__(self.get()) if other.is_present() else False  # type: ignore[no-any-return]
        return NotImplemented

    def __str__(self) -> str:
        return f"Maybe[{type(self.__value).__name__}]({self.__value})"


class _EmptyMaybe(Maybe[VALUE]):
    """Private class defining the behavior of a empty Maybe.

    Warnings:
        It should not be used outside of this file.
    """

    def get(self) -> VALUE:
        raise EmptyMaybeException()

    def filter(self, predicate: Predicate[VALUE]) -> "Maybe[VALUE]":
        return self

    def map(self, mapper: Mapper[VALUE, OUTPUT]) -> "Maybe[OUTPUT]":
        return _EmptyMaybe[OUTPUT]()

    def or_else(self, other: Union[VALUE, Supplier[VALUE]]) -> VALUE:
        if isinstance(other, Supplier):
            return other()
        return other

    def or_none(self) -> Optional[VALUE]:
        return None

    def or_else_raise(self, exception: Exception) -> VALUE:
        raise exception

    def is_present(self) -> bool:
        return False

    def is_empty(self) -> bool:
        return True

    def if_present(self, consumer: Callable[[VALUE], None]) -> None:
        """Do nothing."""

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Maybe):
            return False if other.is_present() else True
        return NotImplemented

    def __str__(self) -> str:
        return "Maybe[empty]"


Empty = Maybe.empty()
