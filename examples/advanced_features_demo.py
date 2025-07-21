#!/usr/bin/env python3
"""
Advanced Features Demo for gign

This script demonstrates the new advanced features added to gign:
- AI-powered recommendations
- GitHub integration
- Advanced template management
- Template marketplace
- Template validation
"""

import asyncio
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_demo_header():
    """Print demo header."""
    header = """
[bold blue]🚀 gign Advanced Features Demo[/bold blue]
[italic]Showcasing the new AI-powered, GitHub-integrated, and community-driven features[/italic]
    """
    console.print(Panel(header, border_style="blue"))


async def demo_ai_recommendations():
    """Demo AI-powered recommendations."""
    console.print("\n[bold cyan]🤖 AI-Powered Recommendations Demo[/bold cyan]")
    
    # Create a sample project structure
    demo_project = Path("demo-ai-project")
    demo_project.mkdir(exist_ok=True)
    
    # Create some files that would trigger recommendations
    (demo_project / "config.json").write_text('{"api_key": "secret123"}')
    (demo_project / ".env").write_text("DATABASE_URL=postgresql://user:pass@localhost/db")
    (demo_project / "logs").mkdir(exist_ok=True)
    (demo_project / "logs" / "app.log").write_text("2024-01-01 INFO: Application started")
    (demo_project / "node_modules").mkdir(exist_ok=True)
    (demo_project / "build").mkdir(exist_ok=True)
    
    console.print("📁 Created demo project with various file types")
    console.print("🔍 Running AI recommendations analysis...")
    
    # This would normally call the AI engine
    # For demo purposes, we'll show what the output would look like
    recommendations = [
        {
            "title": "Sensitive Files Detected",
            "description": "Found 2 potentially sensitive files",
            "priority": "critical",
            "category": "security",
            "action": "Review and add appropriate patterns to .gitignore",
            "confidence": 0.95,
            "reasoning": "Sensitive files like .env, config.json files should never be committed"
        },
        {
            "title": "Log Files",
            "description": "Found 1 log file",
            "priority": "medium",
            "category": "best_practice",
            "action": "Add *.log to .gitignore",
            "confidence": 0.9,
            "reasoning": "Log files contain runtime information and should not be committed"
        },
        {
            "title": "Build Output Directories",
            "description": "Found 1 build output directory",
            "priority": "high",
            "category": "best_practice",
            "action": "Add build output directories to .gitignore",
            "confidence": 0.95,
            "reasoning": "Build outputs are generated files that should not be committed"
        }
    ]
    
    # Display recommendations
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
        }.get(rec["priority"], "⚪")
        
        table.add_row(
            f"{priority_emoji} {rec['priority'].title()}",
            rec["category"].replace("_", " ").title(),
            rec["title"],
            rec["description"],
            rec["action"],
            f"{rec['confidence']:.1%}"
        )
    
    console.print(table)
    
    # Cleanup
    import shutil
    shutil.rmtree(demo_project)
    console.print("🧹 Cleaned up demo project")


async def demo_github_integration():
    """Demo GitHub integration features."""
    console.print("\n[bold cyan]🔗 GitHub Integration Demo[/bold cyan]")
    
    # Show what repository analysis would look like
    console.print("📊 Repository Analysis Example:")
    
    repo_info = {
        "full_name": "example/react-app",
        "description": "A modern React application with TypeScript",
        "stargazers_count": 1250,
        "forks_count": 89,
        "watchers_count": 156
    }
    
    languages = {
        "TypeScript": 45000,
        "JavaScript": 12000,
        "CSS": 8000,
        "HTML": 2000
    }
    
    # Display repository info
    console.print(Panel(
        f"[bold blue]{repo_info['full_name']}[/bold blue]\n"
        f"[dim]{repo_info['description']}[/dim]\n"
        f"⭐ {repo_info['stargazers_count']} stars | "
        f"🔀 {repo_info['forks_count']} forks | "
        f"👀 {repo_info['watchers_count']} watchers",
        title="📊 Repository Information"
    ))
    
    # Display languages
    lang_table = Table(title="🔤 Languages")
    lang_table.add_column("Language", style="cyan")
    lang_table.add_column("Bytes", style="green")
    lang_table.add_column("Percentage", style="yellow")
    
    total_bytes = sum(languages.values())
    for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
        percentage = (bytes_count / total_bytes) * 100
        lang_table.add_row(lang, f"{bytes_count:,}", f"{percentage:.1f}%")
    
    console.print(lang_table)
    
    console.print("✅ .gitignore file found (45 lines)")
    
    # Show recommendations
    rec_table = Table(title="💡 Repository Recommendations")
    rec_table.add_column("Priority", style="bold")
    rec_table.add_column("Message", style="white")
    rec_table.add_column("Action", style="yellow")
    
    rec_table.add_row(
        "🟡 Medium",
        "Missing TypeScript-specific patterns",
        "Add *.tsbuildinfo, .tscache/ patterns"
    )
    
    console.print(rec_table)


