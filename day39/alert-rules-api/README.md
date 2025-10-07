# Alert Rules API - Day 39

A comprehensive alert rules management system with intelligent validation, bulk operations, templates, and testing capabilities.

## Features

- ✅ RESTful API for rule lifecycle management
- ✅ Intelligent validation preventing configuration errors
- ✅ Bulk operations supporting enterprise scale
- ✅ Template system accelerating deployments
- ✅ Testing framework ensuring rule reliability
- ✅ Modern React dashboard with WordPress-inspired UI

## Quick Start

### Without Docker

1. **Setup and Build**
   ```bash
   ./scripts/build.sh
   ```

2. **Start Application**
   ```bash
   ./scripts/start.sh
   ```

3. **Run Demo**
   ```bash
   ./scripts/demo.sh
   ```

4. **Stop Application**
   ```bash
   ./scripts/stop.sh
   ```

### With Docker

1. **Build and Start**
   ```bash
   docker-compose up --build
   ```

2. **Run Demo**
   ```bash
   ./scripts/demo.sh
   ```

## Access Points

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Project Structure

```
alert-rules-api/
├── backend/           # Python FastAPI backend
├── frontend/          # React dashboard
├── docker/           # Docker configurations
├── scripts/          # Build and deployment scripts
└── README.md
```

## API Endpoints

### Rules
- `POST /api/v1/rules` - Create rule
- `GET /api/v1/rules` - List rules
- `PUT /api/v1/rules/{id}` - Update rule
- `DELETE /api/v1/rules/{id}` - Delete rule
- `POST /api/v1/rules/bulk` - Bulk operations

### Templates
- `GET /api/v1/templates` - List templates
- `POST /api/v1/templates/{id}/create-rule` - Create rule from template

### Testing
- `POST /api/v1/test/rule` - Test rule
- `POST /api/v1/test/validate` - Validate syntax

## Testing

The system includes comprehensive testing capabilities:

- **Unit Tests**: Backend validation and business logic
- **Integration Tests**: API endpoint functionality
- **Rule Testing**: Validate rules against sample data
- **Syntax Validation**: Real-time rule validation

## License

MIT License - Educational purposes
