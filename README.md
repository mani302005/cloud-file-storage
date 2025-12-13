# Cloud-Based File Storage and Management System

This is a minimal Flask web app demonstrating storing files in Google Cloud Storage. It supports basic authentication, file upload, listing, download, and deletion.

Key Features
- Secure file upload and download using Google Cloud Storage
- Local fallback `uploads/` for development
- Simple user login using environment-set credentials
- Ready for Cloud Run or App Engine deployment

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
