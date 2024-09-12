The purpose of ___MayPy___ is to provide a type-level solution for representing and manipulating
optional values instead of None reference.
This away around, no need to worry about the optional value and testing it, before applying process on it.

There are two types of _Maybe_ container, either it contains a value or it is empty.

A Maybe object become empty when the value it should contain is `None`.

## Create Maybe objects

### Empty

There are 3 ways to have a empty _Maybe_.

```py
from maypy import Empty, Maybe

assert Maybe.of(None) == Maybe.empty() == Empty
```
!!! note
    `Maybe.of(None)` is here as an example, for readability use the others to instantiate an empty Maybe.


### Valuated

Valuated _Maybe_ is quite straightforward, provide some value whatever it is, as long as is not `None` to [`of`:octicons-link-external-16:](maybe.md#maypy._maybe.Maybe.of) .

```python
assert Maybe.of(12)
```

## Checking value presence

There are three methods to check if the value is present or not.

Either by using [`is_present`:octicons-link-external-16:](maybe.md#maypy._maybe.Maybe.is_present)
to know if the container has a value 
or use [`is_empty`:octicons-link-external-16:](maybe.md#maypy._maybe.Maybe.is_empty) to verify the absence of value.
Another approach is to examine the "truthiness" of _Maybe_.

=== "is_present"
    ```python
    name = Maybe.of("name")
    assert name.is_present()
    
    name = Maybe.empty()
    assert not name.is_present()
    ```

=== "is_empty"
    ```python 
    name = Maybe.of("name")
    assert not name.is_empty()
    
    name = Maybe.empty()
    assert name.is_empty()
    ```
=== "truthiness"
    ```python
    assert Maybe.of("name")

    assert not Maybe.empty()
    ```
## Get wrapped value

To retrieve the value contained inside a _Maybe_, the method [`get`:octicons-link-external-16:](maybe.md#maypy._maybe.Maybe.get)
returns it or raises an [`EmptyMaybeException`:octicons-link-external-16:](exceptions.md#maypy._exceptions.EmptyMaybeException).

```python
assert Maybe.of("Mathieu").get() == "Mathieu"
assert Maybe.empty().get()
>>> EmptyMaybeException
```

## Handle Emptiness
### Default value

When _Maybe_ is empty, it's possible to provide a default value using [`or_else`:octicons-link-external-16:](maybe.md#maypy._maybe.Maybe.or_else).
Taking either a value or a [`Supplier`:octicons-link-external-16:](functional.md#maypy._functional.Supplier) 
(with _mypy_ the value provide as default should be the same type as the hypothetical value wrapped).

=== "by value"
    ```python
    assert Maybe.empty().or_else(12) == 12
    
    assert Maybe.of("present").or_else("absent") == "present"
    ```

    !!! warning
        It is indeed possible to do this way in pur python.
    
        ```python
        assert ("present" or "absent) == "present"
    
        assert (None or 12) == 12
        ```
    
        However, it is using the "truthiness" of the first element, it does not mean that the element is None!
        
        ```python
        >>> assert (0 or 12) == 0
        >>> AssertionError
        ```

=== "by Supplier"
    ```python
    assert Maybe.empty().or_else(lambda: 12) == 12
    
    assert Maybe.of("present").or_else(lambda: "absent") == "present"
    ```

    !!! tips
        We may wonder what is the different between passing the function and calling it as the default value.
        The function is used only if _Maybe_ is empty, whereas in the other hands, it will be invoked no matter what.
    
        ```python
        def populate_data() -> list[str]:
            print("invocation of populate_data")
            return ["python", "c++", "c", "java"]
        
        assert Maybe.empty().or_else(populate_data) == ["python", "c++", "c", "java"]
        >>> "invocation of populate_data"
        assert Maybe.of(["ruby", "kotlin"]).or_else(populate_data) == ["ruby", "kotlin"]
        assert Maybe.of(["ruby", "kotlin"]).or_else(populate_data()) == ["ruby", "kotlin"]
        >>> "invocation of populate_data"
        ```

### Raise error

Another approach for handling value absence, is to raise a custom exception by 
[`or_else_raise`:octicons-link-external-16:](maybe.md#maypy._maybe.Maybe.or_else_raise) when _Maybe_ is empty.

```python
class CustomError(Exception):
    pass

assert Maybe.empty().or_else_raise(CustomError())
>>> CustomError
assert Maybe.of(12).or_else_raise(CustomError()) == 12
```

## Manipulating the value

!!! note
    In the further examples, I keep using lambda function to keep it simple and easy to read.
    It totally possible to use named function, no matter what you use as long as it respects the API contract.
    
    _By the way `mypy` will infer types even with lambda :tada:!!!_

### Filtering

It is possible to perform inline condition on our wrapped value with [`filter`:octicons-link-external-16:](maybe.md#maypy._maybe.Maybe.filter).
Taking a [`Predicate`:octicons-link-external-16:](functional.md#maypy._functional.Predicate), it will check if the value matches the predicate and returning _Maybe_ itself when passing, otherwise an empty _Maybe_ is returned.

```python
price = 999.99

assert Maybe.of(price).filter(lambda x: x <= 1000).is_present()
assert Maybe.of(price).filter(lambda x: x >= 1000).is_empty()
```

You may wonder why using it and what is the gain. Let's dive on a more concrete example!

You want to watch a movie, and you ony care about its release date. It should be in certain interval.

```python
from dataclasses import dataclass, field

@dataclass
class Movie:
    director: str
    title: str
    year: int
    genre: list[str] = field(default_factory=list)
    oscars: list[str] | None = field(default=None)
```

without _Maybe_:

```python
from maypy import Predicate


def interval_checker(start_year: int, end_year: int) -> Predicate[Movie]:
    def is_in_range(movie: Movie | None) -> bool:
        if movie is not None:
            return start_year <= movie.year <= end_year
        return False

    return is_in_range


movie = Movie("Luc Besson", "Taxi", 1998, ["comedy"])

assert interval_checker(1990, 2005)(movie)
assert not interval_checker(2000, 2020)(movie)
assert not interval_checker(2000, 2020)(None)
```

with _Maybe_:
```python

assert Maybe.of(movie).filter(lambda film: 1990 <= film.year <= 2005).is_present()
```

### Mapping

With a similar syntax, we can transform the value inside _Maybe_ using 
[`map`:octicons-link-external-16:](maybe.md#maypy._maybe.Maybe.map).

Reusing a last example, getting the number of oscars rewarding the movie.

```python
movie = Movie("Luc Besson", "Taxi", 1998, ["comedy"])

assert (
        Maybe.of(movie)
        .map(lambda film: movie.oscars)
        .map(lambda oscars: len(oscars))
        .or_else(0) == 0
)
```

It is powerful to chain _filter_ and _map_ together.
Like checking the correctness of an input by a user.

```python
VALID_BOOLS = ("y", "n", "yes", "no")

user_input = "y "

assert (
    Maybe.of(user_input)
    .map(lambda input_: input_.strip())
    .filter(lambda x: x in VALID_BOOLS)
    .is_present()
)
```

### Conditional action

The last method is [`if_present`:octicons-link-external-16:](maybe.md#maypy._maybe.Maybe.if_present),
it allows to perform some code, using a `Consumer` function (`Callable[[VALUE], None]`),
on the wrapped value if present, otherwise nothing will happen.

```python
Maybe.of("name").if_present(lambda val: print(val))
```

!!! warning
    To keep it functional, the function passed should not modify the value but only use it.
    Please use chaining of [`map`](#mapping) and get the value instead.



