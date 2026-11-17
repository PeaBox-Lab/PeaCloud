import os
class SecretBackend:
    name='base'
    def get(self,name):raise NotImplementedError
class EnvironmentSecrets(SecretBackend):
    name='environment'
    def get(self,name):
        v=os.getenv(name)
        if v is None:raise KeyError(name)
        return v
class AWSSecrets(SecretBackend):
    name='aws-secrets-manager'
    def get(self,name):
        import boto3
        return boto3.client('secretsmanager').get_secret_value(SecretId=name).get('SecretString','')
class AzureKeyVault(SecretBackend):
    name='azure-key-vault'
    def __init__(self):
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient
        self.client=SecretClient(os.environ['AZURE_KEY_VAULT_URL'],DefaultAzureCredential())
    def get(self,name):return self.client.get_secret(name).value
class GCPSecrets(SecretBackend):
    name='gcp-secret-manager'
    def get(self,name):
        from google.cloud import secretmanager
        project=os.environ['GCP_PROJECT_ID'];path=f'projects/{project}/secrets/{name}/versions/latest'
        return secretmanager.SecretManagerServiceClient().access_secret_version(request={'name':path}).payload.data.decode()
def backend():
    n=os.getenv('PEACLOUD_SECRET_BACKEND','environment')
    return {'environment':EnvironmentSecrets,'aws':AWSSecrets,'azure':AzureKeyVault,'gcp':GCPSecrets}[n]()
