# Technology Stack

## Build System
- **Package Management**: setuptools with pyproject.toml configuration
- **Development**: Editable installs for local modules (`-e ./GopiAI-*`)
- **Virtual Environments**: Multiple isolated Python environments per component

## Core Technologies
- **Python**: 3.8+ (3.9+ recommended)
- **GUI Framework**: PySide6 6.7.3 (Qt-based desktop application)
- **AI/ML**: OpenAI, Anthropic, LangChain, sentence-transformers, txtai
- **Memory/Search**: txtai 8.2.0+, FAISS, Qdrant
- **Web APIs**: FastAPI, Flask, uvicorn
- **NLP**: spaCy, transformers, tiktoken

## Virtual Environments
The project uses three isolated environments:
1. **crewai_env**: CrewAI server and AI orchestration
2. **gopiai_env**: Main UI application 
3. **txtai_env**: Legacy RAG/memory system (deprecated in v2.0+)

## Common Commands

### Development Startup
```bash
# Auto-launch all services
./start_auto_development.bat

# Individual services
./start_gopiai_ui.bat          # UI application
./start_crewai_api_server.bat  # CrewAI API server
```

### Environment Management
```bash
# Activate environments (Windows)
call crewai_env\Scripts\activate.bat
call gopiai_env\Scripts\activate.bat
call txtai_env\Scripts\activate.bat
```

### Module Installation
```bash
# Install in development mode
pip install -e ./GopiAI-Core
pip install -e ./GopiAI-UI
pip install -e ./GopiAI-Extensions
```

### Testing
```bash
# Run tests with pytest
pytest
pytest-qt  # For GUI components
```

## Configuration
- **Environment Variables**: `.env` files for API keys and settings
- **Smithery MCP**: `smithery_env.bat` for Model Context Protocol integration
- **Logging**: Extensive debug logging to `.log` files
- **Ports**: CrewAI API server runs on port 5051

## Code Style
- **Formatting**: Black (line-length: 88)
- **Import Sorting**: isort with black profile
- **Type Hints**: Encouraged for Python 3.9+ features