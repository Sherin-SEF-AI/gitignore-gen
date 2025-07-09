# ✨ gign

A magical CLI tool that automatically generates and manages `.gitignore` files for your projects. Simply run it in any directory and watch as it intelligently detects your project's technologies and creates the perfect `.gitignore` file.

**Author:** Sherin Joseph Roy  
**Email:** sherin.joseph2217@gmail.com  
**Repository:** https://github.com/Sherin-SEF-AI/gitignore-gen  
**PyPI:** https://pypi.org/project/gign/

## 🚀 Features

- **🔍 Smart Detection**: Automatically detects 50+ technologies including Python, Node.js, Java, Go, Rust, Swift, Unity, VS Code, JetBrains IDEs, and many more
- **🌐 API Integration**: Fetches templates from gitignore.io with intelligent caching
- **🔄 Smart Merging**: Combines multiple templates and removes duplicates
- **🛡️ Security Patterns**: Optional security-focused patterns for API keys, certificates, and secrets
- **📁 Monorepo Support**: Generate per-directory `.gitignore` files for complex projects
- **💾 Backup & Safety**: Automatic backups and dry-run mode for safe experimentation
- **🎨 Beautiful UI**: Rich terminal output with progress bars, colors, and emojis
- **⚡ Performance**: Async operations for fast scanning and template fetching
- **🔧 Advanced Analysis**: Comprehensive project analysis with dependency scanning, security checks, and performance insights
- **📊 Interactive Recommendations**: Get actionable suggestions based on your project structure
- **🔄 Real-time Monitoring**: Watch mode for automatic updates when files change
- **📦 Custom Templates**: Create, manage, and share your own templates
- **🛠️ Auto-fix**: Automatically remove tracked files that should be ignored

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install gign
```

### From Source

```bash
git clone https://github.com/Sherin-SEF-AI/gitignore-gen.git
cd gitignore-gen
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/Sherin-SEF-AI/gitignore-gen.git
cd gitignore-gen
pip install -e ".[dev]"
```

## 🎯 Quick Start

### Basic Usage

Simply run `gign` in your project directory:

```bash
cd your-project
gign
```

The tool will:
1. 🔍 Scan your project for technologies
2. 🚀 Fetch appropriate templates
3. 🔄 Merge and optimize the content
4. 💾 Save a perfect `.gitignore` file

### Interactive Mode

For more control, use interactive mode:

```bash
gign --interactive
```

This will let you:
- Choose which templates to include
- Add custom templates
- Preview changes before applying

## 📚 Complete Command Reference

### Main Commands

#### `gign` - Main Generation
Generate a `.gitignore` file for the current directory.

```bash
# Basic generation
gign

# With options
gign --security --backup --dry-run

# Interactive mode
gign --interactive

# Minimal mode for cleaner output
gign --minimal

# Strict mode for precise patterns
gign --strict
```

**Options:**
- `--verbose, -v`: Enable verbose output
- `--quiet, -q`: Suppress all output except errors
- `--dry-run`: Preview changes without applying them
- `--interactive, -i`: Enable interactive mode
- `--backup`: Create backup of existing .gitignore
- `--security`: Add common security patterns
- `--monorepo`: Generate per-directory .gitignore files
- `--auto-fix`: Automatically remove files that should be ignored from git
- `--watch`: Watch for file changes and auto-update .gitignore
- `--export PATH`: Export current .gitignore configuration
- `--import PATH`: Import .gitignore configuration
- `--custom-templates PATH`: Path to custom templates directory
- `--force`: Force overwrite existing .gitignore
- `--minimal`: Generate minimal .gitignore with only essential patterns
- `--strict`: Use strict pattern matching for better accuracy

#### `gign scan` - Technology Detection
Scan directory and detect technologies in use.

```bash
# Scan current directory
gign scan

# Scan specific path
gign scan --path /path/to/project
```

#### `gign version` - Version Information
Show version information.

```bash
gign version
```

### Template Management

#### `gign list-templates` - List Templates
List available templates (built-in and custom).

```bash
# List all templates
gign list-templates

# Search for specific templates
gign list-templates --template python

# Show only custom templates
gign list-templates --custom-only
```

#### `gign templates` - Show Template Content
Show content of a specific template.

```bash
# Show Python template
gign templates --template python

