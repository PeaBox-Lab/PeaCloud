from app.providers.base import Provider
from app.models import Resource

class MockProvider(Provider):
    name="mock"
    def __init__(self):
        self.resources={r.id:r for r in [
            Resource(id="vm-demo-01",provider="mock",type="virtual_machine",name="payments-api",state="running",region="india-north",account="demo",tags={"env":"dev","owner":"platform"},metadata={"size":"2 vCPU / 8 GB","os":"Ubuntu 24.04"}),
            Resource(id="vm-demo-02",provider="mock",type="virtual_machine",name="hris-worker",state="stopped",region="india-north",account="demo",tags={"env":"test"},metadata={"size":"2 vCPU / 4 GB","os":"Windows Server 2022"}),
            Resource(id="obj-demo-01",provider="mock",type="object_storage",name="peaops-artifacts",state="available",region="india-south",account="demo",tags={"env":"shared"},metadata={"objects":1284,"encrypted":True}),
            Resource(id="db-demo-01",provider="mock",type="database",name="peawork-db",state="available",region="india-north",account="demo",tags={"env":"dev"},metadata={"engine":"PostgreSQL 16","backup":"enabled"}),
        ]}
    def test_connection(self): return {"ok":True,"provider":self.name,"identity":"mock-operator","message":"Demo cloud is ready"}
    def list_resources(self): return list(self.resources.values())
    def act(self, resource_id, action):
        r=self.resources.get(resource_id)
        if not r: raise KeyError(resource_id)
        if r.type!="virtual_machine": raise ValueError("This MVP supports actions only on virtual machines")
        states={"start":"running","stop":"stopped","restart":"running","snapshot":r.state}
        if action not in states: raise ValueError("Unsupported action")
        r.state=states[action]
        return {"status":"succeeded","state":r.state,"message":f"{action} completed for {r.name}"}
