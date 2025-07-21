"""Main CLI interface for gitignore-gen."""

import asyncio
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .core import GitignoreGenerator
from .ai_recommendations import ai_engine, community_insights
from .github_integration import github_integration, repository_sync
from .template_manager import template_manager, template_marketplace, template_validator
# Detector compatibility wrapper
try:
    from .detector import TechnologyDetector as _RealDetector
except ImportError:
    from .detector import AdvancedTechnologyDetector as _RealDetector

class TechnologyDetector:
    def __init__(self, *args, **kwargs):
        self._detector = _RealDetector(*args, **kwargs)
    async def detect(self, path):
        if hasattr(self._detector, 'detect'):
            return await self._detector.detect(path)
        elif hasattr(self._detector, 'detect_advanced'):
            result = await self._detector.detect_advanced(path)
            if isinstance(result, dict) and 'technologies' in result:
                return list(result['technologies'].keys())
            return []
        else:
            raise NotImplementedError('No detect or detect_advanced method found')
from .exceptions import GitignoreGenError
from .utils import setup_logging

console = Console()


def print_banner() -> None:
    """Print the application banner."""
    banner = """
[bold blue]✨ gign[/bold blue] - [italic]Magical .gitignore generation[/italic]
[dim]Automatically detect and generate perfect .gitignore files for your project[/dim]
    """
    console.print(Panel(banner, border_style="blue"))


@click.group(invoke_without_command=True)
@click.option(
    "--verbose", "-v", is_flag=True, help="Enable verbose output"
)
@click.option(
    "--quiet", "-q", is_flag=True, help="Suppress all output except errors"
)
@click.option(
    "--dry-run", is_flag=True, help="Preview changes without applying them"
)
@click.option(
    "--interactive", "-i", is_flag=True, help="Enable interactive mode"
)
@click.option(
    "--backup", is_flag=True, help="Create backup of existing .gitignore"
)
@click.option(
    "--security", is_flag=True, help="Add common security patterns"
)
@click.option(
    "--monorepo", is_flag=True, help="Generate per-directory .gitignore files"
)
@click.option(
    "--auto-fix", is_flag=True, help="Automatically remove files that should be ignored from git"
)
@click.option(
    "--watch", is_flag=True, help="Watch for file changes and auto-update .gitignore"
)
@click.option(
    "--export", type=click.Path(), help="Export current .gitignore configuration"
)
@click.option(
    "--import", "import_config", type=click.Path(), help="Import .gitignore configuration"
)
@click.option(
    "--custom-templates", type=click.Path(), help="Path to custom templates directory"
)
@click.option(
    "--force", is_flag=True, help="Force overwrite existing .gitignore"
)
@click.option(
    "--minimal", is_flag=True, help="Generate minimal .gitignore with only essential patterns"
)
@click.option(
    "--strict", is_flag=True, help="Use strict pattern matching for better accuracy"
)
@click.pass_context
def cli(
    ctx: click.Context,
    verbose: bool,
    quiet: bool,
    dry_run: bool,
    interactive: bool,
    backup: bool,
    security: bool,
    monorepo: bool,
    auto_fix: bool,
    watch: bool,
    export: Optional[str],
    import_config: Optional[str],
    custom_templates: Optional[str],
    force: bool,
    minimal: bool,
    strict: bool,
) -> None:
    """A magical CLI tool that automatically generates and manages .gitignore files."""
    if ctx.invoked_subcommand is not None:
        return

    # Setup logging
    setup_logging(verbose=verbose, quiet=quiet)

    if not quiet:
        print_banner()

    # Run the main generation process
    asyncio.run(
        generate_gitignore(
            dry_run=dry_run,
            interactive=interactive,
            backup=backup,
            security=security,
            monorepo=monorepo,
            auto_fix=auto_fix,
            watch=watch,
            export=export,
            import_config=import_config,
            custom_templates=custom_templates,
            force=force,
            minimal=minimal,
            strict=strict,
        )
    )


@cli.command()
@click.option(
    "--template", "-t", help="Specific template to use (e.g., python,node)"
)
@click.option(
    "--output", "-o", type=click.Path(), help="Output file path"
)
def templates(template: Optional[str], output: Optional[str]) -> None:
    """List available templates or show specific template content."""
    if template:
        show_template(template, output)
    else:
        list_templates()


@cli.command()
@click.option(
    "--path", "-p", type=click.Path(exists=True), help="Path to scan"
)
def scan(path: Optional[str]) -> None:
    """Scan directory and detect technologies in use."""
    scan_path = Path(path) if path else Path.cwd()
    asyncio.run(detect_technologies(scan_path))


@cli.command()
def version() -> None:
    """Show version information."""
    from . import __version__
    
    console.print(f"[bold blue]gign[/bold blue] version [green]{__version__}[/green]")


@cli.command()
@click.option("--path", "-p", type=click.Path(exists=True), help="Path to analyze")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def analyze(path: Optional[str], output: Optional[str]) -> None:
    """Analyze project structure and generate detailed report."""
    analyze_path = Path(path) if path else Path.cwd()
    asyncio.run(analyze_project(analyze_path, output))


@cli.command()
@click.option("--template", "-t", required=True, help="Template name to create")
@click.option("--content", "-c", help="Template content (or use --file)")
@click.option("--file", "-f", type=click.Path(exists=True), help="File containing template content")
def create_template(template: str, content: Optional[str], file: Optional[str]) -> None:
    """Create a custom template."""
    if not content and not file:
        raise click.UsageError("Either --content or --file must be provided")
    
    if file:
        content = Path(file).read_text()
    
    asyncio.run(create_custom_template(template, content or ""))


@cli.command()
@click.option("--path", "-p", type=click.Path(exists=True), help="Path to clean")
@click.option("--dry-run", is_flag=True, help="Preview what would be cleaned")
def clean(path: Optional[str], dry_run: bool) -> None:
    """Clean up files that should be ignored from git tracking."""
    clean_path = Path(path) if path else Path.cwd()
    asyncio.run(clean_ignored_files(clean_path, dry_run))


@cli.command()
@click.option("--path", "-p", type=click.Path(exists=True), help="Path to watch")
@click.option("--interval", "-i", default=5, help="Check interval in seconds")
def watch(path: Optional[str], interval: int) -> None:
    """Watch for file changes and auto-update .gitignore."""
    watch_path = Path(path) if path else Path.cwd()
    asyncio.run(watch_directory(watch_path, interval))


@cli.command()
@click.option("--path", "-p", type=click.Path(exists=True), help="Path to auto-fix")
@click.option("--dry-run", is_flag=True, help="Preview what would be auto-fixed")
def auto_fix(path: Optional[str], dry_run: bool) -> None:
    """Automatically remove files that should be ignored from git tracking."""
    auto_fix_path = Path(path) if path else Path.cwd()
    asyncio.run(run_auto_fix(auto_fix_path, dry_run))


@cli.command()
@click.option("--path", "-p", type=click.Path(exists=True), help="Project path")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output config file (default: .gitignore-gen.json)")
def export_config(path: Optional[str], output: Optional[str]) -> None:
    """Export .gitignore and detected technologies to a JSON config file."""
    export_path = Path(path) if path else Path.cwd()
    config_file = Path(output) if output else (export_path / ".gitignore-gen.json")
    asyncio.run(run_export_config(export_path, config_file))

@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True), required=True, help="Config file to import")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output .gitignore file (default: .gitignore)")
def import_config(config: str, output: Optional[str]) -> None:
    """Import a .gitignore-gen config and regenerate .gitignore."""
    config_file = Path(config)
    output_file = Path(output) if output else (config_file.parent / ".gitignore")
    asyncio.run(run_import_config(config_file, output_file))


