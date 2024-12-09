import re
from datetime import datetime
from typing import Any, ClassVar, Sized

import pytest

from maypy.predicates import (
    between,
    contains,
    equals,
    ge,
    gt,
    is_blank_str,
    is_empty,
    is_falsy,
    is_length,
    is_truthy,
    le,
    lt,
    match_regex,
    neg,
    one_of,
)


class Library:
    def __init__(self, number_of_books: int) -> None:
        self.number_of_books = number_of_books

    def __len__(self) -> int:
        return self.number_of_books


class Person:
    pass


class TestPredicate:
    @pytest.mark.parametrize(
        ("length", "result"),
        [
            (0, False),
            (1, False),
            (2, False),
            (3, True),
            (10, False),
        ],
    )
    def test_is_length(self, length: int, result: bool) -> None:
        assert is_length(length)([1, 2, 3]) is result

    @pytest.mark.parametrize(
        ("sized", "result"),
        [
            ("", True),
            ([], True),
            ({}, True),
            (Library(0), True),
            ("not empty", False),
            ([1], False),
            (Library(3), False),
        ],
    )
    def test_is_empty(self, sized: Sized, result: bool) -> None:
        assert is_empty(sized) is result

    @pytest.mark.parametrize(
        ("string", "result"), [("", True), ("    ", True), ("   1", False), ("maypy", False)]
    )
    def test_is_empty_str(self, string: str, result: bool) -> None:
        assert is_blank_str(string) is result

    TRUTHINESS_TESTS: ClassVar = [
        (False, False),
        ("", False),
        (0, False),
        (None, False),
        ([], False),
        (True, True),
        ("maypy", True),
        ([1], True),
        (Person(), True),
    ]

    @pytest.mark.parametrize(("val", "result"), TRUTHINESS_TESTS)
    def test_is_truthy(self, val: Any, result: bool) -> None:
        assert is_truthy(val) is result

    @pytest.mark.parametrize(("val", "result"), TRUTHINESS_TESTS)
    def test_is_falsy(self, val: Any, result: bool) -> None:
        assert is_falsy(val) is (not result)

    def test_equals(self) -> None:
        equal = equals(5)
        assert not equal(2)
        assert equal(5)

    def test_contains(self) -> None:
        contain = contains("1", "2")

        assert contain(["1", "2"])
        assert contain("1245")
        assert not contain("45")

    def test_contains_should_raise_error_when_no_items_provided(self) -> None:
        with pytest.raises(ValueError, match="At least one item"):
            contains()

    def test_one_of(self) -> None:
        options = one_of(["toto", "titi", "lala"])

        assert options("toto")
        assert options("titi")
        assert options("lala")
        assert not options("maypy")

    def test_match_regex_when_passing_str(self) -> None:
        pattern = r"(\w+\s*)+maypy"

        regex = match_regex(pattern, re.IGNORECASE)

        assert regex("ALL HAIL MAYPY")
        assert regex("all hail maypy")
        assert not regex("Invalid")

    def test_match_regex_when_passing_pattern(self) -> None:
        pattern = re.compile(r"maypy v\d+\.\d+.\d+")

        regex = match_regex(pattern)

        assert regex("maypy v1.2.3")
        assert not regex("v1.2.3")

    def test_match_regex_should_raise_error_when_passing_flags_with_pattern(self) -> None:
        with pytest.raises(TypeError, match="'flags' can only"):
            match_regex(re.compile(".*"), re.IGNORECASE)  # type: ignore[call-overload]

    def test_neg(self) -> None:
        assert not neg(is_empty)([])
        assert neg(is_empty)([1])
        assert not neg(lambda _x: True)("")

    def test_gt(self) -> None:
        greater_than_5 = gt(5)

        assert greater_than_5(10)
        assert not greater_than_5(2)
        assert not greater_than_5(5)

    def test_ge(self) -> None:
        ge_5 = ge(5)

        assert ge_5(10)
        assert ge_5(5)
        assert not ge_5(2)

    def test_lt(self) -> None:
        lt_5 = lt(5)

        assert not lt_5(10)
        assert not lt_5(5)
        assert lt_5(2)

    def test_le(self) -> None:
        le_5 = le(5)

        assert not le_5(10)
        assert le_5(5)
        assert le_5(2)

    def test_comparison_with_date(self) -> None:
        date = datetime(2024, 1, 1)
        le_2024_01_01 = le(date)

        assert le_2024_01_01(datetime(2023, 1, 1))
        assert le_2024_01_01(date)
        assert not le_2024_01_01(datetime(2024, 2, 28))

    def test_between(self) -> None:
        between_0_10 = between(0, 10)

        assert between_0_10(6)
        assert between_0_10(10)
        assert between_0_10(0)
        assert not between_0_10(-1.67)
        assert not between_0_10(11)

    def test_between_exclusive(self) -> None:
        between_0_10 = between(0, 10, True)

        assert between_0_10(6)
        assert not between_0_10(10)
        assert not between_0_10(0)
        assert not between_0_10(-1.67)
        assert not between_0_10(11)
