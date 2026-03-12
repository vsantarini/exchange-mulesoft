#Guida Operativa per esposizione/update API Contract SOAP/REST su Anypoint Exchange in contesto AXA IT

##Definizione pipeline di CI/CD (Jenkins) sfruttando API Amministrative Anypoint Exchange

https://docs.mulesoft.com/gateway/latest/flex-conn-jenkins-api

##Definizione delle API Amministrative Anypoint Exchange

https://anypoint.mulesoft.com/exchange/portals/anypoint-platform/f1e97bc6-315a-4490-82a7-23abe036327a.anypoint-platform/exchange-experience-api/minor/2.4/console/method/%234005/

###API di Interesse
•   token retrieval: a Connected App with the needed roles has to be defined, after that, this curl can be used to retrieve the token

{"grant_type": "client_credentials", "client_id": "<client id>", "client_secret": "<client secret>"}

•	upsert tags and assign them to specific API Contract: PUT https://anypoint.mulesoft.com/exchange/api/v2/assets/{groupId}/{assetId}/{version}/tags
Payload:
[
  {
    "value": "<value of the tag>",
    "key": "<key that identifies the tag>"
  }
]

•	create a category: POST https://anypoint.mulesoft.com/exchange/api/v2/organizations/{organizationId}/categories 
Payload:
{
  "displayName": "<name of the category>",
  "tagKey": "<tag key of the category",
  "assetTypeRestrictions": [
    <the list of asset type where the category is associated (in our case “rest-api” and “soap-api”>
  ],
  "acceptedValues": [
    <the list of accepted values in the category>
  ]
}

•	add category to specific API contract: PUT https://anypoint.mulesoft.com/exchange/api/v2/assets/{groupId}/{assetId}/{version}/tags/categories/<category tag key obtained with previous call> 
Payload: 
{tagValue: ["<one of the possible values of the category>"]}

####Tag Mandatori AXA Gruppo

https://confluence.axa.com/confluence/spaces/APIMgt/pages/466623147/Tagging+policy

•   Publish an Asset (REST OAS or WSDL)

POST https://anypoint.mulesoft.com/exchange/api/v2/assets

Headers:

| Header          | Valore                        |
|-----------------|-------------------------------|
| Authorization   | Bearer {{access_token}}       |
| Content-Type    | multipart/form-data           |

Body (multipart/form-data):

| Campo          | REST (OAS/Swagger)   | SOAP (WSDL)          |
|----------------|----------------------|----------------------|
| organizationId | {{orgId}}            | {{orgId}}            |
| groupId        | {{orgId}}            | {{orgId}}            |
| assetId        | my-rest-api          | my-soap-api          |
| version        | 1.0.0                | 1.0.0                |
| name           | My REST API          | My SOAP API          |
| classifier     | oas                  | wsdl                 |
| apiVersion     | v1                   | v1                   |
| main           | api.yaml             | service.wsdl         |
| file           | *(file .yaml/.json)* | *(file .wsdl)*       |

---

cURL Example — Swagger/OAS

curl -X POST "https://anypoint.mulesoft.com/exchange/api/v2/assets" \
  -H "Authorization: Bearer {{access_token}}" \
  -F "organizationId={{orgId}}" \
  -F "groupId={{orgId}}" \
  -F "assetId=my-rest-api" \
  -F "version=1.0.0" \
  -F "name=My REST API" \
  -F "classifier=oas" \
  -F "apiVersion=v1" \
  -F "main=api.yaml" \
  -F "file=@/path/to/api.yaml"

---

cURL Example — WSDL

curl -X POST "https://anypoint.mulesoft.com/exchange/api/v2/assets" \
  -H "Authorization: Bearer {{access_token}}" \
  -F "organizationId={{orgId}}" \
  -F "groupId={{orgId}}" \
  -F "assetId=my-soap-api" \
  -F "version=1.0.0" \
  -F "name=My SOAP API" \
  -F "classifier=wsdl" \
  -F "apiVersion=v1" \
  -F "main=service.wsdl" \
  -F "file=@/path/to/service.wsdl"

---

•   Verify the Pubblication Status

GET https://anypoint.mulesoft.com/exchange/api/v2/assets/{{groupId}}/{{assetId}}/{{version}}/status
Authorization: Bearer {{access_token}}

# Anypoint Exchange API — Update Documentation Pages & Add Charts

## 1. Update a Documentation Page

PUT https://anypoint.mulesoft.com/exchange/api/v2/assets/{{groupId}}/{{assetId}}/{{version}}/pages/{{pageName}}

### Headers

| Header        | Value                        |
|---------------|------------------------------|
| Authorization | Bearer {{access_token}}      |
| Content-Type  | application/json             |

### Body

{
  "content": "# Title\n\nPage content in **Markdown**"
}

> Documentation pages support **Markdown** or **AsciiDoc** format.

---

## 2. Upload an Image/Chart as a Resource

Before referencing an image in a page, it must be uploaded as a resource.

POST https://anypoint.mulesoft.com/exchange/api/v2/assets/{{groupId}}/{{assetId}}/{{version}}/resources

### Headers

| Header        | Value                        |
|---------------|------------------------------|
| Authorization | Bearer {{access_token}}      |
| Content-Type  | multipart/form-data          |

### Body (multipart/form-data)

| Field  | Value                            |
|--------|----------------------------------|
| file   | *(image file: .png, .jpg, .svg)* |
| name   | my-chart.png                     |

### Response

{
  "resourceKey": "resources/my-chart.png"
}

---

## 3. Reference the Chart in the Page

Once the `resourceKey` is obtained, embed it in the page Markdown content:

# System Architecture

Below is the architectural diagram:

![My Chart](/exchange/api/v2/assets/{{groupId}}/{{assetId}}/{{version}}/resources/my-chart.png)

---

## 4. cURL Example — Upload Image

curl -X POST "https://anypoint.mulesoft.com/exchange/api/v2/assets/{{groupId}}/{{assetId}}/{{version}}/resources" \
  -H "Authorization: Bearer {{access_token}}" \
  -F "file=@/path/to/my-chart.png" \
  -F "name=my-chart.png"

---

## 5. cURL Example — Update Page

curl -X PUT "https://anypoint.mulesoft.com/exchange/api/v2/assets/{{groupId}}/{{assetId}}/{{version}}/pages/home" \
  -H "Authorization: Bearer {{access_token}}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Home\n\n![Chart](resources/my-chart.png)"
  }'