# Save template to file
gign templates --template node --output node.gitignore
```

#### `gign create-template` - Create Custom Template
Create a custom template.

```bash
# Create from content
gign create-template --template myproject --content "*.log\n*.tmp"

# Create from file
gign create-template --template myproject --file template.txt
```

#### `gign update-template` - Update Template
Update an existing custom template.

```bash
# Update with new content
gign update-template --template myproject --content "*.log\n*.tmp\n*.cache"

# Update from file
gign update-template --template myproject --file new-template.txt
```

#### `gign delete-template` - Delete Template
Delete a custom template.

```bash
# Delete with confirmation
gign delete-template --template myproject

# Force delete without confirmation
gign delete-template --template myproject --force
```

#### `gign search-templates` - Search Templates
Search for templates by name or content.

```bash
# Search by name
gign search-templates --query python

# Search only custom templates
gign search-templates --query myproject --custom-only
```

### Project Analysis

#### `gign analyze` - Project Analysis
Analyze project structure and generate detailed report.

```bash
# Analyze current directory
gign analyze

# Analyze specific path
gign analyze --path /path/to/project

# Save report to file
gign analyze --output analysis_report.json
```

#### `gign scan-dependencies` - Dependency Scanning
Scan project dependencies and generate detailed report.

```bash
# Scan current directory
gign scan-dependencies

# Save as JSON
gign scan-dependencies --output deps.json

# Save as YAML
gign scan-dependencies --output deps.yaml --format yaml

# Save as CSV
gign scan-dependencies --output deps.csv --format csv
```

#### `gign performance-insights` - Performance Analysis
Generate performance insights and optimization recommendations.

```bash
# Analyze current directory
gign performance-insights

# Custom threshold (default: 10MB)
gign performance-insights --threshold 50

# Save report
gign performance-insights --output perf_report.json
```

#### `gign security-scan` - Security Analysis
Perform comprehensive security scan and generate report.

```bash
# Full security scan
gign security-scan

# Specific severity level
gign security-scan --severity high

# Save report
gign security-scan --output security_report.json
```

### Advanced Features

#### `gign monorepo-setup` - Monorepo Configuration
Set up comprehensive .gitignore structure for monorepos.

```bash
# Basic setup
gign monorepo-setup

# With shared patterns
gign monorepo-setup --shared

# Generate per-service files
gign monorepo-setup --per-service

# Specific strategy
gign monorepo-setup --strategy nested
```

**Strategies:**
- `flat`: Simple flat structure
- `nested`: Nested directory structure
- `hybrid`: Mixed approach (default)

#### `gign optimize` - .gitignore Optimization
Optimize existing .gitignore file for better performance.

```bash
# Preview optimizations
gign optimize --dry-run

# Apply optimizations
gign optimize

# Aggressive optimization
gign optimize --aggressive
```

#### `gign auto-fix` - Auto-fix Tracked Files
Automatically remove files that should be ignored from git.

```bash
# Preview what would be fixed
gign auto-fix --dry-run

# Apply fixes
gign auto-fix
```

#### `gign clean` - Clean Ignored Files
Clean up files that should be ignored from git.

```bash
# Preview cleanup
gign clean --dry-run

# Apply cleanup
gign clean
```

#### `gign watch` - File Watching
Watch for file changes and auto-update .gitignore.

```bash
# Watch current directory
gign watch

# Custom interval (default: 5 seconds)
gign watch --interval 10

# Watch specific path
gign watch --path /path/to/project
```

### Configuration Management

#### `gign export-config` - Export Configuration
Export .gitignore and detected technologies to a config file.

```bash
# Export to default location
gign export-config

# Export to specific file
gign export-config --output my-config.json
```

#### `gign import-config` - Import Configuration
Import a .gitignore-gen config and regenerate .gitignore.

```bash
# Import from file
gign import-config --config my-config.json

