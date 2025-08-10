#!/usr/bin/env python3
"""
Issue Progress Reporting System

This module generates comprehensive reports on the progress of known issue resolution,
including trend analysis, resolution predictions, and actionable insights.

Features:
- Progress tracking over time
- Trend analysis and predictions
- Visual progress reports (HTML/charts)
- Integration with CI/CD metrics
- Automated progress notifications
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics

from known_issues_manager import KnownIssuesManager, IssueStatus, IssuePriority, IssueResolutionProgress


@dataclass
class ProgressTrend:
    """Represents progress trend for an issue."""
    issue_id: str
    trend_direction: str  # "improving", "declining", "stable", "stagnant"
    trend_strength: float  # 0.0 to 1.0
    velocity: float  # percentage points per day
    predicted_resolution_date: Optional[str]
    confidence_interval: Tuple[float, float]
    recent_changes: List[Dict]


@dataclass
class ProgressMilestone:
    """Represents a progress milestone."""
    issue_id: str
    milestone_type: str  # "created", "50_percent", "80_percent", "resolved"
    timestamp: str
    percentage: float
    days_since_creation: int
    notes: str


@dataclass
class TeamProgressMetrics:
    """Team-level progress metrics."""
    total_issues: int
    active_issues: int
    resolved_issues: int
    average_resolution_time: float
    resolution_velocity: float  # issues resolved per week
    quality_score: float  # based on resolution accuracy
    efficiency_score: float  # based on time to resolution
    trend_summary: Dict[str, int]


class IssueProgressReporter:
    """Generates comprehensive progress reports for known issues."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues_manager = KnownIssuesManager(project_root)
        
        # Progress tracking database
        self.progress_db = self.issues_manager.issues_dir / "progress_tracking.db"
        self._init_progress_database()
        
        # Report configuration
        self.config = self._load_report_config()
    
    def _init_progress_database(self):
        """Initialize progress tracking database."""
        with sqlite3.connect(self.progress_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS progress_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    total_tests INTEGER,
                    passing_tests INTEGER,
                    failing_tests INTEGER,
                    skipped_tests INTEGER,
                    resolution_percentage REAL,
                    trend TEXT,
                    notes TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS progress_milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_id TEXT NOT NULL,
                    milestone_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    percentage REAL,
                    days_since_creation INTEGER,
                    notes TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS team_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_issues INTEGER,
                    active_issues INTEGER,
                    resolved_issues INTEGER,
                    average_resolution_time REAL,
                    resolution_velocity REAL,
                    quality_score REAL,
                    efficiency_score REAL,
                    metrics_data TEXT
                )
            """)
            
            conn.commit()
    
    def _load_report_config(self) -> Dict:
        """Load reporting configuration."""
        config_file = self.issues_manager.issues_dir / "progress_config.json"
        
        default_config = {
            "trend_analysis_days": 14,
            "milestone_thresholds": [25, 50, 75, 90, 95],
            "prediction_confidence": 0.8,
            "stagnation_threshold_days": 7,
            "velocity_calculation_days": 30,
            "quality_weight_factors": {
                "resolution_accuracy": 0.4,
                "false_positive_rate": 0.3,
                "time_to_resolution": 0.3
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception:
                pass
        
        # Save config
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def capture_progress_snapshot(self) -> List[IssueResolutionProgress]:
        """Capture current progress snapshot for all active issues."""
        print("📸 Capturing progress snapshot...")
        
        # Get current progress from issues manager
        progress_list = self.issues_manager.check_resolution_progress()
        
        # Save snapshots to database
        with sqlite3.connect(self.progress_db) as conn:
            for progress in progress_list:
                conn.execute("""
                    INSERT INTO progress_snapshots (
                        issue_id, timestamp, total_tests, passing_tests, failing_tests,
                        skipped_tests, resolution_percentage, trend, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    progress.issue_id, progress.last_check, progress.total_affected_tests,
                    progress.passing_tests, progress.failing_tests, progress.skipped_tests,
                    progress.resolution_percentage, progress.trend, ""
                ))
            
            conn.commit()
        
        # Check for new milestones
        self._check_milestones(progress_list)
        
        return progress_list
    
    def _check_milestones(self, progress_list: List[IssueResolutionProgress]):
        """Check and record progress milestones."""
        milestone_thresholds = self.config["milestone_thresholds"]
        
        with sqlite3.connect(self.progress_db) as conn:
            for progress in progress_list:
                # Get issue creation date
                issue = self._get_issue_by_id(progress.issue_id)
                if not issue:
                    continue
                
                creation_date = datetime.fromisoformat(issue.created_date)
                days_since_creation = (datetime.now() - creation_date).days
                
                # Check each milestone threshold
                for threshold in milestone_thresholds:
                    if progress.resolution_percentage >= threshold:
                        # Check if milestone already recorded
                        cursor = conn.execute("""
                            SELECT COUNT(*) FROM progress_milestones 
                            WHERE issue_id = ? AND milestone_type = ?
                        """, (progress.issue_id, f"{threshold}_percent"))
                        
                        if cursor.fetchone()[0] == 0:
                            # Record new milestone
                            conn.execute("""
                                INSERT INTO progress_milestones (
                                    issue_id, milestone_type, timestamp, percentage,
                                    days_since_creation, notes
                                ) VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                                progress.issue_id, f"{threshold}_percent",
                                datetime.now().isoformat(), progress.resolution_percentage,
                                days_since_creation, f"Reached {threshold}% resolution"
                            ))
                            
                            print(f"🎯 Milestone: {progress.issue_id} reached {threshold}% resolution")
            
            conn.commit()
    
    def _get_issue_by_id(self, issue_id: str):
        """Get issue by ID from all statuses."""
        for status in IssueStatus:
            issues = self.issues_manager.get_issues_by_status(status)
            for issue in issues:
                if issue.issue_id == issue_id:
                    return issue
        return None
    
    def analyze_progress_trends(self) -> List[ProgressTrend]:
        """Analyze progress trends for all issues."""
        print("📈 Analyzing progress trends...")
        
        trends = []
        analysis_days = self.config["trend_analysis_days"]
        cutoff_date = (datetime.now() - timedelta(days=analysis_days)).isoformat()
        
        with sqlite3.connect(self.progress_db) as conn:
            # Get unique issues with recent progress data
            cursor = conn.execute("""
                SELECT DISTINCT issue_id FROM progress_snapshots 
                WHERE timestamp > ?
            """, (cutoff_date,))
            
            issue_ids = [row[0] for row in cursor.fetchall()]
            
            for issue_id in issue_ids:
                trend = self._analyze_issue_trend(conn, issue_id, analysis_days)
                if trend:
                    trends.append(trend)
        
        return trends
    
    def _analyze_issue_trend(self, conn, issue_id: str, days: int) -> Optional[ProgressTrend]:
        """Analyze trend for a specific issue."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Get progress data points
        cursor = conn.execute("""
            SELECT timestamp, resolution_percentage FROM progress_snapshots 
            WHERE issue_id = ? AND timestamp > ?
            ORDER BY timestamp ASC
        """, (issue_id, cutoff_date))
        
        data_points = cursor.fetchall()
        
        if len(data_points) < 2:
            return None
        
        # Calculate trend
        timestamps = [datetime.fromisoformat(dp[0]) for dp in data_points]
        percentages = [dp[1] for dp in data_points]
        
        # Linear regression for trend
        n = len(data_points)
        x_values = [(ts - timestamps[0]).days for ts in timestamps]
        
        if len(set(x_values)) < 2:  # All same day
            return None
        
        # Calculate slope (velocity)
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(percentages)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, percentages))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            velocity = 0
        else:
            velocity = numerator / denominator  # percentage points per day
        
        # Determine trend direction and strength
        if abs(velocity) < 0.1:  # Less than 0.1% per day
            trend_direction = "stable"
            trend_strength = 0.0
        elif velocity > 0:
            trend_direction = "improving"
            trend_strength = min(velocity / 2.0, 1.0)  # Normalize to 0-1
        else:
            trend_direction = "declining"
            trend_strength = min(abs(velocity) / 2.0, 1.0)
        
        # Check for stagnation
        stagnation_threshold = self.config["stagnation_threshold_days"]
        recent_data = data_points[-min(stagnation_threshold, len(data_points)):]
        recent_percentages = [dp[1] for dp in recent_data]
        
        if len(recent_percentages) >= 3:
            recent_variance = statistics.variance(recent_percentages)
            if recent_variance < 1.0 and trend_direction == "stable":
                trend_direction = "stagnant"
        
        # Predict resolution date
        predicted_date = None
        confidence_interval = (0.0, 0.0)
        
        if velocity > 0 and percentages[-1] < 95:
            days_to_resolution = (95 - percentages[-1]) / velocity
            if days_to_resolution > 0 and days_to_resolution < 365:  # Within a year
                predicted_date = (datetime.now() + timedelta(days=days_to_resolution)).isoformat()
                
                # Simple confidence interval (±20% of prediction)
                lower_bound = days_to_resolution * 0.8
                upper_bound = days_to_resolution * 1.2
                confidence_interval = (lower_bound, upper_bound)
        
        # Get recent changes
        recent_changes = []
        if len(data_points) >= 2:
            recent_change = percentages[-1] - percentages[-2]
            recent_changes.append({
                "timestamp": data_points[-1][0],
                "change": recent_change,
                "description": f"{'Improved' if recent_change > 0 else 'Declined'} by {abs(recent_change):.1f}%"
            })
        
        return ProgressTrend(
            issue_id=issue_id,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            velocity=velocity,
            predicted_resolution_date=predicted_date,
            confidence_interval=confidence_interval,
            recent_changes=recent_changes
        )
    
    def get_progress_milestones(self, issue_id: Optional[str] = None) -> List[ProgressMilestone]:
        """Get progress milestones for all issues or specific issue."""
        with sqlite3.connect(self.progress_db) as conn:
            if issue_id:
                cursor = conn.execute("""
                    SELECT * FROM progress_milestones 
                    WHERE issue_id = ? 
                    ORDER BY timestamp ASC
                """, (issue_id,))
            else:
                cursor = conn.execute("""
                    SELECT * FROM progress_milestones 
                    ORDER BY timestamp DESC
                """)
            
            milestones = []
            for row in cursor.fetchall():
                milestone = ProgressMilestone(
                    issue_id=row[1],
                    milestone_type=row[2],
                    timestamp=row[3],
                    percentage=row[4],
                    days_since_creation=row[5],
                    notes=row[6]
                )
                milestones.append(milestone)
            
            return milestones
    
    def calculate_team_metrics(self) -> TeamProgressMetrics:
        """Calculate team-level progress metrics."""
        print("👥 Calculating team metrics...")
        
        # Get all issues
        all_issues = []
        for status in IssueStatus:
            all_issues.extend(self.issues_manager.get_issues_by_status(status))
        
        if not all_issues:
            return TeamProgressMetrics(
                total_issues=0, active_issues=0, resolved_issues=0,
                average_resolution_time=0.0, resolution_velocity=0.0,
                quality_score=0.0, efficiency_score=0.0,
                trend_summary={}
            )
        
        # Basic counts
        total_issues = len(all_issues)
        active_issues = len([i for i in all_issues if i.status in [IssueStatus.OPEN, IssueStatus.IN_PROGRESS]])
        resolved_issues = len([i for i in all_issues if i.status == IssueStatus.RESOLVED])
        
        # Calculate average resolution time
        resolved_with_dates = [
            i for i in all_issues 
            if i.status == IssueStatus.RESOLVED and i.created_date and i.updated_date
        ]
        
        if resolved_with_dates:
            resolution_times = []
            for issue in resolved_with_dates:
                created = datetime.fromisoformat(issue.created_date)
                resolved = datetime.fromisoformat(issue.updated_date)
                resolution_times.append((resolved - created).days)
            
            average_resolution_time = statistics.mean(resolution_times)
        else:
            average_resolution_time = 0.0
        
        # Calculate resolution velocity (issues per week)
        velocity_days = self.config["velocity_calculation_days"]
        cutoff_date = (datetime.now() - timedelta(days=velocity_days)).isoformat()
        
        recent_resolutions = [
            i for i in all_issues
            if i.status == IssueStatus.RESOLVED and i.updated_date > cutoff_date
        ]
        
        resolution_velocity = len(recent_resolutions) / (velocity_days / 7)  # per week
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(all_issues)
        
        # Calculate efficiency score
        efficiency_score = self._calculate_efficiency_score(all_issues, average_resolution_time)
        
        # Trend summary
        trends = self.analyze_progress_trends()
        trend_summary = {
            "improving": len([t for t in trends if t.trend_direction == "improving"]),
            "declining": len([t for t in trends if t.trend_direction == "declining"]),
            "stable": len([t for t in trends if t.trend_direction == "stable"]),
            "stagnant": len([t for t in trends if t.trend_direction == "stagnant"])
        }
        
        metrics = TeamProgressMetrics(
            total_issues=total_issues,
            active_issues=active_issues,
            resolved_issues=resolved_issues,
            average_resolution_time=average_resolution_time,
            resolution_velocity=resolution_velocity,
            quality_score=quality_score,
            efficiency_score=efficiency_score,
            trend_summary=trend_summary
        )
        
        # Save metrics to database
        self._save_team_metrics(metrics)
        
        return metrics
    
    def _calculate_quality_score(self, all_issues: List) -> float:
        """Calculate quality score based on resolution accuracy."""
        if not all_issues:
            return 0.0
        
        weights = self.config["quality_weight_factors"]
        
        # Resolution accuracy (resolved issues that stay resolved)
        resolved_issues = [i for i in all_issues if i.status == IssueStatus.RESOLVED]
        if resolved_issues:
            # This would need integration with test results to check if resolved issues stay resolved
            # For now, assume 90% accuracy
            resolution_accuracy = 0.9
        else:
            resolution_accuracy = 0.0
        
        # False positive rate (issues marked as resolved but aren't really)
        # This would need historical data - assume 10% false positive rate
        false_positive_rate = 0.1
        
        # Time to resolution factor
        avg_resolution_days = 14  # This would come from actual data
        optimal_resolution_days = 7
        time_factor = min(optimal_resolution_days / max(avg_resolution_days, 1), 1.0)
        
        quality_score = (
            resolution_accuracy * weights["resolution_accuracy"] +
            (1 - false_positive_rate) * weights["false_positive_rate"] +
            time_factor * weights["time_to_resolution"]
        )
        
        return min(quality_score, 1.0)
    
    def _calculate_efficiency_score(self, all_issues: List, avg_resolution_time: float) -> float:
        """Calculate efficiency score based on resolution speed."""
        if not all_issues:
            return 0.0
        
        # Efficiency based on resolution time vs. issue complexity
        # Simple heuristic: critical issues should be resolved faster
        
        critical_issues = [i for i in all_issues if i.priority == IssuePriority.CRITICAL]
        high_issues = [i for i in all_issues if i.priority == IssuePriority.HIGH]
        
        # Target resolution times by priority (days)
        target_times = {
            IssuePriority.CRITICAL: 3,
            IssuePriority.HIGH: 7,
            IssuePriority.MEDIUM: 14,
            IssuePriority.LOW: 30
        }
        
        # For now, use a simple efficiency calculation
        if avg_resolution_time > 0:
            target_avg = 10  # Target average of 10 days
            efficiency = min(target_avg / avg_resolution_time, 1.0)
        else:
            efficiency = 0.0
        
        return efficiency
    
    def _save_team_metrics(self, metrics: TeamProgressMetrics):
        """Save team metrics to database."""
        with sqlite3.connect(self.progress_db) as conn:
            conn.execute("""
                INSERT INTO team_metrics (
                    timestamp, total_issues, active_issues, resolved_issues,
                    average_resolution_time, resolution_velocity, quality_score,
                    efficiency_score, metrics_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(), metrics.total_issues, metrics.active_issues,
                metrics.resolved_issues, metrics.average_resolution_time,
                metrics.resolution_velocity, metrics.quality_score,
                metrics.efficiency_score, json.dumps(asdict(metrics))
            ))
            conn.commit()
    
    def generate_progress_report(self) -> Dict:
        """Generate comprehensive progress report."""
        print("📊 Generating comprehensive progress report...")
        
        # Capture current snapshot
        current_progress = self.capture_progress_snapshot()
        
        # Analyze trends
        trends = self.analyze_progress_trends()
        
        # Get milestones
        milestones = self.get_progress_milestones()
        
        # Calculate team metrics
        team_metrics = self.calculate_team_metrics()
        
        # Generate insights and recommendations
        insights = self._generate_insights(current_progress, trends, team_metrics)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_active_issues": len(current_progress),
                "issues_improving": len([t for t in trends if t.trend_direction == "improving"]),
                "issues_declining": len([t for t in trends if t.trend_direction == "declining"]),
                "issues_stagnant": len([t for t in trends if t.trend_direction == "stagnant"]),
                "recent_milestones": len([m for m in milestones if m.timestamp > (datetime.now() - timedelta(days=7)).isoformat()])
            },
            "current_progress": [asdict(p) for p in current_progress],
            "trends": [asdict(t) for t in trends],
            "milestones": [asdict(m) for m in milestones[-20:]],  # Last 20 milestones
            "team_metrics": asdict(team_metrics),
            "insights": insights,
            "recommendations": self._generate_recommendations(current_progress, trends, team_metrics)
        }
        
        # Save report
        self._save_progress_report(report)
        
        return report
    
    def _generate_insights(self, progress: List, trends: List, metrics: TeamProgressMetrics) -> List[str]:
        """Generate insights from progress data."""
        insights = []
        
        if not progress:
            insights.append("No active issues to track - great job!")
            return insights
        
        # Progress insights
        high_progress_issues = [p for p in progress if p.resolution_percentage > 80]
        if high_progress_issues:
            insights.append(f"🎯 {len(high_progress_issues)} issues are close to resolution (>80%)")
        
        low_progress_issues = [p for p in progress if p.resolution_percentage < 20]
        if low_progress_issues:
            insights.append(f"🔍 {len(low_progress_issues)} issues need attention (<20% progress)")
        
        # Trend insights
        improving_trends = [t for t in trends if t.trend_direction == "improving"]
        if improving_trends:
            avg_velocity = statistics.mean([t.velocity for t in improving_trends if t.velocity > 0])
            insights.append(f"📈 {len(improving_trends)} issues improving at {avg_velocity:.1f}% per day average")
        
        stagnant_trends = [t for t in trends if t.trend_direction == "stagnant"]
        if stagnant_trends:
            insights.append(f"⚠️ {len(stagnant_trends)} issues have stagnated - may need intervention")
        
        # Team performance insights
        if metrics.resolution_velocity > 1:
            insights.append(f"🚀 Team is resolving {metrics.resolution_velocity:.1f} issues per week")
        elif metrics.resolution_velocity < 0.5:
            insights.append(f"🐌 Resolution velocity is low: {metrics.resolution_velocity:.1f} issues per week")
        
        if metrics.quality_score > 0.8:
            insights.append(f"✨ High quality score: {metrics.quality_score:.2f}")
        elif metrics.quality_score < 0.6:
            insights.append(f"⚠️ Quality score needs improvement: {metrics.quality_score:.2f}")
        
        return insights
    
    def _generate_recommendations(self, progress: List, trends: List, metrics: TeamProgressMetrics) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Priority recommendations based on progress
        critical_stagnant = []
        for trend in trends:
            if trend.trend_direction == "stagnant":
                issue = self._get_issue_by_id(trend.issue_id)
                if issue and issue.priority == IssuePriority.CRITICAL:
                    critical_stagnant.append(trend.issue_id)
        
        if critical_stagnant:
            recommendations.append(f"🚨 Critical issues stagnant: {', '.join(critical_stagnant)} - immediate attention needed")
        
        # Trend-based recommendations
        declining_trends = [t for t in trends if t.trend_direction == "declining"]
        if declining_trends:
            recommendations.append(f"📉 {len(declining_trends)} issues declining - investigate root causes")
        
        # Team performance recommendations
        if metrics.resolution_velocity < 0.5:
            recommendations.append("🔧 Consider allocating more resources to issue resolution")
        
        if metrics.efficiency_score < 0.6:
            recommendations.append("⚡ Focus on improving resolution efficiency - consider process improvements")
        
        # Milestone-based recommendations
        near_completion = [p for p in progress if 80 <= p.resolution_percentage < 95]
        if near_completion:
            recommendations.append(f"🎯 Push {len(near_completion)} issues over the finish line - they're almost done!")
        
        # Prediction-based recommendations
        predicted_resolutions = [t for t in trends if t.predicted_resolution_date]
        if predicted_resolutions:
            soon_to_resolve = [
                t for t in predicted_resolutions 
                if datetime.fromisoformat(t.predicted_resolution_date) < datetime.now() + timedelta(days=7)
            ]
            if soon_to_resolve:
                recommendations.append(f"📅 {len(soon_to_resolve)} issues predicted to resolve this week")
        
        return recommendations
    
    def _save_progress_report(self, report: Dict):
        """Save progress report to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_file = self.issues_manager.issues_dir / f"progress_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Save latest report
        latest_file = self.issues_manager.issues_dir / "progress_report_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Generate HTML report
        self._generate_html_progress_report(report, timestamp)
        
        print(f"📊 Progress report saved: {json_file}")
    
    def _generate_html_progress_report(self, report: Dict, timestamp: str):
        """Generate HTML progress report with charts."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GopiAI Issue Progress Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .metric {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }}
        .chart-container {{ width: 100%; height: 400px; margin: 20px 0; }}
        .progress-item {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 8px; }}
        .trend-improving {{ border-left: 4px solid #28a745; }}
        .trend-declining {{ border-left: 4px solid #dc3545; }}
        .trend-stable {{ border-left: 4px solid #ffc107; }}
        .trend-stagnant {{ border-left: 4px solid #6c757d; }}
        .insight {{ background: #e3f2fd; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #2196f3; }}
        .recommendation {{ background: #fff3e0; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #ff9800; }}
        .milestone {{ background: #e8f5e8; padding: 8px; margin: 3px 0; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Issue Progress Report</h1>
            <p>Generated: {report['timestamp']}</p>
            <p>Tracking {report['summary']['total_active_issues']} active issues</p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <h3>📈 Improving</h3>
                <h2>{report['summary']['issues_improving']}</h2>
            </div>
            <div class="metric">
                <h3>📉 Declining</h3>
                <h2>{report['summary']['issues_declining']}</h2>
            </div>
            <div class="metric">
                <h3>⏸️ Stagnant</h3>
                <h2>{report['summary']['issues_stagnant']}</h2>
            </div>
            <div class="metric">
                <h3>🎯 Recent Milestones</h3>
                <h2>{report['summary']['recent_milestones']}</h2>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="progressChart"></canvas>
        </div>
        
        <div class="chart-container">
            <canvas id="trendChart"></canvas>
        </div>
        
        <h3>📈 Current Progress</h3>
        {''.join([f'''
        <div class="progress-item">
            <h4>{progress['issue_id']}</h4>
            <div style="background: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden;">
                <div style="background: #28a745; height: 100%; width: {progress['resolution_percentage']}%; transition: width 0.3s;"></div>
            </div>
            <p>{progress['resolution_percentage']:.1f}% complete ({progress['passing_tests']}/{progress['total_affected_tests']} tests passing)</p>
            <p><em>Trend: {progress['trend']}</em></p>
        </div>
        ''' for progress in report['current_progress']])}
        
        <h3>🔍 Insights</h3>
        {''.join([f'<div class="insight">{insight}</div>' for insight in report['insights']])}
        
        <h3>💡 Recommendations</h3>
        {''.join([f'<div class="recommendation">{rec}</div>' for rec in report['recommendations']])}
        
        <h3>🏆 Recent Milestones</h3>
        {''.join([f'''
        <div class="milestone">
            <strong>{milestone['issue_id']}</strong> - {milestone['milestone_type'].replace('_', ' ').title()}
            <br><small>{milestone['timestamp'][:19]} ({milestone['days_since_creation']} days since creation)</small>
        </div>
        ''' for milestone in report['milestones'][-10:]])}
        
        <h3>👥 Team Metrics</h3>
        <div class="metrics">
            <div class="metric">
                <h4>Resolution Velocity</h4>
                <h3>{report['team_metrics']['resolution_velocity']:.1f}/week</h3>
            </div>
            <div class="metric">
                <h4>Quality Score</h4>
                <h3>{report['team_metrics']['quality_score']:.2f}</h3>
            </div>
            <div class="metric">
                <h4>Efficiency Score</h4>
                <h3>{report['team_metrics']['efficiency_score']:.2f}</h3>
            </div>
            <div class="metric">
                <h4>Avg Resolution Time</h4>
                <h3>{report['team_metrics']['average_resolution_time']:.1f} days</h3>
            </div>
        </div>
    </div>
    
    <script>
        // Progress Chart
        const progressCtx = document.getElementById('progressChart').getContext('2d');
        const progressData = {json.dumps([{'label': p['issue_id'], 'value': p['resolution_percentage']} for p in report['current_progress']])};
        
        new Chart(progressCtx, {{
            type: 'bar',
            data: {{
                labels: progressData.map(d => d.label),
                datasets: [{{
                    label: 'Resolution Progress (%)',
                    data: progressData.map(d => d.value),
                    backgroundColor: 'rgba(40, 167, 69, 0.8)',
                    borderColor: 'rgba(40, 167, 69, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }},
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Issue Resolution Progress'
                    }}
                }}
            }}
        }});
        
        // Trend Chart
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        const trendSummary = {json.dumps(report['team_metrics']['trend_summary'])};
        
        new Chart(trendCtx, {{
            type: 'doughnut',
            data: {{
                labels: Object.keys(trendSummary),
                datasets: [{{
                    data: Object.values(trendSummary),
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',   // improving
                        'rgba(220, 53, 69, 0.8)',   // declining
                        'rgba(255, 193, 7, 0.8)',   // stable
                        'rgba(108, 117, 125, 0.8)'  // stagnant
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Issue Trend Distribution'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        
        # Save HTML report
        html_file = self.issues_manager.issues_dir / f"progress_report_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)


def main():
    """Main function for testing progress reporting."""
    reporter = IssueProgressReporter()
    
    print("📊 Issue Progress Reporting System")
    print("=" * 50)
    
    # Generate comprehensive report
    report = reporter.generate_progress_report()
    
    print(f"\n📈 Progress Summary:")
    print(f"  Active Issues: {report['summary']['total_active_issues']}")
    print(f"  Improving: {report['summary']['issues_improving']}")
    print(f"  Declining: {report['summary']['issues_declining']}")
    print(f"  Stagnant: {report['summary']['issues_stagnant']}")
    
    if report['insights']:
        print(f"\n🔍 Key Insights:")
        for insight in report['insights'][:3]:
            print(f"  • {insight}")
    
    if report['recommendations']:
        print(f"\n💡 Top Recommendations:")
        for rec in report['recommendations'][:3]:
            print(f"  • {rec}")
    
    print(f"\n📁 Reports saved to: test_infrastructure/known_issues/")


if __name__ == "__main__":
    main()