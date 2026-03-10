"""
Version Registry: Central source of truth for all API version metadata,
deprecation timelines, migration guides, and compat shim configurations.
"""
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class VersionInfo:
    version: str
    status: str
    release_date: str
    sunset_date: Optional[str] = None
    deprecation_date: Optional[str] = None
    description: str = ""
    changelog: list = field(default_factory=list)
    breaking_changes: list = field(default_factory=list)
    new_features: list = field(default_factory=list)


@dataclass
class MigrationGuide:
    from_version: str
    to_version: str
    steps: list = field(default_factory=list)
    field_mappings: dict = field(default_factory=dict)
    breaking_changes: list = field(default_factory=list)
    estimated_effort: str = "1-2 hours"


class VersionRegistry:
    def __init__(self):
        self._versions: dict[str, VersionInfo] = {}
        self._migration_guides: dict[str, MigrationGuide] = {}
        self._initialize()

    def _initialize(self):
        self._versions["v1"] = VersionInfo(
            version="v1", status="deprecated",
            release_date="2024-01-15", deprecation_date="2025-03-01",
            sunset_date="2025-12-31",
            description="Original REST API. Supports users, teams, basic auth, and metrics.",
            changelog=["2024-01-15: Initial release","2024-06-01: Added team endpoints","2024-09-01: Added pagination support"],
            breaking_changes=[], new_features=[],
        )
        self._versions["v2"] = VersionInfo(
            version="v2", status="stable", release_date="2025-01-01",
            description="Current version. Adds analytics, webhooks, advanced filtering, cursor pagination, and structured error responses.",
            changelog=["2025-01-01: GA release","2025-02-01: Added webhook support","2025-04-01: Cursor-based pagination","2025-05-01: Analytics endpoints"],
            breaking_changes=["users.name split into first_name + last_name","Pagination changed from offset to cursor-based","Error format unified to {code, message, details}","teams.member_count renamed to member_total"],
            new_features=["Webhook subscriptions","Cursor pagination","Analytics endpoints","Structured errors","Rate limit headers"],
        )
        self._versions["v3"] = VersionInfo(
            version="v3", status="beta", release_date="2025-06-01",
            description="Beta. GraphQL-inspired field selection, real-time subscriptions via SSE.",
            changelog=["2025-06-01: Beta release"],
            new_features=["Field selection via ?fields= param","Server-Sent Events subscriptions","Batch operations"],
        )
        self._migration_guides["v1→v2"] = MigrationGuide(
            from_version="v1", to_version="v2", estimated_effort="2-4 hours",
            field_mappings={
                "users.name": "users.first_name + users.last_name",
                "teams.member_count": "teams.member_total",
                "pagination.offset": "pagination.cursor",
                "pagination.limit": "pagination.per_page",
                "error.message": "error.code + error.message + error.details",
            },
            breaking_changes=[
                "User name field split: users.name → {first_name, last_name}",
                "Pagination: offset/page → cursor-based",
                "Error format: {message} → {code, message, details, request_id}",
                "Team membership: member_count → member_total",
            ],
            steps=[
                {"order":1,"title":"Update authentication headers","description":"No auth changes — Bearer tokens remain compatible","code":"Authorization: Bearer <token>  # unchanged"},
                {"order":2,"title":"Update base URL","description":"Change /api/v1/ to /api/v2/ in all calls","code":"BASE_URL = 'https://api.example.com/api/v2'"},
                {"order":3,"title":"Fix user name handling","description":"Split name field into first_name and last_name","code":"first_name, last_name = user['name'].split(' ', 1)"},
                {"order":4,"title":"Update pagination logic","description":"Replace offset/page with cursor-based pagination","code":"next_page = response['pagination']['next_cursor']"},
                {"order":5,"title":"Update error handling","description":"Parse new structured error format","code":"error_code = err['code']; details = err.get('details', [])"},
            ],
        )
        self._migration_guides["v2→v3"] = MigrationGuide(
            from_version="v2", to_version="v3", estimated_effort="1-2 hours",
            breaking_changes=["Response envelope changed to {data, meta, links}"],
            steps=[
                {"order":1,"title":"Add field selection","description":"Optionally use ?fields= to reduce payload","code":"GET /api/v3/users?fields=id,email,first_name"},
                {"order":2,"title":"Update response parsing","description":"Unwrap from data key","code":"users = response['data']"},
            ],
        )

    def get_version(self, version: str) -> Optional[dict]:
        v = self._versions.get(version)
        return asdict(v) if v else None

    def get_all_versions(self) -> list:
        return [asdict(v) for v in self._versions.values()]

    def get_active_versions(self) -> list:
        return [v for v, i in self._versions.items() if i.status in ("stable","beta","deprecated")]

    def get_deprecated_versions(self) -> list:
        return [v for v, i in self._versions.items() if i.status == "deprecated"]

    def get_migration_guide(self, from_v: str, to_v: str) -> Optional[dict]:
        guide = self._migration_guides.get(f"{from_v}→{to_v}")
        return asdict(guide) if guide else None

    def get_version_status(self, version: str) -> Optional[str]:
        v = self._versions.get(version)
        return v.status if v else None

    def get_sunset_date(self, version: str) -> Optional[str]:
        v = self._versions.get(version)
        return v.sunset_date if v else None


version_registry = VersionRegistry()
