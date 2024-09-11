<div align="center" style="margin:40px;">
  <img src="https://raw.githubusercontent.com/MLetrone/maypy/master/docs/pages/assets/img/logo.png" alt="Maypy logo" style="margin-bottom: 20px; border-radius: 2rem" width="300"/>
<!-- --8<-- [start:overview-header] -->

  [![Language](https://img.shields.io/badge/Language-python≥3.9-3776ab?style=flat-square&logo=Python)](https://www.python.org/)
  ![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
  ![Style](https://img.shields.io/badge/Style-ruff-9a9a9a?style=flat-square)
  ![Lint](https://img.shields.io/badge/Lint-ruff,%20mypy-brightgreen?style=flat-square)
  [![Tests](https://github.com/MLetrone/maypy/actions/workflows/check.yml/badge.svg?branch=master)](https://github.com/MLetrone/maypy/actions/workflows/check.yml)

<!-- --8<-- [end:overview-header] -->

---

Source Code: [https://github.com/MLetrone/maypy](https://github.com/MLetrone/maypy)

documentation: [https://mletrone.github.io/maypy](https://mletrone.github.io/maypy/)

---
</div>
<!-- --8<-- [start:overview-body] -->

Maypy is python implementation of the well known Java [Optional](https://docs.oracle.com/en%2Fjava%2Fjavase%2F11%2Fdocs%2Fapi%2F%2F/java.base/java/util/Optional.html) API.
It's designed to help you handle potential `None` values, reducing error from `NoneType`.

## Features :
- Brings functional programming
- Easy to use
- Fully typed and compatible with `mypy` !
- Lightweight

<!-- --8<-- [end:overview-body] -->
## installation

```shell
pip install maypy
```

That's all ! _Ready to use_

## Usage

### Description

<!-- --8<-- [start:description] -->

It's not rare to handle return from function that _maybe_ either a value or None.
Like `.get` from a dictionary, results from api or ORM etc.
With no more `if value is None` with `MayPy`, encapsulate your value and do what you want to.

MayPy brings `Maybe` a wrapper (container), it is either **empty** if the value passed was `None` or valuated,
in this case it contains the value, and we can perform operation on it.

<!-- --8<-- [end:description] -->

### Examples

Checking value presence:
```python
from maypy import Maybe

assert Maybe.empty().is_empty()
assert Maybe.of(None).is_empty()
assert Maybe.of("value").is_present()
```
Using chaining operation over wrapped value:
```python
from maypy import Maybe
from typing import List, Optional


def convert_to_celsius(fahrenheit: float) -> float:
  return (fahrenheit - 32) * 5 / 9


fahrenheit_temperatures: List[Optional[float]] = [32.45, None, 26.6, 100, 72, None, 10]

for temp in fahrenheit_temperatures:
  Maybe.of(temp).map(convert_to_celsius).filter(lambda celsius: celsius > 0)
```

Defining return from database result:

````python
from dataclasses import dataclass
from enum import StrEnum, unique

from maypy import Maybe
from pydantic import BaseModel
from sqlalchemy.orm import Session


@unique
class Gender(StrEnum):
  MALE = "M"
  FEMALE = "F"
  UNKNOWN = "X"


@dataclass
class User:
  id: str
  email: str
  gender: Gender


class UserEntity(BaseModel):
  id: str
  email: str
  gender: str

  class Config:
    orm_mode = True


def get_user(db: Session, user_id: str) -> Maybe[User]:
  return Maybe.of(db.query(UserEntity).filter(UserEntity.id == user_id).first()).map(to_domain)


def to_domain(user_dto: UserEntity) -> User:
  return User(
    id=user_dto.id,
    email=user_dto.email,
    gender=Gender(user_dto.gender)
  )


user = get_user(db, "481efz4x1d").or_else_raise(Exception("User id<481efz4x1d> not found"))
````