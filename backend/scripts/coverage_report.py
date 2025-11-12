#!/usr/bin/env python3
"""
Coverage report generator for VulnScanner backend.

This script generates comprehensive test coverage reports with analysis,
including module-by-module breakdown, missing coverage identification,
and recommendations for improving test coverage.

Usage:
    python scripts/coverage_report.py
    python scripts/coverage_report.py --format html
    python scripts/coverage_report.py --format json --output coverage_analysis.json
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict
import xml.etree.ElementTree as ET


class CoverageAnalyzer:
    """Analyze test coverage and generate detailed reports."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.coverage_xml = project_root / "coverage.xml"
        self.coverage_data = {}
        
    def run_coverage(self) -> bool:
        """Run pytest with coverage to generate coverage data."""
        print("🧪 Running tests with coverage...")
        
        cmd = [
            "python", "-m", "pytest",
            "--cov=.",
            "--cov-report=xml:coverage.xml",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--quiet"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            if result.returncode != 0:
                print(f"❌ Tests failed: {result.stderr}")
                return False
            print("✅ Coverage data generated successfully")
            return True
        except Exception as e:
            print(f"❌ Error running coverage: {e}")
            return False
    
    def parse_coverage_xml(self) -> Dict:
        """Parse coverage XML file and extract coverage data."""
        if not self.coverage_xml.exists():
            print(f"❌ Coverage XML file not found: {self.coverage_xml}")
            return {}
        
        try:
            tree = ET.parse(self.coverage_xml)
            root = tree.getroot()
            
            coverage_data = {
                "summary": {},
                "packages": {},
                "files": {}
            }
            
            # Parse summary
            for counter in root.findall(".//counter"):
                coverage_type = counter.get("type", "").lower()
                covered = int(counter.get("covered", 0))
                missed = int(counter.get("missed", 0))
                total = covered + missed
                percentage = (covered / total * 100) if total > 0 else 0
                
                coverage_data["summary"][coverage_type] = {
                    "covered": covered,
                    "missed": missed,
                    "total": total,
                    "percentage": round(percentage, 2)
                }
            
            # Parse packages and files
            for package in root.findall(".//package"):
                package_name = package.get("name", "")
                package_data = {"files": {}, "summary": {}}
                
                # Package summary
                for counter in package.findall("counter"):
                    coverage_type = counter.get("type", "").lower()
                    covered = int(counter.get("covered", 0))
                    missed = int(counter.get("missed", 0))
                    total = covered + missed
                    percentage = (covered / total * 100) if total > 0 else 0
                    
                    package_data["summary"][coverage_type] = {
                        "covered": covered,
                        "missed": missed,
                        "total": total,
                        "percentage": round(percentage, 2)
                    }
                
                # Files in package
                for sourcefile in package.findall("sourcefile"):
                    filename = sourcefile.get("name", "")
                    file_data = {}
                    
                    for counter in sourcefile.findall("counter"):
                        coverage_type = counter.get("type", "").lower()
                        covered = int(counter.get("covered", 0))
                        missed = int(counter.get("missed", 0))
                        total = covered + missed
                        percentage = (covered / total * 100) if total > 0 else 0
                        
                        file_data[coverage_type] = {
                            "covered": covered,
                            "missed": missed,
                            "total": total,
                            "percentage": round(percentage, 2)
                        }
                    
                    package_data["files"][filename] = file_data
                    coverage_data["files"][f"{package_name}/{filename}"] = file_data
                
                coverage_data["packages"][package_name] = package_data
            
            self.coverage_data = coverage_data
            return coverage_data
            
        except Exception as e:
            print(f"❌ Error parsing coverage XML: {e}")
            return {}
    
    def analyze_coverage(self) -> Dict:
        """Analyze coverage data and provide insights."""
        if not self.coverage_data:
            return {}
        
        analysis = {
            "overall_health": "unknown",
            "recommendations": [],
            "low_coverage_files": [],
            "uncovered_files": [],
            "high_coverage_files": [],
            "statistics": {}
        }
        
        # Overall health assessment
        line_coverage = self.coverage_data.get("summary", {}).get("line", {}).get("percentage", 0)
        
        if line_coverage >= 90:
            analysis["overall_health"] = "excellent"
        elif line_coverage >= 80:
            analysis["overall_health"] = "good"
        elif line_coverage >= 70:
            analysis["overall_health"] = "fair"
        elif line_coverage >= 50:
            analysis["overall_health"] = "poor"
        else:
            analysis["overall_health"] = "critical"
        
        # Analyze files
        for filepath, file_data in self.coverage_data.get("files", {}).items():
            line_data = file_data.get("line", {})
            line_percentage = line_data.get("percentage", 0)
            
            if line_percentage == 0:
                analysis["uncovered_files"].append({
                    "file": filepath,
                    "coverage": line_percentage
                })
            elif line_percentage < 50:
                analysis["low_coverage_files"].append({
                    "file": filepath,
                    "coverage": line_percentage,
                    "lines_missed": line_data.get("missed", 0)
                })
            elif line_percentage >= 95:
                analysis["high_coverage_files"].append({
                    "file": filepath,
                    "coverage": line_percentage
                })
        
        # Sort by coverage percentage
        analysis["low_coverage_files"].sort(key=lambda x: x["coverage"])
        analysis["high_coverage_files"].sort(key=lambda x: x["coverage"], reverse=True)
        
        # Generate recommendations
        if line_coverage < 80:
            analysis["recommendations"].append(
                f"Increase overall line coverage from {line_coverage:.1f}% to at least 80%"
            )
        
        if len(analysis["uncovered_files"]) > 0:
            analysis["recommendations"].append(
                f"Add tests for {len(analysis['uncovered_files'])} completely uncovered files"
            )
        
        if len(analysis["low_coverage_files"]) > 5:
            analysis["recommendations"].append(
                f"Focus on improving coverage for {len(analysis['low_coverage_files'])} low-coverage files"
            )
        
        # Statistics
        total_files = len(self.coverage_data.get("files", {}))
        covered_files = total_files - len(analysis["uncovered_files"])
        
        analysis["statistics"] = {
            "total_files": total_files,
            "covered_files": covered_files,
            "uncovered_files": len(analysis["uncovered_files"]),
            "low_coverage_files": len(analysis["low_coverage_files"]),
            "high_coverage_files": len(analysis["high_coverage_files"]),
            "coverage_distribution": self._calculate_coverage_distribution()
        }
        
        return analysis
    
    def _calculate_coverage_distribution(self) -> Dict[str, int]:
        """Calculate distribution of files by coverage ranges."""
        distribution = {
            "0%": 0,
            "1-25%": 0,
            "26-50%": 0,
            "51-75%": 0,
            "76-90%": 0,
            "91-100%": 0
        }
        
        for file_data in self.coverage_data.get("files", {}).values():
            percentage = file_data.get("line", {}).get("percentage", 0)
            
            if percentage == 0:
                distribution["0%"] += 1
            elif percentage <= 25:
                distribution["1-25%"] += 1
            elif percentage <= 50:
                distribution["26-50%"] += 1
            elif percentage <= 75:
                distribution["51-75%"] += 1
            elif percentage <= 90:
                distribution["76-90%"] += 1
            else:
                distribution["91-100%"] += 1
        
        return distribution
    
    def generate_text_report(self) -> str:
        """Generate a human-readable text report."""
        if not self.coverage_data:
            return "No coverage data available"
        
        analysis = self.analyze_coverage()
        summary = self.coverage_data.get("summary", {})
        
        report = []
        report.append("📊 VulnScanner Test Coverage Report")
        report.append("=" * 50)
        report.append("")
        
        # Overall summary
        line_summary = summary.get("line", {})
        branch_summary = summary.get("branch", {})
        
        report.append("📈 Overall Coverage:")
        report.append(f"  Lines:    {line_summary.get('covered', 0):4d}/{line_summary.get('total', 0):4d} ({line_summary.get('percentage', 0):5.1f}%)")
        if branch_summary:
            report.append(f"  Branches: {branch_summary.get('covered', 0):4d}/{branch_summary.get('total', 0):4d} ({branch_summary.get('percentage', 0):5.1f}%)")
        report.append("")
        
        # Health assessment
        health_emoji = {
            "excellent": "🟢",
            "good": "🟡",
            "fair": "🟠",
            "poor": "🔴",
            "critical": "💀"
        }
        
        health = analysis.get("overall_health", "unknown")
        report.append(f"🏥 Coverage Health: {health_emoji.get(health, '❓')} {health.title()}")
        report.append("")
        
        # Statistics
        stats = analysis.get("statistics", {})
        report.append("📊 File Statistics:")
        report.append(f"  Total files:        {stats.get('total_files', 0)}")
        report.append(f"  Files with tests:   {stats.get('covered_files', 0)}")
        report.append(f"  Uncovered files:    {stats.get('uncovered_files', 0)}")
        report.append(f"  Low coverage files: {stats.get('low_coverage_files', 0)}")
        report.append("")
        
        # Coverage distribution
        distribution = stats.get("coverage_distribution", {})
        report.append("📈 Coverage Distribution:")
        for range_name, count in distribution.items():
            if count > 0:
                report.append(f"  {range_name:>8}: {count:3d} files")
        report.append("")
        
        # Recommendations
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            report.append("💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                report.append(f"  {i}. {rec}")
            report.append("")
        
        # Low coverage files
        low_coverage = analysis.get("low_coverage_files", [])
        if low_coverage:
            report.append("🔍 Files Needing Attention (Low Coverage):")
            for file_info in low_coverage[:10]:  # Show top 10
                report.append(f"  {file_info['coverage']:5.1f}% - {file_info['file']}")
            if len(low_coverage) > 10:
                report.append(f"  ... and {len(low_coverage) - 10} more files")
            report.append("")
        
        # Uncovered files
        uncovered = analysis.get("uncovered_files", [])
        if uncovered:
            report.append("❌ Completely Uncovered Files:")
            for file_info in uncovered[:10]:  # Show top 10
                report.append(f"  {file_info['file']}")
            if len(uncovered) > 10:
                report.append(f"  ... and {len(uncovered) - 10} more files")
            report.append("")
        
        report.append("📁 Detailed HTML report: htmlcov/index.html")
        
        return "\n".join(report)
    
    def save_json_report(self, output_path: Path) -> bool:
        """Save coverage analysis as JSON."""
        try:
            analysis = self.analyze_coverage()
            report_data = {
                "coverage_data": self.coverage_data,
                "analysis": analysis,
                "generated_at": str(Path.cwd()),
                "timestamp": subprocess.check_output(["date"], text=True).strip()
            }
            
            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"✅ JSON report saved to: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving JSON report: {e}")
            return False


def main():
    """Main entry point for coverage report generator."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive test coverage reports",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--format",
        choices=["text", "json", "html"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (for JSON format)"
    )
    
    parser.add_argument(
        "--no-run",
        action="store_true",
        help="Skip running tests, use existing coverage data"
    )
    
    args = parser.parse_args()
    
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    analyzer = CoverageAnalyzer(backend_dir)
    
    # Run coverage if requested
    if not args.no_run:
        if not analyzer.run_coverage():
            return 1
    
    # Parse coverage data
    if not analyzer.parse_coverage_xml():
        print("❌ Failed to parse coverage data")
        return 1
    
    # Generate report based on format
    if args.format == "text":
        report = analyzer.generate_text_report()
        print(report)
    
    elif args.format == "json":
        output_path = args.output or Path("coverage_analysis.json")
        if not analyzer.save_json_report(output_path):
            return 1
    
    elif args.format == "html":
        print("📊 HTML coverage report generated at: htmlcov/index.html")
        
        # Try to open in browser
        try:
            import webbrowser
            report_path = backend_dir / "htmlcov" / "index.html"
            if report_path.exists():
                webbrowser.open(f"file://{report_path.absolute()}")
                print("🌐 Opening coverage report in browser...")
        except Exception as e:
            print(f"⚠️  Could not open browser: {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())