async def demo_template_marketplace():
    """Demo template marketplace features."""
    console.print("\n[bold cyan]🛒 Template Marketplace Demo[/bold cyan]")
    
    # Show marketplace templates
    templates = [
        {
            "name": "fullstack-web",
            "description": "Complete web development stack with Node.js, React, and Python",
            "author": "community",
            "downloads": 1500,
            "rating": 4.8,
            "tags": ["web", "fullstack", "react", "node", "python"],
            "technologies": ["node", "react", "python", "docker"]
        },
        {
            "name": "microservices",
            "description": "Microservices architecture with Docker, Kubernetes, and monitoring",
            "author": "community",
            "downloads": 1200,
            "rating": 4.6,
            "tags": ["microservices", "docker", "kubernetes", "monitoring"],
            "technologies": ["docker", "kubernetes", "prometheus", "grafana"]
        },
        {
            "name": "data-science",
            "description": "Data science and machine learning with Python, Jupyter, and ML frameworks",
            "author": "community",
            "downloads": 2000,
            "rating": 4.9,
            "tags": ["data-science", "ml", "python", "jupyter"],
            "technologies": ["python", "jupyter", "tensorflow", "pytorch"]
        }
    ]
    
    table = Table(title="🛒 Template Marketplace")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Author", style="green")
    table.add_column("Downloads", style="blue")
    table.add_column("Rating", style="magenta")
    table.add_column("Tags", style="yellow")
    
    for template in templates:
        tags_str = ", ".join(template["tags"][:3])
        table.add_row(
            template["name"],
            template["description"][:50] + "..." if len(template["description"]) > 50 else template["description"],
            template["author"],
            str(template["downloads"]),
            f"{template['rating']}⭐",
            tags_str
        )
    
    console.print(table)


async def demo_advanced_templates():
    """Demo advanced template management."""
    console.print("\n[bold cyan]📚 Advanced Template Management Demo[/bold cyan]")
    
    # Show template creation example
    console.print("📝 Creating Advanced Template Example:")
    
    template_data = {
        "name": "my-awesome-project",
        "description": "A comprehensive template for my awesome project",
        "author": "developer",
        "version": "1.0.0",
        "tags": ["custom", "web", "fullstack"],
        "technologies": ["node", "react", "python", "docker"],
        "downloads": 0,
        "rating": 0.0,
        "file_size": 245,
        "checksum": "abc123..."
    }
    
    console.print(f"✅ Template '{template_data['name']}' created successfully!")
    console.print(f"📝 Description: {template_data['description']}")
    console.print(f"🏷️ Tags: {', '.join(template_data['tags'])}")
    console.print(f"🔧 Technologies: {', '.join(template_data['technologies'])}")
    
    # Show template listing
    console.print("\n📚 Local Templates:")
    
    templates_table = Table(title="📚 Templates")
    templates_table.add_column("Name", style="cyan", no_wrap=True)
    templates_table.add_column("Description", style="white")
    templates_table.add_column("Author", style="green")
    templates_table.add_column("Version", style="yellow")
    templates_table.add_column("Downloads", style="blue")
    templates_table.add_column("Rating", style="magenta")
    templates_table.add_column("Type", style="bold")
    
    templates_table.add_row(
        template_data["name"],
        template_data["description"][:50] + "..." if len(template_data["description"]) > 50 else template_data["description"],
        template_data["author"],
        template_data["version"],
        str(template_data["downloads"]),
        f"{template_data['rating']:.1f}⭐" if template_data['rating'] > 0 else "N/A",
        "Custom"
    )
    
    console.print(templates_table)