async def run_export_config(project_path: Path, config_file: Path) -> None:
    detector = TechnologyDetector()
    technologies = await detector.detect(project_path)
    gitignore_path = project_path / ".gitignore"
    content = gitignore_path.read_text() if gitignore_path.exists() else ""
    import json, time
    config = {
        "project_path": str(project_path),
        "technologies": technologies,
        "content": content,
        "exported_at": time.time(),
    }
    config_file.write_text(json.dumps(config, indent=2))
    console.print(f"[green]✅ Exported config to: {config_file}[/green]")

async def run_import_config(config_file: Path, output_file: Path) -> None:
    import json
    config = json.loads(config_file.read_text())
    content = config.get("content")
    if not content and "technologies" in config:
        # Regenerate from techs if content missing
        async with GitignoreGenerator() as generator:
            content = await generator.generate(config["technologies"])
    output_file.write_text(content)
    console.print(f"[green]✅ Imported .gitignore to: {output_file}[/green]")


async def generate_gitignore(
    dry_run: bool = False,
    interactive: bool = False,
    backup: bool = False,
    security: bool = False,
    monorepo: bool = False,
    auto_fix: bool = False,
    watch: bool = False,
    export: Optional[str] = None,
    import_config: Optional[str] = None,
    custom_templates: Optional[str] = None,
    force: bool = False,
    minimal: bool = False,
    strict: bool = False,
) -> None:
    """Main generation process."""
    try:
        current_dir = Path.cwd()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Detect technologies
            task = progress.add_task("🔍 Scanning project...", total=None)
            detector = TechnologyDetector()
            technologies = await detector.detect(current_dir)
            progress.update(task, completed=True)
            
            if not technologies:
                console.print("[yellow]⚠️  No technologies detected in current directory[/yellow]")
                if interactive:
                    if not Confirm.ask("Continue with basic template?"):
                        return
                else:
                    console.print("[dim]Use --interactive to choose templates manually[/dim]")
                    return

            # Show detected technologies
            show_detected_technologies(technologies)

            # Show interactive recommendations
            if interactive:
                security_enabled, minimal_mode, strict_mode = await show_interactive_recommendations(
                    current_dir, technologies, security, minimal, strict
                )
            else:
                security_enabled, minimal_mode, strict_mode = security, minimal, strict

            # Generate gitignore
            task = progress.add_task("🚀 Generating .gitignore...", total=None)
            generator = GitignoreGenerator()
            
            if interactive:
                selected_techs = await interactive_template_selection(technologies)
            else:
                selected_techs = technologies

            gitignore_content = await generator.generate(
                selected_techs,
                security_patterns=security_enabled,
                monorepo=monorepo,
                minimal=minimal_mode,
                strict=strict_mode,
            )
            progress.update(task, completed=True)

            # Show preview
            if dry_run or interactive:
                show_preview(gitignore_content)
                
                if interactive and not Confirm.ask("Apply this .gitignore?"):
                    console.print("[yellow]Operation cancelled[/yellow]")
                    return

            if not dry_run:
                # Apply changes
                task = progress.add_task("💾 Saving .gitignore...", total=None)
                await generator.save_gitignore(
                    current_dir / ".gitignore",
                    gitignore_content,
                    backup=backup,
                )
                progress.update(task, completed=True)

                console.print("[green]✅ .gitignore generated successfully![/green]")

                if auto_fix:
                    await run_auto_fix(current_dir, dry_run)

    except GitignoreGenError as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        console.print_exception()
        sys.exit(1)


def show_detected_technologies(technologies: list[str]) -> None:
    """Display detected technologies in a table."""
    table = Table(title="🔍 Detected Technologies")
    table.add_column("Technology", style="cyan", no_wrap=True)
    table.add_column("Confidence", style="green")
    
    for tech in technologies:
        table.add_row(tech, "High")
    
    console.print(table)


def show_preview(content: str) -> None:
    """Show a preview of the generated .gitignore content."""
    console.print("\n[bold]📋 Generated .gitignore Preview:[/bold]")
    console.print(Panel(content, border_style="green"))


async def interactive_template_selection(technologies: list[str]) -> list[str]:
    """Interactive template selection."""
    console.print("\n[bold]🎯 Template Selection:[/bold]")
    
    selected = []
    for tech in technologies:
        if Confirm.ask(f"Include [cyan]{tech}[/cyan] template?"):
            selected.append(tech)
    
    # Allow adding custom templates
    while True:
        custom = Prompt.ask(
            "Add custom template (or press Enter to finish)",
            default=""
        )
        if not custom:
            break
        selected.append(custom)
    
    return selected


async def detect_technologies(path: Path) -> None:
    """Detect technologies in the given path."""
    detector = TechnologyDetector()
    technologies = await detector.detect(path)
    
    if technologies:
        console.print(f"\n[bold]🔍 Technologies detected in {path}:[/bold]")
        for tech in technologies:
            console.print(f"  • [cyan]{tech}[/cyan]")
    else:
        console.print(f"\n[yellow]No technologies detected in {path}[/yellow]")


@cli.command()
@click.option("--template", "-t", help="Template name to search for")
@click.option("--custom-only", is_flag=True, help="Show only custom templates")
def list_templates(template: Optional[str], custom_only: bool) -> None:
    """List available templates (built-in and custom)."""
    asyncio.run(run_list_templates(template, custom_only))

@cli.command()
@click.option("--template", "-t", required=True, help="Template name to delete")
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
def delete_template(template: str, force: bool) -> None:
    """Delete a custom template."""
    asyncio.run(run_delete_template(template, force))

@cli.command()
@click.option("--template", "-t", required=True, help="Template name to update")
@click.option("--content", "-c", help="New template content")
@click.option("--file", "-f", type=click.Path(exists=True), help="File containing new template content")
def update_template(template: str, content: Optional[str], file: Optional[str]) -> None:
    """Update an existing custom template."""
    if not content and not file:
        raise click.UsageError("Either --content or --file must be provided")
    if file:
        content = Path(file).read_text()
    asyncio.run(run_update_template(template, content or ""))

@cli.command()
@click.option("--query", "-q", required=True, help="Search query")
@click.option("--custom-only", is_flag=True, help="Search only custom templates")
def search_templates(query: str, custom_only: bool) -> None:
    """Search for templates by name or content."""
    asyncio.run(run_search_templates(query, custom_only))


@cli.command()
@click.option("--path", "-p", type=click.Path(exists=True), help="Path to scan")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", "-f", type=click.Choice(["json", "yaml", "csv"]), default="json", help="Output format")
def scan_dependencies(path: Optional[str], output: Optional[str], format: str) -> None:
    """Scan project dependencies and generate detailed report."""
    scan_path = Path(path) if path else Path.cwd()
    asyncio.run(scan_project_dependencies(scan_path, output, format))


@cli.command()
@click.option("--path", "-p", type=click.Path(exists=True), help="Path to analyze")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--threshold", "-t", default=10, help="File size threshold in MB")
def performance_insights(path: Optional[str], output: Optional[str], threshold: int) -> None:
    """Generate performance insights and optimization recommendations."""
    analyze_path = Path(path) if path else Path.cwd()
    asyncio.run(generate_performance_insights(analyze_path, output, threshold))


@cli.command()
@click.option("--path", "-p", type=click.Path(exists=True), help="Monorepo root path")
@click.option("--strategy", "-s", type=click.Choice(["flat", "nested", "hybrid"]), default="hybrid", help="Structure strategy")
@click.option("--shared", is_flag=True, help="Generate shared .gitignore for common patterns")
@click.option("--per-service", is_flag=True, help="Generate per-service .gitignore files")
def monorepo_setup(path: Optional[str], strategy: str, shared: bool, per_service: bool) -> None:
    """Set up comprehensive .gitignore structure for monorepos."""
    monorepo_path = Path(path) if path else Path.cwd()
    asyncio.run(setup_monorepo_gitignore(monorepo_path, strategy, shared, per_service))


