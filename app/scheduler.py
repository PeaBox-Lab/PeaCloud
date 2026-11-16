from datetime import datetime, timezone

def cron_matches(expr,dt=None):
    dt=dt or datetime.now(timezone.utc); parts=expr.split()
    if len(parts)!=5:return False
    vals=[dt.minute,dt.hour,dt.day,dt.month,(dt.weekday()+1)%7]
    for token,val in zip(parts,vals):
        if token=='*':continue
        if ',' in token and str(val) in token.split(','):continue
        if '-' in token:
            a,b=map(int,token.split('-',1))
            if a<=val<=b:continue
        if token.isdigit() and int(token)==val:continue
        return False
    return True

def run_due(schedules,providers,policy,record,now=None):
    output=[]
    for item in schedules:
        if not item.get('enabled') or not cron_matches(item['cron'],now):continue
        p=providers[item['provider']]; resource=next((r for r in p.list_resources() if r.id==item['resource_id']),None)
        if not resource: output.append({'schedule_id':item['id'],'status':'failed','detail':'Resource not found'});continue
        decision=policy.evaluate(item['action'],resource,'admin')
        if not decision['allowed']:output.append({'schedule_id':item['id'],'status':'blocked','detail':'; '.join(decision['reasons'])});continue
        try:r=p.act(item['resource_id'],item['action']);status=r['status'];detail=r['message']
        except Exception as e:status='failed';detail=str(e)
        record('scheduler','schedule.execute',f"{item['id']}:{status}");output.append({'schedule_id':item['id'],'status':status,'detail':detail})
    return output
