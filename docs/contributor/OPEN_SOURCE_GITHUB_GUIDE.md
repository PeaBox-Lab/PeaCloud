# Open Source and GitHub Publishing Guide
1. Create the public repository and push PeaCloud.
2. Replace every `@OWNER` entry in CODEOWNERS with the actual GitHub username/team.
3. Review the MIT license choice with the project owner before publication; changing license later can be difficult once external contributions exist.
4. Enable branch protection/rulesets for `main` and require CI + CodeQL.
5. Enable Dependency Graph, Dependabot, secret scanning and Private Vulnerability Reporting.
6. Require MFA for privileged maintainers.
7. Add repository topics such as `multi-cloud`, `aws`, `azure`, `gcp`, `fastapi`, `react`, `terraform`, `cloud-management`.
8. Create an initial GitHub Release tagged `v0.11.0` only after release checks pass.
9. Do not publish real tenants, logs, credentials, billing exports or proprietary customer configuration.