---

## Important Notes

| Aspect                    | Detail                                                        |
|---------------------------|---------------------------------------------------------------|
| **Content format**        | Markdown or AsciiDoc                                          |
| **Supported image formats** | `.png`, `.jpg`, `.svg`, `.gif`                              |
| **Default page name**     | `home`                                                        |
| **Dynamic charts**        | Not natively supported — upload static images or pre-rendered SVGs |

---
# Anypoint Exchange API — Set Version & Owner

## 1. Version — Set at Publication Time

The version is defined directly in the initial `POST /assets` and **cannot be modified**
once published. To release a new version, republish the asset with a different version number:

curl -X POST "https://anypoint.mulesoft.com/exchange/api/v2/assets" \
 -H "Authorization: Bearer {{access_token}}" \
 -F "groupId={{orgId}}" \
 -F "assetId=my-rest-api" \
 -F "version=2.0.0" \
 -F "name=My REST API" \
 -F "classifier=oas" \
 -F "apiVersion=v2" \
 -F "main=api.yaml" \
 -F "file=@/path/to/api.yaml"

> Versioning follows the **Semantic Versioning** format (`MAJOR.MINOR.PATCH`).

---

## 2. Owner — Update Asset Maintainer

PUT https://anypoint.mulesoft.com/exchange/api/v2/assets/{{groupId}}/{{assetId}}/{{version}}

### Headers