async def demo_template_validation():
    """Demo template validation features."""
    console.print("\n[bold cyan]✅ Template Validation Demo[/bold cyan]")
    
    # Show validation of a good template
    good_template = """# My Awesome Project
# Generated by gign

# Dependencies
node_modules/
vendor/

# Build outputs
dist/
build/
*.egg-info/

# Logs
*.log
logs/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
"""
    
    console.print("🔍 Validating template content...")
    console.print("✅ Template content is valid!")
    
    # Show statistics
    lines = good_template.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    comment_lines = [line for line in lines if line.strip().startswith('#')]
    pattern_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    
    console.print(f"\n📊 Template Statistics:")
    console.print(f"  Total lines: {len(lines)}")
    console.print(f"  Non-empty lines: {len(non_empty_lines)}")
    console.print(f"  Comment lines: {len(comment_lines)}")
    console.print(f"  Pattern lines: {len(pattern_lines)}")
    console.print(f"  File size: {len(good_template.encode())} bytes")
    
    # Show validation of a bad template
    bad_template = """# Bad Template
node_modules/
/node  # Invalid absolute path without trailing slash
**cache  # Invalid ** pattern without trailing slash
"""
    
    console.print("\n🔍 Validating problematic template...")
    console.print("[red]❌ Template content validation failed:[/red]")
    console.print("  ❌ Line 3: Invalid pattern '/node' - absolute paths should end with '/'")
    console.print("  ❌ Line 4: Invalid pattern '**cache' - '**' should be followed by '/'")


async def demo_usage_examples():
    """Show usage examples for new commands."""
    console.print("\n[bold cyan]💡 Usage Examples[/bold cyan]")
    
    examples = [
        ("AI Recommendations", "gign ai-recommendations --path ./my-project --output recommendations.json"),
        ("Analyze GitHub Repo", "gign analyze-repo --repo https://github.com/user/repo --output analysis.json"),
        ("Analyze Multiple Repos", "gign analyze-repos --repos 'https://github.com/user/repo1,https://github.com/user/repo2'"),
        ("Sync to GitHub", "gign sync-to-github --repo https://github.com/user/repo --message 'Update .gitignore'"),
        ("Create Advanced Template", "gign create-advanced-template --name my-template --description 'My awesome template' --content '*.log' --tags 'custom,web' --technologies 'node,python'"),
        ("List Advanced Templates", "gign list-advanced-templates --search web --tags custom"),
        ("Export Template", "gign export-template --name my-template --output template.json"),
        ("Import Template", "gign import-template --file template.json"),
        ("Browse Marketplace", "gign marketplace --category web --trending"),
        ("Download Template", "gign download-template --name fullstack-web"),
        ("Validate Template", "gign validate-template --file .gitignore"),
    ]
    
    table = Table(title="💡 New Command Examples")
    table.add_column("Feature", style="cyan")
    table.add_column("Command", style="green")
    
    for feature, command in examples:
        table.add_row(feature, command)
    
    console.print(table)


async def main():
    """Run the complete demo."""
    print_demo_header()
    
    await demo_ai_recommendations()
    await demo_github_integration()
    await demo_template_marketplace()
    await demo_advanced_templates()
    await demo_template_validation()
    await demo_usage_examples()
    
    console.print("\n[bold green]🎉 Demo completed![/bold green]")
    console.print("\n[dim]These features are now available in gign v1.1.0[/dim]")


if __name__ == "__main__":
    asyncio.run(main()) 