@cli.command()
@click.option("--path", "-p", type=click.Path(exists=True), help="Path to scan")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--severity", "-s", type=click.Choice(["low", "medium", "high", "all"]), default="all", help="Minimum severity level")
def security_scan(path: Optional[str], output: Optional[str], severity: str) -> None:
    """Perform comprehensive security scan and generate report."""
    scan_path = Path(path) if path else Path.cwd()
    asyncio.run(perform_security_scan(scan_path, output, severity))


@cli.command()
@click.option("--path", "-p", type=click.Path(exists=True), help="Path to optimize")
@click.option("--dry-run", is_flag=True, help="Preview optimizations without applying")
@click.option("--aggressive", is_flag=True, help="Apply aggressive optimizations")
def optimize(path: Optional[str], dry_run: bool, aggressive: bool) -> None:
    """Optimize existing .gitignore file for better performance."""
    optimize_path = Path(path) if path else Path.cwd()
    asyncio.run(optimize_gitignore(optimize_path, dry_run, aggressive))

@cli.command()
@click.option("--path", "-p", type=click.Path(exists=True), help="Path to analyze")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def ai_recommendations(path: Optional[str], output: Optional[str]) -> None:
    """Get AI-powered recommendations for .gitignore optimization."""
    analyze_path = Path(path) if path else Path.cwd()
    asyncio.run(run_ai_recommendations(analyze_path, output))

@cli.command()
@click.option("--repo", "-r", required=True, help="GitHub repository URL")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def analyze_repo(repo: str, output: Optional[str]) -> None:
    """Analyze a GitHub repository and extract .gitignore patterns."""
    asyncio.run(run_analyze_repo(repo, output))

@cli.command()
@click.option("--repos", "-r", required=True, help="Comma-separated list of GitHub repository URLs")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def analyze_repos(repos: str, output: Optional[str]) -> None:
    """Analyze multiple GitHub repositories and find common patterns."""
    repo_urls = [url.strip() for url in repos.split(",")]
    asyncio.run(run_analyze_repos(repo_urls, output))

@cli.command()
@click.option("--path", "-p", type=click.Path(exists=True), help="Local project path")
@click.option("--repo", "-r", required=True, help="GitHub repository URL")
@click.option("--message", "-m", help="Commit message")
def sync_to_github(path: Optional[str], repo: str, message: Optional[str]) -> None:
    """Sync local .gitignore to GitHub repository."""
    local_path = Path(path) if path else Path.cwd()
    asyncio.run(run_sync_to_github(local_path, repo, message))

@cli.command()
@click.option("--name", "-n", required=True, help="Template name")
@click.option("--description", "-d", required=True, help="Template description")
@click.option("--content", "-c", help="Template content")
@click.option("--file", "-f", type=click.Path(exists=True), help="File containing template content")
@click.option("--author", "-a", default="user", help="Template author")
@click.option("--tags", "-t", help="Comma-separated tags")
@click.option("--technologies", "-tech", help="Comma-separated technologies")
def create_advanced_template(
    name: str, 
    description: str, 
    content: Optional[str], 
    file: Optional[str],
    author: str,
    tags: Optional[str],
    technologies: Optional[str]
) -> None:
    """Create an advanced template with metadata."""
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    tech_list = [t.strip() for t in technologies.split(",")] if technologies else []
    
    if file:
        with open(file, 'r') as f:
            content = f.read()
    elif not content:
        raise click.UsageError("Either --content or --file must be provided")
    
    asyncio.run(run_create_advanced_template(name, description, content, author, tag_list, tech_list))

@cli.command()
@click.option("--search", "-s", help="Search query")
@click.option("--tags", "-t", help="Comma-separated tags to filter by")
@click.option("--technologies", "-tech", help="Comma-separated technologies to filter by")
@click.option("--custom-only", is_flag=True, help="Show only custom templates")
def list_advanced_templates(
    search: Optional[str],
    tags: Optional[str],
    technologies: Optional[str],
    custom_only: bool
) -> None:
    """List advanced templates with filtering options."""
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    tech_list = [t.strip() for t in technologies.split(",")] if technologies else None
    
    asyncio.run(run_list_advanced_templates(search, tag_list, tech_list, custom_only))

@cli.command()
@click.option("--name", "-n", required=True, help="Template name to export")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def export_template(name: str, output: Optional[str]) -> None:
    """Export a template to a file."""
    output_path = Path(output) if output else Path(f"{name}.json")
    asyncio.run(run_export_template(name, output_path))

@cli.command()
@click.option("--file", "-f", type=click.Path(exists=True), required=True, help="Template file to import")
def import_template(file: str) -> None:
    """Import a template from a file."""
    asyncio.run(run_import_template(Path(file)))

@cli.command()
@click.option("--category", "-c", help="Category to filter by")
@click.option("--language", "-l", help="Language to filter by")
@click.option("--trending", is_flag=True, help="Show trending templates")
def marketplace(category: Optional[str], language: Optional[str], trending: bool) -> None:
    """Discover templates from the marketplace."""
    asyncio.run(run_marketplace(category, language, trending))

@cli.command()
@click.option("--name", "-n", required=True, help="Template name to download")
def download_template(name: str) -> None:
    """Download a template from the marketplace."""
    asyncio.run(run_download_template(name))

@cli.command()
@click.option("--content", "-c", help="Content to validate")
@click.option("--file", "-f", type=click.Path(exists=True), help="File to validate")
def validate_template(content: Optional[str], file: Optional[str]) -> None:
    """Validate template content and structure."""
    if file:
        with open(file, 'r') as f:
            content = f.read()
    elif not content:
        raise click.UsageError("Either --content or --file must be provided")
    
    asyncio.run(run_validate_template(content))

async def run_list_templates(search: Optional[str], custom_only: bool) -> None:
    """List available templates."""
    from .utils import get_cache_dir
    templates_dir = get_cache_dir() / "custom_templates"
    
    # Get custom templates
    custom_templates = []
    if templates_dir.exists():
        for template_file in templates_dir.glob("*.gitignore"):
            custom_templates.append(template_file.stem)
    
    # Get built-in templates (from gitignore.io)
    built_in_templates = [
        "python", "node", "java", "go", "rust", "php", "ruby", "csharp", "swift",
        "kotlin", "scala", "dart", "flutter", "react", "vue", "angular", "svelte",
        "docker", "kubernetes", "terraform", "ansible", "jenkins", "github", "gitlab",
        "vscode", "intellij", "eclipse", "vim", "emacs", "macos", "windows", "linux"
    ]
    
    if search:
        custom_templates = [t for t in custom_templates if search.lower() in t.lower()]
        built_in_templates = [t for t in built_in_templates if search.lower() in t.lower()]
    
    if custom_only:
        templates_to_show = custom_templates
        console.print("[bold]📚 Custom Templates:[/bold]")
    else:
        templates_to_show = custom_templates + built_in_templates
        console.print("[bold]📚 Available Templates:[/bold]")
        if custom_templates:
            console.print(f"[cyan]Custom ({len(custom_templates)}):[/cyan] {', '.join(custom_templates)}")
        console.print(f"[blue]Built-in ({len(built_in_templates)}):[/blue] {', '.join(built_in_templates)}")
    
    if not templates_to_show:
        console.print("[yellow]No templates found.[/yellow]")
    else:
        for template in sorted(templates_to_show):
            marker = "[green]✓[/green]" if template in custom_templates else "[blue]●[/blue]"
            console.print(f"  {marker} {template}")

