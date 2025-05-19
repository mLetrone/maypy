from functools import partial
from typing import List

import pytest

from maypy import EMPTY, EmptyMaybeException, Maybe, maybe
from maypy import EMPTY, EmptyMaybeException, Maybe, MaybeException, Some, maybe


class MaybeTestException(Exception):
    pass


class TestMaybe:
    def test_init_some_with_none_should_raise_error(self) -> None:
        with pytest.raises(MaybeException):
            Some(None)

    def test_of_should_be_present_for_valuated_maybe(self) -> None:
        assert Maybe.of(2).is_present() is True

    def test_of_should_be_empty_for_none_valuated_maybe(self) -> None:
        assert maybe(None).is_present() is False
        assert Maybe.of(None).is_present() is False

    def test_empty_should_be_empty_maybe(self) -> None:
        assert Maybe.empty().is_present() is False

    def test_is_empty_should_be_falsy_when_present(self) -> None:
        assert Maybe.of("str").is_empty() is False

    def test_is_empty_should_be_empty_maybe(self) -> None:
        assert Maybe.empty().is_empty() is True

    def test_get_should_return_wrapped_value(self) -> None:
        assert maybe(False).get() is False

    def test_get_should_raise_empty_error_when_empty_maybe(self) -> None:
        with pytest.raises(EmptyMaybeException):
            EMPTY.get()

    def test_filter_should_not_filter_value_when_match(self) -> None:
        def equality(val: str) -> bool:
            return val == "value"

        assert maybe("value").filter(equality).get() == "value"

    def test_filter_should_filter_value_when_unmatch(self) -> None:
        assert maybe("value").filter(lambda val: len(val) == 1).is_present() is False

    def test_filter_on_empty_maybe_should_be_empty(self) -> None:
        assert Maybe[int].empty().filter(lambda _: True).is_present() is False

    def test_map_should_map_empty_to_empty(self) -> None:
        assert EMPTY.map(lambda val: 12).is_present() is False

    def test_map_should_map_valuated(self) -> None:
        assert maybe("LOLO").map(lambda val: f"new {val}").get() == "new LOLO"

    def test_or_else_should_get_alternative_value_on_empty(self) -> None:
        assert Maybe.empty().or_else("alternative") == "alternative"

    def test_or_else_should_invoke_supplier_for_alternative_value_on_empty(self) -> None:
        assert Maybe.empty().or_else(list) == []

        assert Maybe.empty().or_else(list) is not Maybe.empty().or_else(list)

    def test_or_else_should_get_initial_value_on_valuated_maybe(self) -> None:
        assert maybe("value").or_else("alternative") == "value"

    def test_or_else_raise_should_raise_error_from_empty_maybe(self) -> None:
        with pytest.raises(MaybeTestException):
            Maybe.empty().or_else_raise(MaybeTestException())

    def test_or_else_raise_should_return_initial_value_from_valuated_maybe(self) -> None:
        assert maybe(2345).or_else_raise(MaybeTestException()) == 2345

    def test_if_present_should_do_nothing_with_empty_maybe(self) -> None:
        ok: List[int] = []
        maybe(1).if_present(partial(list.append, ok))
        assert ok == [1]

    def test_or_none_when_valuated_should_return_value(self) -> None:
        assert maybe(45).or_none() == 45

    def test_or_none_when_empty_should_be_none(self) -> None:
        assert Maybe.empty().or_none() is None

    def test__eq__(self) -> None:
        assert Maybe.empty() == Maybe.empty()
        assert Maybe.empty() == EMPTY
        assert maybe(45) == maybe(5).map(lambda x: x * 9)

    def test__eq__should_be_falsy_with_unsupported_type(self) -> None:
        assert not maybe(45) == 45  # type: ignore[comparison-overlap]
        assert not Maybe.empty() == ""  # type: ignore[comparison-overlap]

    def test__bool__(self) -> None:
        assert not Maybe.empty()
        assert maybe("")

    def test__str__(self) -> None:
        assert str(maybe("test")) == "Maybe[str](test)"
        assert str(maybe([12, 45])) == "Maybe[list]([12, 45])"
        assert str(Maybe.empty()) == "Maybe[empty]"
