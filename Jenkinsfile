pipeline {
 agent any

 environment {
 ANYPOINT_HOST = "https://anypoint.mulesoft.com"
 ANYPOINT_CLIENT_ID = credentials('anypoint-client-id')
 ANYPOINT_CLIENT_SECRET = credentials('anypoint-client-secret')
 ANYPOINT_ORG_ID = credentials('anypoint-org-id')
 VAULT_TOKEN = credentials('vault-token')
 VAULT_ADDR = credentials('vault-addr')
 TEAMS_WEBHOOK = credentials('teams-webhook-url')
 NOTIFY_EMAIL = "team@example.com"
 EXCEL_FILE = "api-deployment.xlsx"
 DRY_RUN = "${params.DRY_RUN ?: 'false'}"
 TARGET_ENV = "${params.TARGET_ENV ?: 'dev'}"
 }

 parameters {
 booleanParam(name: 'DRY_RUN', defaultValue: false, description: 'Simulate pipeline without applying changes')
 choice(name: 'TARGET_ENV', choices: ['dev', 'test', 'prod'], description: 'Target deployment environment')
 }

 stages {

 stage('Checkout') {
 steps { checkout scm }
 }

 stage('Install Dependencies') {
 steps {
 sh '''
 pip install --quiet \
 openpyxl requests pyyaml \
 hvac boto3 jinja2
 '''
 }
 }

 stage('Read Excel') {
 steps {
 sh '''
 python3 scripts/deploy/read_excel.py \
 --file ${EXCEL_FILE} \
 --output-deployments deployment-list.json \
 --output-policies policy-list.json \
 --output-alerts alert-list.json \
 --output-sla sla-list.json \
 --env ${TARGET_ENV}
 '''
 archiveArtifacts artifacts: 'deployment-list.json, policy-list.json, alert-list.json, sla-list.json'
 }
 }

 stage('Authenticate') {
 steps {
 sh '''
 python3 scripts/deploy/authenticate_with_refresh.py \
 --client-id ${ANYPOINT_CLIENT_ID} \
 --client-secret ${ANYPOINT_CLIENT_SECRET} \
 --output token.json
 '''
 }
 }

 // ── NUOVO: Governance & Compliance Check ──────────
 stage('Governance & Compliance Check') {
 steps {
 sh '''
 python3 scripts/deploy/governance_check.py \
 --deployment-list deployment-list.json \
 --policy-list policy-list.json \
 --env ${TARGET_ENV} \
 --dry-run ${DRY_RUN}
 '''
 }
 }

 stage('Validate Assets') {
 steps {
 sh '''
 python3 scripts/deploy/validate_assets.py \
 --deployment-list deployment-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID}
 '''
 }
 }

 stage('Validate Gateways') {
 steps {
 sh '''
 python3 scripts/deploy/validate_gateways.py \
 --deployment-list deployment-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID}
 '''
 }
 }

 // ── NUOVO: Upload Certificates ────────────────────
 stage('Upload Certificates') {
 steps {
 sh '''
 python3 scripts/deploy/manage_certificates.py \
 --policy-list policy-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID} \
 --vault-token ${VAULT_TOKEN} \
 --vault-addr ${VAULT_ADDR} \
 --dry-run ${DRY_RUN} \
 --output cert-refs.json
 '''
 archiveArtifacts artifacts: 'cert-refs.json'
 }
 }

 // ── NUOVO: Verify/Create SLA Tiers ───────────────
 stage('Manage SLA Tiers') {
 steps {
 sh '''
 python3 scripts/deploy/manage_sla_tiers.py \
 --sla-list sla-list.json \
 --deployment-list deployment-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID} \
 --dry-run ${DRY_RUN}
 '''
 }
 }

 stage('Register API Instance') {
 steps {
 sh '''
 python3 scripts/deploy/register_api_instance.py \
 --deployment-list deployment-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID} \
 --dry-run ${DRY_RUN} \
 --output api-instances.json
 '''
 archiveArtifacts artifacts: 'api-instances.json'
 }
 }

 stage('Deploy to Flex Gateway') {
 steps {
 sh '''
 python3 scripts/deploy/deploy_flex_gateway.py \
 --deployment-list deployment-list.json \
 --api-instances api-instances.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID} \
 --dry-run ${DRY_RUN}
 '''
 }
 }

// ── NUOVO: Validate Custom Policy Assets ─────────
stage('Validate Custom Policy Assets') {
 steps {
 sh '''
 python3 scripts/deploy/validate_custom_policies.py \
 --policy-list policy-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID} \
 --dry-run ${DRY_RUN}
 '''
 }
}

// ── NUOVO: Publish Custom Policy Assets ──────────
stage('Publish Custom Policy Assets') {
 steps {
 sh '''
 python3 scripts/deploy/publish_custom_policies.py \
 --policy-list policy-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID} \
 --dry-run ${DRY_RUN}
 '''
 }
}

// ── ESISTENTE: Apply Policies (aggiornato) ────────
stage('Apply Policies') {
 steps {
 sh '''
 python3 scripts/deploy/apply_policies.py \
 --policy-list policy-list.json \
 --api-instances api-instances.json \
 --cert-refs cert-refs.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID} \
 --dry-run ${DRY_RUN}
 '''
 }
}

 // ── NUOVO: Configure Autodiscovery ───────────────
 stage('Configure Autodiscovery') {
 steps {
 sh '''
 python3 scripts/deploy/configure_autodiscovery.py \
 --api-instances api-instances.json \
 --deployment-list deployment-list.json \
 --dry-run ${DRY_RUN} \
 --output autodiscovery-config/
 '''
 archiveArtifacts artifacts: 'autodiscovery-config/**'
 }
 }

 // ── NUOVO: Configure Alerting ─────────────────────
 stage('Configure Alerting') {
 steps {
 sh '''
 python3 scripts/deploy/configure_alerting.py \
 --alert-list alert-list.json \
 --api-instances api-instances.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID} \
 --dry-run ${DRY_RUN}
 '''
 }
 }

 // ── NUOVO: Health Check / Smoke Test ─────────────
 stage('Health Check') {
 steps {
 sh '''
 python3 scripts/deploy/health_check.py \
 --deployment-list deployment-list.json \
 --api-instances api-instances.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID}
 '''
 }
 }

 // ── NUOVO: Audit Report ───────────────────────────
 stage('Generate Audit Report') {
 steps {
 sh '''
 python3 scripts/deploy/generate_audit_report.py \
 --deployment-list deployment-list.json \
 --policy-list policy-list.json \
 --api-instances api-instances.json \
 --env ${TARGET_ENV} \
 --dry-run ${DRY_RUN} \
 --output audit-report.json
 '''
 archiveArtifacts artifacts: 'audit-report.json'
 }
 }

 // ── NUOVO: Manual Approval Gate (PROD only) ───────
 stage('Manual Approval') {
 when {
 expression { return params.TARGET_ENV == 'prod' && params.DRY_RUN == false }
 }
 steps {
 input message: "Approve deployment to PRODUCTION?",
 ok: "Deploy to PROD",
 submitter: "ops-team"
 }
 }

 stage('Notify') {
 steps {
 sh '''
 python3 scripts/notify.py \
 --api-list deployment-list.json \
 --teams-webhook ${TEAMS_WEBHOOK} \
 --email ${NOTIFY_EMAIL} \
 --status success \
 --env ${TARGET_ENV} \
 --dry-run ${DRY_RUN}
 '''
 }
 }
 }

 post {
 failure {
 sh '''
 python3 scripts/deploy/rollback.py \
 --api-instances api-instances.json \
 --policy-list policy-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID} \
 --dry-run ${DRY_RUN}

 python3 scripts/notify.py \
 --api-list deployment-list.json \
 --teams-webhook ${TEAMS_WEBHOOK} \
 --email ${NOTIFY_EMAIL} \
 --status failure \
 --env ${TARGET_ENV} \
 --dry-run ${DRY_RUN}
 '''
 }
 always {
 cleanWs()
 }
 }
}