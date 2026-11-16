from datetime import datetime, timezone
class PolicyEngine:
    def evaluate(self, action, resource, role):
        reasons=[]
        if role=='viewer': reasons.append('Viewer role cannot mutate resources')
        if resource.tags.get('protected','').lower()=='true': reasons.append('Resource is protected')
        if resource.tags.get('env','').lower() in {'prod','production'} and role!='admin': reasons.append('Production changes require admin role')
        if action not in {'start','stop','restart','snapshot'}: reasons.append('Action is not allow-listed')
        return {'allowed':not reasons,'reasons':reasons,'evaluated_at':datetime.now(timezone.utc).isoformat()}
