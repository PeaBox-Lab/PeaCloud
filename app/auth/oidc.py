import os,time,json
from dataclasses import dataclass
from urllib.request import urlopen,Request
from fastapi import Header,HTTPException
import jwt
from jwt.algorithms import RSAAlgorithm
@dataclass
class Principal: subject:str; role:str; tenant:str; email:str|None=None
ROLE_ORDER={'viewer':0,'operator':1,'admin':2}
_cache={'keys':None,'expires':0}
def _dev(x_role,x_user,x_tenant):return Principal(x_user or 'demo',x_role or 'viewer',x_tenant or 'demo')
def _jwks():
    now=time.time()
    if _cache['keys'] and _cache['expires']>now:return _cache['keys']
    url=os.getenv('PEACLOUD_OIDC_JWKS_URL')
    if not url:raise HTTPException(503,'PEACLOUD_OIDC_JWKS_URL is required')
    try:
        with urlopen(Request(url,headers={'User-Agent':'PeaCloud/0.13'}),timeout=5) as r:data=json.load(r)
    except Exception as e:raise HTTPException(503,'Unable to retrieve OIDC signing keys') from e
    keys=data.get('keys',[])
    if not keys:raise HTTPException(503,'OIDC JWKS contains no keys')
    _cache.update(keys=keys,expires=now+300);return keys
def current_principal(authorization:str|None=Header(default=None),x_role:str|None=Header(default=None),x_user:str|None=Header(default=None),x_tenant:str|None=Header(default=None)):
    mode=os.getenv('PEACLOUD_AUTH_MODE','dev-header')
    if mode=='dev-header':return _dev(x_role,x_user,x_tenant)
    if mode!='oidc':raise HTTPException(500,'Unsupported authentication mode')
    if not authorization or not authorization.startswith('Bearer '):raise HTTPException(401,'Bearer token required')
    token=authorization[7:];issuer=os.getenv('PEACLOUD_OIDC_ISSUER');aud=os.getenv('PEACLOUD_OIDC_AUDIENCE')
    if not issuer or not aud:raise HTTPException(500,'OIDC issuer/audience not configured')
    try:
        h=jwt.get_unverified_header(token);kid=h.get('kid');alg=h.get('alg')
        if alg!='RS256' or not kid:raise HTTPException(401,'Unsupported token header')
        jwk=next((k for k in _jwks() if k.get('kid')==kid and k.get('kty')=='RSA'),None)
        if not jwk:raise HTTPException(401,'Signing key not found')
        key=RSAAlgorithm.from_jwk(json.dumps(jwk));d=jwt.decode(token,key=key,algorithms=['RS256'],audience=aud,issuer=issuer,options={'require':['exp','iat','sub']})
    except HTTPException:raise
    except jwt.PyJWTError as e:raise HTTPException(401,'Invalid access token') from e
    role=d.get('peacloud_role','viewer');tenant=d.get('tenant_id') or d.get('tid')
    if role not in ROLE_ORDER or not tenant:raise HTTPException(403,'Token lacks valid role or tenant')
    return Principal(d['sub'],role,tenant,d.get('email'))
def require_role(principal,minimum):
    if ROLE_ORDER.get(principal.role,-1)<ROLE_ORDER[minimum]:raise HTTPException(403,f'{minimum} role required')
