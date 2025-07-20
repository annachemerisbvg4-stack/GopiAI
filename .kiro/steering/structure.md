# Project Structure

## Root Level Organization
```
GopiAI/
├── GopiAI-*/              # Modular components (installable packages)
├── 02_DOCUMENTATION/      # Project documentation and guides
├── 03_UTILITIES/          # Development and maintenance scripts
├── examples/              # txtai examples and tutorials
├── conversations/         # Chat history storage
├── logs/                  # Application and debug logs
├── .kiro/                 # Kiro AI assistant configuration
├── .serena/               # Serena AI assistant configuration
└── *.bat                  # Windows startup scripts
```

## Core Modules (GopiAI-*)
Each module is a separate installable Python package:

- **GopiAI-Core/**: Base interfaces, exceptions, and schema definitions
- **GopiAI-UI/**: Main desktop application and user interface
- **GopiAI-CrewAI/**: AI agent orchestration and API server
- **GopiAI-Extensions/**: Plugin system and extensibility framework
- **GopiAI-Widgets/**: Reusable UI components and widgets
- **GopiAI-App/**: Application packaging and distribution
- **GopiAI-Assets/**: Static resources and media files

## Module Structure Pattern
Each GopiAI-* module follows this structure:
```
GopiAI-Module/
├── gopiai/
│   └── module_name/       # Python package
├── tests/                 # Unit tests
├── pyproject.toml         # Package configuration
├── README.md              # Module documentation
└── requirements.txt       # Dependencies (if needed)
```

## Key Directories

### Documentation (02_DOCUMENTATION/)
- Integration guides and API documentation
- Project reports and cleanup summaries
- Memory system and RAG integration docs
- Error fixes and troubleshooting guides

### Utilities (03_UTILITIES/)
- Development and debugging scripts
- Project maintenance tools
- Environment setup utilities
- Logging and monitoring helpers

### Configuration
- **/.env**: Environment variables and API keys
- **/.kiro/**: Kiro AI assistant steering rules
- **/.serena/**: Serena AI assistant configuration

## Naming Conventions
- **Modules**: PascalCase with GopiAI- prefix
- **Python packages**: lowercase with underscores
- **Scripts**: snake_case.py or kebab-case.bat
- **Documentation**: UPPERCASE.md for major docs
- **Logs**: component_YYYYMMDD_HHMMSS.log format

## Import Structure
```python
# Core components
from gopiai.core import interfaces, exceptions, schema

# UI components  
from gopiai.ui import main, widgets, themes

# CrewAI integration
from gopiai.crewai import server, agents, tools

# Extensions
from gopiai.extensions import plugins, integrations
```

## Development Workflow
1. Work in individual GopiAI-* module directories
2. Install modules in development mode (`pip install -e .`)
3. Use batch scripts for multi-service startup
4. Logs automatically generated in /logs/ directory
5. Configuration managed through .env and steering files