from pydantic import BaseModel,Field
from typing import Literal
Provider=Literal['mock','aws','azure','gcp']
class Action(BaseModel): confirmation:str
class BudgetIn(BaseModel): name:str; amount:float; thresholds:list[int]=Field(default_factory=lambda:[50,80,100])
class ResourceIn(BaseModel): provider:Provider='mock';resource_type:str='virtual_machine';name:str;region:str='india-north';environment:str='dev';size:str='small'
