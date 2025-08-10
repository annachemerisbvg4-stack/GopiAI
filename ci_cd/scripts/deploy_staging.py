#!/usr/bin/env python3
"""
Staging Environment Deployment Script
More comprehensive deployment for staging environment
"""

import os
import sys
import json
import argparse
import subprocess
import logging
import time
import shutil
from pathlib import Path
from datetime import datetime


def setup_logging():
    """Setup logging for deployment"""
    log_dir = Path('ci_cd/logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f'deploy_staging_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def deploy_staging(environment: str, version: str, commit_hash: str = None):
    """Deploy to staging environment"""
    logger = setup_logging()
    logger.info(f"Starting staging deployment (version: {version})")
    
    try:
        # Create backup
        logger.info("Creating backup...")
        backup_info = create_backup()
        
        # Stop services gracefully
        logger.info("Stopping services...")
        stop_services_gracefully()
        
        # Update code
        if commit_hash:
            logger.info(f"Updating code to commit: {commit_hash}")
            update_code(commit_hash)
        
        # Build application
        logger.info("Building application...")
        build_application()
        
        # Install dependencies
        logger.info("Installing dependencies...")
        install_dependencies()
        
        # Run database migrations
        logger.info("Running database migrations...")
        run_migrations()
        
        # Update configuration
        logger.info("Updating configuration...")
        update_configuration()
        
        # Start services
        logger.info("Starting services...")
        start_services()
        
        # Wait for services to be ready
        logger.info("Waiting for services to be ready...")
        wait_for_services()
        
        # Update version info
        update_version_file(version, commit_hash)
        
        logger.info("Staging deployment completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Staging deployment failed: {e}")
        logger.info("Attempting rollback...")
        
        try:
            rollback_deployment(backup_info)
            logger.info("Rollback completed")
        except Exception as rollback_error:
            logger.error(f"Rollback failed: {rollback_error}")
        
        return False


def create_backup():
    """Create backup of current deployment"""
    logger = logging.getLogger(__name__)
    
    backup_dir = Path('ci_cd/backups/staging')
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f'backup_{timestamp}'
    backup_path.mkdir()
    
    # Backup current version info
    version_file = Path('ci_cd/versions/staging_version.txt')
    if version_file.exists():
        shutil.copy2(version_file, backup_path / 'version.txt')
    
    # Backup configuration files
    config_files = [
        '.env',
        'GopiAI-CrewAI/.env',
        'ci_cd/config/staging.json'
    ]
    
    for config_file in config_files:
        config_path = Path(config_file)
        if config_path.exists():
            shutil.copy2(config_path, backup_path / config_path.name)
    
    # Backup database (if applicable)
    backup_database(backup_path)
    
    backup_info = {
        'timestamp': timestamp,
        'path': str(backup_path),
        'version': get_current_version(),
        'environment': 'staging'
    }
    
    # Save backup info
    with open(backup_path / 'backup_info.json', 'w', encoding='utf-8') as f:
        json.dump(backup_info, f, indent=2)
    
    logger.info(f"Backup created at: {backup_path}")
    return backup_info


def stop_services_gracefully():
    """Stop services gracefully with proper shutdown"""
    logger = logging.getLogger(__name__)
    
    # Send SIGTERM to services first
    services = [
        {'name': 'CrewAI Server', 'pattern': 'crewai_api_server.py'},
        {'name': 'UI Application', 'pattern': 'gopiai.*ui'},
        {'name': 'Memory System', 'pattern': 'txtai.*server'}
    ]
    
    for service in services:
        try:
            # Send SIGTERM
            result = subprocess.run([
                'pkill', '-TERM', '-f', service['pattern']
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Sent shutdown signal to {service['name']}")
            
        except Exception as e:
            logger.warning(f"Could not signal {service['name']}: {e}")
    
    # Wait for graceful shutdown
    time.sleep(10)
    
    # Force kill if still running
    for service in services:
        try:
            result = subprocess.run([
                'pkill', '-KILL', '-f', service['pattern']
            ], capture_output=True, text=True)
            
        except Exception as e:
            logger.warning(f"Could not force stop {service['name']}: {e}")


def update_code(commit_hash: str):
    """Update code to specific commit"""
    logger = logging.getLogger(__name__)
    
    try:
        # Stash any local changes
        subprocess.run(['git', 'stash'], capture_output=True)
        
        # Fetch latest changes
        subprocess.run(['git', 'fetch', '--all'], check=True)
        
        # Checkout specific commit
        subprocess.run(['git', 'checkout', commit_hash], check=True)
        
        # Clean untracked files
        subprocess.run(['git', 'clean', '-fd'], check=True)
        
        logger.info(f"Updated code to commit: {commit_hash}")
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to update code: {e}")


def build_application():
    """Build application components"""
    logger = logging.getLogger(__name__)
    
    # Build UI components if needed
    ui_build_script = Path('GopiAI-UI/build.py')
    if ui_build_script.exists():
        try:
            subprocess.run([
                sys.executable, str(ui_build_script), '--environment', 'staging'
            ], check=True)
            logger.info("Built UI components")
        except subprocess.CalledProcessError as e:
            logger.warning(f"UI build failed: {e}")
    
    # Compile Python files
    try:
        subprocess.run([
            sys.executable, '-m', 'compileall', '.'
        ], check=True, capture_output=True)
        logger.info("Compiled Python files")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Python compilation failed: {e}")


def install_dependencies():
    """Install dependencies for staging"""
    logger = logging.getLogger(__name__)
    
    # Create virtual environment if it doesn't exist
    venv_path = Path('staging_env')
    if not venv_path.exists():
        subprocess.run([
            sys.executable, '-m', 'venv', str(venv_path)
        ], check=True)
        logger.info("Created virtual environment")
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        pip_path = venv_path / 'Scripts' / 'pip.exe'
        python_path = venv_path / 'Scripts' / 'python.exe'
    else:  # Unix/Linux
        pip_path = venv_path / 'bin' / 'pip'
        python_path = venv_path / 'bin' / 'python'
    
    # Upgrade pip
    subprocess.run([str(pip_path), 'install', '--upgrade', 'pip'], check=True)
    
    # Install requirements
    subprocess.run([
        str(pip_path), 'install', '-r', 'requirements.txt'
    ], check=True)
    
    # Install GopiAI modules
    modules = ['GopiAI-Core', 'GopiAI-UI', 'GopiAI-CrewAI', 'GopiAI-Assets']
    
    for module in modules:
        module_path = Path(module)
        if module_path.exists():
            subprocess.run([
                str(pip_path), 'install', '-e', str(module_path)
            ], check=True)
            logger.info(f"Installed {module}")


def run_migrations():
    """Run database migrations"""
    logger = logging.getLogger(__name__)
    
    migration_script = Path('ci_cd/scripts/run_migrations.py')
    
    if migration_script.exists():
        try:
            subprocess.run([
                sys.executable, str(migration_script), 
                '--environment', 'staging'
            ], check=True)
            logger.info("Database migrations completed")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Migration failed: {e}")
    else:
        logger.info("No migration script found")


def update_configuration():
    """Update configuration for staging environment"""
    logger = logging.getLogger(__name__)
    
    # Update environment-specific configuration
    staging_config = {
        'ENVIRONMENT': 'staging',
        'DEBUG': 'False',
        'LOG_LEVEL': 'INFO',
        'API_PORT': '5051',
        'UI_PORT': '8080'
    }
    
    # Update .env file
    env_file = Path('.env')
    if env_file.exists():
        # Read existing .env
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Update with staging values
        updated_lines = []
        updated_keys = set()
        
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip()
                if key in staging_config:
                    updated_lines.append(f"{key}={staging_config[key]}\n")
                    updated_keys.add(key)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        # Add new keys
        for key, value in staging_config.items():
            if key not in updated_keys:
                updated_lines.append(f"{key}={value}\n")
        
        # Write updated .env
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        logger.info("Updated .env configuration")


def start_services():
    """Start application services"""
    logger = logging.getLogger(__name__)
    
    # Use virtual environment python
    if os.name == 'nt':  # Windows
        python_path = Path('staging_env/Scripts/python.exe')
    else:  # Unix/Linux
        python_path = Path('staging_env/bin/python')
    
    # Start CrewAI server
    crewai_script = Path('GopiAI-CrewAI/crewai_api_server.py')
    if crewai_script.exists():
        subprocess.Popen([
            str(python_path), str(crewai_script)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("Started CrewAI server")
    
    # Start other services as needed
    # Note: UI is typically not auto-started in staging


def wait_for_services():
    """Wait for services to be ready"""
    logger = logging.getLogger(__name__)
    
    import requests
    
    # Wait for CrewAI server
    crewai_url = "http://localhost:5051/health"
    
    for attempt in range(30):  # 30 attempts, 10 seconds each = 5 minutes
        try:
            response = requests.get(crewai_url, timeout=5)
            if response.status_code == 200:
                logger.info("CrewAI server is ready")
                break
        except requests.RequestException:
            pass
        
        time.sleep(10)
    else:
        raise Exception("CrewAI server did not start within timeout")


def backup_database(backup_path: Path):
    """Backup database if applicable"""
    logger = logging.getLogger(__name__)
    
    # Check for SQLite databases
    db_files = list(Path('.').glob('*.db')) + list(Path('.').glob('**/*.db'))
    
    for db_file in db_files:
        try:
            shutil.copy2(db_file, backup_path / db_file.name)
            logger.info(f"Backed up database: {db_file}")
        except Exception as e:
            logger.warning(f"Could not backup database {db_file}: {e}")


def get_current_version():
    """Get current deployed version"""
    version_file = Path('ci_cd/versions/staging_version.txt')
    
    if version_file.exists():
        return version_file.read_text().strip()
    
    return "unknown"


def rollback_deployment(backup_info: dict):
    """Rollback to previous deployment"""
    logger = logging.getLogger(__name__)
    
    backup_path = Path(backup_info['path'])
    
    if not backup_path.exists():
        raise Exception(f"Backup path not found: {backup_path}")
    
    # Stop current services
    stop_services_gracefully()
    
    # Restore configuration files
    config_files = ['version.txt', '.env', 'staging.json']
    
    for config_file in config_files:
        backup_file = backup_path / config_file
        if backup_file.exists():
            if config_file == 'version.txt':
                target = Path('ci_cd/versions/staging_version.txt')
            elif config_file == '.env':
                target = Path('.env')
            elif config_file == 'staging.json':
                target = Path('ci_cd/config/staging.json')
            
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_file, target)
    
    # Restore database
    for db_file in backup_path.glob('*.db'):
        shutil.copy2(db_file, Path('.') / db_file.name)
    
    # Restart services
    start_services()
    wait_for_services()
    
    logger.info(f"Rollback completed to version: {backup_info.get('version', 'unknown')}")


def update_version_file(version: str, commit_hash: str = None):
    """Update version file"""
    version_dir = Path('ci_cd/versions')
    version_dir.mkdir(parents=True, exist_ok=True)
    
    version_file = version_dir / 'staging_version.txt'
    version_file.write_text(version)
    
    # Update deployment info
    deployment_info = {
        'version': version,
        'commit_hash': commit_hash,
        'environment': 'staging',
        'timestamp': datetime.now().isoformat(),
        'deployed_by': os.getenv('USER', 'unknown')
    }
    
    info_file = version_dir / 'staging_deployment.json'
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(deployment_info, f, indent=2)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Deploy to staging environment')
    parser.add_argument('--environment', required=True, help='Target environment')
    parser.add_argument('--version', required=True, help='Version to deploy')
    parser.add_argument('--commit-hash', help='Git commit hash')
    
    args = parser.parse_args()
    
    if args.environment != 'staging':
        print(f"Error: This script is only for staging environment, got: {args.environment}")
        sys.exit(1)
    
    success = deploy_staging(args.environment, args.version, args.commit_hash)
    
    if success:
        print(f"✅ Successfully deployed version {args.version} to staging")
        sys.exit(0)
    else:
        print(f"❌ Failed to deploy version {args.version} to staging")
        sys.exit(1)


if __name__ == '__main__':
    main()