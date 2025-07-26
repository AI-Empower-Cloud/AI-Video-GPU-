#!/bin/bash

# 🚀 Deploy AI Video GPU to Google Cloud Platform
# This script deploys your application to GCP after setup is complete

set -e

echo "🚀 Deploying AI Video GPU to Google Cloud Platform..."
echo "===================================================="

# Source the GCP environment
if [ -f ".env.gcp" ]; then
    source .env.gcp
    echo "✅ Loaded GCP environment configuration"
else
    echo "❌ GCP environment not found. Run ./setup_gcp_complete.sh first"
    exit 1
fi

# Create a simple Dockerfile if it doesn't exist
if [ ! -f "Dockerfile" ]; then
    echo "📝 Creating Dockerfile for deployment..."
    cat > Dockerfile << EOF
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    ffmpeg \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p temp output static/videos

# Set environment variables
ENV PYTHONPATH="/app"
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]
EOF
    echo "✅ Dockerfile created"
fi

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo "📝 Creating requirements.txt..."
    cat > requirements.txt << EOF
flask==2.3.2
requests==2.31.0
openai==0.27.8
google-cloud-storage==2.9.0
google-cloud-aiplatform==1.26.1
google-cloud-bigquery==3.11.1
python-dotenv==1.0.0
moviepy==1.0.3
pillow==9.5.0
numpy==1.24.3
opencv-python-headless==4.7.1.72
pydub==0.25.1
replicate==0.8.4
elevenlabs==0.2.18
markdown==3.4.3
jinja2==3.1.2
gunicorn==20.1.0
EOF
    echo "✅ requirements.txt created"
fi

# Create a simple Flask app if app.py doesn't exist
if [ ! -f "app.py" ]; then
    echo "📝 Creating basic Flask application..."
    cat > app.py << EOF
from flask import Flask, render_template, jsonify
import os
from google.cloud import storage
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>AI Video GPU - GCP Deployment</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
            h1 { color: #4285f4; text-align: center; }
            .status { background: #e8f5e8; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .button { background: #4285f4; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🟢 AI Video GPU - Google Cloud Platform</h1>
            <div class="status">
                <h3>✅ Deployment Successful!</h3>
                <p>Your AI Video GPU application is now running on Google Cloud Platform.</p>
            </div>
            <h3>🔧 Available Services:</h3>
            <ul>
                <li>🟢 Cloud Run - Web Application Hosting</li>
                <li>☁️ Cloud Storage - File Storage</li>
                <li>🧠 Vertex AI - Machine Learning</li>
                <li>📊 BigQuery - Analytics</li>
                <li>🐳 GKE - Container Orchestration</li>
            </ul>
            <h3>📊 System Status:</h3>
            <p>Project ID: ''' + os.environ.get('GOOGLE_CLOUD_PROJECT', 'Not Set') + '''</p>
            <p>Region: ''' + os.environ.get('GCP_REGION', 'Not Set') + '''</p>
            <p>Storage Bucket: ''' + os.environ.get('GCP_STORAGE_BUCKET', 'Not Set') + '''</p>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "ai-video-gpu-gcp"})

@app.route('/api/status')
def api_status():
    return jsonify({
        "cloud_provider": "Google Cloud Platform",
        "project_id": os.environ.get('GOOGLE_CLOUD_PROJECT'),
        "region": os.environ.get('GCP_REGION'),
        "storage_bucket": os.environ.get('GCP_STORAGE_BUCKET'),
        "status": "running"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
EOF
    echo "✅ Flask application created"
fi

# Build and deploy to Cloud Run
echo "🏗️ Building and deploying to Cloud Run..."

# Submit build to Cloud Build
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/ai-video-gpu --quiet

# Deploy to Cloud Run
gcloud run deploy ai-video-gpu-service \
    --image gcr.io/$GOOGLE_CLOUD_PROJECT/ai-video-gpu \
    --platform managed \
    --region $GCP_REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GCP_REGION=$GCP_REGION,GCP_STORAGE_BUCKET=$GCP_STORAGE_BUCKET \
    --quiet

# Get the service URL
SERVICE_URL=$(gcloud run services describe ai-video-gpu-service --region=$GCP_REGION --format='value(status.url)')

echo ""
echo "======================================================"
echo "🎉 Deployment Complete!"
echo "======================================================"
echo ""
echo "🌐 Your application is live at:"
echo "   $SERVICE_URL"
echo ""
echo "📊 Monitor your deployment:"
echo "   Cloud Console: https://console.cloud.google.com/run"
echo "   Logs: gcloud logs read --follow --resource-type cloud_run_revision"
echo ""
echo "🔧 Useful commands:"
echo "   Update deployment: gcloud run deploy ai-video-gpu-service --source ."
echo "   View logs: gcloud logs read --service ai-video-gpu-service"
echo "   Scale service: gcloud run services update ai-video-gpu-service --concurrency=100"
echo ""
echo "✅ GCP deployment successful! 🚀"
