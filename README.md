# VoiceStudio Enhanced Microservices Architecture

A comprehensive voice processing platform with advanced microservices architecture, featuring service discovery, authentication, database integration, and production deployment capabilities.

## 🚀 Features

### Core Services
- **Assistant Service** (Port 5080) - AI/ML interactions and intelligent responses
- **Orchestrator Service** (Port 5090) - Service coordination and workflow management  
- **Autofix Service** (Port 5081) - Automated debugging and repair capabilities

### Advanced Features
- **Service Discovery** - Automatic service registration and health monitoring
- **Authentication & Security** - JWT tokens, API keys, and role-based access control
- **Database Integration** - SQLite/PostgreSQL support with logging and metrics
- **Inter-Service Communication** - RESTful APIs with service-to-service calls
- **Production Deployment** - Docker containerization and orchestration

## 📁 Project Structure

```
VoiceStudio/
├── services/
│   ├── assistant/
│   │   ├── service.py              # Basic assistant service
│   │   ├── enhanced_service.py     # Enhanced with full integration
│   │   └── README.md
│   ├── orchestrator/
│   │   ├── service.py              # Orchestrator service
│   │   └── README.md
│   ├── autofix/
│   │   ├── service.py              # Autofix service
│   │   └── README.md
│   ├── service_discovery.py        # Service discovery system
│   ├── security.py                 # Authentication & security
│   └── database.py                 # Database integration
├── config/
│   └── appsettings.json           # Service configuration
├── tools/
│   ├── audit-changes.ps1          # Comprehensive audit script
│   └── simple-audit.ps1           # Quick health check
├── logs/
│   └── change-audit.md            # Generated audit reports
├── start-services.py              # Basic service manager
├── start-enhanced-services.py     # Enhanced service manager
└── deploy.py                      # Production deployment
```

## 🛠️ Quick Start

### Development Mode

1. **Start Enhanced Services:**
   ```bash
   python start-enhanced-services.py
   ```

2. **Run Health Check:**
   ```powershell
   .\tools\audit-changes.ps1
   ```

3. **Test Services:**
   ```bash
   # Health check
   curl http://127.0.0.1:5080/health
   
   # Service discovery
   curl http://127.0.0.1:5080/discovery
   
   # Authentication (use API key from logs)
   curl -H "X-API-Key: YOUR_API_KEY" http://127.0.0.1:5080/metrics
   ```

### Production Deployment

1. **Generate Deployment Files:**
   ```bash
   python deploy.py generate
   ```

2. **Deploy with Docker:**
   ```bash
   python deploy.py deploy
   ```

3. **Check Service Health:**
   ```bash
   python deploy.py check
   ```

## 🔐 Authentication

### API Key Authentication
```bash
curl -H "X-API-Key: YOUR_API_KEY" http://127.0.0.1:5080/metrics
```

### JWT Token Authentication
```bash
# Login to get JWT token
curl -H "X-API-Key: YOUR_API_KEY" http://127.0.0.1:5080/auth/login

# Use JWT token
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://127.0.0.1:5080/discovery
```

### Default Users
- **Admin User**: `admin` (created automatically)
- **Test User**: `testuser` (created automatically)
- **API Keys**: Generated and displayed in service startup logs

## 📊 Service Endpoints

### Assistant Service (Enhanced)
- `GET /health` - Service health status
- `GET /autofix/status` - Autofix service status
- `GET /discovery` - Service discovery information
- `GET /metrics` - Service performance metrics
- `POST /autofix/analyze` - Error analysis
- `GET /auth/login` - Authentication endpoint

### Orchestrator Service
- `GET /health` - Service health status
- `GET /settings` - Service configuration
- `GET /weights` - Model weights management

### Autofix Service
- `GET /health` - Service health status
- `GET /status` - Service status
- `POST /analyze` - Error analysis

## 🗄️ Database Integration

### SQLite (Development)
- Database file: `voicestudio.db`
- Automatic table creation
- Service logs and metrics storage

### PostgreSQL (Production)
- Docker container with persistent storage
- Advanced indexing and performance
- Connection pooling support

### Database Tables
- `service_logs` - Service event logging
- `service_metrics` - Performance metrics
- `configurations` - System configuration
- `service_registry` - Service discovery data

## 🔍 Monitoring & Auditing

### Audit Scripts
- **Comprehensive Audit**: `.\tools\audit-changes.ps1`
- **Quick Health Check**: `.\tools\simple-audit.ps1`

### Health Monitoring
- Automatic service health checks
- Database logging of all events
- Performance metrics collection
- Service discovery monitoring

### Log Files
- Service logs stored in database
- Audit reports in `logs/change-audit.md`
- Real-time health monitoring

## 🐳 Production Deployment

### Docker Support
- Individual service containers
- Docker Compose orchestration
- Nginx reverse proxy
- PostgreSQL database
- SSL/TLS support ready

### Deployment Commands
```bash
# Generate deployment files
python deploy.py generate

# Build Docker images
python deploy.py build

# Start all services
python deploy.py start

# Check service health
python deploy.py check

# Stop all services
python deploy.py stop

# Full deployment
python deploy.py deploy
```

### Production URLs
- **Assistant**: http://localhost/assistant/
- **Orchestrator**: http://localhost/orchestrator/
- **Autofix**: http://localhost/autofix/
- **Health Check**: http://localhost/health

## 🔧 Configuration

### Service Configuration (`config/appsettings.json`)
```json
{
  "Services": {
    "Assistant": {
      "Port": 5080,
      "HealthEndpoint": "/health",
      "AutofixEndpoint": "/autofix/status"
    },
    "Orchestrator": {
      "Port": 5090,
      "HealthEndpoint": "/health",
      "SettingsEndpoint": "/settings",
      "WeightsEndpoint": "/weights"
    },
    "Autofix": {
      "Port": 5081,
      "HealthEndpoint": "/health",
      "StatusEndpoint": "/status",
      "AnalyzeEndpoint": "/analyze"
    }
  }
}
```

### Environment Variables
- `SERVICE_NAME` - Service identifier
- `SERVICE_PORT` - Service port
- `LOG_LEVEL` - Logging level
- `DATABASE_URL` - Database connection string

## 🚨 Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Check if ports 5080, 5081, 5090 are available
   - Use `netstat -an | findstr "5080\|5081\|5090"`

2. **Service Not Starting**
   - Check Python dependencies: `pip install -r requirements.txt`
   - Verify service scripts exist
   - Check logs in database or console

3. **Authentication Failures**
   - Verify API key is correct
   - Check user permissions
   - Ensure JWT token is not expired

4. **Database Issues**
   - Check database file permissions
   - Verify PostgreSQL connection (production)
   - Review database logs

### Debug Commands
```bash
# Check service status
python deploy.py check

# View service logs
python -c "from services.database import db_manager; print(db_manager.get_service_logs())"

# Test service discovery
curl http://127.0.0.1:5080/discovery

# Verify authentication
curl -H "X-API-Key: YOUR_API_KEY" http://127.0.0.1:5080/metrics
```

## 📈 Performance

### Metrics Collection
- Response time tracking
- Service uptime monitoring
- Error rate analysis
- Resource utilization

### Optimization Features
- Connection pooling
- Database indexing
- Caching strategies
- Load balancing ready

## 🔒 Security Features

- JWT token authentication
- API key management
- Role-based access control
- Service-to-service authentication
- Request logging and auditing
- CORS support
- Input validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review service logs
- Run audit scripts for diagnostics
- Create an issue in the repository

---

**VoiceStudio Enhanced Microservices Architecture** - A production-ready voice processing platform with comprehensive monitoring, security, and deployment capabilities.
