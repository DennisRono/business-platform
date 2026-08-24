from __future__ import annotations

from typing import Annotated, TypeAlias

from fastapi import Depends

from business_platform.dependencies.auth import CurrentUser, GetCurrentUser


async def require_system_admin(current_user: GetCurrentUser) -> CurrentUser:
    """TODO: enforce system-admin access here."""
    return current_user


async def require_business_access(current_user: GetCurrentUser) -> CurrentUser:
    """TODO: enforce caller membership-scoped business access here."""
    return current_user


async def require_business_owner_or_admin(current_user: GetCurrentUser) -> CurrentUser:
    """TODO: enforce business owner/admin access here."""
    return current_user


async def require_business_membership(current_user: GetCurrentUser) -> CurrentUser:
    """TODO: enforce business membership access here."""
    return current_user


async def require_cross_business_person_access(current_user: GetCurrentUser) -> CurrentUser:
    """TODO: enforce shared-business or explicit grant access for person reads."""
    return current_user


async def require_hr_payroll_or_finance(current_user: GetCurrentUser) -> CurrentUser:
    """TODO: enforce hr_payroll or finance access here."""
    return current_user


async def require_sensitive_data_access(current_user: GetCurrentUser) -> CurrentUser:
    """TODO: enforce sensitive-data grant and audit requirements here."""
    return current_user


async def require_audit_log_access(current_user: GetCurrentUser) -> CurrentUser:
    """TODO: enforce system-admin or business-auditor access here."""
    return current_user


async def require_user_update_access(current_user: GetCurrentUser) -> CurrentUser:
    """TODO: enforce self-or-admin user update access here."""
    return current_user


SystemAdminUser: TypeAlias = Annotated[CurrentUser, Depends(require_system_admin)]
BusinessAccessUser: TypeAlias = Annotated[CurrentUser, Depends(require_business_access)]
BusinessOwnerOrAdminUser: TypeAlias = Annotated[CurrentUser, Depends(require_business_owner_or_admin)]
BusinessMembershipUser: TypeAlias = Annotated[CurrentUser, Depends(require_business_membership)]
CrossBusinessPersonUser: TypeAlias = Annotated[CurrentUser, Depends(require_cross_business_person_access)]
HrPayrollOrFinanceUser: TypeAlias = Annotated[CurrentUser, Depends(require_hr_payroll_or_finance)]
SensitiveDataUser: TypeAlias = Annotated[CurrentUser, Depends(require_sensitive_data_access)]
AuditLogAccessUser: TypeAlias = Annotated[CurrentUser, Depends(require_audit_log_access)]
UserUpdateAccessUser: TypeAlias = Annotated[CurrentUser, Depends(require_user_update_access)]