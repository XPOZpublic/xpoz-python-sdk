class XpozError(Exception):
    pass


class AuthenticationError(XpozError):
    pass


class ConnectionError(XpozError):
    pass


class OperationTimeoutError(XpozError):
    def __init__(self, operation_id: str, elapsed_seconds: float):
        self.operation_id = operation_id
        self.elapsed_seconds = elapsed_seconds
        super().__init__(
            f"Operation {operation_id} timed out after {elapsed_seconds:.0f}s"
        )


class OperationFailedError(XpozError):
    def __init__(self, operation_id: str, error: str):
        self.operation_id = operation_id
        self.error = error
        super().__init__(f"Operation {operation_id} failed: {error}")


class OperationCancelledError(XpozError):
    def __init__(self, operation_id: str):
        self.operation_id = operation_id
        super().__init__(f"Operation {operation_id} was cancelled")


class NotFoundError(XpozError):
    pass


class ValidationError(XpozError):
    pass
