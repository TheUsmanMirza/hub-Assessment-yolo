# HUB-Assessment-Yolo Backend

A FastAPI-based backend service for managing YOLO format datasets with support for dataset upload, processing, and image serving capabilities.

## 🚀 Features

- **Dataset Management**: Upload, process, and manage YOLO format datasets
- **YOLO Format Support**: Automatic validation and processing of YOLO dataset structure (train/valid/test)
- **Image Serving**: RESTful API endpoints for serving dataset images
- **Database Integration**: MongoDB integration using Motor for async operations
- **Local File Storage**: Local file system storage for processed images
- **API Documentation**: Auto-generated API documentation with FastAPI
- **CORS Support**: Cross-origin resource sharing enabled for frontend integration
- **Containerization**: Docker support for easy deployment

## 📋 Prerequisites

- Python 3.11+
- MongoDB instance running on localhost:27017
- Docker (optional, for containerized deployment)

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hub-Assessment-yolo/backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8080
   ```

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t hub-assessment-backend .
   ```

2. **Run the container**
   ```bash
   docker run -p 8080:8080 hub-assessment-backend
   ```

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── dataset/               # Dataset management module
│   ├── __init__.py
│   ├── models.py          # Pydantic models for data validation
│   ├── router.py          # API routes for dataset operations
│   └── services.py        # Business logic for dataset operations
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── file_processing.py # File processing utilities
│   ├── storage.py         # Storage operations
│   └── yolo.py           # YOLO format validation and parsing
├── datasets/              # Processed dataset storage
└── README.md             # This file
```

## 🔌 API Endpoints

### Base URL: `http://localhost:8080`

#### Dataset Management

- **POST** `/datasets/upload`
  - Upload a YOLO format dataset
  - Accepts: Multipart file upload
  - Returns: Upload status and dataset information

- **GET** `/datasets/`
  - List all available datasets
  - Returns: Array of dataset objects with metadata

- **GET** `/datasets/{dataset_name}/images`
  - Get paginated list of images for a dataset
  - Query params: `page` (default: 1)
  - Returns: Paginated image list

- **GET** `/datasets/{dataset_name}/image/{image_name}`
  - Serve individual image file
  - Returns: Image file as response

### API Documentation

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

## 📊 YOLO Dataset Format

The API expects datasets in standard YOLO format:

```
dataset.zip
├── train/
│   ├── images/
│   │   ├── img1.jpg
│   │   └── img2.jpg
│   └── labels/
│       ├── img1.txt
│       └── img2.txt
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

**Label Format**: Each `.txt` file contains bounding box annotations:
```
class_id center_x center_y width height
```
- All values are normalized (0-1)
- `class_id`: Integer class identifier
- `center_x, center_y`: Center coordinates of bounding box
- `width, height`: Dimensions of bounding box

## 🏗️ Architecture

### Core Components

1. **FastAPI Application** (`main.py`)
   - CORS middleware configuration
   - Router registration
   - API documentation setup

2. **Dataset Module** (`dataset/`)
   - **Models**: Pydantic schemas for data validation
   - **Router**: API endpoint definitions
   - **Services**: Business logic and database operations

3. **Utils Module** (`utils/`)
   - **YOLO**: Dataset validation and parsing
   - **Storage**: File storage operations
   - **File Processing**: Upload and file handling utilities

### Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **Motor**: Async MongoDB driver
- **Aiofiles**: Async file operations
- **Python Multipart**: File upload support

## 🔧 Configuration

### CORS Configuration

The application is configured to accept requests from any origin (`allow_origins=["*"]`). In production, update this to specific domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🧪 Development

### Adding New Endpoints

1. Define models in `dataset/models.py`
2. Add endpoint logic in `dataset/router.py`
3. Implement business logic in `dataset/services.py`
4. Add utilities in `utils/` if needed

### Testing

The backend includes comprehensive test coverage with pytest:

```bash
# Install test dependencies
pip install -r test_requirements.txt

# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py api          # API endpoint tests
python run_tests.py services     # Service layer tests
python run_tests.py yolo         # YOLO utility tests
python run_tests.py file         # File processing tests
python run_tests.py coverage     # Tests with coverage report
python run_tests.py quick        # Quick tests only

# Run tests manually with pytest
pytest tests/ -v                 # All tests verbose
pytest tests/test_api.py -v      # API tests only
pytest tests/ --cov=dataset --cov=utils  # With coverage
```

**Test Structure:**
- `tests/test_api.py` - API endpoint tests
- `tests/test_services.py` - Service layer unit tests
- `tests/test_yolo.py` - YOLO utility function tests
- `tests/test_file_processing.py` - File processing tests
- `tests/conftest.py` - Test fixtures and configuration

**Coverage Reports:**
- Terminal output shows line-by-line coverage
- HTML report generated in `htmlcov/` directory
- Target coverage: 80%+

## 🚀 Deployment

### Production Considerations

1. **Security**
   - Update CORS origins for production domains
   - Use environment variables for sensitive configuration
   - Implement proper authentication/authorization

2. **Performance**
   - Configure database connection pooling
   - Implement caching strategies
   - Use CDN for image serving

3. **Monitoring**
   - Add logging configuration
   - Implement health checks
   - Set up error tracking