# Import to specific location
gign import-config --config my-config.json --output .gitignore
```

## 🎨 Supported Technologies

### Programming Languages
- **Python** (Django, Flask, FastAPI, Jupyter)
- **Node.js** (React, Vue, Angular, Express)
- **Java** (Spring, Maven, Gradle, Android)
- **Go** (Go modules, Go workspaces)
- **Rust** (Cargo, Rust projects)
- **Swift** (iOS, macOS development)
- **C#** (.NET, Unity, Xamarin)
- **PHP** (Laravel, WordPress, Composer)
- **Ruby** (Rails, Bundler, RVM)
- **Dart** (Flutter, Dart projects)
- **Kotlin** (Android, JVM)
- **Scala** (SBT, Scala projects)

### Frameworks & Libraries
- **Frontend**: React, Vue, Angular, Svelte, Next.js, Nuxt.js
- **Backend**: Django, Flask, FastAPI, Express, Spring, Laravel
- **Mobile**: Flutter, React Native, Ionic
- **Desktop**: Electron, Tauri, PyQt, Tkinter

### Build Tools & Package Managers
- **JavaScript**: npm, yarn, pnpm, webpack, vite, rollup
- **Python**: pip, poetry, pipenv, conda
- **Java**: Maven, Gradle, Ant
- **Go**: go mod, go work
- **Rust**: Cargo, Cargo workspaces

### IDEs & Editors
- **VS Code** (.vscode, settings, extensions)
- **JetBrains** (IntelliJ IDEA, PyCharm, WebStorm, Android Studio)
- **Eclipse** (.metadata, .project, .classpath)
- **Vim/Neovim** (.vim, .nvim, swap files)
- **Emacs** (.emacs, .emacs.d)

### Operating Systems
- **macOS** (.DS_Store, Spotlight, Time Machine)
- **Windows** (Thumbs.db, desktop.ini, Recycle Bin)
- **Linux** (core dumps, temporary files)

### Cloud & DevOps
- **Docker** (Dockerfile, docker-compose, .dockerignore)
- **Kubernetes** (k8s manifests, helm charts)
- **Terraform** (.tfstate, .tfvars, modules)
- **Ansible** (playbooks, inventory, roles)
- **Jenkins** (workspace, builds, logs)

### Version Control
- **Git** (.git, .gitignore, .gitattributes)
- **GitHub** (GitHub Actions, .github)
- **GitLab** (GitLab CI, .gitlab-ci.yml)

### Testing & Quality
- **Jest** (coverage, snapshots)
- **Cypress** (videos, screenshots)
- **Playwright** (test-results, playwright-report)
- **Pytest** (.pytest_cache, coverage)
- **Coverage** (htmlcov, .coverage)

## 🔧 Configuration

Create a configuration file at `~/.gign.toml`:

```toml
[api]
base_url = "https://www.tgitignore.io/api"
timeout = 30

[cache]
enabled = true
ttl = 86400  # 24 hours

[security]
auto_add = false
patterns = [
    "*.key",
    "*.pem",
    "*.env"
]

[detection]
scan_depth = 3
ignore_dirs = [".git", "node_modules", "venv"]
```

## 🧪 Examples

### Python Project

```bash
$ gign
🔍 Scanning project...
🚀 Generating .gitignore...
💾 Saving .gitignore...

✅ .gitignore generated successfully!

Detected technologies:
• python
• vscode
```

### React + Node.js Project

```bash
$ gign --interactive
🔍 Scanning project...
🎯 Template Selection:
Include python template? [y/N]: n
Include node template? [y/N]: y
Include react template? [y/N]: y
Include vscode template? [y/N]: y

📋 Generated .gitignore Preview:
# Generated by gign
# Technologies detected: node, react, vscode

node_modules/
.env
dist/
build/
.vscode/
*.log
...

Apply this .gitignore? [y/N]: y
✅ .gitignore generated successfully!
```

### Monorepo with Security

```bash
$ gign --monorepo --security --backup
🔍 Scanning project...
🚀 Generating .gitignore...
💾 Saving .gitignore...

✅ .gitignore generated successfully!
📁 Created per-directory .gitignore files
🔒 Added security patterns
💾 Backup created: .gitignore.backup
```

### Advanced Analysis

```bash
$ gign analyze --output report.json
🔍 Analyzing project: /path/to/project

📊 Project Analysis Results

🔧 Detected Technologies:
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Technology ┃ Confidence ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ python     │ 100.0%     │
│ node       │ 30.0%      │
│ docker     │ 10.0%      │
└────────────┴────────────┘

📦 Dependencies:
  • python: pyproject.toml

🏗️ Project Structure:
  • Type: desktop
  • Depth: 8 levels

📈 File Statistics:
  • Total files: 1250
  • Total directories: 45

