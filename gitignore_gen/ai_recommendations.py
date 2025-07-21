"""AI-powered recommendations for gitignore-gen."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta

import aiohttp
from rich.console import Console
from rich.table import Table

console = Console()


@dataclass
class Recommendation:
    """A recommendation with metadata."""
    title: str
    description: str
    priority: str  # low, medium, high, critical
    category: str  # security, performance, best_practice, optimization
    action: str
    confidence: float
    reasoning: str


class AIRecommendationEngine:
    """AI-powered recommendation engine for gitignore optimization."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recommendation_patterns = self._load_recommendation_patterns()
        self.community_patterns = self._load_community_patterns()
        
    def _load_recommendation_patterns(self) -> Dict[str, List[Dict]]:
        """Load recommendation patterns based on project characteristics."""
        return {
            "security": [
                {
                    "trigger": ["env", "config", "secrets"],
                    "pattern": "*.env",
                    "priority": "critical",
                    "title": "Environment Variables",
                    "description": "Add .env files to prevent exposing sensitive data",
                    "action": "Add *.env to .gitignore"
                },
                {
                    "trigger": ["key", "pem", "crt", "cert"],
                    "pattern": "*.key,*.pem,*.crt",
                    "priority": "high",
                    "title": "Certificate Files",
                    "description": "Add certificate files to prevent exposing private keys",
                    "action": "Add *.key,*.pem,*.crt to .gitignore"
                }
            ],
            "performance": [
                {
                    "trigger": ["node_modules", "vendor", "target"],
                    "pattern": "node_modules/,vendor/,target/",
                    "priority": "high",
                    "title": "Dependency Directories",
                    "description": "Add dependency directories to improve git performance",
                    "action": "Add dependency directories to .gitignore"
                },
                {
                    "trigger": ["cache", "tmp", "temp"],
                    "pattern": "*.cache,*.tmp,temp/",
                    "priority": "medium",
                    "title": "Cache Files",
                    "description": "Add cache files to prevent committing temporary data",
                    "action": "Add cache patterns to .gitignore"
                }
            ],
            "best_practice": [
                {
                    "trigger": ["log", "logs"],
                    "pattern": "*.log,logs/",
                    "priority": "medium",
                    "title": "Log Files",
                    "description": "Add log files to prevent committing runtime logs",
                    "action": "Add *.log and logs/ to .gitignore"
                },
                {
                    "trigger": ["build", "dist", "out"],
                    "pattern": "build/,dist/,out/",
                    "priority": "high",
                    "title": "Build Outputs",
                    "description": "Add build output directories to prevent committing generated files",
                    "action": "Add build output directories to .gitignore"
                }
            ]
        }
    
    def _load_community_patterns(self) -> Dict[str, List[str]]:
        """Load community-contributed patterns."""
        return {
            "python": [
                "*.pyc", "__pycache__/", ".pytest_cache/", ".coverage",
                "htmlcov/", ".tox/", ".venv/", "venv/", ".mypy_cache/"
            ],
            "node": [
                "node_modules/", "npm-debug.log*", "yarn-debug.log*", "yarn-error.log*",
                ".npm", ".eslintcache", ".next/", "out/", ".nuxt/"
            ],
            "java": [
                "target/", "*.class", "*.jar", ".gradle/", "build/",
                ".idea/", ".eclipse/", "*.iml"
            ]
        }
    
    async def analyze_project_and_recommend(
        self, 
        project_path: Path, 
        detected_technologies: List[str],
        existing_gitignore: Optional[str] = None
    ) -> List[Recommendation]:
        """Analyze project and generate AI-powered recommendations."""
        recommendations = []
        
        # Analyze project structure
        project_analysis = await self._analyze_project_structure(project_path)
        
        # Generate security recommendations
        security_recs = await self._generate_security_recommendations(
            project_path, project_analysis
        )
        recommendations.extend(security_recs)
        
        # Generate performance recommendations
        perf_recs = await self._generate_performance_recommendations(
            project_path, project_analysis
        )
        recommendations.extend(perf_recs)
        
        # Generate best practice recommendations
        best_practice_recs = await self._generate_best_practice_recommendations(
            project_path, detected_technologies, existing_gitignore
        )
        recommendations.extend(best_practice_recs)
        
        # Generate technology-specific recommendations
        tech_recs = await self._generate_technology_recommendations(
            detected_technologies, existing_gitignore
        )
        recommendations.extend(tech_recs)
        
        # Sort by priority and confidence
        recommendations.sort(
            key=lambda x: (self._priority_score(x.priority), x.confidence),
            reverse=True
        )
        
        return recommendations
    
    async def _analyze_project_structure(self, project_path: Path) -> Dict:
        """Analyze project structure for patterns."""
        analysis = {
            "file_types": {},
            "directories": [],
            "sensitive_files": [],
            "large_files": [],
            "cache_dirs": []
        }
        
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                # Analyze file types
                ext = file_path.suffix.lower()
                analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1
                
                # Check for sensitive files
                if self._is_sensitive_file(file_path):
                    analysis["sensitive_files"].append(str(file_path))
                
                # Check for large files
                if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                    analysis["large_files"].append(str(file_path))
            
            elif file_path.is_dir():
                # Check for cache directories
                if self._is_cache_directory(file_path):
                    analysis["cache_dirs"].append(str(file_path))
                
                analysis["directories"].append(str(file_path))
        
        return analysis
    
    def _is_sensitive_file(self, file_path: Path) -> bool:
        """Check if file contains sensitive information."""
        sensitive_patterns = [
            r"\.env", r"\.key", r"\.pem", r"\.crt", r"\.p12", r"\.pfx",
            r"config\.json", r"secrets\.", r"password", r"credential"
        ]
        
        file_name = file_path.name.lower()
        return any(pattern in file_name for pattern in sensitive_patterns)
    
    def _is_cache_directory(self, dir_path: Path) -> bool:
        """Check if directory is a cache directory."""
        cache_patterns = [
            "cache", "tmp", "temp", "node_modules", "vendor", "target",
            "__pycache__", ".pytest_cache", ".mypy_cache", ".gradle"
        ]
        
        dir_name = dir_path.name.lower()
        return any(pattern in dir_name for pattern in cache_patterns)
    
    async def _generate_security_recommendations(
        self, project_path: Path, analysis: Dict
    ) -> List[Recommendation]:
        """Generate security-focused recommendations."""
        recommendations = []
        
        # Check for sensitive files
        if analysis["sensitive_files"]:
            recommendations.append(Recommendation(
                title="Sensitive Files Detected",
                description=f"Found {len(analysis['sensitive_files'])} potentially sensitive files",
                priority="critical",
                category="security",
                action="Review and add appropriate patterns to .gitignore",
                confidence=0.95,
                reasoning="Sensitive files like .env, .key, .pem files should never be committed"
            ))
        
        # Check for configuration files
        config_files = [f for f in analysis["file_types"].keys() if "config" in f]
        if config_files:
            recommendations.append(Recommendation(
                title="Configuration Files",
                description="Configuration files detected that may contain sensitive data",
                priority="high",
                category="security",
                action="Review config files and add sensitive ones to .gitignore",
                confidence=0.8,
                reasoning="Configuration files often contain API keys, passwords, or other secrets"
            ))
        
        return recommendations
    
    async def _generate_performance_recommendations(
        self, project_path: Path, analysis: Dict
    ) -> List[Recommendation]:
        """Generate performance-focused recommendations."""
        recommendations = []
        
        # Check for large files
        if analysis["large_files"]:
            recommendations.append(Recommendation(
                title="Large Files Detected",
                description=f"Found {len(analysis['large_files'])} files larger than 10MB",
                priority="high",
                category="performance",
                action="Add large files to .gitignore or use Git LFS",
                confidence=0.9,
                reasoning="Large files slow down git operations and increase repository size"
            ))
        
        # Check for cache directories
        if analysis["cache_dirs"]:
            recommendations.append(Recommendation(
                title="Cache Directories",
                description=f"Found {len(analysis['cache_dirs'])} cache directories",
                priority="medium",
                category="performance",
                action="Add cache directories to .gitignore",
                confidence=0.85,
                reasoning="Cache directories contain temporary files that should not be committed"
            ))
        
        return recommendations
    
    async def _generate_best_practice_recommendations(
        self, 
        project_path: Path, 
        technologies: List[str],
        existing_gitignore: Optional[str]
    ) -> List[Recommendation]:
        """Generate best practice recommendations."""
        recommendations = []
        
        # Check for log files
        log_files = list(project_path.rglob("*.log"))
        if log_files:
            recommendations.append(Recommendation(
                title="Log Files",
                description=f"Found {len(log_files)} log files",
                priority="medium",
                category="best_practice",
                action="Add *.log to .gitignore",
                confidence=0.9,
                reasoning="Log files contain runtime information and should not be committed"
            ))
        
        # Check for build outputs
        build_dirs = [d for d in project_path.iterdir() if d.is_dir() and d.name in ["build", "dist", "out"]]
        if build_dirs:
            recommendations.append(Recommendation(
                title="Build Output Directories",
                description=f"Found {len(build_dirs)} build output directories",
                priority="high",
                category="best_practice",
                action="Add build output directories to .gitignore",
                confidence=0.95,
                reasoning="Build outputs are generated files that should not be committed"
            ))
        
        return recommendations
    
    async def _generate_technology_recommendations(
        self, 
        technologies: List[str],
        existing_gitignore: Optional[str]
    ) -> List[Recommendation]:
        """Generate technology-specific recommendations."""
        recommendations = []
        
        for tech in technologies:
            if tech in self.community_patterns:
                patterns = self.community_patterns[tech]
                
                # Check if patterns are already in .gitignore
                missing_patterns = []
                if existing_gitignore:
                    for pattern in patterns:
                        if pattern not in existing_gitignore:
                            missing_patterns.append(pattern)
                else:
                    missing_patterns = patterns
                
                if missing_patterns:
                    recommendations.append(Recommendation(
                        title=f"{tech.title()} Best Practices",
                        description=f"Missing {len(missing_patterns)} recommended patterns for {tech}",
                        priority="high",
                        category="best_practice",
                        action=f"Add {tech}-specific patterns to .gitignore",
                        confidence=0.9,
                        reasoning=f"Community best practices for {tech} projects"
                    ))
        
        return recommendations
    
    def _priority_score(self, priority: str) -> int:
        """Convert priority string to numeric score."""
        scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        return scores.get(priority, 1)
    
    def display_recommendations(self, recommendations: List[Recommendation]) -> None:
        """Display recommendations in a beautiful table."""
        if not recommendations:
            console.print("✅ No recommendations found - your .gitignore looks good!")
            return
        
        table = Table(title="🤖 AI Recommendations")
        table.add_column("Priority", style="bold")
        table.add_column("Category", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Description", style="white")
        table.add_column("Action", style="yellow")
        table.add_column("Confidence", style="blue")
        
        for rec in recommendations:
            priority_emoji = {
                "low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"
            }.get(rec.priority, "⚪")
            
            table.add_row(
                f"{priority_emoji} {rec.priority.title()}",
                rec.category.replace("_", " ").title(),
                rec.title,
                rec.description,
                rec.action,
                f"{rec.confidence:.1%}"
            )
        
        console.print(table)
        
        # Show reasoning for top recommendations
        console.print("\n[bold]💡 Top Recommendations Reasoning:[/bold]")
        for i, rec in enumerate(recommendations[:3], 1):
            console.print(f"{i}. [bold]{rec.title}[/bold]: {rec.reasoning}")


class CommunityInsights:
    """Community insights and trending patterns."""
    
    def __init__(self):
        self.api_base = "https://api.github.com"
        self.cache_file = Path.home() / ".gign" / "community_cache.json"
        self.cache_duration = timedelta(hours=24)
    
    async def get_trending_patterns(self) -> Dict[str, List[str]]:
        """Get trending patterns from community repositories."""
        try:
            # This would integrate with GitHub API to find trending patterns
            # For now, return curated patterns
            return {
                "trending": [
                    "*.local", "*.local.*", ".env.local", ".env.*.local",
                    "*.log.*", "logs/*.log", "*.tmp", "*.temp"
                ],
                "security": [
                    "*.key", "*.pem", "*.crt", "*.p12", "*.pfx",
                    "secrets/", "credentials/", "*.env"
                ],
                "performance": [
                    "node_modules/", "vendor/", "target/", "build/",
                    "dist/", "out/", ".cache/", "tmp/"
                ]
            }
        except Exception as e:
            console.print(f"[red]Warning: Could not fetch trending patterns: {e}[/red]")
            return {}
    
    async def get_community_stats(self) -> Dict:
        """Get community statistics."""
        return {
            "total_repositories": 1000000,
            "popular_patterns": [
                "node_modules/", "*.log", "*.env", "build/", "dist/"
            ],
            "trending_technologies": [
                "rust", "go", "flutter", "svelte", "deno"
            ]
        }


# Global instances
ai_engine = AIRecommendationEngine()
community_insights = CommunityInsights() 