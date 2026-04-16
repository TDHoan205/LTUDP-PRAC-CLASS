# =============================================================================
# Package exceptions - Chứa các custom exception cho hệ thống
# =============================================================================
# Mục đích: Tập trung tất cả các exception tùy chỉnh vào một nơi
# Khi import: from exceptions import EmployeeNotFoundError, InvalidSalaryError, ...
# =============================================================================

from .employee_exceptions import (
    EmployeeException,
    EmployeeNotFoundError,
    InvalidSalaryError,
    InvalidAgeError,
    ProjectAllocationError,
    DuplicateEmployeeError
)

__all__ = [
    'EmployeeException',
    'EmployeeNotFoundError',
    'InvalidSalaryError',
    'InvalidAgeError',
    'ProjectAllocationError',
    'DuplicateEmployeeError'
]
