# GopiAI CI/CD System

Comprehensive Continuous Integration and Continuous Deployment system for the GopiAI project.

## Overview

This CI/CD system provides:
- **Automated Test Execution**: Run all types of tests (unit, integration, UI, E2E, performance, security)
- **Multi-Platform CI/CD Integration**: Support for GitHub Actions, Jenkins, Azure DevOps
- **Intelligent Notifications**: Email, Slack, Discord, Teams, and webhook notifications
- **Automated Deployment**: Environment-specific deployment with rollback capabilities
- **Comprehensive Reporting**: HTML, JSON, JUnit XML, and Markdown reports

## Quick Start

### 1. Basic Test Execution

```bash
# Run all tests for development environment
python ci_cd/automated_test_runner.py --environment development

# Run specific test types for staging
python ci_cd/automated_test_runner.py --environment staging --test-types "unit integration ui"

# Run with custom configuration
python ci_cd/automated_test_runner.py --environment production --config ci_cd/config/production.json
```

### 2. Complete CI/CD Pipeline

```bash
# Run full pipeline for staging
python ci_cd/ci_cd_integration.py --environment staging --version v1.2.3 --commit-hash abc123

# Force deployment to production
python ci_cd/ci_cd_integration.py --environment production --version v1.2.3 --force-deploy
```

### 3. Platform-Specific Scripts

```bash
# Windows
ci_cd\run_automated_tests.bat --environment staging --test-types "unit integration"

# Unix/Linux
./ci_cd/run_automated_tests.sh --environment staging --test-types "unit integration"
```

## Architecture

```
ci_cd/
├── automated_test_runner.py      # Core test execution engine
├── notification_system.py        # Multi-channel notifications
├── deployment_system.py          # Automated deployment with rollback
├── ci_cd_integration.py          # Complete pipeline orchestrator
├── generate_ci_report.py         # Report generation
├── send_notification.py          # Notification helper script
├── config/                       # Configuration files
│   ├── notification_config.json
│   └── deployment_config.json
├── scripts/                      # Deployment scripts
│   ├── deploy_development.py
│   ├── deploy_staging.py
│   └── deploy_production.py
└── platform_configs/            # CI/CD platform configurations
    ├── github_actions.yml
    ├── jenkins_pipeline.groovy
    └── azure_pipelines.yml
```

## Configuration

### Environment Configuration

Create environment-specific configurations in `ci_cd/config/`:

```json
{
  "test_types": ["unit", "integration", "ui"],
  "parallel_execution": true,
  "timeout_minutes": 30,
  "coverage_threshold": 80.0,
  "retry_failed_tests": true,
  "max_retries": 2
}
```

### Notification Configuration

Configure notification channels in `ci_cd/config/notification_config.json`:

```json
{
  "slack": {
    "enabled": true,
    "webhook_url": "https://hooks.slack.com/...",
    "channel": "#ci-cd"
  },
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "from_email": "ci@company.com",
    "to_emails": ["team@company.com"]
  }
}
```

### Deployment Configuration

Configure deployment environments in `ci_cd/config/deployment_config.json`:

```json
{
  "staging": {
    "auto_deploy": true,
    "test_requirements": ["unit", "integration"],
    "coverage_threshold": 80.0,
    "health_check_url": "https://staging.gopiai.com/health"
  }
}
```

## CI/CD Platform Integration

### GitHub Actions

1. Copy `ci_cd/github_actions.yml` to `.github/workflows/ci.yml`
2. Set up repository secrets:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `SLACK_WEBHOOK_URL`
   - `SMTP_PASSWORD`

### Jenkins

1. Create a new Pipeline job
2. Use `ci_cd/jenkins_pipeline.groovy` as the pipeline script
3. Configure environment variables and credentials

### Azure DevOps

1. Copy `ci_cd/azure_pipelines.yml` to repository root
2. Set up pipeline variables and service connections

## Test Types

### Unit Tests
- **Purpose**: Test individual functions and classes
- **Speed**: Fast (< 5 minutes)
- **Coverage**: All public methods and critical private methods

### Integration Tests
- **Purpose**: Test component interactions
- **Speed**: Medium (5-15 minutes)
- **Coverage**: API endpoints, database operations, service communication

