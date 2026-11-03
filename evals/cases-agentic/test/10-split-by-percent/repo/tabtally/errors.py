class TabtallyError(Exception):
    """Base class for errors that are reported to the user instead of crashing."""


class MoneyError(TabtallyError):
    """An amount or a split cannot be represented in whole cents."""


class StoreError(TabtallyError):
    """The expense file cannot be read."""
