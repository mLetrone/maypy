class MaybeException(Exception):
    """Base exception for Maybe."""


class EmptyMaybeException(MaybeException):
    """Exception warning that the maybe contains no value to get."""

    def __init__(self) -> None:
        super().__init__("The maybe wrapper contains no value")
