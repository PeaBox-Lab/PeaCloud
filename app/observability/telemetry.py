import os,time
class Telemetry:
    def __init__(self):self.started=time.time();self.requests=0;self.errors=0
    def record(self,status):self.requests+=1;self.errors+=int(status>=500)
    def snapshot(self):return {'requests':self.requests,'errors':self.errors,'uptime_seconds':round(time.time()-self.started,1),'otel_endpoint_configured':bool(os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT'))}
telemetry=Telemetry()
