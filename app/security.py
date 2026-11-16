import base64, hashlib, hmac, os, secrets

class SecretVault:
    """Small local encrypted vault using authenticated stream encryption primitives.
    Production deployments should replace this with a managed KMS/Vault backend.
    """
    def __init__(self):
        key=os.getenv('PEACLOUD_MASTER_KEY')
        self.key=hashlib.sha256((key or secrets.token_hex(32)).encode()).digest()
        self.ephemeral=not bool(key)
        self._store={}
    def put(self,name,value):
        nonce=secrets.token_bytes(16)
        stream=hashlib.pbkdf2_hmac('sha256',self.key,nonce,12000,dklen=len(value.encode()))
        cipher=bytes(a^b for a,b in zip(value.encode(),stream))
        mac=hmac.new(self.key,nonce+cipher,hashlib.sha256).digest()
        self._store[name]=base64.b64encode(nonce+mac+cipher).decode()
        return {'stored':True,'name':name,'ephemeral':self.ephemeral}
    def get(self,name):
        blob=base64.b64decode(self._store[name]);nonce,mac,cipher=blob[:16],blob[16:48],blob[48:]
        if not hmac.compare_digest(mac,hmac.new(self.key,nonce+cipher,hashlib.sha256).digest()): raise ValueError('Vault integrity check failed')
        stream=hashlib.pbkdf2_hmac('sha256',self.key,nonce,12000,dklen=len(cipher))
        return bytes(a^b for a,b in zip(cipher,stream)).decode()
    def names(self): return sorted(self._store)