### UI Tests
- **Purpose**: Test user interface components
- **Speed**: Medium (10-20 minutes)
- **Coverage**: Widget functionality, user interactions, themes

### End-to-End Tests
- **Purpose**: Test complete user scenarios
- **Speed**: Slow (20-45 minutes)
- **Coverage**: Full user workflows, cross-service integration

### Performance Tests
- **Purpose**: Measure system performance
- **Speed**: Variable (10-30 minutes)
- **Coverage**: API response times, memory usage, UI responsiveness

### Security Tests
- **Purpose**: Identify security vulnerabilities
- **Speed**: Medium (10-20 minutes)
- **Coverage**: API security, input validation, secret management

## Deployment Environments

### Development
- **Auto-deploy**: Enabled
- **Test Requirements**: Unit tests only
- **Coverage Threshold**: 70%
- **Approval**: Not required

### Staging
- **Auto-deploy**: Enabled
- **Test Requirements**: Unit, Integration, UI tests
- **Coverage Threshold**: 80%
- **Approval**: Not required
- **Health Checks**: Enabled
- **Rollback**: Automatic on failure

### Production
- **Auto-deploy**: Disabled (manual approval required)
- **Test Requirements**: All test types
- **Coverage Threshold**: 90%
- **Approval**: Required
- **Health Checks**: Comprehensive
- **Rollback**: Automatic on failure

## Notification Channels

### Slack
- Real-time notifications with rich formatting
- Channel-specific routing
- Interactive buttons for reports

### Email
- HTML formatted reports
- Attachment support for detailed reports
- Distribution lists

### Discord
- Embed-rich notifications
- Webhook-based delivery
- Custom bot integration

### Microsoft Teams
- Adaptive card notifications
- Action buttons
- Integration with Office 365

### Webhooks
- Custom integrations
- JSON payload delivery
- Configurable headers and authentication

## Reporting

### HTML Reports
- Interactive web-based reports
- Test result visualization
- Coverage metrics and trends

### JSON Reports
- Machine-readable format
- API integration friendly
- Detailed test case information

### JUnit XML
- Standard CI/CD format
- Compatible with most CI systems
- Test result aggregation

### Markdown Reports
- GitHub/GitLab compatible
- Pull request comments
- Lightweight summaries

## Monitoring and Alerting

### Health Checks
- Application availability monitoring
- Service dependency verification
- Automated recovery procedures

### Performance Monitoring
- Response time tracking
- Resource usage monitoring
- Performance regression detection

### Error Tracking
- Automated error detection
- Stack trace collection
- Error trend analysis

## Troubleshooting

### Common Issues

#### Tests Failing in CI but Passing Locally
1. Check environment differences
2. Verify dependency versions
3. Review test isolation
4. Check for timing issues

#### Deployment Failures
1. Review deployment logs
2. Check health check endpoints
3. Verify configuration files
4. Test rollback procedures

#### Notification Issues
1. Verify webhook URLs
2. Check authentication credentials
3. Review rate limiting
4. Test connectivity

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python ci_cd/automated_test_runner.py --environment development --verbose
```

### Log Files

All operations are logged to:
- `ci_cd/logs/automated_tests_*.log`
- `ci_cd/logs/deployment_*.log`
- `ci_cd/logs/cicd_pipeline_*.log`

## Best Practices

### Test Organization
- Keep tests fast and focused
- Use proper test isolation
- Mock external dependencies
- Maintain test data consistency

### Deployment Strategy
- Use blue-green deployments for production
- Implement comprehensive health checks
- Plan rollback procedures
- Test deployment scripts regularly

### Notification Management
- Configure appropriate notification levels
- Use different channels for different audiences
- Implement notification rate limiting
- Provide actionable information

### Security Considerations
- Store secrets securely
- Use least-privilege access
- Audit deployment activities
- Implement security scanning

## Contributing

When adding new features to the CI/CD system:

1. Update relevant configuration schemas
2. Add comprehensive tests
3. Update documentation
4. Test with all supported platforms
5. Verify notification integrations

## Support

For issues with the CI/CD system:

1. Check the troubleshooting section
2. Review log files for errors
3. Verify configuration files
4. Test individual components
5. Create detailed issue reports

## License

This CI/CD system is part of the GopiAI project and follows the same licensing terms.