class BaseUserException(Exception):

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "Something went wrong during user operation"
        super().__init__(message)


class IncorrectPasswordError(BaseUserException):
    pass


class IncorrectLoginError(BaseUserException):
    pass


class UserAlreadyExistError(BaseUserException):
    pass


class UserNotExistError(BaseUserException):
    pass


class UserGroupNotExistError(BaseUserException):
    pass


class IncorrectCredentialsError(BaseUserException):
    pass


class UserPermissionDeniedError(BaseUserException):
    pass


class InsufficientBalanceError(BaseUserException):
    pass
