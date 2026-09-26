"""errors.py - Simple custom errors. lambda_function.py turns each into an HTTP status."""


class ValidationError(Exception):
    """The request is wrong (missing / invalid data). -> HTTP 400"""


class NotFoundError(Exception):
    """Something asked for does not exist. -> HTTP 404"""


class ServiceUnavailableError(Exception):
    """An AWS service (DynamoDB / S3) failed. -> HTTP 503"""
