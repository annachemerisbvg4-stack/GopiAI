#!/usr/bin/env python3
"""
Development Environment Deployment Script
Simple deployment for local development environment
"""

import os
import sys
import json
import argparse
import subprocess
import logging
from pathlib import Path
from datetime import datetime


def setup_logging():
    """Setup logging for deployment"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def deploy_development(environment: str, version: str, commit_hash: str = None):
    """Deploy to development environment"""
    logger = setup_logging()
    logger.info(f"Starting development deployment (version: {version})")
    
    try:
        # Stop existing services
        logger.info("Stopping existing services...")
        stop_services()
        
        # Update code (if in git repository)
        if commit_hash:
            logger.info(f"Checking out commit: {commit_hash}")
            update_code(commit_hash)
        
        # Install/update dependencies
        logger.info("Installing dependencies...")
        install_dependencies()
        
        # Run database migrations (if any)
        logger.info("Running database migrations...")
        run_migrations()
        
        # Start services
        logger.info("Starting services...")
        start_services()
        
        # Update version file
        update_version_file(version)
        
        logger.info("Development deployment completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Development deployment failed: {e}")
        return False


def stop_services():
    """Stop running services"""
    logger = logging.getLogger(__name__)
    
    # Stop CrewAI server
    try:
        result = subprocess.run(
            ['pkill', '-f', 'crewai_api_server.py'],
            capture_output=True,
            text=True
        )
        logger.info("Stopped CrewAI server")
    except Exception as e:
        logger.warning(f"Could not stop CrewAI server: {e}")
    
    # Stop UI application
    try:
        result = subprocess.run(
            ['pkill', '-f', 'gopiai.*ui'],
            capture_output=True,
            text=True
        )
        logger.info("Stopped UI application")
    except Exception as e:
        logger.warning(f"Could not stop UI application: {e}")


def update_code(commit_hash: str):
    """Update code to specific commit"""
    logger = logging.getLogger(__name__)
    
    try:
        # Check if we're in a git repository
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.info("Not in a git repository, skipping code update")
            return
        
        # Fetch latest changes
        subprocess.run(['git', 'fetch'], check=True)
        
        # Checkout specific commit
        subprocess.run(['git', 'checkout', commit_hash], check=True)
        
        logger.info(f"Updated code to commit: {commit_hash}")
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to update code: {e}")


def install_dependencies():
    """Install or update dependencies"""
    logger = logging.getLogger(__name__)
    
    # Install main requirements
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True)
        logger.info("Installed main requirements")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to install main requirements: {e}")
    
    # Install GopiAI modules in development mode
    modules = ['GopiAI-Core', 'GopiAI-UI', 'GopiAI-CrewAI', 'GopiAI-Assets']
    
    for module in modules:
        module_path = Path(module)
        if module_path.exists():
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-e', str(module_path)
                ], check=True)
                logger.info(f"Installed {module} in development mode")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Could not install {module}: {e}")


def run_migrations():
    """Run database migrations if needed"""
    logger = logging.getLogger(__name__)
    
    # Check if migration script exists
    migration_script = Path('ci_cd/scripts/run_migrations.py')
    
    if migration_script.exists():
        try:
            subprocess.run([
                sys.executable, str(migration_script), '--environment', 'development'
            ], check=True)
            logger.info("Database migrations completed")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Migration failed: {e}")
    else:
        logger.info("No migration script found, skipping migrations")


def start_services():
    """Start application services"""
    logger = logging.getLogger(__name__)
    
    # Start CrewAI server in background
    try:
        crewai_script = Path('GopiAI-CrewAI/crewai_api_server.py')
        if crewai_script.exists():
            subprocess.Popen([
                sys.executable, str(crewai_script)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("Started CrewAI server")
        else:
            logger.warning("CrewAI server script not found")
    except Exception as e:
        logger.warning(f"Could not start CrewAI server: {e}")
    
    # Note: UI application is typically started manually in development


def update_version_file(version: str):
    """Update version file"""
    version_dir = Path('ci_cd/versions')
    version_dir.mkdir(parents=True, exist_ok=True)
    
    version_file = version_dir / 'development_version.txt'
    version_file.write_text(version)
    
    # Also update deployment info
    deployment_info = {
        'version': version,
        'environment': 'development',
        'timestamp': datetime.now().isoformat(),
        'deployed_by': os.getenv('USER', 'unknown')
    }
    
    info_file = version_dir / 'development_deployment.json'
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(deployment_info, f, indent=2)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Deploy to development environment')
    parser.add_argument('--environment', required=True, help='Target environment')
    parser.add_argument('--version', required=True, help='Version to deploy')
    parser.add_argument('--commit-hash', help='Git commit hash')
    
    args = parser.parse_args()
    
    if args.environment != 'development':
        print(f"Error: This script is only for development environment, got: {args.environment}")
        sys.exit(1)
    
    success = deploy_development(args.environment, args.version, args.commit_hash)
    
    if success:
        print(f"✅ Successfully deployed version {args.version} to development")
        sys.exit(0)
    else:
        print(f"❌ Failed to deploy version {args.version} to development")
        sys.exit(1)


if __name__ == '__main__':
    main()