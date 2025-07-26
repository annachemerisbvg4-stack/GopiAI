# Design Document

## Overview

The project cleanup system will be implemented as a comprehensive analysis tool that systematically examines the GopiAI codebase to identify areas for improvement. The system follows a non-destructive approach, focusing on analysis and reporting rather than making immediate changes to the codebase.

## Architecture

The cleanup system will be organized into several specialized analyzer modules, each responsible for a specific aspect of code analysis:

```
ProjectCleanupAnalyzer
├── StructureAnalyzer      # Project organization analysis
├── CodeQualityAnalyzer    # Code style and quality assessment
├── DeadCodeAnalyzer       # Unused code detection
├── FileAnalyzer           # Outdated and temporary file detection
├── DependencyAnalyzer     # External dependency analysis
├── DuplicateAnalyzer      # Code duplication detection
├── ConflictAnalyzer       # Potential error and conflict detection
├── DocumentationAnalyzer  # Documentation quality assessment
└── ReportGenerator        # Comprehensive report creation
```

## Components and Interfaces

### Core Analyzer Interface

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    category: str
    severity: str  # 'high', 'medium', 'low'
    description: str
    file_path: str
    line_number: int = None
    recommendation: str = ""
    
class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, project_path: str) -> List[AnalysisResult]:
        pass
    
    @abstractmethod
    def get_analyzer_name(self) -> str:
        pass
```

### ProjectCleanupAnalyzer (Main Orchestrator)

```python
class ProjectCleanupAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.analyzers = [
            StructureAnalyzer(),
            CodeQualityAnalyzer(),
            DeadCodeAnalyzer(),
            FileAnalyzer(),
            DependencyAnalyzer(),
            DuplicateAnalyzer(),
            ConflictAnalyzer(),
            DocumentationAnalyzer()
        ]
        self.report_generator = ReportGenerator()
    
    def run_full_analysis(self) -> Dict[str, Any]:
        # Orchestrate all analyzers and generate comprehensive report
        pass
```

### Specialized Analyzers

#### StructureAnalyzer
- Analyzes directory organization and module relationships
- Validates adherence to GopiAI-* naming conventions
- Identifies misplaced files and inconsistent structures

#### CodeQualityAnalyzer
- Uses AST parsing to analyze Python code quality
- Checks for PEP 8 compliance using tools like `flake8` or `black --check`
- Identifies complex functions (high cyclomatic complexity)
- Analyzes code consistency across modules

#### DeadCodeAnalyzer
- Uses static analysis to find unused imports, functions, and classes
- Leverages tools like `vulture` for dead code detection
- Analyzes import graphs to identify unreferenced modules
- Scans for commented-out code blocks

#### FileAnalyzer
- Scans for temporary files (*.tmp, *.bak, *~)
- Identifies log files that might be outdated
- Finds duplicate files based on content hashing
- Analyzes file modification timestamps

#### DependencyAnalyzer
- Parses all pyproject.toml and requirements.txt files
- Uses `pip-audit` or similar tools for security analysis
- Checks for version conflicts between modules
- Identifies unused dependencies

#### DuplicateAnalyzer
- Uses AST-based similarity detection
- Implements code clone detection algorithms
- Identifies similar function signatures and implementations
- Suggests refactoring opportunities

#### ConflictAnalyzer
- Analyzes global variable usage patterns
- Identifies potential race conditions in threading code
- Checks for resource management issues
- Scans for unhandled exceptions

#### DocumentationAnalyzer
- Validates README.md files against current project state
- Checks docstring coverage for public APIs
- Analyzes documentation consistency
- Identifies outdated documentation references

## Data Models

### Analysis Configuration

```python
@dataclass
class AnalysisConfig:
    project_path: str
    exclude_patterns: List[str] = None  # Patterns to exclude from analysis
    include_patterns: List[str] = None  # Specific patterns to include
    severity_threshold: str = 'low'     # Minimum severity to report
    output_format: str = 'markdown'     # 'markdown', 'json', 'html'
    detailed_analysis: bool = True      # Include detailed recommendations
```

### Report Structure

```python
@dataclass
class CleanupReport:
    timestamp: str
    project_path: str
    summary: Dict[str, int]  # Category -> count mapping
    results_by_category: Dict[str, List[AnalysisResult]]
    recommendations: List[str]
    priority_actions: List[AnalysisResult]
```

## Error Handling

The system implements comprehensive error handling:

1. **File Access Errors**: Gracefully handle permission issues and missing files
2. **Parsing Errors**: Continue analysis even if some files cannot be parsed
3. **Tool Integration Errors**: Provide fallback analysis when external tools fail
4. **Memory Management**: Handle large codebases without memory exhaustion

```python
class AnalysisError(Exception):
    def __init__(self, analyzer: str, file_path: str, error: str):
        self.analyzer = analyzer
        self.file_path = file_path
        self.error = error
        super().__init__(f"{analyzer}: {error} in {file_path}")

class ErrorHandler:
    def __init__(self):
        self.errors = []
    
    def handle_error(self, error: AnalysisError):
        self.errors.append(error)
        # Log error but continue analysis
```

## Testing Strategy

### Unit Testing
- Test each analyzer independently with mock project structures
- Verify correct identification of various code issues
- Test error handling and edge cases

### Integration Testing
- Test full analysis pipeline with real GopiAI modules
- Verify report generation accuracy
- Test performance with large codebases

### Test Data
- Create sample projects with known issues for validation
- Use existing GopiAI modules as integration test subjects
- Maintain test cases for regression testing

```python
# Example test structure
class TestDeadCodeAnalyzer:
    def test_identifies_unused_imports(self):
        # Test with sample file containing unused imports
        pass
    
    def test_finds_unreferenced_functions(self):
        # Test with sample file containing unused functions
        pass
    
    def test_handles_parsing_errors_gracefully(self):
        # Test with malformed Python files
        pass
```

## Implementation Considerations

### Performance Optimization
- Use multiprocessing for parallel analysis of different modules
- Implement caching for expensive operations (AST parsing, file hashing)
- Provide progress reporting for long-running analyses

### Extensibility
- Plugin architecture for adding new analyzers
- Configuration system for customizing analysis rules
- Support for different programming languages (future enhancement)

### Integration with GopiAI
- Respect existing .gitignore patterns
- Integrate with GopiAI logging system
- Support for GopiAI-specific conventions and patterns

### Output Formats
- Markdown reports for human readability
- JSON output for programmatic processing
- HTML reports with interactive features
- Integration with development tools (VS Code, etc.)