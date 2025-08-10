# GopiAI

A comprehensive collection of artificial intelligence modules for the GopiAI project, featuring multi-agent coordination, intelligent UI components, and advanced LLM provider management.

> 🚀 **Quick Start**: New to GopiAI? Check out our [Quick Start Guide](QUICK_START.md) to get up and running quickly!

## Table of Contents

- [Project Structure](#project-structure)
- [Core Modules](#core-modules)
- [Features](#features)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Documentation](#documentation)
- [Task Status](#task-status)
- [License](#license)

## Project Structure

```text
GopiAI/
├── GopiAI-CrewAI/          # Main CrewAI integration module
├── GopiAI-UI/              # User interface components
├── GopiAI-Assets/          # Project assets and resources
├── 02_DOCUMENTATION/       # Project documentation
├── 03_UTILITIES/           # Utility scripts and tools
├── rag_memory_system/      # RAG memory system implementation
├── test_infrastructure/    # Testing framework and utilities
├── tests/                  # Test suites
└── requirements.txt        # Project dependencies
```

## Features

- 🤖 **Multi-Agent Coordination**: Seamless integration with CrewAI for intelligent agent orchestration
- 🔄 **Smart LLM Switching**: Automatic provider rotation with rate limit handling
- 🎨 **Modern UI**: Qt-based interface with responsive design
- 🧠 **RAG Memory**: Advanced retrieval-augmented generation for context awareness
- 🧪 **Comprehensive Testing**: Automated test suites with continuous validation
- 📊 **Real-time Monitoring**: Live status tracking and performance metrics

## Core Modules

### 1. GopiAI-CrewAI
CrewAI integration module for coordinating agents and tasks.

**Key Files:**
- [`llm_rotation_config.py`](GopiAI-CrewAI/llm_rotation_config.py) - Enhanced LLM provider switching system
- [`crewai_api_server.py`](GopiAI-CrewAI/crewai_api_server.py) - REST API server for state synchronization
- [`state_manager.py`](GopiAI-CrewAI/state_manager.py) - Application state management
- [`model_selector_widget.py`](GopiAI-UI/gopiai/ui/components/model_selector_widget.py) - Model selection UI widget

**Latest Updates:** Successfully implemented enhanced LLM provider switching system! 
- ✅ Stable state synchronization between UI and Backend
- ✅ Soft blacklist for models exceeding rate limits
- ✅ Reliable API key rotation without duplicates
- ✅ Automated tests to prevent regressions

### 2. GopiAI-UI
Qt-based user interface for system interaction and visualization.

### 3. RAG Memory System
Advanced retrieval-augmented generation system for intelligent memory management.

### 4. Testing Infrastructure
Comprehensive testing framework with automated validation and reporting.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For REST API server functionality
pip install fastapi uvicorn requests
```

## Getting Started

### Starting the REST API Server
```bash
cd GopiAI-CrewAI
python crewai_api_server.py
```

### Running Tests
```bash
cd GopiAI-CrewAI
python run_all_tests.py
```

### Basic Usage Example
```python
# Example: Using the CrewAI integration
from GopiAI-CrewAI.crewai_api_server import CrewAIServer
from GopiAI-CrewAI.state_manager import StateManager

# Initialize the system
server = CrewAIServer()
state_manager = StateManager()

# Start coordinating AI agents
server.start()
```

## Documentation

Comprehensive documentation is available in the [`02_DOCUMENTATION/`](02_DOCUMENTATION/) directory:
- [`MODEL_SWITCHING_README.md`](GopiAI-CrewAI/MODEL_SWITCHING_README.md) - Provider switching system documentation
- [`MODEL_SWITCHING_FINAL_REPORT.md`](GopiAI-CrewAI/MODEL_SWITCHING_FINAL_REPORT.md) - Implementation final report
- [`CREWAI_INTEGRATION_PLAN.md`](02_DOCUMENTATION/CREWAI_INTEGRATION_PLAN.md) - CrewAI integration plan

## Task Status

The project uses the Agentic Control Framework (ACF) for task management. Current task status can be viewed in the ACF tools.

**Latest Implementation:** Enhanced LLM provider switching system (Task #74 - COMPLETED)

## License

MIT License - see the LICENSE file for details.
