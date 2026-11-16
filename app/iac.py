import json, os, shutil, subprocess, tempfile
from pathlib import Path
class IaCError(RuntimeError): pass
class IaCRunner:
    def __init__(self):
        self.mode=os.getenv('PEACLOUD_IAC_MODE','disabled')
        self.timeout=int(os.getenv('PEACLOUD_IAC_TIMEOUT','900'))
    def capabilities(self):
        return {'mode':self.mode,'terraform_available':bool(shutil.which('terraform')),'pulumi_available':bool(shutil.which('pulumi')),'timeout_seconds':self.timeout,'real_apply_enabled':os.getenv('PEACLOUD_ALLOW_IAC_APPLY','false').lower()=='true'}
    def _run(self,cmd,cwd,env=None):
        try:r=subprocess.run(cmd,cwd=cwd,env={**os.environ,**(env or {})},capture_output=True,text=True,timeout=self.timeout,check=False)
        except subprocess.TimeoutExpired as e:raise IaCError(f'IaC command timed out after {self.timeout}s') from e
        if r.returncode:raise IaCError((r.stderr or r.stdout)[-4000:])
        return {'stdout':r.stdout[-10000:],'stderr':r.stderr[-4000:],'returncode':r.returncode}
    def render_terraform(self,plan):
        p=plan['spec']; provider=p['provider']; typ=p['resource_type']; name=p['name'].replace('-','_')
        blocks={'aws':{'virtual_machine':f'resource "aws_instance" "{name}" {{ ami = var.image_id instance_type = var.instance_type tags = var.tags }}','object_storage':f'resource "aws_s3_bucket" "{name}" {{ bucket = var.resource_name tags = var.tags }}'},'azure':{'object_storage':f'resource "azurerm_storage_account" "{name}" {{ name = var.resource_name resource_group_name = var.resource_group location = var.region account_tier = "Standard" account_replication_type = "LRS" tags = var.tags }}'},'gcp':{'object_storage':f'resource "google_storage_bucket" "{name}" {{ name = var.resource_name location = var.region labels = var.tags }}'}}
        block=blocks.get(provider,{}).get(typ)
        if not block:raise IaCError(f'Terraform template not available for {provider}/{typ}')
        req={'aws':'hashicorp/aws','azure':'hashicorp/azurerm','gcp':'hashicorp/google'}[provider]
        pname={'aws':'aws','azure':'azurerm','gcp':'google'}[provider]
        return f'''terraform {{ required_version = ">= 1.6" required_providers {{ {pname} = {{ source = "{req}" }} }} }}\nprovider "{pname}" {{}}\nvariable "resource_name" {{ type=string }}\nvariable "region" {{ type=string }}\nvariable "tags" {{ type=map(string) }}\nvariable "image_id" {{ type=string default="REPLACE_ME" }}\nvariable "instance_type" {{ type=string default="t3.small" }}\nvariable "resource_group" {{ type=string default="peacloud-rg" }}\n{block}\n'''
    def terraform_preview(self,plan):
        code=self.render_terraform(plan)
        return {'engine':'terraform','configuration':code,'executable':bool(shutil.which('terraform')),'validated':False,'note':'Generated configuration. Provider validation needs Terraform and authenticated provider credentials.'}
    def terraform_apply(self,plan):
        if os.getenv('PEACLOUD_ALLOW_IAC_APPLY','false').lower()!='true':raise IaCError('Set PEACLOUD_ALLOW_IAC_APPLY=true to enable real IaC mutation')
        if not shutil.which('terraform'):raise IaCError('Terraform CLI is not installed')
        with tempfile.TemporaryDirectory(prefix='peacloud-iac-') as d:
            Path(d,'main.tf').write_text(self.render_terraform(plan))
            vals={'resource_name':plan['name'],'region':plan['region'],'tags':plan['spec']['tags']}
            Path(d,'terraform.tfvars.json').write_text(json.dumps(vals))
            self._run(['terraform','init','-input=false','-no-color'],d)
            self._run(['terraform','plan','-input=false','-out=tfplan','-no-color'],d)
            out=self._run(['terraform','apply','-input=false','-auto-approve','-no-color','tfplan'],d)
            return {'engine':'terraform','status':'succeeded','output':out['stdout']}
runner=IaCRunner()
