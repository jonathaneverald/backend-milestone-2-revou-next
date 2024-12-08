from enum import Enum


class UserRoleEnum(Enum):
    admin = 1
    instructor = 2
    student = 3


class RoleStatusEnum(Enum):
    active = 1
    inactive = 2
    pending = 3


class AssesmentTypeEnum(Enum):
    essay = 1
    choices = 2


class EnrollStatusEnum(Enum):
    passed = 1
    pending = 2
    accepted = 3
