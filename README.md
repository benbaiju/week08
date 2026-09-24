# Week 08 – Continuous Delivery with GitHub Actions and Kubernetes

In Week 07, we implemented a Continuous Integration (CI) pipeline using GitHub Actions. The pipeline automatically tested the backend services, built Docker images, and pushed the successfully built images to Azure Container Registry (ACR).

In Week 08, we extend this workflow to implement **Continuous Delivery (CD)**.

The application will first be automatically deployed to a **staging environment**. After deployment, automated tests will verify that the staging application is working correctly. A tested version can then be manually promoted to the **production environment**.

The same Docker images that are tested in staging are deployed to production. The application is **not rebuilt** during production deployment.

---

## 1. Continuous Delivery Workflow

The Week 08 pipeline consists of four GitHub Actions workflows:

![](./workflow.png)

The first three workflows run automatically.

Production deployment is intentionally manual.

Task 10.3HD keeps those four workflows and adds `05-destroy-infra.yml`. Production can still be started by hand, and it also starts automatically after a successful staging test. 

---

# 2. Prepare the Infrastructure

Create the Terraform infrastructure files using the same approach demonstrated in **Week 06**.

The infrastructure should provide the Azure resources required by the application, including the Kubernetes infrastructure, Azure Container Registry, and Azure Storage configuration used by the application.

### Important AKS Change

When creating the Kubernetes infrastructure, update the AKS node count to:

```hcl
node_count = 3
```

Three nodes are required for this practical because both the staging and production environments run persistent PostgreSQL database workloads.

After running Terraform, verify that the AKS cluster contains three nodes:

```bash
kubectl get nodes
```

---

# 4. Fork the Repository

Fork the provided Week 08 repository into your own GitHub account.

Clone your fork:

```bash
git clone <YOUR-FORK-URL>
```

Move into the project:

```bash
cd week08
```

Ensure that your remote points to your fork:

```bash
git remote -v
```

---

# 5. Create Azure Service Principal

GitHub Actions requires permission to interact with Azure.

Create a Service Principal following the same process introduced previously.

The Service Principal must have sufficient permissions to:

* authenticate with Azure;
* push Docker images to Azure Container Registry;
* access the AKS cluster;
* deploy Kubernetes workloads.

Store the Service Principal credentials as a GitHub Repository Secret named:

```text
AZURE_CREDENTIALS
```

The value must use the following structure:

```json
{
  "clientId": "YOUR_CLIENT_ID",
  "clientSecret": "YOUR_CLIENT_SECRET",
  "subscriptionId": "YOUR_SUBSCRIPTION_ID",
  "tenantId": "YOUR_TENANT_ID"
}
```

Do not commit these credentials to the repository.

---

# 6. Configure GitHub Repository Variables

Go to:

```text
GitHub Repository
→ Settings
→ Secrets and variables
→ Actions
→ Variables
```

Create the following **Repository Variables**.

### ACR_NAME

The name of your Azure Container Registry.

---

### ACR_LOGIN_SERVER

The complete ACR login server.

---

### AKS_RESOURCE_GROUP

The Resource Group containing your AKS cluster.

---

### AKS_CLUSTER_NAME

The name of your AKS cluster.

---

### TFSTATE_RG

The Azure resource group that stores Terraform remote state.

---

### TFSTATE_STORAGE_ACCOUNT

The Azure Storage Account that stores Terraform remote state.

---

### TFSTATE_CONTAINER

The blob container inside that storage account (for example `tfstate`).

---

# 7. Repository Secret

Under:

```text
Settings
→ Secrets and variables
→ Actions
→ Secrets
```

create:

```text
AZURE_CREDENTIALS
```

This contains the Service Principal authentication JSON.

Also create these repository secrets:

```text
DISCORD_WEBHOOK_URL
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

`DISCORD_WEBHOOK_URL` is used by production and destroy workflows to send Discord alerts.

`DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` are used by Docker Scout during CI.

---

# 8. Create the Staging GitHub Environment

Go to:

```text
GitHub Repository
→ Settings
→ Environments
→ New environment
```

Create:

```text
staging
```

Add the following **Environment Secrets**:

```text
POSTGRES_USER = postgres
POSTGRES_PASSWORD = postgres
JWT_SECRET_KEY = koalatech-local-development-secret
DEFAULT_ADMIN_USERNAME = admin
DEFAULT_ADMIN_EMAIL = admin@koalatech.edu.au
DEFAULT_ADMIN_PASSWORD = AdminPassword123!
AZURE_STORAGE_CONNECTION_STRING = <YOUR_STORAGE_ACCOUNT_CONNECTION_STRING>
```
---

# 9. Create the Production GitHub Environment

Create another environment:

```text
production
```

Add the same Environment Secret names:

```text
POSTGRES_USER = postgres
POSTGRES_PASSWORD = postgres
JWT_SECRET_KEY = koalatech-local-development-secret
DEFAULT_ADMIN_USERNAME = admin
DEFAULT_ADMIN_EMAIL = admin@koalatech.edu.au
DEFAULT_ADMIN_PASSWORD = AdminPassword123!
AZURE_STORAGE_CONNECTION_STRING = <YOUR_STORAGE_ACCOUNT_CONNECTION_STRING>
```

Staging and production therefore have independent environment configuration.

---

# 10. GitHub Configuration Summary

The final GitHub configuration should be:

| Type                          | Name                              |
| ----------------------------- | --------------------------------- |
| Repository Secret             | `AZURE_CREDENTIALS`               |
| Repository Variable           | `ACR_NAME`                        |
| Repository Variable           | `ACR_LOGIN_SERVER`                |
| Repository Variable           | `AKS_RESOURCE_GROUP`              |
| Repository Variable           | `AKS_CLUSTER_NAME`                |
| Repository Variable           | `TFSTATE_RG`                      |
| Repository Variable           | `TFSTATE_STORAGE_ACCOUNT`         |
| Repository Variable           | `TFSTATE_CONTAINER`               |
| Repository Secret             | `DISCORD_WEBHOOK_URL`             |
| Repository Secret             | `DOCKERHUB_USERNAME`              |
| Repository Secret             | `DOCKERHUB_TOKEN`                 |
| Staging Environment Secret    | `POSTGRES_USER`                   |
| Staging Environment Secret    | `POSTGRES_PASSWORD`               |
| Staging Environment Secret    | `JWT_SECRET_KEY`                  |
| Staging Environment Secret    | `DEFAULT_ADMIN_USERNAME`          |
| Staging Environment Secret    | `DEFAULT_ADMIN_EMAIL`             |
| Staging Environment Secret    | `DEFAULT_ADMIN_PASSWORD`          |
| Staging Environment Secret    | `AZURE_STORAGE_CONNECTION_STRING` |
| Production Environment Secret | `POSTGRES_USER`                   |
| Production Environment Secret | `POSTGRES_PASSWORD`               |
| Production Environment Secret | `JWT_SECRET_KEY`                  |
| Production Environment Secret | `DEFAULT_ADMIN_USERNAME`          |
| Production Environment Secret | `DEFAULT_ADMIN_EMAIL`             |
| Production Environment Secret | `DEFAULT_ADMIN_PASSWORD`          |
| Production Environment Secret | `AZURE_STORAGE_CONNECTION_STRING` |

---

# 11. GitHub Actions Workflows

The repository contains four workflow files:

```text
.github/
└── workflows/
    ├── 01-ci.yml
    ├── 02-deploy-staging.yml
    ├── 03-staging-test.yml
    └── 04-deploy-production.yml
```

Task 10.3HD also adds:

```text
    └── 05-destroy-infra.yml
```

---

# 12. Run and Verify the Staging Application

Verify that the following workflows complete successfully:

01 - CI
02 - Deploy to Staging
03 - Staging Test

Once the deployment is complete, verify the Kubernetes resources in the staging namespace and access the staging application using the frontend external IP.

Confirm that the application is working correctly before proceeding to production.

13. Deploy to Production

Production deployment is performed manually.

Go to:

GitHub Repository
→ Actions
→ 04 - Deploy to Production
→ Run workflow

Provide the image SHA that successfully passed the staging deployment and testing process.

### Find the Image SHA

Before running the production workflow, obtain the Git commit SHA of the version that was successfully deployed and tested in staging:

```bash
git rev-parse HEAD
```

Copy the returned SHA and provide it as the `image_tag` when manually running the **04 - Deploy to Production** workflow.

> Make sure the SHA belongs to the version that successfully passed the staging pipeline.

Task 10.3HD no longer uses an `image_tag` input. The production workflow checks out `workflow_run.head_sha` or `github.sha` and deploys that SHA.


Run the production workflow and verify that it completes successfully.

Important: Production must use the same image version that was tested in staging. Do not rebuild the Docker images for production.

14. Verify the Production Application

After the production deployment completes:

- Verify the Kubernetes resources in the production namespace.
- Find the external IP of the production frontend service.
- Access the production application.
- Confirm that the application is working correctly.
- Verify that production is running the same image SHA that was tested in staging.

---

# 15. Task 10.3HD additions

The Week 08 Continuous Delivery path above is still the base pipeline.

Task 10.3HD extends it with:

* Terraform applied from `01 - CI` (AKS, ACR, storage, Log Analytics);
* Docker Scout image scans after the images are pushed;
* Prometheus and Grafana installed when staging deploys;
* automatic production promotion after staging tests pass;
* blue/green production Deployments with live and preview Services;
* a 90 second live `/health` soak plus Azure Log Analytics error checks;
* automatic rollback if soak or logs fail;
* Discord notifications for success, rollback, and hard failure;
* a manual `05 - Destroy infra` workflow.

Production still uses the **same Docker images** that passed staging. Images are **not rebuilt** for production.

---

# 16. What each workflow does now

### 01 - CI

Runs on push to `main`, or from **Actions → 01 - CI → Run workflow**.

1. Bootstraps Terraform state storage from `TFSTATE_RG`, `TFSTATE_STORAGE_ACCOUNT`, and `TFSTATE_CONTAINER`.
2. Runs `terraform init`, `fmt`, `validate`, `plan`, and `apply`.
3. Runs pytest for every backend service.
4. Runs `npm run test:run` for the frontend.
5. Builds and pushes `koalatech-*` images tagged with `${{ github.sha }}`.
6. Scans those images with Docker Scout (`continue-on-error`).

### 02 - Deploy to Staging

Starts automatically when `01 - CI` succeeds on `main`.

1. Applies `kubernetes/staging/`.
2. Sets every staging Deployment to the tested commit SHA.
3. Waits for rollouts.
4. Installs `kube-prometheus-stack` into the `monitoring` namespace.
5. Applies `kubernetes/monitoring/staging-servicemonitors.yaml`.

### 03 - Test Staging

Starts automatically when `02 - Deploy to Staging` succeeds on `main`.

1. Waits for the staging frontend LoadBalancer IP.
2. Curls `http://<staging-frontend-ip>/health`.
3. Curls `/health` in-cluster for frontend and all five backend services.

