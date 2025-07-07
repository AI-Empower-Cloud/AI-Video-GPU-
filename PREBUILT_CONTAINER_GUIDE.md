# AI Video GPU - Prebuilt Container System

## 🚀 Quick Start

Get the complete AI Video GPU system running in minutes with our prebuilt Docker containers:

```bash
# One-command setup
./setup-prebuilt.sh

# Or using Make
make setup
```

## 📦 Prebuilt Container Features

### Complete System Integration
- **GPU-Optimized**: CUDA 12.2 with all AI libraries pre-installed
- **Multi-Service**: API, Web UI, Workers, Database, Monitoring
- **Production-Ready**: Security, scaling, monitoring built-in
- **One-Click Deploy**: Automated setup and deployment

### Included Services
- **AI Video GPU API** - Main application server
- **PostgreSQL** - Database for jobs and metadata
- **Redis** - Caching and task queue
- **Celery Workers** - Background processing
- **Nginx** - Reverse proxy and load balancer
- **Prometheus** - Metrics collection
- **Grafana** - Monitoring dashboards
- **Flower** - Celery monitoring

## 🛠 Management Commands

### Quick Commands (Make)
```bash
# Setup and start everything
make setup                    # Complete setup
make start                    # Start all services
make stop                     # Stop all services
make logs                     # View all logs
make health                   # Check service health
make shell                    # Open shell in container

# Development
make test                     # Run tests
make lint                     # Code linting
make format                   # Format code

# Deployment
make deploy ENV=production    # Deploy to production
make backup                   # Backup data
make monitor                  # Open monitoring
```

### Advanced Management (Scripts)
```bash
# Service orchestration
./scripts/orchestrate.sh start
./scripts/orchestrate.sh stop
./scripts/orchestrate.sh logs -s ai-video-gpu
./scripts/orchestrate.sh scale -s ai-video-gpu=3
./scripts/orchestrate.sh backup
./scripts/orchestrate.sh health

# Full deployment
./scripts/deploy.sh -e production
./scripts/deploy.sh -e staging --skip-tests
```

## 🏗 Container Architecture

### Multi-Stage Build
```dockerfile
# Stage 1: Base CUDA environment
FROM nvidia/cuda:12.2-devel-ubuntu22.04 AS base

# Stage 2: Python dependencies
FROM base AS python-deps

# Stage 3: Model pre-download
FROM python-deps AS model-cache

# Stage 4: Application
FROM model-cache AS app
```

### Pre-installed Components
- **AI/ML Libraries**: PyTorch, Transformers, Diffusers, XFormers
- **Video Processing**: OpenCV, FFmpeg, MoviePy
- **Audio Processing**: Librosa, TTS engines, Wav2Lip
- **3D Graphics**: Blender API, Trimesh, PyRender
- **Monitoring**: Prometheus, Grafana, GPU metrics
- **Web Frameworks**: FastAPI, Gradio, Streamlit

## 🔧 Configuration

### Environment Files
```yaml
# config/development.yml
environment: development
api:
  host: 0.0.0.0
  port: 8000
  workers: 4
gpu:
  enabled: true
  device_ids: [0]
  memory_fraction: 0.8
```

### Docker Compose Override
```yaml
# docker-compose.production.yml
version: '3.8'
services:
  ai-video-gpu:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 16G
        reservations:
          devices:
            - driver: nvidia
              count: 2
```

## 📊 Monitoring & Observability

### Grafana Dashboards
- **System Metrics**: CPU, Memory, Disk, Network
- **GPU Metrics**: Utilization, Memory, Temperature
- **Application Metrics**: API requests, processing times
- **Service Health**: Uptime, error rates, dependencies

### Prometheus Metrics
```yaml
# Available metrics endpoints
- http://localhost:8000/metrics     # Application metrics
- http://localhost:9100/metrics     # Node exporter
- http://localhost:9102/metrics     # GPU exporter
```

### Access URLs
- **Grafana**: http://localhost:3000 (admin/aivideoadmin)
- **Prometheus**: http://localhost:9090
- **Flower**: http://localhost:5555

## 🚀 Deployment Options

### Development
```bash
# Quick development setup
make dev

# Manual setup
./setup-prebuilt.sh -e development
docker-compose -f docker-compose.prebuilt.yml up -d
```

### Staging
```bash
# Deploy to staging
make deploy ENV=staging

# With custom configuration
./scripts/deploy.sh -e staging -v
```

