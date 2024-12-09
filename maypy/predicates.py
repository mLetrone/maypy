import operator
import re
from collections.abc import Callable, Container, Sized
from re import Pattern
from typing import Any, Protocol, TypeVar, Union, overload

from maypy import Predicate

T = TypeVar("T")

__all__ = [
    "is_falsy",
    "is_truthy",
    "is_length",
    "is_empty",
    "is_blank_str",
    "equals",
    "contains",
    "one_of",
    "neg",
    "match_regex",
]

"""
Notes:
    Classes are used to have ``__repr__`` for debugging purpose
"""


def is_falsy(val: T) -> bool:
    """Check if value is falsy.

    Examples:
        >>> assert is_falsy(0)
        >>> assert not is_falsy(12)
    """
    return not bool(val)


def is_truthy(val: T) -> bool:
    """Check if value is truthy.

    Examples:
        >>> assert is_truthy("maypy")
        >>> assert not is_truthy("")
    """
    return bool(val)


class _IsLength(Predicate[Sized]):
    """Predicate to check if the length of value is equal to the expected length."""

    def __init__(self, expected_len: int) -> None:
        self.expected_len = expected_len

    def __call__(self, val: Sized) -> bool:
        return len(val) == self.expected_len

    def __repr__(self) -> str:
        return f"<is_length predicate with expected at {self.expected_len}>"


def is_length(expected_len: int) -> Predicate[Sized]:
    """Return a predicate that checks if the len of value equals to the expected length provided.

    Examples:
        >>> is_length_at_5 = is_length(5)
        >>> assert is_length_at_5([1,3,3,4,5])
        >>> assert not is_length_at_5({5})
    """
    return _IsLength(expected_len)


def is_empty(val: Sized) -> bool:
    """Checks if the element is empty."""
    return _IsLength(0)(val)


def is_blank_str(val: str) -> bool:
    """Checks if the string is either empty or blank.

    Examples:
        >>> assert is_blank_str("")
        >>> assert is_blank_str("   ")
        >>> assert not is_blank_str("maypy")

    Args:
        val: string to verify
    """
    return is_empty(val.strip())


class _Neg(Predicate[T]):
    def __init__(self, predicate: Predicate[T]) -> None:
        self.predicate = predicate

    def __call__(self, val: T) -> bool:
        return not self.predicate(val)

    def __repr__(self) -> str:
        return f"<neg predicate of {self.predicate}>"


def neg(predicate: Predicate[T]) -> Predicate[T]:
    """Create a new predicate that is the negation of the provided.

    If the predicate would yield True, the negated one would yield False, and vice versa.

    Examples:
        >>> assert Maybe.of("maypy").filter(is_blank_str).is_empty()
        >>> assert Maybe.of("maypy").filter(neg(is_blank_str)).is_present()

    Args:
        predicate: preddicate to negate

    Returns:
        Negate predicate of the provided
    """
    return _Neg(predicate)


class _Equals(Predicate[T]):
    def __init__(self, expected: T) -> None:
        self.expected = expected

    def __call__(self, val: T) -> bool:
        return val == self.expected

    def __repr__(self) -> str:
        return f"<equals predicate with {self.expected}>"


def equals(expected: T) -> Predicate[T]:
    """Returns a predicate of equality with the provided value.

    Examples:
        >>> equal_maypy = equals("maypy")
        >>> assert equal_maypy("maypy")
        >>> assert not equal_maypy("mypy")

    Args:
        expected: expected equality
    """
    return _Equals(expected)


class _Contains(Predicate[Container[T]]):
    def __init__(self, *items: T) -> None:
        self.items = items

    def __call__(self, val: Container[T]) -> bool:
        return all(item in val for item in self.items)

    def __repr__(self) -> str:
        return f"<contains predicate with items: {self.items}>"


def contains(*items: T) -> Predicate[Container[T]]:
    """Returns a predicate to verify if value contains all the items.

    Examples:
        >>> contain = contains("1", "2", "3")
        >>> assert contain(["1", "2", "3", "4"])
        >>> assert contain("456123")

    Args:
        items: items to check presence
    Raises:
        ValueError: if no item has been passed
    """
    if is_empty(items):
        raise ValueError("At least one item is required")
    return _Contains(*items)


