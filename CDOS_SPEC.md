# CDOS Application Format Specification v2.0

The `.cdos` format is CommanDOS's application package format, allowing developers to create feature-rich applications that integrate seamlessly with the system.

## 📋 Basic Structure

Every `.cdos` file must contain:

1. **APP_INFO Dictionary** - Application metadata
2. **run() Function** - Main entry point
3. **Optional Functions** - Additional functionality

### Minimal Example
```python
APP_INFO = {
    "name": "MyApp",
    "version": "1.0",
    "author": "Developer Name",
    "description": "Short description of the app"
}

def run(args):
    print("Hello from MyApp!")
    return 0  # 0 = success, 1+ = error
```

## 🏷️ APP_INFO Metadata

### Required Fields
```python
APP_INFO = {
    "name": "AppName",           # String: App name (alphanumeric + underscore)
    "version": "1.0",            # String: Version number
    "author": "Author Name",     # String: Developer name
    "description": "App desc"    # String: Brief description
}
```

### Optional Fields
```python
APP_INFO = {
    # Required fields...
    "min_system_version": "1.0", # Minimum CommanDOS version required
    "dependencies": [],          # List of required system features
    "category": "utility",       # App category (utility, game, tool, etc.)
    "icon": "📁",               # Unicode emoji for app icon
    "hidden": False,            # Hide from app list if True
    "permissions": []           # Required permissions (future use)
}
```

## 🔧 Core Functions

### run(args) - Required
Main entry point called when app is executed.

```python
def run(args):
    """
    Main application function
    
    Args:
        args (list): Command line arguments passed to the app
        
    Returns:
        int: Exit code (0 = success, 1+ = error)
    """
    if not args:
        show_help()
        return 0
    
    command = args[0].lower()
    if command == "help":
        show_help()
    elif command == "version":
        print(f"{APP_INFO['name']} v{APP_INFO['version']}")
    else:
        print("Unknown command")
        return 1
    
    return 0
```

### help() - Optional
Provide detailed help information.

```python
def help():
    """Display help information for the app"""
    print(f"{APP_INFO['name']} v{APP_INFO['version']}")
    print(APP_INFO['description'])
    print("\nUsage:")
    print("  appname help     - Show this help")
    print("  appname version  - Show version")
```

### install() - Optional
Custom installation logic.

```python
def install():
    """Called when app is installed"""
    print("Setting up application...")
    # Create config files, directories, etc.
    return True  # Return False to abort installation
```

### uninstall() - Optional
Custom cleanup logic.

```python
def uninstall():
    """Called when app is uninstalled"""
    print("Cleaning up application data...")
    # Remove config files, temporary data, etc.
    return True  # Return False to abort uninstallation
```

## 📝 Example Applications

### 1. Calculator App
```python
APP_INFO = {
    "name": "Calculator",
    "version": "2.0",
    "author": "CommanDOS Team",
    "description": "Advanced calculator with multiple operations",
    "category": "utility",
    "icon": "🧮"
}

def run(args):
    if not args:
        interactive_mode()
        return 0
    
    if args[0] == "help":
        show_help()
        return 0
    
    if len(args) >= 3:
        return calculate(args)
    else:
        print("Usage: calc <num1> <op> <num2> or 'calc help'")
        return 1

def calculate(args):
    try:
        num1 = float(args[0])
        operator = args[1]
        num2 = float(args[2])
        
        operations = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y if y != 0 else None,
            '^': lambda x, y: x ** y,
            '%': lambda x, y: x % y
        };
        
        if operator not in operations:
            print("Invalid operator. Use: +, -, *, /, ^, %")
            return 1;
        
        result = operations[operator](num1, num2);
        if result is None:
            print("Error: Division by zero");
            return 1;
        
        print(f"Result: {result}");
        return 0;
        
    except ValueError:
        print("Error: Invalid numbers");
        return 1;
    except Exception as e:
        print(f"Error: {e}");
        return 1;

def interactive_mode():
    print("Calculator Interactive Mode (type 'exit' to quit)");
    while True:
        try:
            expr = input("calc> ").strip();
            if expr.lower() == 'exit':
                break;
            if expr:
                parts = expr.split();
                if len(parts) >= 3:
                    calculate(parts);
                else:
                    print("Enter: <number> <operator> <number>");
        except KeyboardInterrupt:
            break;

def show_help():
    print("Calculator v2.0 - Advanced calculator");
    print("Usage:");
    print("  calc <num1> <op> <num2>  - Perform calculation");
    print("  calc                     - Interactive mode");
    print("  calc help                - Show this help");
    print("\nOperators: +, -, *, /, ^ (power), % (modulo)");
    print("Examples:");
    print("  calc 5 + 3     # Addition");
    print("  calc 10 / 2    # Division");
    print("  calc 2 ^ 8     # Power");
```

