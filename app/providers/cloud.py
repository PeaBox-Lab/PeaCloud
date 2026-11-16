import os
from app.models import Resource
from app.providers.base import Provider

class AWSProvider(Provider):
    name="aws"
    def _session(self):
        try:
            import boto3
        except ImportError as e: raise RuntimeError("Install requirements-cloud.txt for AWS support") from e
        return boto3.Session()
    def test_connection(self):
        s=self._session(); ident=s.client("sts").get_caller_identity()
        return {"ok":True,"provider":"aws","identity":ident.get("Arn"),"account":ident.get("Account")}
    def list_resources(self):
        s=self._session(); out=[]
        for region in s.get_available_regions("ec2"):
            try:
                ec2=s.client("ec2",region_name=region)
                for res in ec2.describe_instances(MaxResults=100).get("Reservations",[]):
                    for i in res.get("Instances",[]):
                        tags={t["Key"]:t["Value"] for t in i.get("Tags",[])}
                        out.append(Resource(id=i["InstanceId"],provider="aws",type="virtual_machine",name=tags.get("Name",i["InstanceId"]),state=i["State"]["Name"],region=region,account="current",tags=tags,metadata={"instance_type":i.get("InstanceType")}))
            except Exception: continue
        return out
    def act(self, resource_id, action):
        if os.getenv("PEACLOUD_ALLOW_CHANGES","false").lower()!="true": raise PermissionError("Real cloud changes are disabled")
        s=self._session()
        for region in s.get_available_regions("ec2"):
            ec2=s.client("ec2",region_name=region)
            try:
                if action=="start": ec2.start_instances(InstanceIds=[resource_id])
                elif action=="stop": ec2.stop_instances(InstanceIds=[resource_id])
                elif action=="restart": ec2.reboot_instances(InstanceIds=[resource_id])
                elif action=="snapshot":
                    i=ec2.describe_instances(InstanceIds=[resource_id])["Reservations"][0]["Instances"][0]
                    for b in i.get("BlockDeviceMappings",[]): ec2.create_snapshot(VolumeId=b["Ebs"]["VolumeId"],Description=f"PeaCloud snapshot for {resource_id}")
                else: raise ValueError("Unsupported action")
                return {"status":"submitted","message":f"{action} submitted in {region}"}
            except Exception: continue
        raise KeyError(resource_id)

class AzureProvider(Provider):
    name="azure"
    def _clients(self):
        try:
            from azure.identity import DefaultAzureCredential
            from azure.mgmt.compute import ComputeManagementClient
        except ImportError as e: raise RuntimeError("Install requirements-cloud.txt for Azure support") from e
        sub=os.getenv("AZURE_SUBSCRIPTION_ID")
        if not sub: raise RuntimeError("AZURE_SUBSCRIPTION_ID is required")
        return DefaultAzureCredential(),ComputeManagementClient(DefaultAzureCredential(),sub),sub
    def test_connection(self):
        _,c,sub=self._clients(); next(iter(c.virtual_machines.list_all()),None)
        return {"ok":True,"provider":"azure","identity":"DefaultAzureCredential","account":sub}
    def list_resources(self):
        _,c,sub=self._clients(); out=[]
        for vm in c.virtual_machines.list_all():
            rg=vm.id.split('/resourceGroups/')[1].split('/')[0]
            view=c.virtual_machines.instance_view(rg,vm.name)
            state=next((x.code.split('/')[-1] for x in view.statuses if x.code.startswith('PowerState/')),'unknown')
            out.append(Resource(id=vm.id,provider="azure",type="virtual_machine",name=vm.name,state=state,region=vm.location,account=sub,tags=vm.tags or {},metadata={"size":vm.hardware_profile.vm_size,"resource_group":rg}))
        return out
    def act(self, resource_id, action):
        if os.getenv("PEACLOUD_ALLOW_CHANGES","false").lower()!="true": raise PermissionError("Real cloud changes are disabled")
        _,c,_=self._clients(); rg=resource_id.split('/resourceGroups/')[1].split('/')[0]; name=resource_id.rsplit('/',1)[-1]
        ops={"start":c.virtual_machines.begin_start,"stop":c.virtual_machines.begin_deallocate,"restart":c.virtual_machines.begin_restart}
        if action not in ops: raise ValueError("Azure snapshot is not enabled in this MVP")
        ops[action](rg,name); return {"status":"submitted","message":f"{action} submitted"}

class GCPProvider(Provider):
    name="gcp"
    def _client(self):
        try: from google.cloud import compute_v1
        except ImportError as e: raise RuntimeError("Install requirements-cloud.txt for GCP support") from e
        project=os.getenv("GCP_PROJECT_ID")
        if not project: raise RuntimeError("GCP_PROJECT_ID is required")
        return compute_v1,compute_v1.InstancesClient(),project
    def test_connection(self):
        _,c,p=self._client(); list(c.aggregated_list(project=p))
        return {"ok":True,"provider":"gcp","identity":"Application Default Credentials","account":p}
    def list_resources(self):
        _,c,p=self._client(); out=[]
        for zone,scoped in c.aggregated_list(project=p):
            for vm in (scoped.instances or []):
                out.append(Resource(id=str(vm.id),provider="gcp",type="virtual_machine",name=vm.name,state=vm.status.lower(),region=zone.split('/')[-1],account=p,tags=dict(vm.labels or {}),metadata={"machine_type":vm.machine_type.split('/')[-1]}))
        return out
    def act(self, resource_id, action): raise ValueError("GCP mutations require zone-aware lookup and are deferred to v0.2.0")
