# CommanDOS

A modern MS-DOS simulation system written in Python with advanced features and app ecosystem.

## 🚀 Quick Start

### Prerequisites
- Python 3.6 or higher
- Internet connection (for updates)

### Installation

1. **Download CommanDOS**
   ```bash
   git clone <repository-url>
   cd CommanDOS
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run CommanDOS**
   - **Linux/macOS**: `./start_linux.sh`
   - **Windows**: Double-click `start_windows.bat`

## 🎯 First Run Setup

The setup wizard will guide you through:

1. **Accept Terms** - Review and accept the terms of service
2. **Create User Account** - Set up your username and password
3. **Install Apps** - Optionally install .cdos applications
4. **System Check** - Verify installation and check for updates

## 📋 Core Features

### Command Interface
- **MS-DOS Style Commands**: `dir`, `cd`, `cls`, `ver`, etc.
- **Tab Completion**: Press Tab to auto-complete commands and paths
- **Command History**: Use Up/Down arrows to navigate command history
- **Context Help**: Type `help <command>` for detailed command info

### User Management
- Multi-user authentication system
- Secure password storage
- Login preferences and customization

### App Ecosystem
- Install custom applications with `.cdos` files
- Built-in app manager with install/uninstall capabilities
- App registry system for command integration

### System Features
- **Auto-updates**: Automatic system update checking
- **Recovery Mode**: System recovery and troubleshooting tools
- **Crash Simulation**: Testing and debugging features
- **System Monitoring**: Performance and usage statistics

## 🔧 Available Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `help` | Show available commands | `help` or `help <command>` |
| `dir` | List directory contents | `dir [path]` |
| `cd` | Change directory | `cd <path>` |
| `cls` | Clear screen | `cls` |
| `ver` | Show system version | `ver` |
| `time` | Display current time | `time` |
| `update` | Check for system updates | `update` |
| `install` | Install/uninstall apps | `install <path>` or `install -d <app>` |
| `apps` | List installed applications | `apps` |
| `sysinfo` | Show system information | `sysinfo` |
| `history` | Show command history | `history` |
| `exit` | Restart system | `exit` |

## 📱 App Development

Create your own applications using the `.cdos` format. See [CDOS_SPEC.md](CDOS_SPEC.md) for detailed documentation.

### Quick Example
```python
APP_INFO = {
    "name": "HelloWorld",
    "version": "1.0",
    "author": "Your Name",
    "description": "A simple hello world app"
}

def run(args):
    print("Hello, CommanDOS World!")
    return 0
```

## 🛠️ Recovery Mode

Boot into recovery mode for system maintenance:
- Password recovery
- Factory reset options
- Manual system updates
- System diagnostics

Access via boot menu or run `python3 recovery.py` directly.

## 📞 Support

- Check [CDOS_SPEC.md](CDOS_SPEC.md) for app development
- Use Recovery Mode for system issues
- Report bugs and request features on our repository

## 📄 License

This software is provided as-is under the terms specified during setup.