### 2. File Manager App
```python
APP_INFO = {
    "name": "FileManager",
    "version": "2.0",
    "author": "CommanDOS Team",
    "description": "Advanced file management utility",
    "category": "utility",
    "icon": "📁"
}

import os
import datetime
import shutil

def run(args):
    if not args:
        show_help()
        return 0
    
    commands = {
        'list': list_files,
        'info': file_info,
        'copy': copy_file,
        'move': move_file,
        'delete': delete_file,
        'mkdir': make_directory,
        'search': search_files
    }
    
    command = args[0].lower()
    if command in commands:
        return commands[command](args[1:])
    else:
        print(f"Unknown command: {command}")
        return 1

def list_files(args):
    path = args[0] if args else "."
    try:
        items = os.listdir(path)
        print(f"\nContents of {os.path.abspath(path)}:");
        print("-" * 50);
        
        dirs = [item for item in items if os.path.isdir(os.path.join(path, item))]
        files = [item for item in items if os.path.isfile(os.path.join(path, item))]
        
        for d in sorted(dirs):
            print(f"📁 {d}/");
        for f in sorted(files):
            size = os.path.getsize(os.path.join(path, f))
            print(f"📄 {f} ({size} bytes)");
            
        print(f"\n{len(dirs)} directories, {len(files)} files");
        return 0;
    except Exception as e:
        print(f"Error: {e}");
        return 1;

def file_info(args):
    if not args:
        print("Usage: fm info <filename>");
        return 1;
    
    filepath = args[0];
    try:
        stat = os.stat(filepath);
        size = stat.st_size;
        modified = datetime.datetime.fromtimestamp(stat.st_mtime);
        
        print(f"\nFile Information:");
        print(f"Name: {os.path.basename(filepath)}");
        print(f"Path: {os.path.abspath(filepath)}");
        print(f"Size: {size:,} bytes");
        print(f"Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}");
        print(f"Type: {'Directory' if os.path.isdir(filepath) else 'File'}");
        return 0;
    except Exception as e:
        print(f"Error: {e}");
        return 1;

def show_help():
    print("FileManager v2.0 - File Management Utility");
    print("\nCommands:");
    print("  fm list [path]           - List files and directories");
    print("  fm info <file>           - Show file information");
    print("  fm copy <src> <dest>     - Copy file");
    print("  fm move <src> <dest>     - Move file");
    print("  fm delete <file>         - Delete file");
    print("  fm mkdir <name>          - Create directory");
    print("  fm search <pattern>      - Search for files");
```

## ✅ Best Practices

### Error Handling
- Always return appropriate exit codes
- Handle exceptions gracefully
- Provide meaningful error messages

### User Experience
- Include help functionality
- Support both interactive and command-line modes
- Provide clear usage instructions

### Code Quality
- Use descriptive function names
- Add comments for complex logic
- Follow Python coding standards

### System Integration
- Don't modify system files directly
- Use relative paths when possible
- Respect user permissions

## 🔍 Validation

CommanDOS validates apps during installation:

1. **Syntax Check** - Valid Python syntax
2. **Required Elements** - APP_INFO and run() function present
3. **Metadata Validation** - Required fields in APP_INFO
4. **Security Check** - No dangerous operations (future)

## 🚀 Advanced Features

### Persistent Storage
```python
import os
import json

def save_config(data):
    config_dir = "System/Apps/MyApp/config"
    os.makedirs(config_dir, exist_ok=True)
    with open(f"{config_dir}/settings.json", 'w') as f:
        json.dump(data, f)

def load_config():
    config_file = "System/Apps/MyApp/config/settings.json"
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
```

### System Integration
```python
def get_system_info():
    # Access CommanDOS system information
    return {
        "version": "1.0",  # Would be provided by system
        "user": "current_user",
        "apps": []  # List of installed apps
    }
```

## 📦 Distribution

Package your app for distribution:

1. Create a `.cdos` file with your app code
2. Test installation with `install <path>`
3. Share the `.cdos` file with users
4. Consider creating an installer package with dependencies

---

*For more examples and templates, check the `sample_app.cdos` file included with CommanDOS.*
