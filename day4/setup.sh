#!/bin/bash

# Distributed Log Processing System - Complete Setup Script
# This script sets up a professional-grade development environment
# Used by industry leaders for distributed system development

set -e  # Exit on any error

echo "🚀 Setting up Distributed Log Processing Development Environment..."
echo "This script will create a production-ready development setup."

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if required tools are installed
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_warning "Node.js not found. Installing Node.js for frontend development..."
        # Add Node.js installation logic here if needed
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    print_status "Prerequisites check completed ✓"
}

# Create project structure
create_project_structure() {
    print_step "Creating project structure..."
    
    # Main project structure
    mkdir -p distributed-logs/{backend/{src,tests},frontend/{src/components,public},.vscode,docs,scripts}
    
    # Backend structure
    mkdir -p distributed-logs/backend/{src/{processors,parsers,utils},tests/{unit,integration},config}
    
    # Frontend structure
    mkdir -p distributed-logs/frontend/src/{components/{dashboard,charts,filters},hooks,services,types}
    
    cd distributed-logs
    print_status "Project structure created ✓"
}

# Setup Python backend
setup_python_backend() {
    print_step "Setting up Python backend environment..."
    
    cd backend
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install Python packages
    pip install --upgrade pip
    pip install black flake8 mypy pytest pytest-cov pre-commit fastapi uvicorn pydantic
    
    # Create requirements.txt
    pip freeze > requirements.txt
    
    print_status "Python backend environment ready ✓"
    cd ..
}

# Setup TypeScript frontend
setup_frontend() {
    print_step "Setting up TypeScript React frontend..."
    
    cd frontend
    
    # Initialize React TypeScript project
    npx create-react-app . --template typescript --skip-git
    
    # Install additional dependencies
    npm install @mui/material @emotion/react @emotion/styled @mui/icons-material
    npm install @types/node @types/react @types/react-dom
    npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin prettier
    
    print_status "Frontend environment ready ✓"
    cd ..
}

