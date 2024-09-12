from typing import Any, Callable, Dict

import pytest

from maypy import Supplier


def create() -> Dict[str, str]:
    return {"a": "test"}


@pytest.mark.parametrize("supplier", [create, lambda: [1], list])
def test_is_supplier(supplier: Callable[..., Any]) -> None:
    assert isinstance(supplier, Supplier)


@pytest.mark.parametrize("value", [{}, [1], ""])
def test_is_not_supplier(value: Any) -> None:
    assert not isinstance(value, Supplier)