### Production
```bash
# Production deployment
make deploy-prod

# With monitoring and scaling
./scripts/deploy.sh -e production
kubectl apply -f k8s/
```

## 🔄 CI/CD Integration

### GitHub Actions Workflow
The system includes a complete CI/CD pipeline:

```yaml
# .github/workflows/complete-automation.yml
- Code Quality Analysis
- Security Scanning
- Unit & Integration Tests
- Container Build & Scan
- Performance Testing
- Deployment to Staging/Production
- Monitoring Setup
```

### Manual Trigger
```bash
# Trigger deployment via GitHub Actions
gh workflow run complete-automation.yml -f deploy_environment=production
```

## 📱 API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Generate Video
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "A beautiful sunset over mountains",
    "duration": 10,
    "resolution": "1080p"
  }'
```

### Web Interface
- **Gradio UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Web App**: http://localhost:8080

## 💾 Data Management

### Persistent Volumes
```yaml
volumes:
  ai_video_models:     # Pre-trained AI models
  ai_video_outputs:    # Generated videos
  ai_video_logs:       # Application logs
  postgres_data:       # Database
  redis_data:          # Cache
  prometheus_data:     # Metrics
  grafana_data:        # Dashboards
```

### Backup & Restore
```bash
# Create backup
make backup

# Restore from backup
make restore BACKUP_DIR=backups/20240101_120000

# Automated backup (daily)
echo "0 2 * * * cd /app && make backup" | crontab -
```

## 🔒 Security Features

### Container Security
- Non-root user execution
- Minimal attack surface
- Security scanning with Trivy
- Regular vulnerability updates

### Network Security
- Internal Docker network
- SSL/TLS termination at Nginx
- Rate limiting and CORS protection
- Network policies in Kubernetes

### Data Security
- Encrypted data at rest
- Secure secrets management
- Authentication and authorization
- Audit logging

## 🧪 Testing

### Test Suite
```bash
# Run all tests
make test

# Specific test types
make test-unit          # Unit tests
make test-integration   # Integration tests
make test-api          # API tests
make test-gpu          # GPU tests (requires GPU)
```

### Performance Testing
```bash
# Load testing with Locust
make performance-test

# GPU performance
make gpu-check
```

## 🛡 Troubleshooting

### Common Issues

#### GPU Not Detected
```bash
# Check GPU availability
make gpu-check
nvidia-smi

# Check Docker GPU runtime
docker run --rm --gpus all nvidia/cuda:12.2-base nvidia-smi
```

#### Service Not Starting
```bash
# Check service status
make status

# View logs
make logs SERVICE=ai-video-gpu

# Check health
make health
```

#### Out of Memory
```bash
# Check resource usage
docker stats

# Scale down services
make scale SERVICE=ai-video-gpu COUNT=1

# Clean up old containers
make clean
```

### Log Locations
- Container logs: `docker-compose logs`
- Application logs: `/app/logs/`
- Setup logs: `setup.log`
- Deployment logs: `logs/deployment_*.log`

## 📈 Scaling & Performance

### Horizontal Scaling
```bash
# Scale main application
make scale SERVICE=ai-video-gpu COUNT=3

# Scale workers
make scale SERVICE=celery-worker COUNT=5
```

### Resource Optimization
```yaml
# docker-compose.production.yml
services:
  ai-video-gpu:
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '8'
        reservations:
          memory: 8G
          cpus: '4'
```

### GPU Optimization
```yaml
# Multiple GPU support
environment:
  - CUDA_VISIBLE_DEVICES=0,1,2,3
  - TORCH_CUDA_ARCH_LIST="6.0;6.1;7.0;7.5;8.0;8.6;8.9;9.0"
```

## 🔧 Customization

### Custom Models
```bash
# Add custom models to container
COPY custom_models/ /app/models/custom/
```

### Custom Configuration
```bash
# Override default config
COPY custom_config.yml /app/config/custom.yml
```

### Custom Services
```yaml
# Add to docker-compose.yml
services:
  custom-service:
    build: ./custom-service
    depends_on:
      - ai-video-gpu
```

## 📚 Documentation

- **Main README**: [README.md](README.md)
- **Integration Guide**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **API Documentation**: http://localhost:8000/docs
- **Use Cases**: [use_cases/README.md](use_cases/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test: `make test`
4. Commit changes: `git commit -am 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Submit pull request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

**🎯 Ready to generate amazing AI videos? Start with `make setup` and let the magic begin!**
