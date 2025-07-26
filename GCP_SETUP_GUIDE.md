# 🟢 Google Cloud Platform Setup Guide
## AI Video GPU - Complete GCP Deployment

### 🎯 **Method 1: Service Account Key (Recommended for Automation)**

#### Step 1: Create a Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin** → **Service Accounts**
3. Click **"+ CREATE SERVICE ACCOUNT"**
4. Fill in:
   - **Service account name**: `ai-video-gpu-service`
   - **Description**: `Service account for AI Video GPU deployment`
5. Click **"CREATE AND CONTINUE"**

#### Step 2: Grant Permissions
Add these roles to your service account:
- **Editor** (for general resource management)
- **Storage Admin** (for Cloud Storage)
- **Kubernetes Engine Admin** (for GKE clusters)
- **AI Platform Admin** (for Vertex AI)
- **BigQuery Admin** (for analytics)

#### Step 3: Create and Download Key
1. Click on your newly created service account
2. Go to **"Keys"** tab
3. Click **"ADD KEY"** → **"Create new key"**
4. Choose **JSON** format
5. Click **"CREATE"** - this downloads the key file

#### Step 4: Upload Key to Workspace
1. Rename the downloaded file to `gcp-service-account.json`
2. Upload it to this workspace (drag and drop into VS Code)

---

### 🎯 **Method 2: Browser Authentication**
If you prefer browser authentication, follow these steps:

1. **Open a new terminal in VS Code** (Terminal → New Terminal)
2. Run: `gcloud auth login`
3. **Copy the URL** that appears in the terminal

4. **Open the URL in your browser**
5. **Sign in with your Google account**
6. **Copy the verification code** from the browser
7. **Return to the terminal** and paste the code
8. Press Enter

---

### 🚀 **Quick Setup Script**
Once authenticated, run this automated setup:

```bash
# Set your project ID (replace with your actual project ID)
export GCP_PROJECT_ID="your-project-id-here"

# Run the automated GCP setup
./setup_gcp_complete.sh
```

---

### 🛠️ **Manual Setup Commands**
If you prefer step-by-step manual setup:

```bash
# 1. Set project
gcloud config set project $GCP_PROJECT_ID

# 2. Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable bigquery.googleapis.com

# 3. Create storage bucket
gsutil mb gs://ai-video-gpu-${GCP_PROJECT_ID}

# 4. Create GKE cluster with GPU support
gcloud container clusters create ai-video-gpu-cluster \
  --zone=us-central1-a \
  --num-nodes=2 \
  --machine-type=n1-standard-4 \
  --enable-autorepair \
  --enable-autoupgrade

# 5. Get cluster credentials
gcloud container clusters get-credentials ai-video-gpu-cluster --zone=us-central1-a
```

---

### 📋 **What We'll Deploy**
- ✅ **Cloud Storage**: For video files and assets
- ✅ **Cloud Run**: For web application hosting
- ✅ **Vertex AI**: For AI/ML model serving
- ✅ **BigQuery**: For analytics and logging
- ✅ **GKE**: For container orchestration
- ✅ **Cloud Build**: For CI/CD pipelines

---

### 💰 **Cost Estimate**
- **Development**: ~$10-50/month
- **Production**: ~$100-500/month (depending on usage)
- **Free Credits**: $300 for new accounts

---

### 🔧 **Troubleshooting**
- **"Project not found"**: Make sure you've created a project in Google Cloud Console
- **"Permission denied"**: Ensure your account has the necessary IAM roles
- **"Quota exceeded"**: Request quota increases in the console
- **"Authentication failed"**: Try `gcloud auth revoke --all` then re-authenticate

---

### 📞 **Next Steps**
1. Choose your authentication method above
2. Complete the authentication
3. Let me know when you're ready, and I'll run the automated deployment!

**Which method would you prefer to use?**
