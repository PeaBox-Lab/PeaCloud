import os
from dataclasses import dataclass
@dataclass(frozen=True)
class Settings:
    environment:str=os.getenv('PEACLOUD_ENV','development')
    allowed_origins:tuple[str,...]=tuple(x.strip() for x in os.getenv('PEACLOUD_ALLOWED_ORIGINS','http://localhost:5173').split(',') if x.strip())
    trust_proxy_headers:bool=os.getenv('PEACLOUD_TRUST_PROXY_HEADERS','false').lower()=='true'
    docs_enabled:bool=os.getenv('PEACLOUD_DOCS_ENABLED','true').lower()=='true'
    app_version:str='0.15.0'
settings=Settings()
