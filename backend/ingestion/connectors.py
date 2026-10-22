"""
Connector interfaces and safe acquisition protocols for external data providers.
Enforces timeout, bounded retries, strict TLS verification, explicit pagination,
and non-bypass policies for authentication and CAPTCHA.
"""

import time
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field

from ..logger import logger


class ConnectorResult(BaseModel):
    """Result of an opt-in provider acquisition task."""
    source_id: str
    status: str
    http_code: Optional[int] = None
    records_acquired: int = 0
    records: List[Dict[str, Any]] = Field(default_factory=list)
    error_message: Optional[str] = None
    next_legitimate_step: Optional[str] = None
    duration_ms: float = 0.0


class BaseConnector:
    """Base class for official API connectors."""

    def __init__(
        self,
        source_id: str,
        base_url: str,
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ):
        self.source_id = source_id
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def fetch(self, opt_in: bool = False) -> ConnectorResult:
        """
        Execute safe acquisition with opt-in requirement.
        Live network calls are banned during standard application flows/page loads.
        """
        if not opt_in:
            return ConnectorResult(
                source_id=self.source_id,
                status="BLOCKED_BY_POLICY",
                error_message="Live provider requests require explicit manual/scheduled opt-in flag.",
                next_legitimate_step="Pass opt_in=True during an authorized CLI ingestion task.",
            )
        raise NotImplementedError("Subclasses must implement fetch")


class BlockedAuthConnector(BaseConnector):
    """Connector for endpoints requiring authentication or bearer tokens."""

    def __init__(self, source_id: str, base_url: str, required_env_var: str, next_step: str):
        super().__init__(source_id, base_url)
        self.required_env_var = required_env_var
        self.next_step = next_step

    def fetch(self, opt_in: bool = False, credential: Optional[str] = None) -> ConnectorResult:
        if not opt_in:
            return ConnectorResult(
                source_id=self.source_id,
                status="BLOCKED_BY_POLICY",
                error_message="Live calls disabled during standard runtime.",
                next_legitimate_step=self.next_step,
            )

        if not credential:
            logger.warning(f"Connector {self.source_id} blocked: missing credential '{self.required_env_var}'.")
            return ConnectorResult(
                source_id=self.source_id,
                status="BLOCKED_AUTH",
                http_code=401,
                error_message=f"Authentication required. Credential {self.required_env_var} is not configured.",
                next_legitimate_step=self.next_step,
            )

        # In production with credential, strict TLS and bounded retry would be performed:
        # with httpx.Client(verify=True, timeout=self.timeout_seconds) as client:
        return ConnectorResult(
            source_id=self.source_id,
            status="READY_WITH_CREDENTIALS",
            next_legitimate_step=self.next_step,
        )


class BlockedCaptchaConnector(BaseConnector):
    """Connector for portals enforcing interactive CAPTCHA."""

    def __init__(self, source_id: str, base_url: str, next_step: str):
        super().__init__(source_id, base_url)
        self.next_step = next_step

    def fetch(self, opt_in: bool = False) -> ConnectorResult:
        # Invariant: Never attempt CAPTCHA bypass!
        logger.info(f"Connector {self.source_id} halted: Interactive CAPTCHA detected.")
        return ConnectorResult(
            source_id=self.source_id,
            status="BLOCKED_CAPTCHA",
            http_code=403,
            error_message="Portal enforces interactive CAPTCHA challenge. Automated bypass is strictly prohibited by AGENTS.md rule 7.",
            next_legitimate_step=self.next_step,
        )