async def run_delete_template(template_name: str, force: bool) -> None:
    """Delete a custom template."""
    from .utils import get_cache_dir
    templates_dir = get_cache_dir() / "custom_templates"
    template_file = templates_dir / f"{template_name}.gitignore"
    
    if not template_file.exists():
        console.print(f"[red]❌ Template '{template_name}' not found.[/red]")
        return
    
    if not force and not Confirm.ask(f"Delete template '{template_name}'?"):
        console.print("[yellow]Operation cancelled.[/yellow]")
        return
    
    template_file.unlink()
    console.print(f"[green]✅ Template '{template_name}' deleted successfully![/green]")

async def run_update_template(template_name: str, content: str) -> None:
    """Update an existing custom template."""
    from .utils import get_cache_dir
    templates_dir = get_cache_dir() / "custom_templates"
    template_file = templates_dir / f"{template_name}.gitignore"
    
    if not template_file.exists():
        console.print(f"[red]❌ Template '{template_name}' not found. Use create-template instead.[/red]")
        return
    
    template_file.write_text(content)
    console.print(f"[green]✅ Template '{template_name}' updated successfully![/green]")

async def run_search_templates(query: str, custom_only: bool) -> None:
    """Search for templates by name or content."""
    from .utils import get_cache_dir
    templates_dir = get_cache_dir() / "custom_templates"
    
    results = []
    
    # Search custom templates
    if templates_dir.exists():
        for template_file in templates_dir.glob("*.gitignore"):
            template_name = template_file.stem
            template_content = template_file.read_text()
            
            if (query.lower() in template_name.lower() or 
                query.lower() in template_content.lower()):
                results.append({
                    "name": template_name,
                    "type": "custom",
                    "file": template_file
                })
    
    # Search built-in templates (if not custom_only)
    if not custom_only:
        built_in_templates = [
            "python", "node", "java", "go", "rust", "php", "ruby", "csharp", "swift",
            "kotlin", "scala", "dart", "flutter", "react", "vue", "angular", "svelte",
            "docker", "kubernetes", "terraform", "ansible", "jenkins", "github", "gitlab",
            "vscode", "intellij", "eclipse", "vim", "emacs", "macos", "windows", "linux"
        ]
        
        for template_name in built_in_templates:
            if query.lower() in template_name.lower():
                results.append({
                    "name": template_name,
                    "type": "built-in",
                    "file": None
                })
    
    if not results:
        console.print(f"[yellow]No templates found matching '{query}'.[/yellow]")
    else:
        console.print(f"[bold]🔍 Search Results for '{query}':[/bold]")
        for result in results:
            marker = "[green]✓[/green]" if result["type"] == "custom" else "[blue]●[/blue]"
            console.print(f"  {marker} {result['name']} ({result['type']})")


async def analyze_project(path: Path, output: Optional[str]) -> None:
    """Analyze project structure and generate detailed report."""
    try:
        console.print(f"[bold]🔍 Analyzing project: {path}[/bold]")
        
        # Use advanced detector for comprehensive analysis
        from .detector import AdvancedTechnologyDetector
        detector = AdvancedTechnologyDetector()
        analysis = await detector.detect_advanced(path)
        
        if not analysis:
            console.print("[red]❌ Analysis failed[/red]")
            return
        
        # Generate comprehensive report
        report = {
            "project_path": str(path),
            "analysis_date": asyncio.get_event_loop().time(),
            "technologies": analysis.get("technologies", {}),
            "dependencies": analysis.get("dependencies", {}),
            "structure": analysis.get("structure", {}),
            "statistics": analysis.get("statistics", {}),
            "security": analysis.get("security", {}),
            "performance": analysis.get("performance", {}),
            "recommendations": analysis.get("recommendations", [])
        }
        
        # Display results in rich format
        console.print("\n[bold]📊 Project Analysis Results[/bold]")
        
        # Technologies
        if report["technologies"]:
            console.print("\n[bold cyan]🔧 Detected Technologies:[/bold cyan]")
            tech_table = Table(show_header=True, header_style="bold magenta")
            tech_table.add_column("Technology", style="cyan")
            tech_table.add_column("Confidence", style="green")
            for tech, confidence in report["technologies"].items():
                confidence_str = f"{confidence:.1%}" if isinstance(confidence, float) else str(confidence)
                tech_table.add_row(tech, confidence_str)
            console.print(tech_table)
        
        # Dependencies
        if report["dependencies"]:
            console.print("\n[bold cyan]📦 Dependencies:[/bold cyan]")
            for tech, dep_info in report["dependencies"].items():
                console.print(f"  • [green]{tech}[/green]: {dep_info.get('file', 'Unknown')}")
        
        # Structure
        structure = report["structure"]
        if structure:
            console.print(f"\n[bold cyan]🏗️ Project Structure:[/bold cyan]")
            console.print(f"  • Type: [yellow]{structure.get('type', 'Unknown')}[/yellow]")
            console.print(f"  • Depth: [yellow]{structure.get('depth', 0)}[/yellow] levels")
            if structure.get("indicators"):
                console.print(f"  • Indicators: [yellow]{', '.join(structure['indicators'])}[/yellow]")
        
        # Statistics
        stats = report["statistics"]
        if stats:
            console.print(f"\n[bold cyan]📈 File Statistics:[/bold cyan]")
            console.print(f"  • Total files: [yellow]{stats.get('total_files', 0)}[/yellow]")
            console.print(f"  • Total directories: [yellow]{stats.get('total_dirs', 0)}[/yellow]")
            
            if stats.get("file_types"):
                console.print(f"  • File types: [yellow]{len(stats['file_types'])}[/yellow] different extensions")
                top_types = sorted(stats["file_types"].items(), key=lambda x: x[1], reverse=True)[:5]
                for ext, count in top_types:
                    console.print(f"    - {ext}: {count} files")
        
        # Security
        security = report["security"]
        if security:
            console.print(f"\n[bold cyan]🔒 Security Analysis:[/bold cyan]")
            if security.get("sensitive_files"):
                console.print(f"  • [red]⚠️ Sensitive files found: {len(security['sensitive_files'])}[/red]")
                for file_path in security["sensitive_files"][:3]:  # Show first 3
                    console.print(f"    - {file_path}")
                if len(security["sensitive_files"]) > 3:
                    console.print(f"    ... and {len(security['sensitive_files']) - 3} more")
            else:
                console.print("  • [green]✅ No obvious security concerns detected[/green]")
            
            if security.get("recommendations"):
                console.print("  • [yellow]Recommendations:[/yellow]")
                for rec in security["recommendations"]:
                    console.print(f"    - {rec}")
        
        # Performance
        performance = report["performance"]
        if performance:
            console.print(f"\n[bold cyan]⚡ Performance Analysis:[/bold cyan]")
            if performance.get("large_files"):
                console.print(f"  • [yellow]⚠️ Large files: {len(performance['large_files'])}[/yellow]")
                for file_info in performance["large_files"][:3]:  # Show first 3
                    size_mb = file_info["size"] / (1024 * 1024)
                    console.print(f"    - {file_info['path']} ({size_mb:.1f} MB)")
            
            if performance.get("many_files"):
                console.print("  • [yellow]⚠️ Many files detected - consider .gitignore optimization[/yellow]")
            
            if performance.get("deep_nesting"):
                console.print("  • [yellow]⚠️ Deep directory nesting detected[/yellow]")
            
            if performance.get("recommendations"):
                console.print("  • [yellow]Recommendations:[/yellow]")
                for rec in performance["recommendations"]:
                    console.print(f"    - {rec}")
        
        # Recommendations
        if report["recommendations"]:
            console.print(f"\n[bold cyan]💡 Recommendations:[/bold cyan]")
            for i, rec in enumerate(report["recommendations"], 1):
                console.print(f"  {i}. {rec}")
        
        # Save to file if requested
        if output:
            import json
            Path(output).write_text(json.dumps(report, indent=2, default=str))
            console.print(f"\n[green]✅ Report saved to: {output}[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Analysis failed: {e}[/red]")
        console.print_exception()


