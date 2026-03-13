pipeline {
 agent any

 environment {
 ANYPOINT_HOST       = "https://anypoint.mulesoft.com"
 ANYPOINT_CLIENT_ID     = credentials('anypoint-client-id')
 ANYPOINT_CLIENT_SECRET  = credentials('anypoint-client-secret')
 ANYPOINT_ORG_ID      = credentials('anypoint-org-id')
 ANYPOINT_ENV_ID      = credentials('anypoint-env-id')
 //OPENAI_API_KEY       = credentials('openai-api-key')
 EXCEL_FILE          = "api-catalog.xlsx"
 NOTIFY_EMAIL        = "v.santarini@reply.it"
 TEAMS_WEBHOOK       = credentials('teams-webhook-url')

 }

 stages {

 stage('Checkout') {
 steps { checkout scm }
 }
 
stage('Install Python') {
 steps {
 bat '''
 IF EXIST "%PYTHON%" (
 echo Python already installed — skipping.
 ) ELSE (
 echo Installing Python...
 curl -o python-installer.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
 python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
 echo Python installed successfully.
 )
 '''
 }
 }

 stage('Debug') {
 steps {
 bat '"%PYTHON%" --version'
 bat '"%PYTHON%" -m pip --version'
 bat 'dir'
 }
 }

 stage('Install Dependencies') {
	 steps {
	 bat '%PYTHON% -m pip install --quiet openpyxl'
	 bat '%PYTHON% -m pip install --quiet requests'
	 bat '%PYTHON% -m pip install --quiet openai'
	 bat '%PYTHON% -m pip install --quiet pyyaml'
	 bat '%PYTHON% -m pip install --quiet zeep'
	 bat '%PYTHON% -m pip install --quiet Pillow'
	 bat '%PYTHON% -m pip install --quiet swagger-spec-validator'
	 }
}

 stage('Read Excel') {
 steps {
 sh '''
 python3 scripts/read_excel.py \
 --file ${EXCEL_FILE} \
 --output-apis api-list.json \
 --output-apps app-list.json \
 --output-contracts contract-list.json
 '''
 archiveArtifacts artifacts: 'api-list.json, app-list.json, contract-list.json'
 }
 }

 stage('Authenticate') {
 steps {
 sh '''
 python3 scripts/authenticate.py \
 --client-id ${ANYPOINT_CLIENT_ID} \
 --client-secret ${ANYPOINT_CLIENT_SECRET} \
 --output token.json
 '''
 }
 }

 // ── NUOVO ──────────────────────────────────────
 stage('Validate Specs') {
 steps {
 sh '''
 python3 scripts/validate_specs.py \
 --api-list api-list.json \
 --fail-on-warnings
 '''
 archiveArtifacts artifacts: 'spectral-reports/**'
 }
}

 // ── NUOVO ──────────────────────────────────────
 stage('Check Version Conflicts') {
 steps {
 sh '''
 python3 scripts/check_versions.py \
 --api-list api-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID}
 '''
 }
 }

 // ── NUOVO ──────────────────────────────────────
 stage('Ensure Categories Exist') {
 steps {
 sh '''
 python3 scripts/ensure_categories.py \
 --api-list api-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID}
 '''
 }
 }

 stage('Generate AI Documentation') {
 steps {
 sh '''
 python3 scripts/generate_docs.py \
 --api-list api-list.json \
 --openai-key ${OPENAI_API_KEY} \
 --output-dir generated-docs/
 '''
 archiveArtifacts artifacts: 'generated-docs/**'
 }
 }

 stage('Publish Assets') {
 steps {
 sh '''
 python3 scripts/publish_assets.py \
 --api-list api-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID}
 '''
 }
 }
 
 stage('Publish SOAP Definition Pages') {
 steps {
 sh '''
 python3 scripts/publish_soap_pages.py \
 --api-list api-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID}
 '''
 }
}

 stage('Assign Tags & Categories') {
 steps {
 sh '''
 python3 scripts/assign_tags.py \
 --api-list api-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID}
 '''
 }
 }

 stage('Upload Integration Pattern Image') {
 steps {
 sh '''
 python3 scripts/upload_image.py \
 --api-list api-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID}
 '''
 }
 }

 stage('Update & Publish Home Page') {
 steps {
 sh '''
 python3 scripts/update_home_page.py \
 --api-list api-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID} \
 --docs-dir generated-docs/

 python3 scripts/publish_pages.py \
 --api-list api-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID}
 '''
 }
 }

 stage('Create/Update Consumer Applications') {
 steps {
 sh '''
 python3 scripts/manage_applications.py \
 --app-list app-list.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID} \
 --output app-ids.json
 '''
 archiveArtifacts artifacts: 'app-ids.json'
 }
 }

 stage('Create Contracts') {
 steps {
 sh '''
 python3 scripts/manage_contracts.py \
 --contract-list contract-list.json \
 --app-ids app-ids.json \
 --token token.json \
 --org-id ${ANYPOINT_ORG_ID} \
 --env-id ${ANYPOINT_ENV_ID}
 '''
 }
 }

 // ── NUOVO ──────────────────────────────────────
/** 
stage('Notify') {
 steps {
 sh '''
 python3 scripts/notify.py \
 --api-list api-list.json \
 --teams-webhook ${TEAMS_WEBHOOK} \
 --email ${NOTIFY_EMAIL} \
 --status success
 '''
 }
 }
 }

 post {
 success {
 echo '✅ Pipeline completed successfully.'
 }
 failure {
 sh '''
 python3 scripts/notify.py \
 --api-list api-list.json \
 --teams-webhook ${TEAMS_WEBHOOK} \
 --email ${NOTIFY_EMAIL} \
 --status failure
 '''
 }
 always {
 cleanWs()
 }
 }
 **/

  stage('Cleanup') {
 steps {
 cleanWs()
 }
}
 }
}