class _OneOf(Predicate[T]):
    def __init__(self, options: Container[T]) -> None:
        self.options = options

    def __call__(self, val: T) -> bool:
        return val in self.options

    def __repr__(self) -> str:
        return f"<one_of predicate with options {self.options}>"


def one_of(options: Container[T]) -> Predicate[T]:
    """Returns a predicate to check if value is one of these options.

    Examples:
        >>> option = one_of(["foo", "bar"])
        >>> assert option("foo")
        >>> assert option("bar")
        >>> assert not option("maypy")
    """
    return _OneOf(options)


class _MatchRegex(Predicate[str]):
    def __init__(self, pattern: re.Pattern[str]) -> None:
        self.pattern = pattern

    def __call__(self, val: str) -> bool:
        return bool(self.pattern.match(val))

    def __repr__(self) -> str:
        return f"<match regex predicate with pattern {self.pattern}]>"


@overload
def match_regex(regex: re.Pattern[str]) -> Predicate[str]:
    pass


@overload
def match_regex(regex: str, flags: Union[re.RegexFlag, int] = 0) -> Predicate[str]:
    pass


def match_regex(
    regex: Union[re.Pattern[str], str], flags: Union[re.RegexFlag, int] = 0
) -> Predicate[str]:
    """Returns a predicate that checks if value match the regex pattern provided.

    Args:
        regex: regex to match (either a string or a Pattern)
        flags: regex flags; should bot be passed with a pattern.

    Raises:
        TypeError: when passing flags whereas a `Pattern` have been passed
    """
    if isinstance(regex, Pattern):
        if flags:
            raise TypeError(
                "'flags' can only be used with a string pattern; used the flags in re.compile() instead"
            )
        return _MatchRegex(regex)

    return _MatchRegex(re.compile(regex, flags))


class Comparison(Protocol):
    def __le__(self, other: Any) -> bool: ...
    def __lt__(self, other: Any) -> bool: ...
    def __ge__(self, other: Any) -> bool: ...
    def __gt__(self, other: Any) -> bool: ...


class _Comparator(Predicate[Comparison]):
    def __init__(
        self,
        bound: Comparison,
        comp_operator: Callable[[Comparison, Comparison], bool],
        operator: str,
    ) -> None:
        self.comp_operator = comp_operator
        self.bound = bound
        self.operator = operator

    def __call__(self, val: Comparison) -> bool:
        return self.comp_operator(val, self.bound)

    def __repr__(self) -> str:
        return f"<comparison predicate x {self.operator} {self.bound}>"


def gt(bound: Comparison) -> Predicate[Comparison]:
    """Returns a predicate corresponding to x > bound."""
    return _Comparator(bound, operator.gt, ">")


def ge(bound: Comparison) -> Predicate[Comparison]:
    """Returns a predicate corresponding to x >= bound."""
    return _Comparator(bound, operator.ge, ">=")


def lt(bound: Comparison) -> Predicate[Comparison]:
    """Returns a predicate corresponding to x < bound."""
    return _Comparator(bound, operator.lt, "<")


def le(bound: Comparison) -> Predicate[Comparison]:
    """Returns a predicate corresponding to x <= bound."""
    return _Comparator(bound, operator.le, "<=")


class _Between(Predicate[Comparison]):
    def __init__(self, inf_bound: Comparison, sup_bound: Comparison, exclude_bound: bool) -> None:
        self.inf_bound = inf_bound
        self.sup_bound = sup_bound
        self.exclude_bound = exclude_bound

    def __call__(self, val: Comparison) -> bool:
        if self.exclude_bound:
            return self.inf_bound < val < self.sup_bound

        return self.inf_bound <= val <= self.sup_bound

    def __repr__(self) -> str:
        op = "<" if self.exclude_bound else "<="
        return f"<between predicate {self.inf_bound} {op} x {op} {self.sup_bound}>"


def between(
    inf_bound: Comparison, sup_bound: Comparison, exclude: bool = False
) -> Predicate[Comparison]:
    """Returns a between predicate.

    Corresponding to inf_bound < x < sup_bound if exclude,
    otherwise inf_bound <= x <= sup_bound.
    """
    return _Between(inf_bound, sup_bound, exclude)