🔒 Security Analysis:
  • ⚠️ Sensitive files found: 3
  • Recommendations:
    - Ensure .env files are in .gitignore

⚡ Performance Analysis:
  • ⚠️ Deep directory nesting detected
  • Recommendations:
    - Consider flattening directory structure

💡 Recommendations:
  1. Consider adding __pycache__/ and *.pyc to .gitignore
  2. Ensure node_modules/ is in .gitignore
  3. Ensure .env files are in .gitignore

✅ Report saved to: report.json
```

### Custom Template Management

```bash
# Create a custom template
$ gign create-template --template myproject --content "*.log\n*.tmp\n.env.local"

# List templates (custom template will show with ✓)
$ gign list-templates
📚 Available Templates:
Custom (1): myproject
Built-in (32): python, node, java, go, rust, php, ruby, csharp, swift, kotlin, scala, dart, flutter, react, vue, angular, svelte, docker, kubernetes, terraform, ansible, jenkins, github, gitlab, vscode, intellij, eclipse, vim, emacs, macos, windows, linux
  ✓ myproject
  ● python
  ● node
  ...

# Search for templates
$ gign search-templates --query myproject
🔍 Search Results for "myproject":
  ✓ myproject (custom template)
```

### Performance Optimization

```bash
$ gign optimize --dry-run
⚡ Optimizing .gitignore in: /path/to/project
Original .gitignore: 150 lines

🔍 Optimization Analysis:
  • Duplicate patterns: 5
    Line 145: .coverage
    Line 146: htmlcov/
    Line 147: .pytest_cache/
  • Redundant patterns: 2
    Line 140: .cache/
  • Inefficient patterns: 1
    Line 25: *.egg-info/

Potential optimization: Remove 8 lines
Dry run mode - no changes applied
```

### Security Scanning

```bash
$ gign security-scan --severity high
🔒 Performing security scan in: /path/to/project
Severity level: high

🔒 Security Analysis Results:
  • ⚠️ Sensitive files found: 5
    - /path/to/project/.env
    - /path/to/project/config/private.key
    - /path/to/project/secrets/database.yml
    - /path/to/project/certificates/server.crt
    - /path/to/project/.aws/credentials

💡 Security Recommendations:
  1. Ensure .env files are in .gitignore
  2. Add *.key and *.pem to .gitignore
  3. Consider using environment variables for secrets
  4. Review certificate files for sensitive data

✅ Security report saved to: security_report.json
```

## 🔍 How It Works

1. **Directory Scanning**: Recursively scans your project directory
2. **Pattern Matching**: Uses intelligent patterns to detect technologies
3. **Template Fetching**: Retrieves templates from gitignore.io API
4. **Smart Merging**: Combines templates and removes duplicates
5. **Content Generation**: Creates optimized `.gitignore` content
6. **File Writing**: Saves the result with optional backup

## 🐛 Troubleshooting

### No Technologies Detected

If no technologies are detected, try:

```bash
# Use interactive mode to manually select templates
gign --interactive

# Or specify a template directly
gign templates --template python
```

### API Connection Issues

The tool includes fallback templates for common technologies. If the API is unavailable, it will use bundled templates.

### Permission Errors

Ensure you have read permissions for the directory you're scanning:

```bash
# Check permissions
ls -la

# Run with appropriate permissions
sudo gign  # if needed
```

### Template Fetch Errors

If templates fail to fetch, the tool will use built-in fallbacks:

```bash
# Check network connectivity
ping www.tgitignore.io

# Use offline mode (built-in templates)
gign --offline
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/Sherin-SEF-AI/gitignore-gen.git
cd gitignore-gen
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gitignore_gen

# Run specific test file
pytest tests/test_detector.py
```

### Code Quality

```bash
# Format code
black gitignore_gen tests

# Sort imports
isort gitignore_gen tests

# Lint code
flake8 gitignore_gen tests

# Type checking
mypy gitignore_gen
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [gitignore.io](https://www.tgitignore.io/) for providing the template API
- [Click](https://click.palletsprojects.com/) for the CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- [Watchdog](https://python-watchdog.readthedocs.io/) for file system monitoring

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Sherin-SEF-AI/gitignore-gen/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Sherin-SEF-AI/gitignore-gen/discussions)
- **Email**: sherin.joseph2217@gmail.com

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

---

**By Sherin Joseph Roy** 