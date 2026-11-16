from pydantic import BaseModel, Field
from typing import Literal, Any

ProviderName = Literal["mock", "aws", "azure", "gcp"]

class Resource(BaseModel):
    id: str
    provider: ProviderName
    type: str
    name: str
    state: str
    region: str
    account: str
    tags: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

class ActionRequest(BaseModel):
    confirmation: str

class ConnectionTest(BaseModel):
    provider: ProviderName

class Operation(BaseModel):
    id: str
    timestamp: str
    user: str
    provider: str
    resource_id: str
    action: str
    status: str
    detail: str
