ALTER TABLE tenant_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_records FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_records_isolation ON tenant_records;
CREATE POLICY tenant_records_isolation ON tenant_records USING (tenant_id=current_setting('peacloud.tenant_id',true)) WITH CHECK (tenant_id=current_setting('peacloud.tenant_id',true));
ALTER TABLE principals ENABLE ROW LEVEL SECURITY;
ALTER TABLE principals FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS principals_isolation ON principals;
CREATE POLICY principals_isolation ON principals USING (tenant_id=current_setting('peacloud.tenant_id',true)) WITH CHECK (tenant_id=current_setting('peacloud.tenant_id',true));