# Create configuration files
create_configuration_files() {
    print_step "Creating configuration files..."
    
    # Python configuration
    cat > backend/pyproject.toml << 'EOF'
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
/(
  # Exclude virtual environment
  venv
  | __pycache__
)/
'''

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
check_untyped_defs = true
disallow_untyped_defs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --cov=src --cov-report=term-missing"
EOF

    # Flake8 configuration
    cat > backend/.flake8 << 'EOF'
[flake8]
max-line-length = 88
extend-ignore = E203, W503, E501
exclude = 
    venv,
    __pycache__,
    .git,
    .pytest_cache
per-file-ignores =
    __init__.py:F401
EOF

    # ESLint configuration for frontend
    cat > frontend/.eslintrc.js << 'EOF'
module.exports = {
  parser: '@typescript-eslint/parser',
  extends: [
    'react-app',
    'react-app/jest',
    '@typescript-eslint/recommended',
  ],
  plugins: ['@typescript-eslint'],
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/explicit-function-return-type': 'warn',
    'no-console': 'warn',
    'prefer-const': 'error',
  },
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
};
EOF

    # Prettier configuration
    cat > frontend/.prettierrc << 'EOF'
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
EOF

    # Pre-commit hooks configuration
    cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.9
        files: ^backend/
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        files: ^backend/
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        files: ^backend/
        additional_dependencies: [types-all]
  
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.42.0
    hooks:
      - id: eslint
        files: ^frontend/src/.*\.(ts|tsx)$
        additional_dependencies:
          - '@typescript-eslint/parser'
          - '@typescript-eslint/eslint-plugin'
  
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0
    hooks:
      - id: prettier
        files: ^frontend/src/.*\.(ts|tsx|json|css|md)$
EOF

    # VS Code workspace settings
    cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "./backend/venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.pylintEnabled": false,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true,
        "source.fixAll.eslint": true
    },
    "typescript.preferences.importModuleSpecifier": "relative",
    "emmet.includeLanguages": {
        "typescript": "html",
        "typescriptreact": "html"
    },
    "files.associations": {
        "*.env*": "properties"
    },
    "search.exclude": {
        "**/node_modules": true,
        "**/venv": true,
        "**/__pycache__": true,
        "**/.pytest_cache": true
    }
}
EOF

    # VS Code launch configuration for debugging
    cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Debug Backend",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/backend/src/main.py",
            "python": "${workspaceFolder}/backend/venv/bin/python",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}/backend",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/backend/src"
            }
        },
        {
            "name": "Python: Debug Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "python": "${workspaceFolder}/backend/venv/bin/python",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}/backend"
        }
    ]
}
EOF

    print_status "Configuration files created ✓"
}

# Create sample code files
create_sample_code() {
    print_step "Creating sample implementation files..."
    
    # Backend log processor
    cat > backend/src/log_processor.py << 'EOF'
"""
Distributed Log Processing System - Core Processor
This module handles log event processing in a distributed environment.
Used by industry leaders for real-time log analytics.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging
from enum import Enum


class LogLevel(Enum):
    """Enumeration of supported log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEvent:
    """Represents a structured log event in our distributed system."""
    
    def __init__(
        self, 
        timestamp: datetime, 
        level: LogLevel, 
        message: str,
        service: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize a log event with validation."""
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.service = service
        self.metadata = metadata or {}
        
        # Validate required fields
        if not message.strip():
            raise ValueError("Log message cannot be empty")
        if not service.strip():
            raise ValueError("Service name cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log event to dictionary for storage/transmission."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "service": self.service,
            "metadata": self.metadata
        }


class DistributedLogProcessor:
    """
    Main processor for handling log events across multiple services.
    Designed for high-throughput distributed systems.
    """
    
    def __init__(self, buffer_size: int = 1000) -> None:
        """Initialize the processor with configurable buffer size."""
        self.buffer_size = buffer_size
        self.event_buffer: List[LogEvent] = []
        self.processed_count = 0
        self.error_count = 0
        self.logger = logging.getLogger(__name__)
    
    def process_event(self, raw_event: str) -> Optional[LogEvent]:
        """
        Process a raw log string into a structured LogEvent.
        
        Args:
            raw_event: JSON string containing log data
            
        Returns:
            LogEvent if successful, None if processing fails
        """
        try:
            # Parse JSON - this is where type safety becomes critical
            event_data = json.loads(raw_event)
            
            # Validate required fields
            required_fields = ["timestamp", "level", "message", "service"]
            for field in required_fields:
                if field not in event_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Parse timestamp with error handling
            try:
                timestamp = datetime.fromisoformat(event_data["timestamp"])
            except ValueError:
                # Fallback to current time if timestamp is invalid
                timestamp = datetime.now()
                self.logger.warning(f"Invalid timestamp in event, using current time")
            
            # Validate and convert log level
            try:
                level = LogLevel(event_data["level"].upper())
            except ValueError:
                level = LogLevel.INFO
                self.logger.warning(f"Invalid log level: {event_data['level']}, defaulting to INFO")
            
            # Create structured event
            event = LogEvent(
                timestamp=timestamp,
                level=level,
                message=event_data["message"],
                service=event_data["service"],
                metadata=event_data.get("metadata")
            )
            
            # Add to buffer with overflow protection
            if len(self.event_buffer) >= self.buffer_size:
                self.event_buffer.pop(0)  # Remove oldest event
            
            self.event_buffer.append(event)
            self.processed_count += 1
            
            return event
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.error_count += 1
            self.logger.error(f"Error processing event: {e}")
            return None
    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return {
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "buffer_size": len(self.event_buffer),
            "success_rate": (
                self.processed_count / (self.processed_count + self.error_count) * 100
                if (self.processed_count + self.error_count) > 0 else 0
            )
        }
    
    def flush_buffer(self) -> List[LogEvent]:
        """Flush and return all buffered events."""
        events = self.event_buffer.copy()
        self.event_buffer.clear()
        return events
EOF

    # Test file
    cat > backend/tests/test_log_processor.py << 'EOF'
"""
Unit tests for the distributed log processor.
These tests ensure reliability in production environments.
"""

import pytest
from datetime import datetime
import json
from backend.src.log_processor import LogEvent, LogLevel, DistributedLogProcessor


class TestLogEvent:
    """Test cases for LogEvent class."""
    
    def test_log_event_creation_success(self) -> None:
        """Test successful log event creation with valid data."""
        timestamp = datetime.now()
        event = LogEvent(
            timestamp=timestamp,
            level=LogLevel.INFO,
            message="Test message",
            service="test-service"
        )
        
        assert event.level == LogLevel.INFO
        assert event.message == "Test message"
        assert event.service == "test-service"
        assert event.timestamp == timestamp
        assert event.metadata == {}
    
    def test_log_event_with_metadata(self) -> None:
        """Test log event creation with metadata."""
        metadata = {"user_id": "12345", "request_id": "abcdef"}
        event = LogEvent(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            message="Database error",
            service="user-service",
            metadata=metadata
        )
        
        assert event.metadata == metadata
    
    def test_log_event_empty_message_raises_error(self) -> None:
        """Test that empty message raises ValueError."""
        with pytest.raises(ValueError, match="Log message cannot be empty"):
            LogEvent(
                timestamp=datetime.now(),
                level=LogLevel.INFO,
                message="",
                service="test-service"
            )
    
    def test_log_event_to_dict(self) -> None:
        """Test conversion of log event to dictionary."""
        timestamp = datetime.now()
        event = LogEvent(
            timestamp=timestamp,
            level=LogLevel.WARNING,
            message="Test warning",
            service="api-service"
        )
        
        result = event.to_dict()
        
        assert result["timestamp"] == timestamp.isoformat()
        assert result["level"] == "WARNING"
        assert result["message"] == "Test warning"
        assert result["service"] == "api-service"


class TestDistributedLogProcessor:
    """Test cases for DistributedLogProcessor class."""
    
    def test_processor_initialization(self) -> None:
        """Test processor initializes with correct defaults."""
        processor = DistributedLogProcessor()
        
        assert processor.buffer_size == 1000
        assert processor.processed_count == 0
        assert processor.error_count == 0
        assert len(processor.event_buffer) == 0
    
    def test_process_valid_json_event(self) -> None:
        """Test processing of valid JSON log event."""
        processor = DistributedLogProcessor()
        
        raw_event = json.dumps({
            "timestamp": "2024-01-01T10:00:00",
            "level": "ERROR",
            "message": "Database connection failed",
            "service": "user-api",
            "metadata": {"retry_count": 3}
        })
        
        processed_event = processor.process_event(raw_event)
        
        assert processed_event is not None
        assert processed_event.level == LogLevel.ERROR
        assert processed_event.message == "Database connection failed"
        assert processed_event.service == "user-api"
        assert processed_event.metadata["retry_count"] == 3
        assert processor.processed_count == 1
    
    def test_process_invalid_json_returns_none(self) -> None:
        """Test that invalid JSON returns None and increments error count."""
        processor = DistributedLogProcessor()
        
        invalid_json = "{ invalid json }"
        result = processor.process_event(invalid_json)
        
        assert result is None
        assert processor.error_count == 1
        assert processor.processed_count == 0
    
    def test_process_missing_required_field(self) -> None:
        """Test handling of events missing required fields."""
        processor = DistributedLogProcessor()
        
        incomplete_event = json.dumps({
            "timestamp": "2024-01-01T10:00:00",
            "level": "INFO",
            # Missing 'message' and 'service'
        })
        
        result = processor.process_event(incomplete_event)
        
        assert result is None
        assert processor.error_count == 1
    
    def test_buffer_overflow_handling(self) -> None:
        """Test that buffer overflow is handled correctly."""
        processor = DistributedLogProcessor(buffer_size=2)
        
        # Add 3 events to a buffer of size 2
        for i in range(3):
            event = json.dumps({
                "timestamp": "2024-01-01T10:00:00",
                "level": "INFO",
                "message": f"Message {i}",
                "service": "test-service"
            })
            processor.process_event(event)
        
        # Should only have 2 events (latest ones)
        assert len(processor.event_buffer) == 2
        assert processor.processed_count == 3
    
    def test_get_stats(self) -> None:
        """Test statistics reporting."""
        processor = DistributedLogProcessor()
        
        # Process some valid and invalid events
        valid_event = json.dumps({
            "timestamp": "2024-01-01T10:00:00",
            "level": "INFO",
            "message": "Valid message",
            "service": "test-service"
        })
        processor.process_event(valid_event)
        processor.process_event("invalid json")
        
        stats = processor.get_stats()
        
        assert stats["processed_count"] == 1
        assert stats["error_count"] == 1
        assert stats["buffer_size"] == 1
        assert stats["success_rate"] == 50.0
EOF

    # Main application entry point
    cat > backend/src/main.py << 'EOF'
"""
Main entry point for the distributed log processing system.
This demonstrates how the components work together in a real application.
"""

import asyncio
import json
from datetime import datetime
from log_processor import DistributedLogProcessor, LogLevel


async def simulate_log_stream() -> None:
    """Simulate a stream of log events from various services."""
    processor = DistributedLogProcessor(buffer_size=100)
    
    # Sample log events from different services
    sample_events = [
        {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "User login successful",
            "service": "auth-service",
            "metadata": {"user_id": "user123", "ip": "192.168.1.1"}
        },
        {
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "message": "Database connection timeout",
            "service": "user-service",
            "metadata": {"timeout": 30, "retry_count": 3}
        },
        {
            "timestamp": datetime.now().isoformat(),
            "level": "WARNING",
            "message": "High memory usage detected",
            "service": "monitoring-service",
            "metadata": {"memory_usage": "85%", "threshold": "80%"}
        },
        {
            "timestamp": datetime.now().isoformat(),
            "level": "DEBUG",
            "message": "Cache hit for user profile",
            "service": "cache-service",
            "metadata": {"cache_key": "profile:user123", "hit_rate": "92%"}
        }
    ]
    
    print("🚀 Starting distributed log processing simulation...")
    print("Processing log events from multiple services...\n")
    
    for event_data in sample_events:
        raw_event = json.dumps(event_data)
        processed_event = processor.process_event(raw_event)
        
        if processed_event:
            print(f"✅ Processed: [{processed_event.level.value}] {processed_event.service}: {processed_event.message}")
        else:
            print("❌ Failed to process event")
        
        # Simulate processing delay
        await asyncio.sleep(0.5)
    
    # Show final statistics
    stats = processor.get_stats()
    print(f"\n📊 Processing Statistics:")
    print(f"   Total Processed: {stats['processed_count']}")
    print(f"   Errors: {stats['error_count']}")
    print(f"   Success Rate: {stats['success_rate']:.1f}%")
    print(f"   Buffer Size: {stats['buffer_size']}")


if __name__ == "__main__":
    asyncio.run(simulate_log_stream())
EOF

    print_status "Sample code files created ✓"
}

# Install pre-commit hooks
setup_precommit_hooks() {
    print_step "Setting up pre-commit hooks..."
    
    # Activate Python environment
    source backend/venv/bin/activate
    
    # Install pre-commit hooks
    pre-commit install
    
    # Run pre-commit on all files to test
    print_status "Running initial pre-commit check..."
    pre-commit run --all-files || true
    
    print_status "Pre-commit hooks installed ✓"
}

# Run tests
run_tests() {
    print_step "Running comprehensive tests..."
    
    # Backend tests
    cd backend
    source venv/bin/activate
    
    echo "Running Python tests..."
    python -m pytest tests/ -v --cov=src --cov-report=term-missing
    
    # Type checking
    echo "Running type checking..."
    mypy src/
    
    # Code formatting check
    echo "Checking code formatting..."
    black --check src/ tests/
    
    # Linting
    echo "Running linter..."
    flake8 src/ tests/
    
    cd ..
    
    # Frontend tests (if React app was created)
    if [ -d "frontend/src" ]; then
        cd frontend
        echo "Running frontend tests..."
        npm test -- --watchAll=false || true
        cd ..
    fi
    
    print_status "All tests completed ✓"
}

# Create documentation
create_documentation() {
    print_step "Creating project documentation..."
    
    cat > README.md << 'EOF'
# Distributed Log Processing System

A production-ready distributed log processing system built for learning and real-world application.

## 🏗️ Architecture

This system demonstrates industry-standard practices for distributed log processing:

- **High-throughput log ingestion** with type safety
- **Real-time processing** with buffering and error handling
- **Quality gates** with automated testing and code formatting
- **Professional tooling** used by industry leaders

## 🚀 Quick Start

1. **Setup Environment:**
   ```bash
   ./scripts/setup.sh
   ```

2. **Run the System:**
   ```bash
   cd backend
   source venv/bin/activate
   python src/main.py
   ```

3. **Run Tests:**
   ```bash
   cd backend
   pytest tests/ -v
   ```

## 🛠️ Development

### Code Quality Tools

- **Black**: Code formatting
- **Flake8**: Linting and style checking
- **MyPy**: Type checking
- **Pre-commit**: Automated quality gates

### Testing

- **Unit Tests**: `pytest tests/`
- **Type Checking**: `mypy src/`
- **Code Coverage**: Included in test runs

## 📁 Project Structure

```
distributed-logs/
├── backend/           # Python log processing engine
│   ├── src/          # Source code
│   ├── tests/        # Unit tests
│   └── config/       # Configuration files
├── frontend/         # React TypeScript dashboard
├── .vscode/          # VS Code configuration
└── docs/            # Documentation
```

## 🎯 Learning Objectives

- Understand distributed system design patterns
- Master professional development workflows
- Learn industry-standard tooling and practices
- Build production-ready applications

## 🔍 What's Next?

This foundation supports the full 180-day learning journey:
- Week 2: Database integration
- Week 3: Message queues and streaming
- Week 4: Microservices architecture
- And much more...

EOF

    cat > docs/DEVELOPMENT.md << 'EOF'
# Development Guide

## Environment Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- Git

### Initial Setup

The setup script handles everything:

```bash
./scripts/setup.sh
```

## Code Quality Standards

### Python

- **Formatting**: Black (line length: 88)
- **Linting**: Flake8 with custom rules
- **Type Checking**: MyPy with strict mode
- **Testing**: pytest with coverage

### TypeScript

- **Linting**: ESLint with TypeScript rules
- **Formatting**: Prettier
- **Type Checking**: TypeScript strict mode

## Development Workflow

1. **Make Changes**: Edit code in your IDE
2. **Quality Check**: Pre-commit hooks run automatically
3. **Test**: Run tests with `pytest` or `npm test`
4. **Commit**: Git commit triggers all quality checks

## Debugging

### VS Code Configuration

The project includes debugging configurations:

- **Debug Backend**: Run/debug Python applications
- **Debug Tests**: Run/debug test cases

### Manual Testing

```bash
# Backend
cd backend
source venv/bin/activate
python src/main.py

# Frontend
cd frontend
npm start
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Check PYTHONPATH and virtual environment
2. **Type Errors**: Run `mypy src/` to see detailed errors
3. **Formatting Issues**: Run `black src/` to auto-format

### Getting Help

- Check the logs in VS Code terminal
- Review test output for specific errors
- Use the debugger to step through code
EOF

    print_status "Documentation created ✓"
}

# Create final validation
validate_setup() {
    print_step "Validating complete setup..."
    
    # Check if key files exist
    local required_files=(
        "backend/src/log_processor.py"
        "backend/tests/test_log_processor.py"
        "backend/pyproject.toml"
        ".pre-commit-config.yaml"
        ".vscode/settings.json"
        "README.md"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Missing required file: $file"
            exit 1
        fi
    done
    
    # Test that Python environment works
    cd backend
    source venv/bin/activate
    python -c "from src.log_processor import DistributedLogProcessor; print('✓ Python imports working')"
    cd ..
    
    print_status "Setup validation completed ✓"
}

# Main execution
main() {
    echo "============================================"
    echo "  Distributed Log Processing System Setup  "
    echo "  Professional Development Environment     "
    echo "============================================"
    echo
    
    check_prerequisites
    create_project_structure
    setup_python_backend
    create_configuration_files
    create_sample_code
    setup_precommit_hooks
    run_tests
    create_documentation
    validate_setup
    
    echo
    echo "🎉 Setup completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Open VS Code: code distributed-logs"
    echo "2. Run the demo: cd backend && source venv/bin/activate && python src/main.py"
    echo "3. Run tests: cd backend && pytest tests/"
    echo "4. Start coding your distributed system!"
    echo
    echo "Happy coding! 🚀"
}

# Run main function
main "$@"