async def create_custom_template(template_name: str, content: str) -> None:
    """Create a custom template."""
    try:
        from .utils import get_cache_dir
        templates_dir = get_cache_dir() / "custom_templates"
        templates_dir.mkdir(exist_ok=True)
        
        template_file = templates_dir / f"{template_name}.gitignore"
        template_file.write_text(content)
        
        console.print(f"[green]✅ Custom template '{template_name}' created successfully![/green]")
        console.print(f"[dim]Location: {template_file}[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to create template: {e}[/red]")


async def clean_ignored_files(path: Path, dry_run: bool) -> None:
    """Clean up files that should be ignored from git tracking."""
    try:
        console.print(f"[bold]🧹 Cleaning ignored files in: {path}[/bold]")
        
        async with GitignoreGenerator() as generator:
            ignored_files = await generator.check_git_status(path)
            
            if not ignored_files:
                console.print("[green]✅ No files to clean![/green]")
                return
            
            console.print(f"[yellow]Found {len(ignored_files)} files that should be ignored:[/yellow]")
            for file_path in ignored_files:
                console.print(f"  - {file_path}")
            
            if dry_run:
                console.print("[dim]Dry run mode - no files will be removed[/dim]")
                return
            
            if Confirm.ask("Remove these files from git tracking?"):
                import git
                repo = git.Repo(path)
                
                for file_path in ignored_files:
                    try:
                        repo.index.remove([file_path], working_tree=True)
                        console.print(f"[green]✅ Removed: {file_path}[/green]")
                    except Exception as e:
                        console.print(f"[red]❌ Failed to remove {file_path}: {e}[/red]")
                
                console.print("[green]✅ Cleanup completed![/green]")
                
    except Exception as e:
        console.print(f"[red]❌ Cleanup failed: {e}[/red]")


class _WatchHandler(FileSystemEventHandler):
    def __init__(self, path, interval, callback):
        super().__init__()
        self.path = path
        self.interval = interval
        self.callback = callback
        self._last_event = 0

    def on_any_event(self, event):
        import time
        now = time.time()
        # Debounce: only trigger if enough time has passed
        if now - self._last_event > self.interval:
            self._last_event = now
            asyncio.run(self.callback())

async def watch_directory(path: Path, interval: int) -> None:
    """Watch for file changes and auto-update .gitignore using watchdog."""
    try:
        console.print(f"[bold]👀 Watching directory: {path}[/bold]")
        console.print(f"[dim]Check interval: {interval} seconds[/dim]")
        console.print("[dim]Press Ctrl+C to stop[/dim]")

        last_technologies = set()
        is_scanning = False

        async def scan_and_update():
            nonlocal last_technologies, is_scanning
            if is_scanning:
                return
            is_scanning = True
            try:
                detector = TechnologyDetector()
                current_technologies = set(await detector.detect(path))
                if current_technologies != last_technologies:
                    console.print(f"[yellow]🔄 Technologies changed![/yellow]")
                    console.print(f"New technologies: {', '.join(current_technologies - last_technologies)}")
                    async with GitignoreGenerator() as generator:
                        content = await generator.generate(list(current_technologies))
                        await generator.save_gitignore(path / ".gitignore", content, backup=True)
                    console.print("[green]✅ .gitignore updated![/green]")
                    last_technologies = current_technologies
            finally:
                is_scanning = False

        # Initial scan
        await scan_and_update()

        event_handler = _WatchHandler(path, interval, scan_and_update)
        observer = Observer()
        observer.schedule(event_handler, str(path), recursive=True)
        observer.start()
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            console.print("\n[green]👋 Watching stopped[/green]")
        observer.join()
    except Exception as e:
        console.print(f"[red]❌ Watch failed: {e}[/red]")


async def run_auto_fix(path: Path, dry_run: bool = False) -> None:
    """Run auto-fix to remove tracked files that should be ignored."""
    from gitignore_gen.core import GitignoreGenerator
    console.print(f"[bold]🛠️ Auto-fixing tracked files that should be ignored in: {path}[/bold]")
    async with GitignoreGenerator() as generator:
        ignored_files = await generator.check_git_status(path)
        if not ignored_files:
            console.print("[green]✅ No files to auto-fix![/green]")
            return
        console.print(f"[yellow]Found {len(ignored_files)} files that should be ignored:[/yellow]")
        for file_path in ignored_files:
            console.print(f"  - {file_path}")
        if dry_run:
            console.print("[dim]Dry run mode - no files will be removed[/dim]")
            return
        if Confirm.ask("Remove these files from git tracking?"):
            removed = await generator.auto_fix_ignored_files(path)
            for file_path in removed:
                console.print(f"[green]✅ Removed: {file_path}[/green]")
            console.print("[green]✅ Auto-fix completed![/green]")
        else:
            console.print("[yellow]Operation cancelled.[/yellow]")


async def show_interactive_recommendations(
    project_path: Path, 
    technologies: List[str], 
    security_enabled: bool, 
    minimal_mode: bool, 
    strict_mode: bool
) -> tuple[bool, bool, bool]:
    """Show interactive recommendations and prompts."""
    console.print("\n[bold]💡 Interactive Recommendations[/bold]")
    
    recommendations = []
    actions = []
    
    # Technology-specific recommendations
    if "python" in technologies:
        recommendations.append("Add __pycache__/ and *.pyc to .gitignore")
        actions.append("python_cache")
    
    if "node" in technologies:
        recommendations.append("Ensure node_modules/ is in .gitignore")
        actions.append("node_modules")
    
    if "java" in technologies:
        recommendations.append("Add target/ and *.class to .gitignore")
        actions.append("java_build")
    
    # Security recommendations
    if not security_enabled:
        recommendations.append("Enable security patterns for better protection")
        actions.append("security")
    
    # Mode-specific recommendations
    if not minimal_mode and not strict_mode:
        recommendations.append("Consider --minimal for a cleaner .gitignore")
        actions.append("minimal")
    
    if not strict_mode:
        recommendations.append("Consider --strict for more precise patterns")
        actions.append("strict")
    
    # Check for potential issues
    try:
        from .detector import AdvancedTechnologyDetector
        detector = AdvancedTechnologyDetector()
        analysis = await detector.detect_advanced(project_path)
        
        if analysis.get("security", {}).get("sensitive_files"):
            sensitive_count = len(analysis["security"]["sensitive_files"])
            recommendations.append(f"⚠️ Found {sensitive_count} sensitive files - review security")
            actions.append("security_review")
        
        if analysis.get("performance", {}).get("large_files"):
            large_count = len(analysis["performance"]["large_files"])
            recommendations.append(f"⚠️ Found {large_count} large files - consider optimization")
            actions.append("performance")
        
    except Exception:
        pass  # Skip advanced analysis if it fails
    
    # Show recommendations
    if recommendations:
        console.print("\n[bold cyan]🔍 Detected Issues & Suggestions:[/bold cyan]")
        for i, rec in enumerate(recommendations, 1):
            if "⚠️" in rec:
                console.print(f"  {i}. [red]{rec}[/red]")
            else:
                console.print(f"  {i}. [yellow]{rec}[/yellow]")
        
        # Interactive prompts
        console.print("\n[bold cyan]🎯 Available Actions:[/bold cyan]")
        
        if "security" in actions and not security_enabled:
            if Confirm.ask("Enable security patterns?"):
                security_enabled = True
                console.print("[green]✅ Security patterns enabled[/green]")
        
        if "minimal" in actions:
            if Confirm.ask("Use minimal mode for cleaner .gitignore?"):
                minimal_mode = True
                console.print("[green]✅ Minimal mode enabled[/green]")
        
        if "strict" in actions:
            if Confirm.ask("Use strict mode for more precise patterns?"):
                strict_mode = True
                console.print("[green]✅ Strict mode enabled[/green]")
        
        if "security_review" in actions:
            if Confirm.ask("Review sensitive files?"):
                console.print("[yellow]📋 Use 'gitignore-gen analyze' for detailed security report[/yellow]")
        
        if "performance" in actions:
            if Confirm.ask("Generate performance report?"):
                console.print("[yellow]📋 Use 'gitignore-gen analyze' for detailed performance analysis[/yellow]")
        
        # Auto-fix suggestions
        if any(action in actions for action in ["python_cache", "node_modules", "java_build"]):
            if Confirm.ask("Auto-fix tracked files that should be ignored?"):
                console.print("[yellow]💡 Use 'gitignore-gen auto-fix' after generation[/yellow]")
        
        # Custom template suggestions
        if len(technologies) > 3:
            if Confirm.ask("Create custom template for this project?"):
                template_name = Prompt.ask("Template name", default="myproject")
                console.print(f"[yellow]💡 Use 'gitignore-gen create-template --template {template_name}'[/yellow]")
    
    else:
        console.print("[green]✅ No specific recommendations - your project looks good![/green]")
    
    # Return updated settings
    return security_enabled, minimal_mode, strict_mode


