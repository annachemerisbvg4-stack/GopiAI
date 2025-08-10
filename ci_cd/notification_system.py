#!/usr/bin/env python3
"""
Notification System for CI/CD Test Results
Supports multiple notification channels: email, Slack, Discord, Teams, webhooks
"""

import os
import json
import smtplib
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
from pathlib import Path


@dataclass
class NotificationConfig:
    """Configuration for notification channels"""
    email: Optional[Dict[str, Any]] = None
    slack: Optional[Dict[str, str]] = None
    discord: Optional[Dict[str, str]] = None
    teams: Optional[Dict[str, str]] = None
    webhooks: Optional[List[Dict[str, str]]] = None


@dataclass
class TestResult:
    """Test execution result for notifications"""
    timestamp: str
    environment: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    coverage_percentage: float
    exit_code: int
    report_url: Optional[str] = None
    build_number: Optional[str] = None
    commit_hash: Optional[str] = None
    branch: Optional[str] = None


class NotificationSystem:
    """Comprehensive notification system for test results"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
    def _load_config(self, config_path: Optional[str]) -> NotificationConfig:
        """Load notification configuration"""
        default_config = {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "",
                "to_emails": [],
                "use_tls": True
            },
            "slack": {
                "enabled": False,
                "webhook_url": "",
                "channel": "#ci-cd",
                "username": "GopiAI CI/CD Bot"
            },
            "discord": {
                "enabled": False,
                "webhook_url": "",
                "username": "GopiAI CI/CD Bot"
            },
            "teams": {
                "enabled": False,
                "webhook_url": ""
            },
            "webhooks": []
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load notification config: {e}")
        
        # Override with environment variables
        self._override_with_env_vars(default_config)
        
        return NotificationConfig(**default_config)
    
    def _override_with_env_vars(self, config: Dict):
        """Override config with environment variables"""
        # Email configuration
        if os.getenv('SMTP_USERNAME'):
            config['email']['username'] = os.getenv('SMTP_USERNAME')
        if os.getenv('SMTP_PASSWORD'):
            config['email']['password'] = os.getenv('SMTP_PASSWORD')
        if os.getenv('FROM_EMAIL'):
            config['email']['from_email'] = os.getenv('FROM_EMAIL')
        if os.getenv('TO_EMAILS'):
            config['email']['to_emails'] = os.getenv('TO_EMAILS').split(',')
        
        # Slack configuration
        if os.getenv('SLACK_WEBHOOK_URL'):
            config['slack']['webhook_url'] = os.getenv('SLACK_WEBHOOK_URL')
            config['slack']['enabled'] = True
        
        # Discord configuration
        if os.getenv('DISCORD_WEBHOOK_URL'):
            config['discord']['webhook_url'] = os.getenv('DISCORD_WEBHOOK_URL')
            config['discord']['enabled'] = True
        
        # Teams configuration
        if os.getenv('TEAMS_WEBHOOK_URL'):
            config['teams']['webhook_url'] = os.getenv('TEAMS_WEBHOOK_URL')
            config['teams']['enabled'] = True
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for notification system"""
        logger = logging.getLogger('notification_system')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def send_test_results(self, result: TestResult, notification_type: str = "test_completion"):
        """Send test results through all configured channels"""
        self.logger.info(f"Sending {notification_type} notifications...")
        
        success_count = 0
        total_channels = 0
        
        # Send email notification
        if self.config.email and self.config.email.get('enabled'):
            total_channels += 1
            if self._send_email_notification(result, notification_type):
                success_count += 1
        
        # Send Slack notification
        if self.config.slack and self.config.slack.get('enabled'):
            total_channels += 1
            if self._send_slack_notification(result, notification_type):
                success_count += 1
        
        # Send Discord notification
        if self.config.discord and self.config.discord.get('enabled'):
            total_channels += 1
            if self._send_discord_notification(result, notification_type):
                success_count += 1
        
        # Send Teams notification
        if self.config.teams and self.config.teams.get('enabled'):
            total_channels += 1
            if self._send_teams_notification(result, notification_type):
                success_count += 1
        
        # Send webhook notifications
        if self.config.webhooks:
            for webhook in self.config.webhooks:
                total_channels += 1
                if self._send_webhook_notification(result, webhook, notification_type):
                    success_count += 1
        
        self.logger.info(f"Sent notifications to {success_count}/{total_channels} channels")
        return success_count, total_channels
    
    def _send_email_notification(self, result: TestResult, notification_type: str) -> bool:
        """Send email notification"""
        try:
            email_config = self.config.email
            
            # Create message
            msg = MimeMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = ', '.join(email_config['to_emails'])
            msg['Subject'] = self._get_email_subject(result, notification_type)
            
            # Create HTML body
            html_body = self._create_email_html_body(result, notification_type)
            msg.attach(MimeText(html_body, 'html'))
            
            # Attach report if available
            if result.report_url and os.path.exists(result.report_url):
                self._attach_report_file(msg, result.report_url)
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            if email_config.get('use_tls', True):
                server.starttls()
            
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info("Email notification sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
            return False
    
    def _send_slack_notification(self, result: TestResult, notification_type: str) -> bool:
        """Send Slack notification"""
        try:
            slack_config = self.config.slack
            
            # Create Slack message
            message = self._create_slack_message(result, notification_type)
            
            payload = {
                "channel": slack_config.get('channel', '#ci-cd'),
                "username": slack_config.get('username', 'GopiAI CI/CD Bot'),
                "icon_emoji": self._get_status_emoji(result.exit_code),
                "attachments": [message]
            }
            
            response = requests.post(
                slack_config['webhook_url'],
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            self.logger.info("Slack notification sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def _send_discord_notification(self, result: TestResult, notification_type: str) -> bool:
        """Send Discord notification"""
        try:
            discord_config = self.config.discord
            
            # Create Discord embed
            embed = self._create_discord_embed(result, notification_type)
            
            payload = {
                "username": discord_config.get('username', 'GopiAI CI/CD Bot'),
                "embeds": [embed]
            }
            
            response = requests.post(
                discord_config['webhook_url'],
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            self.logger.info("Discord notification sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Discord notification: {e}")
            return False
    
    def _send_teams_notification(self, result: TestResult, notification_type: str) -> bool:
        """Send Microsoft Teams notification"""
        try:
            teams_config = self.config.teams
            
            # Create Teams card
            card = self._create_teams_card(result, notification_type)
            
            response = requests.post(
                teams_config['webhook_url'],
                json=card,
                timeout=30
            )
            response.raise_for_status()
            
            self.logger.info("Teams notification sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Teams notification: {e}")
            return False
    
    def _send_webhook_notification(self, result: TestResult, webhook_config: Dict, notification_type: str) -> bool:
        """Send generic webhook notification"""
        try:
            payload = {
                "notification_type": notification_type,
                "result": asdict(result),
                "timestamp": datetime.now().isoformat()
            }
            
            headers = webhook_config.get('headers', {})
            headers.setdefault('Content-Type', 'application/json')
            
            response = requests.post(
                webhook_config['url'],
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            self.logger.info(f"Webhook notification sent to {webhook_config['url']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {e}")
            return False
    
    def _get_email_subject(self, result: TestResult, notification_type: str) -> str:
        """Generate email subject line"""
        status = "✅ PASSED" if result.exit_code == 0 else "❌ FAILED"
        
        if notification_type == "deployment":
            return f"GopiAI Deployment {status} - {result.environment.upper()}"
        else:
            return f"GopiAI Tests {status} - {result.environment.upper()} ({result.passed}/{result.total_tests})"
    
    def _create_email_html_body(self, result: TestResult, notification_type: str) -> str:
        """Create HTML email body"""
        status_color = "#28a745" if result.exit_code == 0 else "#dc3545"
        status_text = "PASSED" if result.exit_code == 0 else "FAILED"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .header {{ background-color: {status_color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .metric {{ text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric-value {{ font-size: 24px; font-weight: bold; }}
                .metric-label {{ font-size: 12px; color: #666; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>GopiAI Test Results - {status_text}</h1>
                <p>Environment: {result.environment.upper()}</p>
            </div>
            
            <div class="content">
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">{result.total_tests}</div>
                        <div class="metric-label">Total Tests</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" style="color: #28a745;">{result.passed}</div>
                        <div class="metric-label">Passed</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" style="color: #dc3545;">{result.failed}</div>
                        <div class="metric-label">Failed</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" style="color: #ffc107;">{result.skipped}</div>
                        <div class="metric-label">Skipped</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{result.coverage_percentage:.1f}%</div>
                        <div class="metric-label">Coverage</div>
                    </div>
                </div>
                
                <h3>Execution Details</h3>
                <ul>
                    <li><strong>Duration:</strong> {result.duration:.2f} seconds</li>
                    <li><strong>Timestamp:</strong> {result.timestamp}</li>
                    {f'<li><strong>Build Number:</strong> {result.build_number}</li>' if result.build_number else ''}
                    {f'<li><strong>Branch:</strong> {result.branch}</li>' if result.branch else ''}
                    {f'<li><strong>Commit:</strong> {result.commit_hash}</li>' if result.commit_hash else ''}
                </ul>
                
                {f'<p><a href="{result.report_url}">View Detailed Report</a></p>' if result.report_url else ''}
            </div>
            
            <div class="footer">
                <p>This is an automated message from GopiAI CI/CD system</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_slack_message(self, result: TestResult, notification_type: str) -> Dict:
        """Create Slack message attachment"""
        color = "good" if result.exit_code == 0 else "danger"
        status_text = "PASSED" if result.exit_code == 0 else "FAILED"
        
        fields = [
            {"title": "Total Tests", "value": str(result.total_tests), "short": True},
            {"title": "Passed", "value": str(result.passed), "short": True},
            {"title": "Failed", "value": str(result.failed), "short": True},
            {"title": "Coverage", "value": f"{result.coverage_percentage:.1f}%", "short": True},
            {"title": "Duration", "value": f"{result.duration:.2f}s", "short": True},
            {"title": "Environment", "value": result.environment.upper(), "short": True}
        ]
        
        if result.build_number:
            fields.append({"title": "Build", "value": result.build_number, "short": True})
        
        attachment = {
            "color": color,
            "title": f"GopiAI Tests {status_text}",
            "fields": fields,
            "footer": "GopiAI CI/CD",
            "ts": int(datetime.now().timestamp())
        }
        
        if result.report_url:
            attachment["actions"] = [{
                "type": "button",
                "text": "View Report",
                "url": result.report_url
            }]
        
        return attachment
    
    def _create_discord_embed(self, result: TestResult, notification_type: str) -> Dict:
        """Create Discord embed"""
        color = 0x28a745 if result.exit_code == 0 else 0xdc3545  # Green or Red
        status_text = "PASSED" if result.exit_code == 0 else "FAILED"
        
        embed = {
            "title": f"GopiAI Tests {status_text}",
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {"name": "Environment", "value": result.environment.upper(), "inline": True},
                {"name": "Total Tests", "value": str(result.total_tests), "inline": True},
                {"name": "Passed", "value": str(result.passed), "inline": True},
                {"name": "Failed", "value": str(result.failed), "inline": True},
                {"name": "Coverage", "value": f"{result.coverage_percentage:.1f}%", "inline": True},
                {"name": "Duration", "value": f"{result.duration:.2f}s", "inline": True}
            ],
            "footer": {"text": "GopiAI CI/CD"}
        }
        
        if result.build_number:
            embed["fields"].append({"name": "Build", "value": result.build_number, "inline": True})
        
        return embed
    
    def _create_teams_card(self, result: TestResult, notification_type: str) -> Dict:
        """Create Microsoft Teams adaptive card"""
        color = "Good" if result.exit_code == 0 else "Attention"
        status_text = "PASSED" if result.exit_code == 0 else "FAILED"
        
        card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "28a745" if result.exit_code == 0 else "dc3545",
            "summary": f"GopiAI Tests {status_text}",
            "sections": [{
                "activityTitle": f"GopiAI Tests {status_text}",
                "activitySubtitle": f"Environment: {result.environment.upper()}",
                "facts": [
                    {"name": "Total Tests", "value": str(result.total_tests)},
                    {"name": "Passed", "value": str(result.passed)},
                    {"name": "Failed", "value": str(result.failed)},
                    {"name": "Coverage", "value": f"{result.coverage_percentage:.1f}%"},
                    {"name": "Duration", "value": f"{result.duration:.2f}s"}
                ]
            }]
        }
        
        if result.report_url:
            card["potentialAction"] = [{
                "@type": "OpenUri",
                "name": "View Report",
                "targets": [{"os": "default", "uri": result.report_url}]
            }]
        
        return card
    
    def _get_status_emoji(self, exit_code: int) -> str:
        """Get emoji based on test status"""
        return ":white_check_mark:" if exit_code == 0 else ":x:"
    
    def _attach_report_file(self, msg: MimeMultipart, report_path: str):
        """Attach report file to email"""
        try:
            with open(report_path, "rb") as attachment:
                part = MimeBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(report_path)}'
            )
            msg.attach(part)
            
        except Exception as e:
            self.logger.warning(f"Could not attach report file: {e}")


def main():
    """Main entry point for notification system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Send CI/CD notifications')
    parser.add_argument('--type', required=True, 
                       choices=['test_completion', 'deployment', 'pipeline'],
                       help='Notification type')
    parser.add_argument('--status', required=True,
                       choices=['success', 'failure', 'unstable'],
                       help='Status of the operation')
    parser.add_argument('--environment', required=True,
                       help='Target environment')
    parser.add_argument('--build-number', help='Build number')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--result-file', help='JSON file with test results')
    
    args = parser.parse_args()
    
    # Initialize notification system
    notifier = NotificationSystem(args.config)
    
    # Load test results
    if args.result_file and os.path.exists(args.result_file):
        with open(args.result_file, 'r', encoding='utf-8') as f:
            result_data = json.load(f)
            result = TestResult(**result_data)
    else:
        # Create minimal result for deployment notifications
        result = TestResult(
            timestamp=datetime.now().isoformat(),
            environment=args.environment,
            total_tests=0,
            passed=0,
            failed=0 if args.status == 'success' else 1,
            skipped=0,
            errors=0,
            duration=0.0,
            coverage_percentage=0.0,
            exit_code=0 if args.status == 'success' else 1,
            build_number=args.build_number
        )
    
    # Send notifications
    success_count, total_channels = notifier.send_test_results(result, args.type)
    
    print(f"Sent notifications to {success_count}/{total_channels} channels")
    
    if success_count == 0:
        sys.exit(1)


if __name__ == '__main__':
    import sys
    main()