# YOLO Dataset Management System

A full-stack application for managing YOLO format datasets with Docker Compose orchestration.

## ��️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    MongoDB      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Database)    │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 27017   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 1. Clone and Navigate

```bash
git clone https://github.com/TheUsmanMirza/hub-Assessment-yolo
cd hub-Assessment-yolo
```

### 2. Start All Services

```bash
# Build and start all containers
docker-compose up --build

# Or run in detached mode (background)
docker-compose up --build -d
```

### 3. Access Applications

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MongoDB**: localhost:27017

## �� Services Overview

### �� Frontend (Next.js)
- **Technology**: Next.js with TypeScript
- **Port**: 3000
- **Features**: 
  - Modern React-based UI
  - Tailwind CSS styling
  - File upload interface
  - Dataset visualization
  - Responsive design

### �� Backend (FastAPI)
- **Technology**: Python 3.11 with FastAPI
- **Port**: 8000
- **Features**:
  - RESTful API endpoints
  - YOLO dataset validation
  - File processing and storage
  - MongoDB integration
  - Auto-generated API docs

### ��️ Database (MongoDB)
- **Technology**: MongoDB 7.0
- **Port**: 27017
- **Features**:
  - Document-based storage
  - Dataset metadata management
  - Automatic health checks