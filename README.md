# Cloud-Based File Storage and Management System

[![CI](https://github.com/mani302005/cloud-file-storage/actions/workflows/ci.yml/badge.svg)](https://github.com/mani302005/cloud-file-storage/actions/workflows/ci.yml)

This is a minimal Flask web app demonstrating storing files in Google Cloud Storage. It supports basic authentication, file upload, listing, download, and deletion.

Key Features
- Secure file upload and download using Google Cloud Storage
- Local fallback `uploads/` for development
- Simple user login using environment-set credentials
- Ready for Cloud Run or App Engine deployment

CI & Deployment
-: GitHub Actions workflows are included under `.github/workflows/`:
	- `ci.yml` — Runs `pytest` on push and pull requests.
	- `docker-build-deploy.yml` — Builds a Docker image, pushes to Google Container Registry, and deploys to Cloud Run when changes are pushed to `main`.

Required GitHub Secrets for deployment (set in repo Settings > Secrets):
- `GCP_PROJECT_ID` — Your Google Cloud project ID.
- `GCP_REGION` — Region for Cloud Run (e.g., `us-central1`).
- `GCP_WORKLOAD_IDENTITY_PROVIDER` — Workload identity provider resource for GitHub -> GCP authentication.
- `GCP_SA` — Service account email (or JSON credential depending on your setup).

Notes:
- The deploy workflow assumes authentication is configured using Workload Identity or service account key stored in repo secrets. Configure these secrets before enabling deploy workflows.
- The CI workflow runs `pytest` which uses local uploads fallback; ensure `pytest` dependencies are installed for local testing as described above.

Quick Start (Local)
1. Create virtual environment and install dependencies
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
2. Set environment variables
```powershell
set APP_USER=admin
set APP_PASS=password
set SECRET_KEY=very-secret
set LOCAL_UPLOAD_DIR=uploads
# For Google Cloud Storage integration
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account.json
set GCS_BUCKET=my-bucket
```
3. Run the app
```powershell
python app.py
```
4. Open http://localhost:8080 and login

Deploy to Cloud Run (example)
```powershell
gcloud builds submit --tag gcr.io/<PROJECT_ID>/cloud-file-storage
gcloud run deploy cloud-file-storage --image gcr.io/<PROJECT_ID>/cloud-file-storage --platform managed --region=us-central1 --allow-unauthenticated --set-env-vars APP_USER=admin,APP_PASS=password,GCS_BUCKET=my-bucket
```

Security Note
- This example uses simple username/password and is intended for demo/teaching purposes only. For production, use proper authentication and HTTPS endpoints.

License
- MIT License — see LICENSE file for details.
