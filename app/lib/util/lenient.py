from typing import Any, Generic, TypeVar


T = TypeVar("T")


class Lenient(Generic[T]):
    """
    Wrapper class for an object to allow access to non existent attributes
    This is handy for use in templates where we have an Optional[T]
    """

    def __init__(self, thing: T, default_value: Any = None):
        self.thing = thing
        self.default_value = default_value

    def __getattr__(self, field):
        """
        Get and cache attributes from the underlying Alchemy
        """
        if self.thing and hasattr(self.thing, field):
            return getattr(self.thing, field)

        return self.default_value


def lenient_wrap(thing: T, default_value: Any = None) -> Lenient[T]:
    return Lenient(thing, default_value)
