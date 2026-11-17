# Role Permission Matrix
|Capability|Viewer/Customer|Operator/SRE|Admin|Security/FinOps|
|---|---:|---:|---:|---:|
|Dashboard / inventory|Yes|Yes|Yes|Yes|
|Cost view|Yes|Yes|Yes|Yes|
|Routine VM mutation|No|Yes|Yes|No by default|
|Provisioning plan|No|Yes|Yes|No by default|
|Approve high-risk change|No|No|Yes|Policy dependent|
|Create budget|No|No|Yes|Via Admin workflow|
|Audit administration|No|No|Yes|Read role planned|
|Repository security settings|No|No|Maintainer|Security maintainer|
