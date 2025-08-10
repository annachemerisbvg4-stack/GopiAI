#!/usr/bin/env python3
"""
CI Report Generator
Consolidates test results from multiple sources into comprehensive reports
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import xml.etree.ElementTree as ET


def load_test_results(artifacts_dir: Path) -> Dict[str, Any]:
    """Load test results from artifacts directory"""
    results = {}
    
    # Look for test result files
    for result_dir in artifacts_dir.rglob('*test-results*'):
        if result_dir.is_dir():
            # Load JSON results
            for json_file in result_dir.glob('*.json'):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        results[json_file.stem] = data
                except Exception as e:
                    print(f"Warning: Could not load {json_file}: {e}")
            
            # Load JUnit XML results
            for xml_file in result_dir.glob('*.xml'):
                try:
                    results[xml_file.stem] = parse_junit_xml(xml_file)
                except Exception as e:
                    print(f"Warning: Could not parse {xml_file}: {e}")
    
    return results


def parse_junit_xml(xml_file: Path) -> Dict[str, Any]:
    """Parse JUnit XML file"""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    result = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'errors': 0,
        'duration': 0.0,
        'test_cases': []
    }
    
    # Handle both testsuite and testsuites root elements
    testsuites = [root] if root.tag == 'testsuite' else root.findall('testsuite')
    
    for testsuite in testsuites:
        result['total'] += int(testsuite.get('tests', 0))
        result['failed'] += int(testsuite.get('failures', 0))
        result['errors'] += int(testsuite.get('errors', 0))
        result['skipped'] += int(testsuite.get('skipped', 0))
        result['duration'] += float(testsuite.get('time', 0))
        
        # Parse individual test cases
        for testcase in testsuite.findall('testcase'):
            case_info = {
                'name': testcase.get('name'),
                'class': testcase.get('classname'),
                'duration': float(testcase.get('time', 0)),
                'status': 'passed'
            }
            
            if testcase.find('failure') is not None:
                case_info['status'] = 'failed'
                failure = testcase.find('failure')
                case_info['error'] = failure.get('message', '')
                case_info['traceback'] = failure.text or ''
            elif testcase.find('error') is not None:
                case_info['status'] = 'error'
                error = testcase.find('error')
                case_info['error'] = error.get('message', '')
                case_info['traceback'] = error.text or ''
            elif testcase.find('skipped') is not None:
                case_info['status'] = 'skipped'
                skipped = testcase.find('skipped')
                case_info['reason'] = skipped.get('message', '')
            
            result['test_cases'].append(case_info)
    
    result['passed'] = result['total'] - result['failed'] - result['errors'] - result['skipped']
    
    return result


def generate_html_report(results: Dict[str, Any], output_file: Path):
    """Generate HTML report"""
    # Calculate summary statistics
    total_tests = sum(r.get('total', 0) for r in results.values())
    total_passed = sum(r.get('passed', 0) for r in results.values())
    total_failed = sum(r.get('failed', 0) for r in results.values())
    total_skipped = sum(r.get('skipped', 0) for r in results.values())
    total_errors = sum(r.get('errors', 0) for r in results.values())
    total_duration = sum(r.get('duration', 0) for r in results.values())
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GopiAI CI/CD Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ color: #333; margin-bottom: 10px; }}
            .header .timestamp {{ color: #666; font-size: 14px; }}
            .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .metric {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }}
            .metric.success {{ border-left-color: #28a745; }}
            .metric.danger {{ border-left-color: #dc3545; }}
            .metric.warning {{ border-left-color: #ffc107; }}
            .metric-value {{ font-size: 32px; font-weight: bold; margin-bottom: 5px; }}
            .metric-label {{ font-size: 14px; color: #666; }}
            .test-results {{ margin-top: 30px; }}
            .test-suite {{ margin-bottom: 30px; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }}
            .test-suite-header {{ background-color: #f8f9fa; padding: 15px; border-bottom: 1px solid #ddd; }}
            .test-suite-title {{ font-size: 18px; font-weight: bold; margin: 0; }}
            .test-suite-stats {{ font-size: 14px; color: #666; margin-top: 5px; }}
            .test-cases {{ max-height: 400px; overflow-y: auto; }}
            .test-case {{ padding: 10px 15px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }}
            .test-case:last-child {{ border-bottom: none; }}
            .test-case.passed {{ background-color: #f8fff8; }}
            .test-case.failed {{ background-color: #fff8f8; }}
            .test-case.skipped {{ background-color: #fffef8; }}
            .test-case-name {{ font-weight: 500; }}
            .test-case-status {{ padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
            .status-passed {{ background-color: #28a745; color: white; }}
            .status-failed {{ background-color: #dc3545; color: white; }}
            .status-skipped {{ background-color: #ffc107; color: black; }}
            .status-error {{ background-color: #6c757d; color: white; }}
            .progress-bar {{ width: 100%; height: 20px; background-color: #e9ecef; border-radius: 10px; overflow: hidden; margin: 10px 0; }}
            .progress-fill {{ height: 100%; background-color: #28a745; transition: width 0.3s ease; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>GopiAI CI/CD Test Report</h1>
                <div class="timestamp">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <div class="metric-value">{total_tests}</div>
                    <div class="metric-label">Total Tests</div>
                </div>
                <div class="metric success">
                    <div class="metric-value">{total_passed}</div>
                    <div class="metric-label">Passed</div>
                </div>
                <div class="metric danger">
                    <div class="metric-value">{total_failed}</div>
                    <div class="metric-label">Failed</div>
                </div>
                <div class="metric warning">
                    <div class="metric-value">{total_skipped}</div>
                    <div class="metric-label">Skipped</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{success_rate:.1f}%</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{total_duration:.1f}s</div>
                    <div class="metric-label">Duration</div>
                </div>
            </div>
            
            <div class="progress-bar">
                <div class="progress-fill" style="width: {success_rate}%;"></div>
            </div>
            
            <div class="test-results">
    """
    
    # Add test suite details
    for suite_name, suite_results in results.items():
        suite_total = suite_results.get('total', 0)
        suite_passed = suite_results.get('passed', 0)
        suite_failed = suite_results.get('failed', 0)
        suite_skipped = suite_results.get('skipped', 0)
        suite_duration = suite_results.get('duration', 0)
        
        html_content += f"""
                <div class="test-suite">
                    <div class="test-suite-header">
                        <div class="test-suite-title">{suite_name.replace('-', ' ').title()}</div>
                        <div class="test-suite-stats">
                            {suite_total} tests • {suite_passed} passed • {suite_failed} failed • {suite_skipped} skipped • {suite_duration:.1f}s
                        </div>
                    </div>
        """
        
        if 'test_cases' in suite_results:
            html_content += '<div class="test-cases">'
            
            for test_case in suite_results['test_cases']:
                status = test_case.get('status', 'unknown')
                name = test_case.get('name', 'Unknown Test')
                duration = test_case.get('duration', 0)
                
                html_content += f"""
                        <div class="test-case {status}">
                            <div class="test-case-name">{name}</div>
                            <div>
                                <span class="test-case-status status-{status}">{status.upper()}</span>
                                <span style="margin-left: 10px; color: #666; font-size: 12px;">{duration:.2f}s</span>
                            </div>
                        </div>
                """
            
            html_content += '</div>'
        
        html_content += '</div>'
    
    html_content += """
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


def generate_json_report(results: Dict[str, Any], output_file: Path):
    """Generate JSON report"""
    # Calculate summary
    summary = {
        'total_tests': sum(r.get('total', 0) for r in results.values()),
        'total_passed': sum(r.get('passed', 0) for r in results.values()),
        'total_failed': sum(r.get('failed', 0) for r in results.values()),
        'total_skipped': sum(r.get('skipped', 0) for r in results.values()),
        'total_errors': sum(r.get('errors', 0) for r in results.values()),
        'total_duration': sum(r.get('duration', 0) for r in results.values()),
        'timestamp': datetime.now().isoformat()
    }
    
    summary['success_rate'] = (summary['total_passed'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
    
    report = {
        'summary': summary,
        'test_suites': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def generate_junit_xml(results: Dict[str, Any], output_file: Path):
    """Generate consolidated JUnit XML"""
    root = ET.Element('testsuites')
    
    for suite_name, suite_results in results.items():
        testsuite = ET.SubElement(root, 'testsuite')
        testsuite.set('name', suite_name)
        testsuite.set('tests', str(suite_results.get('total', 0)))
        testsuite.set('failures', str(suite_results.get('failed', 0)))
        testsuite.set('errors', str(suite_results.get('errors', 0)))
        testsuite.set('skipped', str(suite_results.get('skipped', 0)))
        testsuite.set('time', str(suite_results.get('duration', 0)))
        
        # Add test cases
        for test_case in suite_results.get('test_cases', []):
            testcase = ET.SubElement(testsuite, 'testcase')
            testcase.set('name', test_case.get('name', 'unknown'))
            testcase.set('classname', test_case.get('class', suite_name))
            testcase.set('time', str(test_case.get('duration', 0)))
            
            status = test_case.get('status', 'passed')
            if status == 'failed':
                failure = ET.SubElement(testcase, 'failure')
                failure.set('message', test_case.get('error', 'Test failed'))
                failure.text = test_case.get('traceback', '')
            elif status == 'error':
                error = ET.SubElement(testcase, 'error')
                error.set('message', test_case.get('error', 'Test error'))
                error.text = test_case.get('traceback', '')
            elif status == 'skipped':
                skipped = ET.SubElement(testcase, 'skipped')
                skipped.set('message', test_case.get('reason', 'Test skipped'))
    
    # Write XML
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)


def generate_summary_markdown(results: Dict[str, Any], output_file: Path):
    """Generate summary in Markdown format for PR comments"""
    total_tests = sum(r.get('total', 0) for r in results.values())
    total_passed = sum(r.get('passed', 0) for r in results.values())
    total_failed = sum(r.get('failed', 0) for r in results.values())
    total_skipped = sum(r.get('skipped', 0) for r in results.values())
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    status_emoji = "✅" if total_failed == 0 else "❌"
    
    markdown = f"""# {status_emoji} GopiAI Test Results