### 04 - Deploy to Production

Starts automatically when `03 - Test Staging` succeeds on `main`.

It can also be started manually from **Actions → 04 - Deploy to Production → Run workflow**.

Manual runs do **not** ask for an `image_tag`. The workflow uses:

* `github.event.workflow_run.head_sha` when it is started by the staging test workflow;
* `github.sha` when it is started by hand.

Optional mutually exclusive demo flags on a manual run:

| Input | What it does |
| ----- | ------------ |
| `simulate_smoke_failure` | Sets `FORCE_UNHEALTHY` before preview smoke. The switch never runs. |
| `simulate_post_switch_failure` | Sets `FORCE_UNHEALTHY` after the switch. Soak fails, then rollback and Discord. |
| `simulate_log_errors` | Hits `/demo/error` after the switch. `/health` stays 200. Log Analytics over threshold 5 triggers rollback. |

Do not enable more than one flag in the same run.

### 05 - Destroy infra

Manual only.

Go to:

```text
GitHub Repository
→ Actions
→ 05 - Destroy infra
→ Run workflow
```

Type `destroy` in the confirmation box.

The workflow runs `terraform destroy`, then deletes the Terraform state resource group, and sends a Discord notification.

---

# 17. Production blue/green

Production keeps two complete copies of each app:

* `*-blue` Deployments
* `*-green` Deployments

The live Service (`frontend`, `user-service`, and so on) selects the **active** colour.

The preview Service (`frontend-preview`, `user-service-preview`, and so on) selects the **target** colour.

The active colour is stored in:

```text
configmap/active-color
namespace: production
```

The production job order is:

1. **Determine active and target colors** — read `active-color`, pick the other colour as the target.
2. **Deploy target color** — apply `kubernetes/production/`, set target images to the tested SHA, wait for rollouts.
3. **Smoke test target (preview)** — curl preview `/health` (and frontend/user-service `/`) before any live traffic moves.
4. **Switch traffic to target color** — patch live Service selectors to the target colour and write `active-color`.
5. **Soak live traffic and auto-rollback** — poll live `/health` for 90 seconds, then query Log Analytics. If soak or logs fail, selectors go back to the previous colour.
6. **Discord notification** — success, rollback, or hard failure.

Verify production colour and images after a run:

```bash
kubectl get configmap active-color -n production -o yaml
kubectl get deploy -n production
kubectl get svc -n production
kubectl get pods -n production -o wide
```

Confirm that the live frontend LoadBalancer is serving the colour recorded in `active-color`, and that those pods use the same SHA that passed staging.

---

# 18. Monitoring

Staging deploy installs kube-prometheus-stack and ServiceMonitors.

Production deploy applies `kubernetes/monitoring/production-servicemonitors.yaml`.

Check the monitoring namespace:

```bash
kubectl get pods -n monitoring
kubectl get svc -n monitoring
```

Grafana and Prometheus Services are in the `monitoring` namespace. Use those Services to confirm scrape targets for staging and production.

Azure Log Analytics is created by Terraform as `${AKS_CLUSTER_NAME}-logs`. Production soak queries `ContainerLogV2` in that workspace. If the workspace cannot be queried, the Log Analytics check is skipped (fail-open) and soak still uses `/health`.

---

# 19. Discord

Create a Discord incoming webhook and store it as the repository secret `DISCORD_WEBHOOK_URL`.

Production sends a Discord embed for:

* a successful blue/green switch and soak;
* an automatic rollback (health soak or Log Analytics);
* a hard workflow failure.

Destroy infra also sends a Discord embed when Terraform destroy finishes or fails.

---

# 20. Verify the 10.3HD path

After a push to `main`, confirm this order succeeds:

```text
01 - CI
02 - Deploy to Staging
03 - Test Staging
04 - Deploy to Production
```

Then:

* open the staging frontend IP and confirm the app works;
* open the production frontend IP and confirm the app works;
* confirm production pods use the same SHA as staging;
* confirm Discord received the production result;
* optionally run `04 - Deploy to Production` by hand with one simulate flag to show gate failure or rollback.

To tear everything down after the demo, run `05 - Destroy infra` and type `destroy`.