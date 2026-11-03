class AdminError(Exception):
    """Base class for errors the API layer turns into responses."""


class NotFound(AdminError):
    pass


class BadRequest(AdminError):
    pass
