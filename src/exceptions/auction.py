class BaseAuctionException(Exception):

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "Something went wrong during Collection operation"
        super().__init__(message)


class AuctionAlreadyEndedError(BaseAuctionException):
    """Exception raised when user interacts with ended auction"""

    pass


class SelfBetNotAllowedError(BaseAuctionException):
    """Exception raised when user tries place a bet on his own lot"""

    pass


class BidBelowMinimumError(BaseAuctionException):
    """Exception raised when user tries to place a bid lower than the minimum required amount"""  # noqa

    pass