| Header | Value |
|---------------|--------------------------|
| Authorization | Bearer {{access_token}} |
| Content-Type | application/json |

### Body

{
 "name": "My REST API",
 "description": "API description",
 "contactName": "John Doe",
 "contactEmail": "john.doe@example.com"
}

---

## 3. cURL Example — Update Owner

curl -X PUT "https://anypoint.mulesoft.com/exchange/api/v2/assets/{{groupId}}/{{assetId}}/{{version}}" \
 -H "Authorization: Bearer {{access_token}}" \
 -H "Content-Type: application/json" \
 -d '{
 "name": "My REST API",
 "contactName": "John Doe",
 "contactEmail": "john.doe@example.com"
 }'

---

## Important Notes

| Aspect | Detail |
|------------------------|----------------------------------------------------------------------|
| **Version** | Immutable after publication — create a new version to update |
| **Owner/Maintainer** | Updatable via `PUT /assets` using `contactName` and `contactEmail` |
| **Required permissions** | **Exchange Contributor** role or higher on the organization |
| **groupId** | Typically matches the `organizationId` |

---

# Anypoint Exchange API — Create/Update Application & Contract

## 2. Application — Create

POST https://anypoint.mulesoft.com/exchange/api/v2/organizations/{{orgId}}/applications

### Headers

| Header        | Value                    |
|---------------|--------------------------|
| Authorization | Bearer {{access_token}}  |
| Content-Type  | application/json         |

### Body

{
  "name": "My Application",
  "description": "Application description",
  "url": "https://myapp.example.com",
  "redirectUri": ["https://myapp.example.com/callback"],
  "grantTypes": ["authorization_code", "implicit"],
  "apiEndpoints": false
}

### Response

{
  "id": "{{applicationId}}",
  "name": "My Application",
  "clientId": "{{clientId}}",
  "clientSecret": "{{clientSecret}}"
}

---

## 3. Application — Update

PATCH https://anypoint.mulesoft.com/exchange/api/v2/organizations/{{orgId}}/applications/{{applicationId}}

### Headers

| Header        | Value                    |
|---------------|--------------------------|
| Authorization | Bearer {{access_token}}  |
| Content-Type  | application/json         |

### Body

{
  "name": "My Updated Application",
  "description": "Updated description",
  "url": "https://myapp.example.com",
  "redirectUri": ["https://myapp.example.com/callback"]
}

---

## 4. Application — Get

GET https://anypoint.mulesoft.com/exchange/api/v2/organizations/{{orgId}}/applications/{{applicationId}}

### Headers

| Header        | Value                    |
|---------------|--------------------------|
| Authorization | Bearer {{access_token}}  |

---

## 5. Contract — Create (Request API Access)

POST https://anypoint.mulesoft.com/exchange/api/v2/organizations/{{orgId}}/applications/{{applicationId}}/contracts

### Headers

| Header        | Value                    |
|---------------|--------------------------|
| Authorization | Bearer {{access_token}}  |
| Content-Type  | application/json         |

### Body

{
  "apiId": "{{apiId}}",
  "environmentId": "{{environmentId}}",
  "acceptedTerms": true,
  "organizationId": "{{orgId}}",
  "groupId": "{{groupId}}",
  "assetId": "{{assetId}}",
  "version": "{{version}}",
  "versionGroup": "v1",
  "tier": {
    "id": "{{tierId}}"
  }
}

> `tierId` refers to the **SLA tier** defined on the API. If no SLA is configured, omit the `tier` field.

---

## 6. Contract — Update (Modify SLA Tier)

PATCH https://anypoint.mulesoft.com/exchange/api/v2/organizations/{{orgId}}/applications/{{applicationId}}/contracts/{{contractId}}

### Headers

| Header        | Value                    |
|---------------|--------------------------|
| Authorization | Bearer {{access_token}}  |
| Content-Type  | application/json         |

### Body

{
  "tier": {
    "id": "{{newTierId}}"
  },
  "status": "APPROVED"
}

