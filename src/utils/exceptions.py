class AzureDevOpsAIException(Exception):
    """Base exception for Azure DevOps AI Assistant"""
    pass

class ConfigurationError(AzureDevOpsAIException):
    """Raised when there's a configuration error"""
    pass

class AuthenticationError(AzureDevOpsAIException):
    """Raised when authentication fails"""
    pass

class AzureDevOpsAPIError(AzureDevOpsAIException):
    """Raised when Azure DevOps API returns an error"""
    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

class LLMProviderError(AzureDevOpsAIException):
    """Raised when LLM provider returns an error"""
    def __init__(self, provider: str, message: str, status_code: int = None):
        super().__init__(f"{provider}: {message}")
        self.provider = provider
        self.status_code = status_code

class ValidationError(AzureDevOpsAIException):
    """Raised when input validation fails"""
    pass

class WorkItemNotFoundError(AzureDevOpsAIException):
    """Raised when a work item is not found"""
    def __init__(self, work_item_id: int):
        super().__init__(f"Work item {work_item_id} not found")
        self.work_item_id = work_item_id

class BoardNotFoundError(AzureDevOpsAIException):
    """Raised when a board is not found"""
    def __init__(self, board_id: str):
        super().__init__(f"Board {board_id} not found")
        self.board_id = board_id 