class XpozError(Exception):
    pass


class AuthenticationError(XpozError):
    pass


class XpozConnectionError(XpozError):
    pass


class OperationTimeoutError(XpozError):
    def __init__(self, operation_id: str, elapsed_seconds: float):
        self.operation_id = operation_id
        self.elapsed_seconds = elapsed_seconds
        super().__init__(
            f"Operation {operation_id} timed out after {elapsed_seconds:.0f}s"
        )


class OperationFailedError(XpozError):
    def __init__(
        self,
        error: str,
        *,
        operation_id: str | None = None,
        message: str | None = None,
        category: str | None = None,
    ):
        self.operation_id = operation_id
        self.error = error
        self.message = message
        self.category = category
        prefix = f"Operation {operation_id}" if operation_id else "Operation"
        super().__init__(f"{prefix} failed: {error}")


class OperationCancelledError(XpozError):
    def __init__(self, operation_id: str | None = None):
        self.operation_id = operation_id
        target = f"Operation {operation_id}" if operation_id else "Operation"
        super().__init__(f"{target} was cancelled")


class NotFoundError(XpozError):
    pass


class ValidationError(XpozError):
    pass