### Allowed Status Values

| Status      | Description                        |
|-------------|------------------------------------|
| `APPROVED`  | Contract approved                  |
| `PENDING`   | Awaiting approval                  |
| `REJECTED`  | Contract rejected                  |
| `REVOKED`   | Contract revoked                   |

---

## 7. Contract — Get

GET https://anypoint.mulesoft.com/exchange/api/v2/organizations/{{orgId}}/applications/{{applicationId}}/contracts/{{contractId}}

### Headers

| Header        | Value                    |
|---------------|--------------------------|
| Authorization | Bearer {{access_token}}  |

---

## 8. cURL Examples

### Create Application

curl -X POST "https://anypoint.mulesoft.com/exchange/api/v2/organizations/{{orgId}}/applications" \
  -H "Authorization: Bearer {{access_token}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Application",
    "description": "Application description",
    "url": "https://myapp.example.com",
    "redirectUri": ["https://myapp.example.com/callback"],
    "grantTypes": ["authorization_code"],
    "apiEndpoints": false
  }'

### Create Contract

curl -X POST "https://anypoint.mulesoft.com/exchange/api/v2/organizations/{{orgId}}/applications/{{applicationId}}/contracts" \
  -H "Authorization: Bearer {{access_token}}" \
  -H "Content-Type: application/json" \
  -d '{
    "apiId": "{{apiId}}",
    "environmentId": "{{environmentId}}",
    "acceptedTerms": true,
    "organizationId": "{{orgId}}",
    "groupId": "{{groupId}}",
    "assetId": "{{assetId}}",
    "version": "{{version}}",
    "versionGroup": "v1"
  }'

### Update Contract Status

curl -X PATCH "https://anypoint.mulesoft.com/exchange/api/v2/organizations/{{orgId}}/applications/{{applicationId}}/contracts/{{contractId}}" \
  -H "Authorization: Bearer {{access_token}}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "APPROVED"
  }'

---

## Important Notes

| Aspect | Detail |
|---|---|
| **clientId / clientSecret** | Returned only on application creation — store them securely |
| **contractId** | Returned in the response of `POST /contracts` |
| **SLA Tier** | Optional — required only if the API enforces SLA policies |
| **acceptedTerms** | Must be `true` to complete the contract creation |
| **Required permissions** | **Exchange Contributor** or **Organization Admin** role |

---

## References

- [Exchange Experience API v2](https://anypoint.mulesoft.com/exchange/portals/anypoint-platform/f1e97bc6-315a-4490-82a7-23abe036327a.anypoint-platform/exchange-experience-api/)
- [Anypoint Platform APIs](https://anypoint.mulesoft.com/exchange/portals/anypoint-platform/)


repo/
├── Jenkinsfile
├── api-catalog.xlsx
├── scripts/
│ ├── read_excel.py
│ ├── authenticate.py
│ ├── validate_specs.py       ← NUOVO
│ ├── check_versions.py       ← NUOVO
│ ├── ensure_categories.py    ← NUOVO
│ ├── generate_docs.py
│ ├── publish_assets.py
│ ├── assign_tags.py
│ ├── upload_image.py
│ ├── update_home_page.py
│ ├── publish_pages.py
│ ├── manage_applications.py
│ ├── manage_contracts.py
│ └── notify.py               ← NUOVO
├── rulesets/
│ ├── default-oas.yaml ← ruleset aziendale base OAS
│ ├── default-wsdl.yaml ← ruleset aziendale base WSDL
│ └── finance-api.yaml ← ruleset custom per dominio Finance
├── apis/
│ ├── my-rest-api.yaml
│ ├── soap/
│ │	├── service.wsdl ← entry-point (filePath)
│ │	├── extended.wsdl ← WSDL aggiuntivo (additionalFiles)
│ │	├── types.xsd ← XSD principale (additionalFiles)
│ │	└── common.xsd ← XSD condiviso (additionalFiles)
│ └── images/
│   └── integration-pattern.png