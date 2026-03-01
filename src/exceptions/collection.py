class BaseCollectionException(Exception):

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "Something went wrong during Collection operation"
        super().__init__(message)


class CollectionNotExistError(BaseCollectionException):
    """Exception raised when collection not found"""

    pass
