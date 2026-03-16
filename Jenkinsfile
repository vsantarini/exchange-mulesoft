pipeline {
 agent any

 environment {
 ANYPOINT_HOST       = "https://anypoint.mulesoft.com"
 ANYPOINT_CLIENT_ID     = credentials('anypoint-client-id')
 ANYPOINT_CLIENT_SECRET  = credentials('anypoint-client-secret')
 ANYPOINT_ORG_ID      = credentials('anypoint-org-id')
 ANYPOINT_ENV_ID      = credentials('anypoint-env-id')
 OPENAI_API_KEY       = credentials('openai-api-key')
 EXCEL_FILE          = ".\\api-catalog.xlsx"
 NOTIFY_EMAIL        = "v.santarini@reply.it"
 TEAMS_WEBHOOK       = credentials('teams-webhook-url')
 PYTHON = "C:\\Python311\\python.exe"
 PYTHONHOME = "C:\\Python311"
 PYTHONPATH = "C:\\Python311\\Lib;C:\\Python311\\DLLs"
 PYTHONIOENCODING       = "utf-8"
 NODE_HOME              = "C:\\Program Files\\nodejs"
 SPECTRAL = "C:\\Users\\v.santarini\\AppData\\Roaming\\npm\\spectral.cmd"
 }

 stages {

 stage('Checkout') {
 steps { checkout scm }
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
	bat '"%PYTHON%" scripts/read_input_excel.py --file "%WORKSPACE%\\api-catalog.xlsx" --output-apis api-list.json --output-apps app-list.json --output-contracts contract-list.json'
 }
 }


 stage('Authenticate') {
 steps {
bat '"%PYTHON%" scripts/authenticate.py --client-id %ANYPOINT_CLIENT_ID% --client-secret %ANYPOINT_CLIENT_SECRET% --output token.json'
 }
 }

 // ── NUOVO ──────────────────────────────────────
 stage('Validate Specs') {
 steps {
 bat '"%PYTHON%" scripts/validate_specs.py --api-list api-list.json'
 }
}

 // ── NUOVO ──────────────────────────────────────
 stage('Check Version Conflicts') {
 steps {
 bat '"%PYTHON%" scripts/check_versions.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID%'
 }
 }

 // ── NUOVO ──────────────────────────────────────
 stage('Ensure Categories Exist') {
 steps {
 bat '"%PYTHON%" scripts/ensure_categories.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID%'
 }
 }

/**
 stage('Generate AI Documentation') {
 steps {
 bat '"%PYTHON%" scripts/generate_docs.py --api-list api-list.json --openai-key %OPENAI_API_KEY% --output-dir generated-docs/'
 archiveArtifacts artifacts: 'generated-docs/**'
 }
 }

**/
 stage('Publish Assets') {
 steps {
 bat '"%PYTHON%" scripts/publish_assets.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID%'
 }
 }
 
 stage('Publish SOAP Definition Pages') {
 steps {
 bat '"%PYTHON%" scripts/publish_soap_pages.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID%'
 }
}

 stage('Assign Tags & Categories') {
 steps {
bat '"%PYTHON%" scripts/assign_tags.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID%'
 }
 }

 stage('Upload Integration Pattern Image') {
 steps {
 bat '"%PYTHON%" scripts/upload_image.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID%'
 }
 }

 stage('Update & Publish Home Page') {
 steps {
 bat '"%PYTHON%" scripts/update_home_page.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID% --docs-dir generated-docs'
 bat '"%PYTHON%" scripts/publish_pages.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID%'
 }
 }

 stage('Create/Update Consumer Applications') {
 steps {
 bat '"%PYTHON%" scripts/manage_applications.py --app-list app-list.json --token token.json --org-id %ANYPOINT_ORG_ID% --output app-ids.json'
 archiveArtifacts artifacts: 'app-ids.json'
 }
 }

 stage('Create Contracts') {
 steps {
 bat '"%PYTHON%" scripts/manage_contracts.py --contract-list contract-list.json --app-ids app-ids.json --token token.json --org-id %ANYPOINT_ORG_ID% --env-id %ANYPOINT_ENV_ID%'
 }
 }

 // ── NUOVO ──────────────────────────────────────
 
stage('Notify') {
 steps {
 bat '"%PYTHON%" scripts/notify.py --api-list api-list.json --teams-webhook %TEAMS_WEBHOOK% --email %NOTIFY_EMAIL% --status success'
 }
 }
 }

 post {
 success {
 echo '✅ Pipeline completed successfully.'
 }
 failure {
 bat '"%PYTHON%" scripts/notify.py --api-list api-list.json --teams-webhook %TEAMS_WEBHOOK% --email %NOTIFY_EMAIL% --status failure'
 }
 always {
 cleanWs()
 }
 }

}