#!/bin/bash
# Automated Test Runner Shell Script for Unix/Linux CI/CD
# Supports different environments and test types

set -e  # Exit on any error

# Default values
ENVIRONMENT="development"
TEST_TYPES=""
CONFIG_FILE=""
OUTPUT_DIR=""
VERBOSE=false

# Function to show help
show_help() {
    cat << EOF
GopiAI Automated Test Runner

Usage: run_automated_tests.sh [OPTIONS]

Options:
  --environment, -e    Target environment (development, staging, production)
  --test-types, -t     Test types to run (unit, integration, ui, e2e, performance, security)
  --config, -c         Configuration file path
  --output, -o         Output directory for reports
  --verbose            Show verbose output
  --help               Show this help message

Examples:
  ./run_automated_tests.sh --environment staging --test-types "unit integration"
  ./run_automated_tests.sh -e production -t "unit integration ui e2e"
  ./run_automated_tests.sh --config ci_cd/config/production.json --verbose
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --environment|-e)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --test-types|-t)
            TEST_TYPES="$2"
            shift 2
            ;;
        --config|-c)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --output|-o)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to archive artifacts
archive_artifacts() {
    log "Archiving test artifacts..."
    ARCHIVE_DIR="ci_cd/artifacts/$(date '+%Y%m%d_%H%M%S')"
    mkdir -p "$ARCHIVE_DIR"
    
    # Copy reports
    if [ -d "ci_cd/reports" ]; then
        cp -r ci_cd/reports/* "$ARCHIVE_DIR/reports/" 2>/dev/null || true
    fi
    
    # Copy logs
    cp "$LOG_FILE" "$ARCHIVE_DIR/" 2>/dev/null || true
    
    # Copy coverage files
    cp .coverage* "$ARCHIVE_DIR/" 2>/dev/null || true
    
    log "Artifacts archived to: $ARCHIVE_DIR"
}

# Main execution
main() {
    echo "========================================"
    echo "GopiAI Automated Test Runner"
    echo "========================================"
    echo "Environment: $ENVIRONMENT"
    echo "Test Types: $TEST_TYPES"
    echo "Timestamp: $(date)"
    echo "========================================"
    
    # Create necessary directories
    mkdir -p ci_cd/{logs,reports,artifacts}
    
    # Set log file
    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    LOG_FILE="ci_cd/logs/automated_tests_${TIMESTAMP}.log"
    
    log "Starting automated test execution..."
    
    # Check Python availability
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        log "ERROR: Python is not available in PATH"
        exit 1
    fi
    
    # Use python3 if available, otherwise python
    PYTHON_CMD="python3"
    if ! command -v python3 &> /dev/null; then
        PYTHON_CMD="python"
    fi
    
    # Build command
    CMD="$PYTHON_CMD ci_cd/automated_test_runner.py --environment $ENVIRONMENT"
    
    if [ -n "$TEST_TYPES" ]; then
        CMD="$CMD --test-types $TEST_TYPES"
    fi
    
    if [ -n "$CONFIG_FILE" ]; then
        CMD="$CMD --config \"$CONFIG_FILE\""
    fi
    
    if [ -n "$OUTPUT_DIR" ]; then
        CMD="$CMD --output \"$OUTPUT_DIR\""
    fi
    
    # Execute tests
    log "Executing: $CMD"
    echo
    
    EXIT_CODE=0
    if [ "$VERBOSE" = true ]; then
        eval $CMD 2>&1 | tee -a "$LOG_FILE"
        EXIT_CODE=${PIPESTATUS[0]}
    else
        eval $CMD >> "$LOG_FILE" 2>&1
        EXIT_CODE=$?
    fi
    
    # Show results
    echo
    log "========================================"
    log "Test execution completed with exit code: $EXIT_CODE"
    log "Log file: $LOG_FILE"
    
    # Show last execution result if available
    if [ -f "ci_cd/last_execution_result.json" ]; then
        echo
        log "Last execution summary:"
        cat "ci_cd/last_execution_result.json" | tee -a "$LOG_FILE"
    fi
    
    log "========================================"
    
    # Archive artifacts if tests passed
    if [ $EXIT_CODE -eq 0 ]; then
        archive_artifacts
    fi
    
    exit $EXIT_CODE
}

# Run main function
main "$@"