## Summary
- **Total Tests**: {total_tests}
- **Passed**: {total_passed} ✅
- **Failed**: {total_failed} ❌
- **Skipped**: {total_skipped} ⏭️
- **Success Rate**: {success_rate:.1f}%

## Test Suites
"""
    
    for suite_name, suite_results in results.items():
        suite_status = "✅" if suite_results.get('failed', 0) == 0 else "❌"
        markdown += f"- **{suite_name}** {suite_status}: {suite_results.get('passed', 0)}/{suite_results.get('total', 0)} passed\n"
    
    if total_failed > 0:
        markdown += "\n## Failed Tests\n"
        for suite_name, suite_results in results.items():
            failed_cases = [tc for tc in suite_results.get('test_cases', []) if tc.get('status') == 'failed']
            if failed_cases:
                markdown += f"\n### {suite_name}\n"
                for case in failed_cases[:5]:  # Limit to first 5 failures
                    markdown += f"- `{case.get('name', 'unknown')}`: {case.get('error', 'No error message')}\n"
                if len(failed_cases) > 5:
                    markdown += f"- ... and {len(failed_cases) - 5} more failures\n"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generate CI/CD test reports')
    parser.add_argument('--artifacts-dir', required=True,
                       help='Directory containing test artifacts')
    parser.add_argument('--output-dir', required=True,
                       help='Output directory for reports')
    parser.add_argument('--format', nargs='+', 
                       choices=['html', 'json', 'junit', 'markdown'],
                       default=['html', 'json'],
                       help='Report formats to generate')
    
    args = parser.parse_args()
    
    artifacts_dir = Path(args.artifacts_dir)
    output_dir = Path(args.output_dir)
    
    if not artifacts_dir.exists():
        print(f"Error: Artifacts directory not found: {artifacts_dir}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading test results...")
    results = load_test_results(artifacts_dir)
    
    if not results:
        print("Warning: No test results found")
        # Create empty results
        results = {'no_tests': {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'errors': 0, 'duration': 0.0}}
    
    print(f"Found {len(results)} test suites")
    
    # Generate reports
    for format_type in args.format:
        print(f"Generating {format_type} report...")
        
        if format_type == 'html':
            generate_html_report(results, output_dir / 'index.html')
        elif format_type == 'json':
            generate_json_report(results, output_dir / 'test_results.json')
        elif format_type == 'junit':
            generate_junit_xml(results, output_dir / 'consolidated-junit.xml')
        elif format_type == 'markdown':
            generate_summary_markdown(results, output_dir / 'summary.md')
    
    print(f"Reports generated in: {output_dir}")


if __name__ == '__main__':
    main()