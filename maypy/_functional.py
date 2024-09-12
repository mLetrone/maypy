from typing import Protocol, TypeVar, runtime_checkable

"""
Notes:
    All of the functionals represent callables

    - Predicate -> Callable[[T], bool]
    - Mapper -> Callable[[T], V]
    - Supplier -> Callable[[], V]
"""


T = TypeVar("T", contravariant=True)
V = TypeVar("V", covariant=True)


@runtime_checkable
class Predicate(Protocol[T]):
    """Protocol describing predicate function.

    The corresponding signature is `Callable[[T], bool]`.

    Its goal is to verify if a value `T` match the conditions define.
    (can be a named function or lambda function).

    Examples:
        >>> lambda string: bool(string) and bool(string.strip())
        >>> # OR
        >>> from typing import Sequence
        >>>
        >>> def is_empty(seq: Sequence) -> bool:
        >>>     return len(seq) == 0
    """

    def __call__(self, val: T) -> bool:
        """Predicate logic."""


T_MAPPER = TypeVar("T_MAPPER", covariant=True)


@runtime_checkable
class Mapper(Protocol[T_MAPPER, V]):
    """Protocol describing mapper function.

    The corresponding signature is `Callable[[T], V]`.

    Its goal is to transform a value to another.
    (can be a named function or lambda function).

    Examples:
        >>> lambda val: val * 15
        >>> # OR
        >>> from numbers import Number
        >>> def multiply_by_ten(val: int) -> int:
        >>>     return 10 * val
    """

    def __call__(self, val: T) -> V:
        """Mapping logic."""


@runtime_checkable
class Supplier(Protocol[V]):
    """Protocol describing supplier function.

    The corresponding signature is `Callable[[], None]`.

    Its goal is to supply a new `V` value at invocation.
    (can be a named function or lambda function).

    Examples:
        >>> lambda: list(range(5))
        >>> # OR
        >>> def create_list() -> list[int]:
        >>>     return list(range(5))
    """

    def __call__(self) -> V:
        """Supply logic."""
