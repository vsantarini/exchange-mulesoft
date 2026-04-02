pipeline {
 agent any

 environment {
 ANYPOINT_HOST       = "https://anypoint.mulesoft.com"
 ANYPOINT_CLIENT_ID     = credentials('anypoint-client-id')
 ANYPOINT_CLIENT_SECRET  = credentials('anypoint-client-secret')
 ANYPOINT_ORG_ID      = credentials('anypoint-org-id')
 ANYPOINT_ENV_ID      = credentials('anypoint-env-id')
 OPENAI_API_KEY       = credentials('openai-api-key')
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
	 bat '"%PYTHON%" -m pip install --quiet openpyxl requests openai pyyaml zeep Pillow swagger-spec-validator cryptography pyjks asn1crypto'
	 }
}

 stage('Read Excel') {
 steps {

	bat '"%PYTHON%" scripts/read_input_excel.py --file "%WORKSPACE%\\api-catalog.xlsx" --output-apis api-list.json --output-apps app-list.json --output-certs cert-list.json'
	bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step read_excel'
	
 }
 }
 
 stage('Extract Certificate SDN') {
 steps {
 bat '"%PYTHON%" scripts/extract_cert_sdn.py --cert-list cert-list.json --output cert-list-enriched.json --full-metadata'
 bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step extract_cert_sdn'
 }
}


 stage('Authenticate') {
 steps {

		bat '"%PYTHON%" scripts/authenticate.py --client-id %ANYPOINT_CLIENT_ID% --client-secret %ANYPOINT_CLIENT_SECRET% --output token.json'
		bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step authenticate'
		
 }
 }

 // ── NUOVO ──────────────────────────────────────
 stage('Validate Specs') {
 steps {

	bat '"%PYTHON%" scripts/validate_specs.py --api-list api-list.json'
	bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step validate_specs'
	
 }
}

 // ── NUOVO ──────────────────────────────────────
 stage('Check Version Conflicts') {
	steps {

		bat '"%PYTHON%" scripts/check_versions.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID%'
		bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step check_versions'
		
	}
 }

 // ── NUOVO ──────────────────────────────────────
 stage('Ensure Categories Exist') {
	steps {

		bat '"%PYTHON%" scripts/ensure_categories.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID%'
		bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step ensure_categories'
		
	}
 }

/**
 stage('Generate AI Documentation') {
	steps {

		bat '"%PYTHON%" scripts/generate_docs.py --api-list api-list.json --openai-key %OPENAI_API_KEY% --output-dir generated-docs/'
		archiveArtifacts artifacts: 'generated-docs/**'
		bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step generate_docs'
		
		
	}
 }

**/
 stage('Publish Assets') {
	steps {

		bat '"%PYTHON%" scripts/publish_assets.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID%'
		bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step publish_assets'
		
	}
 }
 
 stage('Wait for Exchange Propagation') {
	steps {
		echo '[INFO] Waiting 20 seconds for Exchange propagation...'
		bat 'ping -n 21 127.0.0.1 > nul'
	}
}
 
 stage('Publish SOAP Definition Pages') {
	steps {
		bat '"%PYTHON%" scripts/publish_soap_pages.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID%'
		bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step publish_soap_pages'
		
	}
}

 stage('Assign Tags & Categories') {
	steps {
		bat '"%PYTHON%" scripts/assign_tags.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID%'
		bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step assign_tags'
		
	}
 }

 stage('Upload Integration Pattern Image') {
	steps {
		bat '"%PYTHON%" scripts/upload_image.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID%'
		bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step upload_image'
	}
 }

 stage('Update & Publish Home Page') {
	steps {
		bat '"%PYTHON%" scripts/update_home_page.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID% --docs-dir generated-docs'
		bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step update_home_page'
		bat '"%PYTHON%" scripts/publish_pages.py --api-list api-list.json --token token.json --org-id %ANYPOINT_ORG_ID%'
		bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step publish_pages'
	}
 }

 stage('Create/Update Consumer Applications') {
	steps {
		bat '"%PYTHON%" scripts/manage_applications.py --app-list app-list.json --token token.json --org-id %ANYPOINT_ORG_ID% --cert-list cert-list-enriched.json --output app-ids.json'
		archiveArtifacts artifacts: 'app-ids.json'
		bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step manage_applications'
	}
 }
 
 stage('Add Client Cert to Flex GW Truststore') {
 steps {
 bat '"%PYTHON%" scripts/manage_flex_truststore.py --token token.json --org-id %ANYPOINT_ORG_ID% --cert-list cert-list-enriched.json'
 }
}
 /**

 stage('Create Contracts') {
	steps {
		bat '"%PYTHON%" scripts/manage_contracts.py --contract-list contract-list.json --app-ids app-ids.json --token token.json --org-id %ANYPOINT_ORG_ID% --env-id %ANYPOINT_ENV_ID%'
		bat '"%PYTHON%" scripts/pipeline_state.py --action mark --step manage_contracts'
	}
 }

 **/ 
}


post {
 always {
 script {
  def status = currentBuild.result == 'FAILURE' ? 'failure' : 'success'
  bat '"%PYTHON%" scripts/notify.py --api-list api-list.json --teams-webhook %TEAMS_WEBHOOK% --email %NOTIFY_EMAIL% --status failure'
  }
 }
 cleanup{
 cleanWs()
 }
}

}