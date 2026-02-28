class BaseUserException(Exception):

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "Something went wrong during user operation"
        super().__init__(message)


class IncorrectPasswordError(BaseUserException):
    pass


class IncorrectLoginError(BaseUserException):
    pass


class UserAlreadyExist(BaseUserException):
    pass


class UserNotExist(BaseUserException):
    pass


class UserGroupNotExist(BaseUserException):
    pass


class IncorrectCredentials(BaseUserException):
    pass


class UserPermissionDenied(BaseUserException):
    pass


class InsufficientBalance(BaseUserException):
    pass