def show_template(template: str, output: Optional[str]) -> None:
    """Show content of a specific template."""
    console.print(f"[bold]📄 Template: {template}[/bold]")
    
    # Try to find custom template first
    from .utils import get_cache_dir
    templates_dir = get_cache_dir() / "custom_templates"
    template_file = templates_dir / f"{template}.gitignore"
    
    if template_file.exists():
        content = template_file.read_text()
        console.print(f"[green]Custom template found[/green]")
    else:
        # Try to fetch from gitignore.io API
        console.print(f"[blue]Built-in template[/blue]")
        console.print("[dim]Fetching from gitignore.io...[/dim]")
        # TODO: Implement API fetching
        content = f"# Template: {template}\n# Content would be fetched from gitignore.io API"
    
    if output:
        Path(output).write_text(content)
        console.print(f"[green]✅ Template content saved to: {output}[/green]")
    else:
        console.print(Panel(content, title=f"Template: {template}", border_style="green"))


def main() -> None:
    """Main entry point."""
    cli()


# New advanced feature implementations

async def scan_project_dependencies(path: Path, output: Optional[str], format: str) -> None:
    """Scan project dependencies and generate detailed report."""
    try:
        console.print(f"[bold]📦 Scanning dependencies in: {path}[/bold]")
        
        from .detector import AdvancedTechnologyDetector
        detector = AdvancedTechnologyDetector()
        analysis = await detector.detect_advanced(path)
        
        dependencies = analysis.get("dependencies", {})
        
        if not dependencies:
            console.print("[yellow]No dependency files found[/yellow]")
            return
        
        # Display results
        console.print("\n[bold cyan]📦 Detected Dependencies:[/bold cyan]")
        for tech, dep_info in dependencies.items():
            console.print(f"  • [green]{tech}[/green]: {dep_info.get('file', 'Unknown')}")
            if 'path' in dep_info:
                console.print(f"    Path: {dep_info['path']}")
            if 'size' in dep_info:
                size_kb = dep_info['size'] / 1024
                console.print(f"    Size: {size_kb:.1f} KB")
        
        # Generate report
        report = {
            "scan_path": str(path),
            "scan_date": asyncio.get_event_loop().time(),
            "dependencies": dependencies,
            "total_technologies": len(dependencies)
        }
        
        # Save to file if requested
        if output:
            if format == "json":
                import json
                Path(output).write_text(json.dumps(report, indent=2, default=str))
            elif format == "yaml":
                import yaml
                Path(output).write_text(yaml.dump(report, default_flow_style=False))
            elif format == "csv":
                import csv
                with open(output, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Technology', 'File', 'Path', 'Size (bytes)'])
                    for tech, dep_info in dependencies.items():
                        writer.writerow([
                            tech,
                            dep_info.get('file', ''),
                            dep_info.get('path', ''),
                            dep_info.get('size', 0)
                        ])
            
            console.print(f"\n[green]✅ Dependency report saved to: {output}[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Dependency scan failed: {e}[/red]")


async def generate_performance_insights(path: Path, output: Optional[str], threshold: int) -> None:
    """Generate performance insights and optimization recommendations."""
    try:
        console.print(f"[bold]⚡ Generating performance insights for: {path}[/bold]")
        
        from .detector import AdvancedTechnologyDetector
        detector = AdvancedTechnologyDetector()
        analysis = await detector.detect_advanced(path)
        
        performance = analysis.get("performance", {})
        statistics = analysis.get("statistics", {})
        
        # Display insights
        console.print("\n[bold cyan]⚡ Performance Insights:[/bold cyan]")
        
        # File statistics
        if statistics:
            console.print(f"  • Total files: [yellow]{statistics.get('total_files', 0)}[/yellow]")
            console.print(f"  • Total directories: [yellow]{statistics.get('total_dirs', 0)}[/yellow]")
            
            if statistics.get("file_types"):
                console.print(f"  • File types: [yellow]{len(statistics['file_types'])}[/yellow] different extensions")
        
        # Performance issues
        if performance.get("large_files"):
            large_files = performance["large_files"]
            console.print(f"  • [red]⚠️ Large files: {len(large_files)}[/red]")
            for file_info in large_files[:5]:  # Show first 5
                size_mb = file_info["size"] / (1024 * 1024)
                console.print(f"    - {file_info['path']} ({size_mb:.1f} MB)")
        
        if performance.get("many_files"):
            console.print("  • [yellow]⚠️ Many files detected - consider .gitignore optimization[/yellow]")
        
        if performance.get("deep_nesting"):
            console.print("  • [yellow]⚠️ Deep directory nesting detected[/yellow]")
        
        # Recommendations
        if performance.get("recommendations"):
            console.print("\n[bold cyan]💡 Optimization Recommendations:[/bold cyan]")
            for i, rec in enumerate(performance["recommendations"], 1):
                console.print(f"  {i}. {rec}")
        
        # Generate report
        report = {
            "scan_path": str(path),
            "scan_date": asyncio.get_event_loop().time(),
            "threshold_mb": threshold,
            "statistics": statistics,
            "performance": performance,
            "recommendations": performance.get("recommendations", [])
        }
        
        # Save to file if requested
        if output:
            import json
            Path(output).write_text(json.dumps(report, indent=2, default=str))
            console.print(f"\n[green]✅ Performance report saved to: {output}[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Performance analysis failed: {e}[/red]")


async def setup_monorepo_gitignore(path: Path, strategy: str, shared: bool, per_service: bool) -> None:
    """Set up comprehensive .gitignore structure for monorepos."""
    try:
        console.print(f"[bold]🏗️ Setting up monorepo .gitignore structure in: {path}[/bold]")
        console.print(f"Strategy: [cyan]{strategy}[/cyan]")
        
        from .core import GitignoreGenerator
        
        # Detect services/projects
        services = []
        for item in path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if it looks like a service/project
                if any((item / f).exists() for f in ['package.json', 'pyproject.toml', 'go.mod', 'Cargo.toml']):
                    services.append(item)
        
        console.print(f"Detected {len(services)} potential services/projects")
        
        # Generate shared .gitignore if requested
        if shared:
            console.print("\n[bold cyan]📁 Generating shared .gitignore...[/bold cyan]")
            shared_content = """# Shared .gitignore for monorepo
# Common patterns for all services

# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache/
.pytest_cache/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Build outputs
dist/
build/
*.egg-info/
target/
"""
            shared_path = path / ".gitignore"
            shared_path.write_text(shared_content)
            console.print(f"[green]✅ Shared .gitignore created: {shared_path}[/green]")
        
        # Generate per-service .gitignore files
        if per_service and services:
            console.print("\n[bold cyan]🔧 Generating per-service .gitignore files...[/bold cyan]")
            
            for service in services:
                try:
                    detector = TechnologyDetector()
                    technologies = await detector.detect(service)
                    
                    if technologies:
                        async with GitignoreGenerator() as generator:
                            content = await generator.generate(technologies, minimal=True)
                            service_gitignore = service / ".gitignore"
                            service_gitignore.write_text(content)
                            console.print(f"[green]✅ {service.name}: {len(technologies)} technologies[/green]")
                    else:
                        console.print(f"[yellow]⚠️ {service.name}: No technologies detected[/yellow]")
                        
                except Exception as e:
                    console.print(f"[red]❌ {service.name}: Failed - {e}[/red]")
        
        console.print(f"\n[green]✅ Monorepo setup completed![/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Monorepo setup failed: {e}[/red]")


async def perform_security_scan(path: Path, output: Optional[str], severity: str) -> None:
    """Perform comprehensive security scan and generate report."""
    try:
        console.print(f"[bold]🔒 Performing security scan in: {path}[/bold]")
        console.print(f"Severity level: [cyan]{severity}[/cyan]")
        
        from .detector import AdvancedTechnologyDetector
        detector = AdvancedTechnologyDetector()
        analysis = await detector.detect_advanced(path)
        
        security = analysis.get("security", {})
        
        # Display security findings
        console.print("\n[bold cyan]🔒 Security Analysis Results:[/bold cyan]")
        
        sensitive_files = security.get("sensitive_files", [])
        if sensitive_files:
            console.print(f"  • [red]⚠️ Sensitive files found: {len(sensitive_files)}[/red]")
            for file_path in sensitive_files[:10]:  # Show first 10
                console.print(f"    - {file_path}")
            if len(sensitive_files) > 10:
                console.print(f"    ... and {len(sensitive_files) - 10} more")
        else:
            console.print("  • [green]✅ No obvious sensitive files detected[/green]")
        
        exposed_secrets = security.get("exposed_secrets", [])
        if exposed_secrets:
            console.print(f"  • [red]🚨 Exposed secrets found: {len(exposed_secrets)}[/red]")
            for secret in exposed_secrets:
                console.print(f"    - {secret}")
        
        weak_patterns = security.get("weak_patterns", [])
        if weak_patterns:
            console.print(f"  • [yellow]⚠️ Weak patterns detected: {len(weak_patterns)}[/yellow]")
            for pattern in weak_patterns:
                console.print(f"    - {pattern}")
        
        # Recommendations
        recommendations = security.get("recommendations", [])
        if recommendations:
            console.print("\n[bold cyan]💡 Security Recommendations:[/bold cyan]")
            for i, rec in enumerate(recommendations, 1):
                console.print(f"  {i}. {rec}")
        
        # Generate report
        report = {
            "scan_path": str(path),
            "scan_date": asyncio.get_event_loop().time(),
            "severity_level": severity,
            "sensitive_files": sensitive_files,
            "exposed_secrets": exposed_secrets,
            "weak_patterns": weak_patterns,
            "recommendations": recommendations,
            "risk_score": len(sensitive_files) * 10 + len(exposed_secrets) * 50
        }
        
        # Save to file if requested
        if output:
            import json
            Path(output).write_text(json.dumps(report, indent=2, default=str))
            console.print(f"\n[green]✅ Security report saved to: {output}[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Security scan failed: {e}[/red]")


async def optimize_gitignore(path: Path, dry_run: bool, aggressive: bool) -> None:
    """Optimize existing .gitignore file for better performance."""
    try:
        console.print(f"[bold]⚡ Optimizing .gitignore in: {path}[/bold]")
        
        gitignore_path = path / ".gitignore"
        if not gitignore_path.exists():
            console.print("[yellow]No .gitignore file found[/yellow]")
            return
        
        content = gitignore_path.read_text()
        original_lines = content.splitlines()
        
        console.print(f"Original .gitignore: {len(original_lines)} lines")
        
        # Analyze patterns
        patterns = {
            "duplicates": [],
            "redundant": [],
            "inefficient": [],
            "suggestions": []
        }
        
        # Check for duplicates
        seen_patterns = set()
        for i, line in enumerate(original_lines):
            line = line.strip()
            if line and not line.startswith('#'):
                if line in seen_patterns:
                    patterns["duplicates"].append((i + 1, line))
                else:
                    seen_patterns.add(line)
        
        # Check for inefficient patterns
        for i, line in enumerate(original_lines):
            line = line.strip()
            if line and not line.startswith('#'):
                if line.endswith('/') and line[:-1] in seen_patterns:
                    patterns["redundant"].append((i + 1, line))
                elif line.startswith('*') and len(line) > 10:
                    patterns["inefficient"].append((i + 1, line))
        
        # Generate suggestions
        if aggressive:
            patterns["suggestions"].extend([
                "Consider using more specific patterns",
                "Group related patterns together",
                "Add comments for clarity"
            ])
        
        # Display analysis
        console.print("\n[bold cyan]🔍 Optimization Analysis:[/bold cyan]")
        
        if patterns["duplicates"]:
            console.print(f"  • [yellow]Duplicate patterns: {len(patterns['duplicates'])}[/yellow]")
            for line_num, pattern in patterns["duplicates"][:5]:
                console.print(f"    Line {line_num}: {pattern}")
        
        if patterns["redundant"]:
            console.print(f"  • [yellow]Redundant patterns: {len(patterns['redundant'])}[/yellow]")
            for line_num, pattern in patterns["redundant"][:5]:
                console.print(f"    Line {line_num}: {pattern}")
        
        if patterns["inefficient"]:
            console.print(f"  • [yellow]Inefficient patterns: {len(patterns['inefficient'])}[/yellow]")
            for line_num, pattern in patterns["inefficient"][:5]:
                console.print(f"    Line {line_num}: {pattern}")
        
        if patterns["suggestions"]:
            console.print("\n[bold cyan]💡 Suggestions:[/bold cyan]")
            for suggestion in patterns["suggestions"]:
                console.print(f"  • {suggestion}")
        
        # Calculate optimization potential
        total_issues = len(patterns["duplicates"]) + len(patterns["redundant"]) + len(patterns["inefficient"])
        if total_issues == 0:
            console.print("\n[green]✅ .gitignore is already well optimized![/green]")
            return
        
        potential_savings = total_issues
        console.print(f"\n[cyan]Potential optimization: Remove {potential_savings} lines[/cyan]")
        
        if dry_run:
            console.print("[dim]Dry run mode - no changes applied[/dim]")
            return
        
        # Apply optimizations
        if Confirm.ask("Apply optimizations?"):
            # Remove duplicates and redundant patterns
            optimized_lines = []
            seen = set()
            
            for line in original_lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    if stripped not in seen:
                        optimized_lines.append(line)
                        seen.add(stripped)
                else:
                    optimized_lines.append(line)
            
            # Create backup
            backup_path = gitignore_path.with_suffix('.gitignore.backup')
            gitignore_path.rename(backup_path)
            
            # Write optimized content
            gitignore_path.write_text('\n'.join(optimized_lines))
            
            console.print(f"[green]✅ Optimization completed![/green]")
            console.print(f"  • Removed {len(original_lines) - len(optimized_lines)} lines")
            console.print(f"  • Backup saved to: {backup_path}")
        else:
            console.print("[yellow]Optimization cancelled[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Optimization failed: {e}[/red]")


async def run_ai_recommendations(path: Path, output: Optional[str]) -> None:
    """Run AI-powered recommendations."""
    console.print(f"🤖 Analyzing project for AI recommendations: {path}")
    
    try:
        # Detect technologies
        detector = TechnologyDetector()
        technologies = await detector.detect(path)
        
        # Get existing .gitignore content
        gitignore_file = path / ".gitignore"
        existing_gitignore = None
        if gitignore_file.exists():
            existing_gitignore = gitignore_file.read_text()
        
        # Generate recommendations
        recommendations = await ai_engine.analyze_project_and_recommend(
            path, technologies, existing_gitignore
        )
        
        # Display recommendations
        ai_engine.display_recommendations(recommendations)
        
        # Save to file if requested
        if output:
            output_data = {
                "project_path": str(path),
                "detected_technologies": technologies,
                "recommendations": [
                    {
                        "title": rec.title,
                        "description": rec.description,
                        "priority": rec.priority,
                        "category": rec.category,
                        "action": rec.action,
                        "confidence": rec.confidence,
                        "reasoning": rec.reasoning
                    }
                    for rec in recommendations
                ],
                "generated_at": datetime.now().isoformat()
            }
            
            with open(output, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            console.print(f"✅ Recommendations saved to: {output}")
    
    except Exception as e:
        console.print(f"[red]Error generating AI recommendations: {e}[/red]")

async def run_analyze_repo(repo_url: str, output: Optional[str]) -> None:
    """Analyze a GitHub repository."""
    console.print(f"🔍 Analyzing GitHub repository: {repo_url}")
    
    try:
        analysis = await github_integration.analyze_repository(repo_url)
        
        if analysis:
            github_integration.display_repository_analysis(analysis)
            
            if output:
                with open(output, 'w') as f:
                    json.dump(analysis, f, indent=2, default=str)
                console.print(f"✅ Analysis saved to: {output}")
        else:
            console.print("[red]Failed to analyze repository[/red]")
    
    except Exception as e:
        console.print(f"[red]Error analyzing repository: {e}[/red]")

async def run_analyze_repos(repo_urls: List[str], output: Optional[str]) -> None:
    """Analyze multiple GitHub repositories."""
    console.print(f"🔍 Analyzing {len(repo_urls)} GitHub repositories")
    
    try:
        analysis = await github_integration.analyze_multiple_repositories(repo_urls)
        
        if analysis:
            # Display common patterns
            github_integration.display_common_patterns(analysis["common_patterns"])
            
            # Display recommendations
            if analysis["recommendations"]:
                console.print("\n[bold]📊 Analysis Summary:[/bold]")
                for rec in analysis["recommendations"]:
                    if rec["type"] == "missing_gitignore":
                        console.print(f"❌ {rec['count']} repositories missing .gitignore files ({rec['percentage']:.1f}%)")
                    elif rec["type"] == "top_languages":
                        console.print(f"🔤 Top languages: {', '.join([lang for lang, _ in rec['languages'][:3]])}")
            
            if output:
                with open(output, 'w') as f:
                    json.dump(analysis, f, indent=2, default=str)
                console.print(f"✅ Analysis saved to: {output}")
        else:
            console.print("[red]Failed to analyze repositories[/red]")
    
    except Exception as e:
        console.print(f"[red]Error analyzing repositories: {e}[/red]")

async def run_sync_to_github(local_path: Path, repo_url: str, message: Optional[str]) -> None:
    """Sync local .gitignore to GitHub."""
    console.print(f"🔄 Syncing .gitignore to GitHub: {repo_url}")
    
    try:
        commit_message = message or "Update .gitignore via gign"
        success = await repository_sync.sync_to_github(local_path, repo_url, commit_message)
        
        if success:
            console.print("✅ Sync completed successfully")
        else:
            console.print("[red]Sync failed[/red]")
    
    except Exception as e:
        console.print(f"[red]Error syncing to GitHub: {e}[/red]")

async def run_create_advanced_template(
    name: str, 
    description: str, 
    content: str, 
    author: str, 
    tags: List[str], 
    technologies: List[str]
) -> None:
    """Create an advanced template."""
    try:
        # Validate template
        is_valid, errors = template_validator.validate_template_content(content)
        if not is_valid:
            console.print("[red]Template validation failed:[/red]")
            for error in errors:
                console.print(f"  ❌ {error}")
            return
        
        is_valid, errors = template_validator.validate_template_name(name)
        if not is_valid:
            console.print("[red]Template name validation failed:[/red]")
            for error in errors:
                console.print(f"  ❌ {error}")
            return
        
        # Create template
        template = await template_manager.create_template(
            name, description, content, author, tags, technologies
        )
        
        console.print(f"✅ Advanced template '{name}' created successfully!")
        console.print(f"📝 Description: {template.description}")
        console.print(f"🏷️ Tags: {', '.join(template.tags)}")
        console.print(f"🔧 Technologies: {', '.join(template.technologies)}")
    
    except Exception as e:
        console.print(f"[red]Error creating template: {e}[/red]")

async def run_list_advanced_templates(
    search: Optional[str],
    tags: Optional[List[str]],
    technologies: Optional[List[str]],
    custom_only: bool
) -> None:
    """List advanced templates."""
    try:
        templates = await template_manager.list_templates(
            search=search,
            tags=tags,
            technologies=technologies,
            custom_only=custom_only
        )
        
        template_manager.display_templates(templates)
    
    except Exception as e:
        console.print(f"[red]Error listing templates: {e}[/red]")

async def run_export_template(name: str, output_path: Path) -> None:
    """Export a template."""
    try:
        success = await template_manager.export_template(name, output_path)
        if not success:
            console.print(f"[red]Failed to export template '{name}'[/red]")
    
    except Exception as e:
        console.print(f"[red]Error exporting template: {e}[/red]")

async def run_import_template(import_path: Path) -> None:
    """Import a template."""
    try:
        success = await template_manager.import_template(import_path)
        if not success:
            console.print(f"[red]Failed to import template from '{import_path}'[/red]")
    
    except Exception as e:
        console.print(f"[red]Error importing template: {e}[/red]")

async def run_marketplace(category: Optional[str], language: Optional[str], trending: bool) -> None:
    """Discover templates from marketplace."""
    try:
        templates = await template_marketplace.discover_templates(
            category=category,
            language=language,
            trending=trending
        )
        
        template_marketplace.display_marketplace(templates)
    
    except Exception as e:
        console.print(f"[red]Error accessing marketplace: {e}[/red]")

async def run_download_template(name: str) -> None:
    """Download a template from marketplace."""
    try:
        template = await template_marketplace.download_template(name)
        
        if template:
            # Add to local templates
            await template_manager.create_template(
                template.name,
                template.description,
                template.content,
                template.author,
                template.tags,
                template.technologies
            )
            console.print(f"✅ Template '{name}' downloaded and added to local templates")
        else:
            console.print(f"[red]Failed to download template '{name}'[/red]")
    
    except Exception as e:
        console.print(f"[red]Error downloading template: {e}[/red]")

async def run_validate_template(content: str) -> None:
    """Validate template content."""
    try:
        # Validate content
        is_valid, errors = template_validator.validate_template_content(content)
        
        if is_valid:
            console.print("✅ Template content is valid!")
        else:
            console.print("[red]❌ Template content validation failed:[/red]")
            for error in errors:
                console.print(f"  ❌ {error}")
        
        # Show statistics
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        comment_lines = [line for line in lines if line.strip().startswith('#')]
        pattern_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        
        console.print(f"\n📊 Template Statistics:")
        console.print(f"  Total lines: {len(lines)}")
        console.print(f"  Non-empty lines: {len(non_empty_lines)}")
        console.print(f"  Comment lines: {len(comment_lines)}")
        console.print(f"  Pattern lines: {len(pattern_lines)}")
        console.print(f"  File size: {len(content.encode())} bytes")
    
    except Exception as e:
        console.print(f"[red]Error validating template: {e}[/red]")

if __name__ == "__main__":
    main() 