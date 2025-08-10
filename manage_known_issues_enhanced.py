#!/usr/bin/env python3
"""
Enhanced CLI script for comprehensive known issues management.

This enhanced version includes:
- Automatic resolution detection
- Progress reporting and trend analysis
- Advanced issue lifecycle management
- Integration with CI/CD workflows
- Notification and alerting capabilities

Usage examples:
    python manage_known_issues_enhanced.py monitor --start
    python manage_known_issues_enhanced.py progress --report
    python manage_known_issues_enhanced.py auto-resolve --check
    python manage_known_issues_enhanced.py dashboard --generate
"""

import argparse
import sys
import time
from pathlib import Path

# Add test_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / "test_infrastructure"))

from known_issues_manager import KnownIssuesManager, IssueStatus, IssuePriority
from automatic_resolution_detector import AutomaticResolutionDetector
from issue_progress_reporter import IssueProgressReporter
from known_issues_integration import KnownIssuesIntegration


def main():
    """Main CLI function with enhanced functionality."""
    parser = argparse.ArgumentParser(
        description="Enhanced Known Issues Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic issue management
  python manage_known_issues_enhanced.py add ISSUE-001 "API timeout" "API calls timing out" "test_api_*"
  python manage_known_issues_enhanced.py update ISSUE-001 resolved
  
  # Automatic resolution detection
  python manage_known_issues_enhanced.py auto-resolve --check
  python manage_known_issues_enhanced.py auto-resolve --enable-monitoring
  
  # Progress reporting
  python manage_known_issues_enhanced.py progress --report
  python manage_known_issues_enhanced.py progress --trends
  
  # Monitoring and alerts
  python manage_known_issues_enhanced.py monitor --start
  python manage_known_issues_enhanced.py monitor --status
  
  # Dashboard and visualization
  python manage_known_issues_enhanced.py dashboard --generate
  python manage_known_issues_enhanced.py dashboard --serve
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Basic issue management commands
    add_parser = subparsers.add_parser('add', help='Add a new known issue')
    add_parser.add_argument('issue_id', help='Issue ID')
    add_parser.add_argument('title', help='Issue title')
    add_parser.add_argument('description', help='Issue description')
    add_parser.add_argument('test_pattern', help='Test pattern to match affected tests')
    add_parser.add_argument('--priority', choices=['critical', 'high', 'medium', 'low'], default='medium')
    add_parser.add_argument('--assigned-to', help='Assign to person')
    add_parser.add_argument('--github', help='GitHub issue URL')
    
    update_parser = subparsers.add_parser('update', help='Update issue status')
    update_parser.add_argument('issue_id', help='Issue ID')
    update_parser.add_argument('status', choices=['open', 'in_progress', 'resolved', 'wont_fix', 'duplicate'])
    update_parser.add_argument('--notes', help='Resolution notes')
    
    list_parser = subparsers.add_parser('list', help='List issues')
    list_parser.add_argument('status', nargs='?', choices=['open', 'in_progress', 'resolved', 'wont_fix', 'duplicate'])
    
    # Automatic resolution detection
    auto_resolve_parser = subparsers.add_parser('auto-resolve', help='Automatic resolution detection')
    auto_resolve_parser.add_argument('--check', action='store_true', help='Check for resolutions now')
    auto_resolve_parser.add_argument('--enable-monitoring', action='store_true', help='Enable continuous monitoring')
    auto_resolve_parser.add_argument('--disable-monitoring', action='store_true', help='Disable continuous monitoring')
    auto_resolve_parser.add_argument('--config', action='store_true', help='Show/edit configuration')
    auto_resolve_parser.add_argument('--history', help='Show resolution history for issue')
    
    # Progress reporting
    progress_parser = subparsers.add_parser('progress', help='Progress reporting and analysis')
    progress_parser.add_argument('--report', action='store_true', help='Generate comprehensive progress report')
    progress_parser.add_argument('--trends', action='store_true', help='Analyze progress trends')
    progress_parser.add_argument('--milestones', action='store_true', help='Show progress milestones')
    progress_parser.add_argument('--team-metrics', action='store_true', help='Show team performance metrics')
    progress_parser.add_argument('--issue', help='Show progress for specific issue')
    
    # Monitoring and alerts
    monitor_parser = subparsers.add_parser('monitor', help='Monitoring and alerting')
    monitor_parser.add_argument('--start', action='store_true', help='Start monitoring daemon')
    monitor_parser.add_argument('--stop', action='store_true', help='Stop monitoring daemon')
    monitor_parser.add_argument('--status', action='store_true', help='Show monitoring status')
    monitor_parser.add_argument('--alerts', action='store_true', help='Show recent alerts')
    
    # Dashboard and visualization
    dashboard_parser = subparsers.add_parser('dashboard', help='Dashboard and visualization')
    dashboard_parser.add_argument('--generate', action='store_true', help='Generate HTML dashboard')
    dashboard_parser.add_argument('--serve', action='store_true', help='Serve dashboard on local port')
    dashboard_parser.add_argument('--export', choices=['json', 'csv', 'pdf'], help='Export data')
    
    # Integration and workflow
    workflow_parser = subparsers.add_parser('workflow', help='Workflow integration')
    workflow_parser.add_argument('--suggest', action='store_true', help='Suggest new issues from failures')
    workflow_parser.add_argument('--auto-create', action='store_true', help='Auto-create suggested issues')
    workflow_parser.add_argument('--update-markers', action='store_true', help='Update pytest markers')
    workflow_parser.add_argument('--ci-report', action='store_true', help='Generate CI/CD integration report')
    
    # Comprehensive report
    report_parser = subparsers.add_parser('report', help='Generate comprehensive report')
    report_parser.add_argument('--format', choices=['console', 'json', 'html'], default='console')
    report_parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize managers
    issues_manager = KnownIssuesManager()
    detector = AutomaticResolutionDetector()
    reporter = IssueProgressReporter()
    integration = KnownIssuesIntegration()
    
    try:
        if args.command == 'add':
            handle_add_command(issues_manager, args)
        elif args.command == 'update':
            handle_update_command(issues_manager, args)
        elif args.command == 'list':
            handle_list_command(issues_manager, args)
        elif args.command == 'auto-resolve':
            handle_auto_resolve_command(detector, args)
        elif args.command == 'progress':
            handle_progress_command(reporter, args)
        elif args.command == 'monitor':
            handle_monitor_command(detector, args)
        elif args.command == 'dashboard':
            handle_dashboard_command(reporter, issues_manager, args)
        elif args.command == 'workflow':
            handle_workflow_command(integration, args)
        elif args.command == 'report':
            handle_report_command(issues_manager, reporter, args)
        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def handle_add_command(manager: KnownIssuesManager, args):
    """Handle add command."""
    try:
        priority = IssuePriority(args.priority)
        issue = manager.add_known_issue(
            args.issue_id, args.title, args.description, args.test_pattern,
            priority, args.assigned_to, args.github
        )
        print(f"✅ Added issue {args.issue_id} affecting {len(issue.affected_tests)} tests")
    except Exception as e:
        print(f"❌ Error adding issue: {e}")


def handle_update_command(manager: KnownIssuesManager, args):
    """Handle update command."""
    try:
        status = IssueStatus(args.status)
        success = manager.update_issue_status(args.issue_id, status, args.notes)
        if success:
            print(f"✅ Updated issue {args.issue_id} to {status.value}")
        else:
            print(f"❌ Issue {args.issue_id} not found")
    except Exception as e:
        print(f"❌ Error updating issue: {e}")


def handle_list_command(manager: KnownIssuesManager, args):
    """Handle list command."""
    try:
        if args.status:
            status_filter = IssueStatus(args.status)
            issues = manager.get_issues_by_status(status_filter)
            print(f"\n📋 Issues with status: {status_filter.value}")
        else:
            issues = []
            for status in IssueStatus:
                issues.extend(manager.get_issues_by_status(status))
            print(f"\n📋 All Issues")
        
        print("=" * 80)
        
        if not issues:
            print("No issues found")
            return
        
        for issue in issues:
            priority_emoji = {
                IssuePriority.CRITICAL: "🚨",
                IssuePriority.HIGH: "🔴",
                IssuePriority.MEDIUM: "🟡",
                IssuePriority.LOW: "🟢"
            }.get(issue.priority, "❓")
            
            print(f"\n{issue.issue_id} {priority_emoji} [{issue.status.value}]")
            print(f"  Title: {issue.title}")
            print(f"  Priority: {issue.priority.value}")
            print(f"  Created: {issue.created_date[:10]}")
            print(f"  Updated: {issue.updated_date[:10]}")
            print(f"  Affected Tests: {len(issue.affected_tests)}")
            if issue.assigned_to:
                print(f"  Assigned: {issue.assigned_to}")
            if issue.github_issue:
                print(f"  GitHub: {issue.github_issue}")
        
        print(f"\nTotal: {len(issues)} issues")
        
    except Exception as e:
        print(f"❌ Error listing issues: {e}")


def handle_auto_resolve_command(detector: AutomaticResolutionDetector, args):
    """Handle automatic resolution detection commands."""
    if args.check:
        print("🤖 Checking for automatic resolutions...")
        events = detector.check_for_resolutions()
        
        if events:
            print(f"\n🎉 Found {len(events)} resolution events:")
            for event in events:
                status = "✅ Auto-resolved" if event.auto_resolved else "📋 Detected (manual action needed)"
                print(f"  {event.issue_id}: {event.resolution_percentage:.1f}% - {status}")
                print(f"    Confidence: {event.confidence_score:.2f}")
                print(f"    Tests: {event.test_results}")
        else:
            print("✅ No issues ready for automatic resolution")
    
    elif args.enable_monitoring:
        print("🔄 Starting automatic resolution monitoring...")
        detector.start_monitoring()
        print("✅ Monitoring started - will run in background")
        print("💡 Use --disable-monitoring to stop")
    
    elif args.disable_monitoring:
        print("⏹️ Stopping automatic resolution monitoring...")
        detector.stop_monitoring()
        print("✅ Monitoring stopped")
    
    elif args.config:
        print("⚙️ Automatic Resolution Configuration:")
        print(f"  Resolution Threshold: {detector.config.resolution_threshold}%")
        print(f"  Confidence Threshold: {detector.config.confidence_threshold}")
        print(f"  Verification Runs: {detector.config.verification_runs}")
        print(f"  Monitoring Interval: {detector.config.monitoring_interval}s")
        print(f"  Auto-Resolve Enabled: {detector.config.auto_resolve_enabled}")
        print(f"  Notifications Enabled: {detector.config.notification_enabled}")
    
    elif args.history:
        print(f"📜 Resolution history for {args.history}:")
        events = detector.get_resolution_history(args.history)
        
        if events:
            for event in events:
                print(f"  {event.timestamp[:19]}: {event.previous_status} → {event.new_status}")
                print(f"    Resolution: {event.resolution_percentage:.1f}%")
                print(f"    Confidence: {event.confidence_score:.2f}")
                if event.notes:
                    print(f"    Notes: {event.notes}")
                print()
        else:
            print("  No resolution history found")
    
    else:
        # Generate resolution report
        report = detector.generate_resolution_report()
        print("📊 Automatic Resolution Report:")
        print(f"  Total Events: {report['total_resolution_events']}")
        print(f"  Auto-Resolved: {report['auto_resolved_count']}")
        print(f"  Recent Activity: {report['recent_activity']}")
        print(f"  Average Confidence: {report['average_confidence_score']:.2f}")
        
        if report['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")


def handle_progress_command(reporter: IssueProgressReporter, args):
    """Handle progress reporting commands."""
    if args.report:
        print("📊 Generating comprehensive progress report...")
        report = reporter.generate_progress_report()
        
        print(f"\n📈 Progress Summary:")
        print(f"  Active Issues: {report['summary']['total_active_issues']}")
        print(f"  Improving: {report['summary']['issues_improving']} 📈")
        print(f"  Declining: {report['summary']['issues_declining']} 📉")
        print(f"  Stagnant: {report['summary']['issues_stagnant']} ⏸️")
        print(f"  Recent Milestones: {report['summary']['recent_milestones']} 🎯")
        
        if report['insights']:
            print(f"\n🔍 Key Insights:")
            for insight in report['insights']:
                print(f"  • {insight}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        print(f"\n📁 Detailed reports saved to: test_infrastructure/known_issues/")
    
    elif args.trends:
        print("📈 Analyzing progress trends...")
        trends = reporter.analyze_progress_trends()
        
        if trends:
            print(f"\n🔍 Trend Analysis ({len(trends)} issues):")
            for trend in trends:
                trend_emoji = {
                    "improving": "📈",
                    "declining": "📉", 
                    "stable": "➡️",
                    "stagnant": "⏸️"
                }.get(trend.trend_direction, "❓")
                
                print(f"  {trend.issue_id} {trend_emoji} {trend.trend_direction}")
                print(f"    Velocity: {trend.velocity:.2f}% per day")
                print(f"    Strength: {trend.trend_strength:.2f}")
                
                if trend.predicted_resolution_date:
                    print(f"    Predicted Resolution: {trend.predicted_resolution_date[:10]}")
                print()
        else:
            print("✅ No trend data available - need more historical data")
    
    elif args.milestones:
        print("🏆 Progress Milestones:")
        milestones = reporter.get_progress_milestones()
        
        if milestones:
            for milestone in milestones[-20:]:  # Last 20
                print(f"  {milestone.timestamp[:19]} - {milestone.issue_id}")
                print(f"    {milestone.milestone_type.replace('_', ' ').title()}: {milestone.percentage:.1f}%")
                print(f"    Days since creation: {milestone.days_since_creation}")
                if milestone.notes:
                    print(f"    Notes: {milestone.notes}")
                print()
        else:
            print("  No milestones recorded yet")
    
    elif args.team_metrics:
        print("👥 Team Performance Metrics:")
        metrics = reporter.calculate_team_metrics()
        
        print(f"  Total Issues: {metrics.total_issues}")
        print(f"  Active Issues: {metrics.active_issues}")
        print(f"  Resolved Issues: {metrics.resolved_issues}")
        print(f"  Resolution Velocity: {metrics.resolution_velocity:.1f} issues/week")
        print(f"  Average Resolution Time: {metrics.average_resolution_time:.1f} days")
        print(f"  Quality Score: {metrics.quality_score:.2f}")
        print(f"  Efficiency Score: {metrics.efficiency_score:.2f}")
        
        print(f"\n📊 Trend Distribution:")
        for trend, count in metrics.trend_summary.items():
            print(f"  {trend.title()}: {count}")
    
    elif args.issue:
        print(f"📊 Progress for issue {args.issue}:")
        # Get specific issue progress
        milestones = reporter.get_progress_milestones(args.issue)
        
        if milestones:
            print("  Milestones:")
            for milestone in milestones:
                print(f"    {milestone.timestamp[:19]}: {milestone.milestone_type.replace('_', ' ').title()}")
                print(f"      {milestone.percentage:.1f}% ({milestone.days_since_creation} days)")
        else:
            print("  No milestone data found")
    
    else:
        # Capture current snapshot
        print("📸 Capturing current progress snapshot...")
        progress = reporter.capture_progress_snapshot()
        
        if progress:
            print(f"\n📊 Current Progress ({len(progress)} issues):")
            for p in progress:
                trend_emoji = {"improving": "📈", "declining": "📉", "stable": "➡️"}.get(p.trend, "❓")
                print(f"  {p.issue_id}: {p.resolution_percentage:.1f}% {trend_emoji}")
                print(f"    Tests: {p.passing_tests}/{p.total_affected_tests} passing")
        else:
            print("✅ No active issues to track")


def handle_monitor_command(detector: AutomaticResolutionDetector, args):
    """Handle monitoring commands."""
    if args.start:
        print("🔄 Starting issue monitoring daemon...")
        detector.start_monitoring()
        print("✅ Monitoring started")
        print("💡 Monitoring will run in background and check for resolutions periodically")
        print("💡 Use --stop to stop monitoring")
        
        # Keep the process running
        try:
            while detector.monitoring_active:
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n⏹️ Stopping monitoring...")
            detector.stop_monitoring()
    
    elif args.stop:
        print("⏹️ Stopping monitoring daemon...")
        detector.stop_monitoring()
        print("✅ Monitoring stopped")
    
    elif args.status:
        print("📊 Monitoring Status:")
        print(f"  Active: {detector.monitoring_active}")
        print(f"  Interval: {detector.config.monitoring_interval}s")
        print(f"  Auto-resolve: {detector.config.auto_resolve_enabled}")
        print(f"  Notifications: {detector.config.notification_enabled}")
    
    elif args.alerts:
        print("🚨 Recent Alerts:")
        # Read recent notifications
        notification_file = detector.issues_manager.issues_dir / "resolution_notifications.log"
        if notification_file.exists():
            with open(notification_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-10:]:  # Last 10 alerts
                    if line.strip():
                        print(f"  {line.strip()}")
        else:
            print("  No alerts found")
    
    else:
        print("💡 Use --start, --stop, --status, or --alerts")


def handle_dashboard_command(reporter: IssueProgressReporter, manager: KnownIssuesManager, args):
    """Handle dashboard commands."""
    if args.generate:
        print("🎨 Generating HTML dashboard...")
        
        # Generate comprehensive report (includes HTML)
        report = reporter.generate_progress_report()
        
        # Generate issues report (includes HTML)
        issues_report = manager.generate_report()
        
        print("✅ Dashboard generated!")
        print("📁 Files created:")
        print("  • Progress Report: test_infrastructure/known_issues/progress_report_*.html")
        print("  • Issues Report: test_infrastructure/known_issues/known_issues_report_*.html")
        
    elif args.serve:
        print("🌐 Starting dashboard server...")
        print("💡 This would start a local web server to serve the dashboard")
        print("💡 Implementation: Use Python's http.server or Flask")
        # TODO: Implement web server
        
    elif args.export:
        print(f"📤 Exporting data to {args.export} format...")
        
        if args.export == 'json':
            report = reporter.generate_progress_report()
            print("✅ JSON export completed")
        elif args.export == 'csv':
            print("💡 CSV export would generate tabular data")
            # TODO: Implement CSV export
        elif args.export == 'pdf':
            print("💡 PDF export would generate formatted report")
            # TODO: Implement PDF export
    
    else:
        print("💡 Use --generate, --serve, or --export")


def handle_workflow_command(integration: KnownIssuesIntegration, args):
    """Handle workflow integration commands."""
    if args.suggest:
        print("🎯 Analyzing failures for potential known issues...")
        suggestions = integration.suggest_known_issues(auto_create=False)
        
        if suggestions:
            print("\n💡 Suggestions:")
            for suggestion in suggestions:
                print(f"  {suggestion}")
        else:
            print("✅ No new issues suggested")
    
    elif args.auto_create:
        print("🤖 Auto-creating issues from recurring failures...")
        suggestions = integration.suggest_known_issues(auto_create=True)
        
        for suggestion in suggestions:
            print(f"  {suggestion}")
    
    elif args.update_markers:
        print("🏷️ Updating pytest markers...")
        integration.update_pytest_configuration()
        print("✅ Pytest configuration updated")
    
    elif args.ci_report:
        print("🔄 Generating CI/CD integration report...")
        report = integration.generate_integration_report()
        
        print(f"📊 Integration Status:")
        print(f"  Active Issues: {report['known_issues_summary']['active_issues']}")
        print(f"  Total Failures: {report['failure_analysis']['total_failures']}")
        print(f"  Potential New Issues: {report['failure_analysis']['potential_new_issues']}")
        print(f"  Pytest Configured: {report['integration_status']['pytest_configured']}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
    
    else:
        print("💡 Use --suggest, --auto-create, --update-markers, or --ci-report")


def handle_report_command(manager: KnownIssuesManager, reporter: IssueProgressReporter, args):
    """Handle comprehensive report generation."""
    print("📊 Generating comprehensive report...")
    
    # Generate both reports
    issues_report = manager.generate_report()
    progress_report = reporter.generate_progress_report()
    
    if args.format == 'console':
        print("\n" + "="*60)
        print("📋 COMPREHENSIVE KNOWN ISSUES REPORT")
        print("="*60)
        
        print(f"\n📊 Overview:")
        print(f"  Total Issues: {issues_report.total_issues}")
        print(f"  Active Issues: {progress_report['summary']['total_active_issues']}")
        print(f"  Generated: {issues_report.timestamp[:19]}")
        
        print(f"\n📈 Status Distribution:")
        for status, count in issues_report.issues_by_status.items():
            print(f"  {status.replace('_', ' ').title()}: {count}")
        
        print(f"\n🎯 Priority Distribution:")
        for priority, count in issues_report.issues_by_priority.items():
            print(f"  {priority.title()}: {count}")
        
        print(f"\n📈 Progress Trends:")
        print(f"  Improving: {progress_report['summary']['issues_improving']} 📈")
        print(f"  Declining: {progress_report['summary']['issues_declining']} 📉")
        print(f"  Stagnant: {progress_report['summary']['issues_stagnant']} ⏸️")
        
        if issues_report.recommendations:
            print(f"\n💡 Key Recommendations:")
            for rec in issues_report.recommendations[:5]:
                print(f"  • {rec}")
        
        if progress_report['insights']:
            print(f"\n🔍 Key Insights:")
            for insight in progress_report['insights'][:5]:
                print(f"  • {insight}")
        
        print(f"\n📁 Detailed reports available at:")
        print(f"  • test_infrastructure/known_issues/")
    
    elif args.format == 'json':
        combined_report = {
            "timestamp": issues_report.timestamp,
            "issues_report": issues_report.__dict__,
            "progress_report": progress_report
        }
        
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(combined_report, f, indent=2, default=str)
            print(f"✅ JSON report saved to: {args.output}")
        else:
            import json
            print(json.dumps(combined_report, indent=2, default=str))
    
    elif args.format == 'html':
        print("🎨 HTML report generated with dashboard")
        if args.output:
            print(f"💡 Copy HTML files to: {args.output}")


if __name__ == "__main__":
    main()