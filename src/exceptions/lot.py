class BaseLotException(Exception):

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "Something went wrong during Lot operation"
        super().__init__(message)


class LotItemNotExistsError(BaseLotException):
    """Exception raised when lot item not found"""

    pass


class LotItemAlreadyOnSaleError(BaseLotException):
    """Exception raised when lot item already on auction"""

    pass
