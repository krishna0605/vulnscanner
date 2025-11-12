#!/usr/bin/env python3
"""
Enhanced Vulnerability Scanner - Production Deployment Script

This script automates the deployment process for the vulnerability scanner,
including health checks, database migrations, and rollback capabilities.
"""

import os
import sys
import time
import json
import subprocess
import argparse
import logging
from typing import Dict, Optional
from pathlib import Path
import requests
import yaml
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deployment.log')
    ]
)
logger = logging.getLogger(__name__)


class DeploymentError(Exception):
    """Custom exception for deployment errors."""
    pass


class HealthCheckError(Exception):
    """Custom exception for health check failures."""
    pass


class DeploymentManager:
    """
    Manages the deployment process for the Enhanced Vulnerability Scanner.
    """
    
    def __init__(self, environment: str = "production", config_file: Optional[str] = None):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.config = self._load_config(config_file)
        self.deployment_id = f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Deployment state
        self.previous_version = None
        self.current_version = None
        self.rollback_data = {}
        
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """Load deployment configuration."""
        if config_file:
            config_path = Path(config_file)
        else:
            config_path = self.project_root / "deployment" / f"{self.environment}.yml"
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}")
            return self._get_default_config()
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict:
        """Get default deployment configuration."""
        return {
            "environment": self.environment,
            "deployment_type": "docker-compose",  # or "kubernetes"
            "health_check": {
                "timeout": 300,
                "interval": 10,
                "retries": 30
            },
            "services": {
                "backend": {
                    "image": "vulscanner/backend:latest",
                    "health_endpoint": "/api/v1/health",
                    "port": 8000
                },
                "frontend": {
                    "image": "vulscanner/frontend:latest",
                    "health_endpoint": "/",
                    "port": 3000
                },
                "celery": {
                    "image": "vulscanner/backend:latest",
                    "health_command": ["celery", "-A", "tasks.celery_app", "inspect", "ping"]
                }
            },
            "database": {
                "migration_timeout": 600,
                "backup_before_migration": True
            },
            "monitoring": {
                "slack_webhook": os.getenv("SLACK_WEBHOOK_URL"),
                "email_notifications": True
            }
        }
    
    def deploy(self, version: Optional[str] = None, skip_tests: bool = False) -> bool:
        """
        Execute the complete deployment process.
        
        Args:
            version: Specific version to deploy (defaults to latest)
            skip_tests: Skip pre-deployment tests
            
        Returns:
            bool: True if deployment successful, False otherwise
        """
        try:
            logger.info(f"Starting deployment {self.deployment_id} to {self.environment}")
            
            # Pre-deployment checks
            self._pre_deployment_checks()
            
            # Store current state for rollback
            self._store_rollback_data()
            
            # Run tests if not skipped
            if not skip_tests:
                self._run_tests()
            
            # Build and push images
            if version:
                self.current_version = version
            else:
                self.current_version = self._build_and_push_images()
            
            # Database backup and migration
            self._handle_database_migration()
            
            # Deploy services
            self._deploy_services()
            
            # Health checks
            self._perform_health_checks()
            
            # Post-deployment tasks
            self._post_deployment_tasks()
            
            # Send success notification
            self._send_notification("success", f"Deployment {self.deployment_id} completed successfully")
            
            logger.info(f"Deployment {self.deployment_id} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            self._send_notification("error", f"Deployment {self.deployment_id} failed: {e}")
            
            # Attempt rollback
            if self.rollback_data:
                logger.info("Attempting automatic rollback...")
                try:
                    self.rollback()
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")
                    self._send_notification("critical", f"Deployment and rollback both failed: {rollback_error}")
            
            return False
    
    def _pre_deployment_checks(self):
        """Perform pre-deployment validation checks."""
        logger.info("Performing pre-deployment checks...")
        
        # Check required environment variables
        required_env_vars = [
            "DATABASE_URL", "REDIS_URL", "SECRET_KEY",
            "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            raise DeploymentError(f"Missing required environment variables: {missing_vars}")
        
        # Check Docker/Kubernetes availability
        if self.config["deployment_type"] == "docker-compose":
            self._check_docker()
        elif self.config["deployment_type"] == "kubernetes":
            self._check_kubernetes()
        
        # Check external dependencies
        self._check_external_dependencies()
        
        logger.info("Pre-deployment checks passed")
    
    def _check_docker(self):
        """Check Docker and Docker Compose availability."""
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            raise DeploymentError("Docker or Docker Compose not available")
    
    def _check_kubernetes(self):
        """Check Kubernetes cluster connectivity."""
        try:
            subprocess.run(["kubectl", "cluster-info"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            raise DeploymentError("Kubernetes cluster not accessible")
    
    def _check_external_dependencies(self):
        """Check external service availability."""
        dependencies = [
            ("Supabase", os.getenv("SUPABASE_URL")),
            ("Redis", os.getenv("REDIS_URL")),
        ]
        
        for name, url in dependencies:
            if url:
                try:
                    # Simple connectivity check
                    if url.startswith("http"):
                        response = requests.get(f"{url}/health", timeout=10)
                        if response.status_code >= 400:
                            logger.warning(f"{name} health check returned {response.status_code}")
                except Exception as e:
                    logger.warning(f"Could not verify {name} connectivity: {e}")
    
    def _store_rollback_data(self):
        """Store current deployment state for potential rollback."""
        logger.info("Storing rollback data...")
        
        try:
            if self.config["deployment_type"] == "docker-compose":
                # Get current container images
                result = subprocess.run(
                    ["docker-compose", "-f", "docker-compose.prod.yml", "images", "--quiet"],
                    capture_output=True, text=True, cwd=self.project_root
                )
                self.rollback_data["images"] = result.stdout.strip().split('\n')
                
            elif self.config["deployment_type"] == "kubernetes":
                # Get current deployment images
                result = subprocess.run(
                    ["kubectl", "get", "deployments", "-n", "vulscanner", "-o", "json"],
                    capture_output=True, text=True
                )
                deployments = json.loads(result.stdout)
                self.rollback_data["deployments"] = deployments
            
            # Store database schema version
            self.rollback_data["db_version"] = self._get_database_version()
            
            logger.info("Rollback data stored successfully")
            
        except Exception as e:
            logger.warning(f"Could not store rollback data: {e}")
    
    def _run_tests(self):
        """Run pre-deployment tests."""
        logger.info("Running pre-deployment tests...")
        
        test_commands = [
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
            ["python", "-m", "pytest", "tests/integration/", "-v"],
        ]
        
        for cmd in test_commands:
            try:
                subprocess.run(cmd, check=True, cwd=self.project_root / "backend")
            except subprocess.CalledProcessError as e:
                raise DeploymentError(f"Tests failed: {e}")
        
        logger.info("All tests passed")
    
    def _build_and_push_images(self) -> str:
        """Build and push Docker images."""
        logger.info("Building and pushing Docker images...")
        
        # Generate version tag
        version = f"v{datetime.now().strftime('%Y.%m.%d')}-{self.deployment_id[-6:]}"
        
        # Build backend image
        backend_tag = f"vulscanner/backend:{version}"
        subprocess.run([
            "docker", "build", "-t", backend_tag,
            "-f", "backend/Dockerfile", "backend/"
        ], check=True, cwd=self.project_root)
        
        # Build frontend image
        frontend_tag = f"vulscanner/frontend:{version}"
        subprocess.run([
            "docker", "build", "-t", frontend_tag,
            "-f", "frontend/Dockerfile", "frontend/"
        ], check=True, cwd=self.project_root)
        
        # Push images (if registry configured)
        registry = os.getenv("DOCKER_REGISTRY")
        if registry:
            for tag in [backend_tag, frontend_tag]:
                registry_tag = f"{registry}/{tag}"
                subprocess.run(["docker", "tag", tag, registry_tag], check=True)
                subprocess.run(["docker", "push", registry_tag], check=True)
        
        logger.info(f"Images built and tagged with version: {version}")
        return version
    
    def _handle_database_migration(self):
        """Handle database backup and migration."""
        logger.info("Handling database migration...")
        
        if self.config["database"]["backup_before_migration"]:
            self._backup_database()
        
        # Run database migrations
        try:
            subprocess.run([
                "python", "-m", "alembic", "upgrade", "head"
            ], check=True, cwd=self.project_root / "backend", timeout=self.config["database"]["migration_timeout"])
            
            logger.info("Database migration completed")
            
        except subprocess.TimeoutExpired:
            raise DeploymentError("Database migration timed out")
        except subprocess.CalledProcessError as e:
            raise DeploymentError(f"Database migration failed: {e}")
    
    def _backup_database(self):
        """Create database backup."""
        logger.info("Creating database backup...")
        
        backup_file = f"backup-{self.deployment_id}.sql"
        backup_path = self.project_root / "backups" / backup_file
        backup_path.parent.mkdir(exist_ok=True)
        
        # Extract database connection details
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            logger.warning("No DATABASE_URL found, skipping backup")
            return
        
        try:
            subprocess.run([
                "pg_dump", db_url, "-f", str(backup_path)
            ], check=True, timeout=300)
            
            self.rollback_data["backup_file"] = str(backup_path)
            logger.info(f"Database backup created: {backup_file}")
            
        except Exception as e:
            logger.warning(f"Database backup failed: {e}")
    
    def _deploy_services(self):
        """Deploy application services."""
        logger.info("Deploying services...")
        
        if self.config["deployment_type"] == "docker-compose":
            self._deploy_docker_compose()
        elif self.config["deployment_type"] == "kubernetes":
            self._deploy_kubernetes()
        else:
            raise DeploymentError(f"Unsupported deployment type: {self.config['deployment_type']}")
    
    def _deploy_docker_compose(self):
        """Deploy using Docker Compose."""
        compose_file = "docker-compose.prod.yml"
        
        # Set version in environment
        env = os.environ.copy()
        if self.current_version:
            env["IMAGE_TAG"] = self.current_version
        
        # Pull latest images
        subprocess.run([
            "docker-compose", "-f", compose_file, "pull"
        ], check=True, cwd=self.project_root, env=env)
        
        # Deploy with rolling update
        subprocess.run([
            "docker-compose", "-f", compose_file, "up", "-d", "--remove-orphans"
        ], check=True, cwd=self.project_root, env=env)
        
        logger.info("Docker Compose deployment completed")
    
    def _deploy_kubernetes(self):
        """Deploy using Kubernetes."""
        k8s_dir = self.project_root / "k8s"
        
        # Apply configurations
        for manifest in ["namespace.yaml", "configmap.yaml", "secrets.yaml"]:
            subprocess.run([
                "kubectl", "apply", "-f", str(k8s_dir / manifest)
            ], check=True)
        
        # Deploy applications
        for manifest in ["backend-deployment.yaml", "frontend-deployment.yaml", "celery-deployment.yaml"]:
            if (k8s_dir / manifest).exists():
                subprocess.run([
                    "kubectl", "apply", "-f", str(k8s_dir / manifest)
                ], check=True)
        
        # Wait for rollout
        subprocess.run([
            "kubectl", "rollout", "status", "deployment/vulscanner-backend", "-n", "vulscanner"
        ], check=True, timeout=600)
        
        logger.info("Kubernetes deployment completed")
    
    def _perform_health_checks(self):
        """Perform comprehensive health checks."""
        logger.info("Performing health checks...")
        
        health_config = self.config["health_check"]
        timeout = health_config["timeout"]
        interval = health_config["interval"]
        max_retries = health_config["retries"]
        
        start_time = time.time()
        
        for service_name, service_config in self.config["services"].items():
            logger.info(f"Checking health of {service_name}...")
            
            retries = 0
            while retries < max_retries:
                try:
                    if "health_endpoint" in service_config:
                        self._check_http_health(service_name, service_config)
                    elif "health_command" in service_config:
                        self._check_command_health(service_name, service_config)
                    
                    logger.info(f"{service_name} is healthy")
                    break
                    
                except HealthCheckError as e:
                    retries += 1
                    elapsed = time.time() - start_time
                    
                    if elapsed > timeout:
                        raise DeploymentError(f"Health check timeout for {service_name}")
                    
                    if retries >= max_retries:
                        raise DeploymentError(f"Health check failed for {service_name}: {e}")
                    
                    logger.warning(f"{service_name} health check failed (attempt {retries}/{max_retries}): {e}")
                    time.sleep(interval)
        
        logger.info("All health checks passed")
    
    def _check_http_health(self, service_name: str, service_config: Dict):
        """Check HTTP endpoint health."""
        endpoint = service_config["health_endpoint"]
        port = service_config["port"]
        
        # Determine URL based on deployment type
        if self.config["deployment_type"] == "docker-compose":
            url = f"http://localhost:{port}{endpoint}"
        else:
            # For Kubernetes, use port-forward or service URL
            url = f"http://vulscanner-{service_name}:{port}{endpoint}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code >= 400:
                raise HealthCheckError(f"HTTP {response.status_code}: {response.text}")
        except requests.RequestException as e:
            raise HealthCheckError(f"HTTP request failed: {e}")
    
    def _check_command_health(self, service_name: str, service_config: Dict):
        """Check service health using command."""
        command = service_config["health_command"]
        
        try:
            if self.config["deployment_type"] == "docker-compose":
                # Execute in container
                container_name = f"vulscanner-{service_name}-prod"
                full_command = ["docker", "exec", container_name] + command
            else:
                # Execute in Kubernetes pod
                pod_name = subprocess.run([
                    "kubectl", "get", "pods", "-n", "vulscanner",
                    "-l", f"app.kubernetes.io/component={service_name}",
                    "-o", "jsonpath={.items[0].metadata.name}"
                ], capture_output=True, text=True, check=True).stdout.strip()
                
                full_command = ["kubectl", "exec", "-n", "vulscanner", pod_name, "--"] + command
            
            subprocess.run(full_command, check=True, capture_output=True, timeout=30)
            
        except subprocess.CalledProcessError as e:
            raise HealthCheckError(f"Command failed: {e}")
        except subprocess.TimeoutExpired:
            raise HealthCheckError("Command timed out")
    
    def _post_deployment_tasks(self):
        """Execute post-deployment tasks."""
        logger.info("Executing post-deployment tasks...")
        
        # Clear caches
        self._clear_caches()
        
        # Update monitoring dashboards
        self._update_monitoring()
        
        # Run smoke tests
        self._run_smoke_tests()
        
        logger.info("Post-deployment tasks completed")
    
    def _clear_caches(self):
        """Clear application caches."""
        try:
            # Clear Redis cache
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                import redis
                r = redis.from_url(redis_url)
                r.flushdb()
                logger.info("Redis cache cleared")
        except Exception as e:
            logger.warning(f"Could not clear cache: {e}")
    
    def _update_monitoring(self):
        """Update monitoring configurations."""
        try:
            # Reload Prometheus configuration
            prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
            requests.post(f"{prometheus_url}/-/reload", timeout=10)
            logger.info("Prometheus configuration reloaded")
        except Exception as e:
            logger.warning(f"Could not reload Prometheus: {e}")
    
    def _run_smoke_tests(self):
        """Run basic smoke tests."""
        logger.info("Running smoke tests...")
        
        smoke_tests = [
            ("API Health", "http://localhost:8000/api/v1/health"),
            ("Frontend", "http://localhost:3000"),
            ("Metrics", "http://localhost:8000/api/v1/metrics"),
        ]
        
        for test_name, url in smoke_tests:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code < 400:
                    logger.info(f"✓ {test_name} smoke test passed")
                else:
                    logger.warning(f"✗ {test_name} smoke test failed: HTTP {response.status_code}")
            except Exception as e:
                logger.warning(f"✗ {test_name} smoke test failed: {e}")
    
    def rollback(self) -> bool:
        """Rollback to previous deployment."""
        logger.info(f"Starting rollback for deployment {self.deployment_id}")
        
        try:
            if not self.rollback_data:
                raise DeploymentError("No rollback data available")
            
            # Rollback services
            if self.config["deployment_type"] == "docker-compose":
                self._rollback_docker_compose()
            elif self.config["deployment_type"] == "kubernetes":
                self._rollback_kubernetes()
            
            # Rollback database if needed
            if "backup_file" in self.rollback_data:
                self._rollback_database()
            
            # Health checks
            self._perform_health_checks()
            
            logger.info("Rollback completed successfully")
            self._send_notification("warning", f"Rollback for deployment {self.deployment_id} completed")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            self._send_notification("critical", f"Rollback failed: {e}")
            return False
    
    def _rollback_docker_compose(self):
        """Rollback Docker Compose deployment."""
        if "images" in self.rollback_data:
            # This is a simplified rollback - in practice, you'd need to track
            # the previous docker-compose configuration
            subprocess.run([
                "docker-compose", "-f", "docker-compose.prod.yml", "down"
            ], cwd=self.project_root)
            
            # Restore previous images (implementation depends on your tagging strategy)
            logger.info("Docker Compose rollback completed")
    
    def _rollback_kubernetes(self):
        """Rollback Kubernetes deployment."""
        subprocess.run([
            "kubectl", "rollout", "undo", "deployment/vulscanner-backend", "-n", "vulscanner"
        ], check=True)
        
        subprocess.run([
            "kubectl", "rollout", "undo", "deployment/vulscanner-frontend", "-n", "vulscanner"
        ], check=True)
        
        logger.info("Kubernetes rollback completed")
    
    def _rollback_database(self):
        """Rollback database changes."""
        backup_file = self.rollback_data["backup_file"]
        db_url = os.getenv("DATABASE_URL")
        
        if backup_file and db_url:
            logger.warning("Database rollback is destructive - manual intervention recommended")
            # In practice, you might want to require manual confirmation for DB rollback
    
    def _get_database_version(self) -> Optional[str]:
        """Get current database schema version."""
        try:
            result = subprocess.run([
                "python", "-c",
                "from alembic import command; from alembic.config import Config; "
                "cfg = Config('alembic.ini'); command.current(cfg)"
            ], capture_output=True, text=True, cwd=self.project_root / "backend")
            return result.stdout.strip()
        except Exception:
            return None
    
    def _send_notification(self, level: str, message: str):
        """Send deployment notification."""
        logger.info(f"Notification ({level}): {message}")
        
        # Slack notification
        slack_webhook = self.config["monitoring"].get("slack_webhook")
        if slack_webhook:
            try:
                color_map = {
                    "success": "good",
                    "warning": "warning",
                    "error": "danger",
                    "critical": "danger"
                }
                
                payload = {
                    "attachments": [{
                        "color": color_map.get(level, "warning"),
                        "title": f"Deployment {level.title()}",
                        "text": message,
                        "fields": [
                            {"title": "Environment", "value": self.environment, "short": True},
                            {"title": "Deployment ID", "value": self.deployment_id, "short": True},
                            {"title": "Version", "value": self.current_version or "unknown", "short": True},
                            {"title": "Timestamp", "value": datetime.now().isoformat(), "short": True}
                        ]
                    }]
                }
                
                requests.post(slack_webhook, json=payload, timeout=10)
            except Exception as e:
                logger.warning(f"Failed to send Slack notification: {e}")


def main():
    """Main deployment script entry point."""
    parser = argparse.ArgumentParser(description="Enhanced Vulnerability Scanner Deployment")
    parser.add_argument("--environment", "-e", default="production", help="Deployment environment")
    parser.add_argument("--version", "-v", help="Specific version to deploy")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--skip-tests", action="store_true", help="Skip pre-deployment tests")
    parser.add_argument("--rollback", action="store_true", help="Rollback previous deployment")
    parser.add_argument("--dry-run", action="store_true", help="Simulate deployment without changes")
    
    args = parser.parse_args()
    
    # Initialize deployment manager
    deployment_manager = DeploymentManager(
        environment=args.environment,
        config_file=args.config
    )
    
    try:
        if args.rollback:
            success = deployment_manager.rollback()
        else:
            if args.dry_run:
                logger.info("DRY RUN MODE - No actual changes will be made")
                # Implement dry-run logic here
                success = True
            else:
                success = deployment_manager.deploy(
                    version=args.version,
                    skip_tests=args.skip_tests
                )
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Deployment interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Deployment script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()