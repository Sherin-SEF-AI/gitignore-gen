#!/bin/bash
# Installation script for gign

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
    PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8 or higher is required. Found version $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Found Python $PYTHON_VERSION"
}

# Check if pip is installed
check_pip() {
    if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
        print_error "pip is not installed. Please install pip first."
        exit 1
    fi
    
    print_success "Found pip"
}

# Install gign
install_gign() {
    print_status "Installing gign..."
    
    # Upgrade pip first
    print_status "Upgrading pip..."
    $PYTHON_CMD -m pip install --upgrade pip
    
    # Install gign
    print_status "Installing gign from current directory..."
    $PYTHON_CMD -m pip install -e .
    
    print_success "gign installed successfully!"
}

# Install shell completion
install_completion() {
    print_status "Installing shell completion..."
    
    COMPLETION_DIR=""
    if [ -d "/etc/bash_completion.d" ]; then
        COMPLETION_DIR="/etc/bash_completion.d"
    elif [ -d "/usr/local/etc/bash_completion.d" ]; then
        COMPLETION_DIR="/usr/local/etc/bash_completion.d"
    else
        print_warning "Could not find bash completion directory. Skipping completion installation."
        return
    fi
    
    if [ -f "scripts/gign-completion.bash" ]; then
        sudo cp scripts/gign-completion.bash "$COMPLETION_DIR/"
        print_success "Shell completion installed to $COMPLETION_DIR"
    else
        print_warning "Completion script not found. Skipping completion installation."
    fi
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    if command -v gign &> /dev/null; then
        print_success "gign is available in PATH"
        
        # Test basic functionality
        print_status "Testing basic functionality..."
        gign --version
        print_success "Installation test passed!"
    else
        print_error "gign is not available in PATH"
        exit 1
    fi
}

# Main installation process
main() {
    echo "🚀 gign Installation Script"
    echo "=================================="
    echo ""
    
    check_python
    check_pip
    install_gign
    
    # Ask user if they want to install shell completion
    read -p "Do you want to install shell completion? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_completion
    fi
    
    test_installation
    
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "Usage examples:"
    echo "  gign                    # Generate .gitignore for current directory"
    echo "  gign --interactive      # Interactive mode"
    echo "  gign --help             # Show help"
    echo "  gign scan               # Scan directory for technologies"
    echo ""
    echo "For more information, visit: https://github.com/Sherin-SEF-AI/gitignore-gen"
}

# Run main function
main "$@" 