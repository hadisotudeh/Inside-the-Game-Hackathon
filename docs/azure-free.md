# Azure App Service free demo

Deployed on October 23, 2026: [Touchline overlay](https://touchline-inside-the-game.azurewebsites.net).
The Azure for Students subscription hosts `touchline-inside-the-game` in Sweden Central,
in resource group `touchline-free-rg`, on plan `touchline-free-plan`.
Requested SKU F1; Azure reports SKU U13, tier LinuxFree, and app SKU Free.
HTTPS is required. The live chat uses Azure-hosted GPT-4.1 mini via Microsoft
Foundry. The model resource is `touchline-inside-game-ai`; deployment
`touchline-chat` uses model version `2025-04-14`, GlobalStandard, capacity 30.
Model inference consumes student credit by usage; the App Service plan remains free.
The API key is stored only in server-side Azure application settings.
A real `/chat` probe returned HTTP 200 with the expected shot comparison,
`provider=Microsoft Foundry`, deployment `touchline-chat`, Microsoft Agent
Framework orchestration, and all three evidence tools. All 58 tests pass locally.

Verified on the new hostname: `/health` returns `{"status":"ok"}`, `/`
serves the overlay with HTTP 200, and `/overlay` redirects to `/` with HTTP 308.
The matchroom is available at `/matchroom`.
The original deployment returned 380 historical fixtures from `/matches`.
An accelerated 12-second SSE probe returned HTTP 200, one `match` event and
2,801 `update` events before the client deliberately timed out. This verifies
initial streaming, not full-match connection longevity or browser interaction.

Use Linux App Service **F1**, with Python 3.14. F1 provides shared compute,
60 CPU minutes per day, 1 GB RAM and 1 GB storage. It has no availability SLA
and can sleep when idle. Quota exhaustion can stop the demo until quotas reset.
See [Azure pricing](https://azure.microsoft.com/en-us/pricing/details/app-service/linux/).

An active Azure subscription and Azure CLI are required. Free SKU availability
depends on the subscription and region. If F1 provisioning fails, stop rather
than switching to a paid SKU. These commands do not provision a database,
model deployment, registry, or monitoring service.

Azure for Students requires no credit card and includes $100 credit valid for
one year for eligible verified students. Use that subscription when signing in;
these instructions still select F1 rather than spending the student credit on
a paid hosting tier. See [Microsoft's student program](https://learn.microsoft.com/azure/education-hub/about-azure-for-students).

Build the ZIP locally (only application files and locked runtime requirements):

```bash
pipenv run python tools/package_azure.py
```

Sign in, select your subscription, and choose a globally unique app name.
Use a new resource group and plan dedicated to this demo:

```bash
az login
az account list --output table
az account set --subscription 'YOUR_SUBSCRIPTION_ID'
RESOURCE_GROUP=touchline-free-rg
PLAN=touchline-free-plan
APP=YOUR_GLOBALLY_UNIQUE_APP_NAME
LOCATION=westeurope

az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
az appservice plan create --name "$PLAN" --resource-group "$RESOURCE_GROUP" --is-linux --sku F1
az appservice plan show --name "$PLAN" --resource-group "$RESOURCE_GROUP" --query sku --output json
# Continue only if the plan is Free / LinuxFree (Azure may report U13 for Linux F1).
az webapp create --name "$APP" --resource-group "$RESOURCE_GROUP" --plan "$PLAN" --runtime 'PYTHON:3.14'
az webapp update --name "$APP" --resource-group "$RESOURCE_GROUP" --https-only true
az webapp config set --name "$APP" --resource-group "$RESOURCE_GROUP" --startup-file 'python -m uvicorn app.main:app --host 0.0.0.0 --port 8000'
az webapp config appsettings set --name "$APP" --resource-group "$RESOURCE_GROUP" --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true GAME_EXPLANATION_PROVIDER=off
az webapp deploy --name "$APP" --resource-group "$RESOURCE_GROUP" --src-path .demo-production/azure/touchline.zip --type zip
az webapp show --name "$APP" --resource-group "$RESOURCE_GROUP" --query defaultHostName --output tsv
```

Open `https://<defaultHostName>/health` and confirm `{"status":"ok"}`,
then open `/overlay`, select a fixture, and start replay. Verify streaming on
the hosted app, including an extended replay: cloud proxy timeouts and free
compute quotas can interrupt long SSE connections. Reconnecting currently
restarts replay. Historical data requires outbound access to StatsBomb on GitHub.

The ZIP contains no credentials. To configure another deployment or a local copy,
set `GAME_CHAT_PROVIDER=foundry`, `GAME_FOUNDRY_ENDPOINT` to the HTTPS resource
root, `GAME_FOUNDRY_DEPLOYMENT` to its deployment name, and
`GAME_FOUNDRY_API_KEY` in server-side environment settings. Keep
`GAME_EXPLANATION_PROVIDER=off` to limit model calls to explicit chat questions.
Gemini is retained only as an optional compatibility provider for local setups.
The public chat endpoint has no authentication or global spending cap; its
per-request timeout and token limit do not constitute a monetary budget.

To remove this demo's resources, delete the dedicated `touchline-free-rg`
resource group in the Azure portal after checking its contents.

Deployment reference: [Microsoft Python App Service quickstart](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python).

If Azure rejects a region under your student subscription's policy, inspect the
allowed regions before retrying the plan creation with `--location`:

```bash
az policy assignment list --disable-scope-strict-match --query '[].{name:displayName,parameters:parameters}' --output json
```
