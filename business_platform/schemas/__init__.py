"""
Schemas package initializer.
Re-exports every schema so controllers/endpoints can import from
`business_platform.schemas` directly without knowing which module a
given schema lives in.
"""
from business_platform.schemas.base import (  # noqa: F401
    BaseSchema,
    PaginatedResponse,
    PaginationLinks,
    PaginationMeta,
)
from business_platform.schemas.user import (  # noqa: F401
    UserCreate,
    UserUpdate,
    UserResponse,
    Token,
    RefreshRequest,
)
from business_platform.schemas.business import (  # noqa: F401
    BusinessCreate,
    BusinessUpdate,
    BusinessResponse,
)
from business_platform.schemas.business_relationship import (  # noqa: F401
    BusinessRelationshipCreate,
    BusinessRelationshipUpdate,
    BusinessRelationshipResponse,
)
from business_platform.schemas.membership import (  # noqa: F401
    MembershipCreate,
    MembershipUpdate,
    MembershipResponse,
)
from business_platform.schemas.person import (  # noqa: F401
    PersonCreate,
    PersonUpdate,
    PersonResponse,
)
from business_platform.schemas.ownership import (  # noqa: F401
    OwnershipRecordCreate,
    OwnershipTransitionRequest,
    OwnershipRecordResponse,
    OwnershipTransitionResponse,
)
from business_platform.schemas.leader import (  # noqa: F401
    LeaderCreate,
    LeaderUpdate,
    LeaderResponse,
)
from business_platform.schemas.employee import (  # noqa: F401
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeTerminateRequest,
    EmployeeResponse,
    EmployeeHistoryResponse,
)
from business_platform.schemas.compensation import (  # noqa: F401
    CompensationRecordCreate,
    CompensationRecordUpdate,
    CompensationRecordResponse,
)
from business_platform.schemas.tax import (  # noqa: F401
    TaxProfileCreate,
    TaxProfileUpdate,
    TaxProfileResponse,
    TaxIdentifierCreate,
    TaxIdentifierResponse,
)
from business_platform.schemas.document import (  # noqa: F401
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentVersionCreate,
    DocumentVersionResponse,
)
from business_platform.schemas.event import (  # noqa: F401
    EventCreate,
    EventUpdate,
    EventResponse,
)
from business_platform.schemas.task import (  # noqa: F401
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)
from business_platform.schemas.financial import (  # noqa: F401
    FinancialAccountCreate,
    FinancialAccountUpdate,
    FinancialAccountResponse,
    FinancialTransactionCreate,
    FinancialTransactionUpdate,
    FinancialTransactionResponse,
)
from business_platform.schemas.contact import (  # noqa: F401
    ContactCreate,
    ContactUpdate,
    ContactResponse,
)
from business_platform.schemas.audit_log import AuditLogResponse  # noqa: F401
from business_platform.schemas.aggregates import (  # noqa: F401
    DashboardOverviewResponse,
    UpcomingItemResponse,
    CompensationSummaryResponse,
    FinancialSummaryResponse,
    PersonBusinessRelationshipResponse,
)
