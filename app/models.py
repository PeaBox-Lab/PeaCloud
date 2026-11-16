from pydantic import BaseModel, Field
from typing import Literal, Any
ProviderName=Literal['mock','aws','azure','gcp']
class Resource(BaseModel):
    id:str; provider:ProviderName; type:str; name:str; state:str; region:str; account:str
    tags:dict[str,str]=Field(default_factory=dict); metadata:dict[str,Any]=Field(default_factory=dict)
class ActionRequest(BaseModel): confirmation:str
class ConnectionTest(BaseModel): provider:ProviderName
class ConnectionProfile(BaseModel): provider:ProviderName; name:str; account_id:str=''; region:str=''; secret_ref:str|None=None
class SecretInput(BaseModel): name:str; value:str
class Operation(BaseModel):
    id:str; timestamp:str; user:str; provider:str; resource_id:str; action:str; status:str; detail:str
class ScheduleInput(BaseModel):
    resource_id:str; provider:ProviderName; action:Literal['start','stop','restart']; cron:str; enabled:bool=True
class ProfileWizardInput(BaseModel):
    provider:ProviderName; name:str; account_id:str=''; region:str=''; auth_method:Literal['environment','sso','managed_identity','workload_identity','adc']='environment'
class ScheduleRunInput(BaseModel):
    minute:int|None=None; hour:int|None=None; day:int|None=None; month:int|None=None; weekday:int|None=None
class ApprovalDecision(BaseModel):
    decision:Literal['approved','rejected']; comment:str=''
