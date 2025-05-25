import os
import sys
import platform
import datetime
import requests
import json
import shutil
import zipfile
import tempfile
import time
import psutil
from getpass import getpass

class CommanDOS:
    def __init__(self):
        # Verify setup before login
        try:
            with open("System/USER_SETUP_COMPLETED", "r") as f:
                if f.read().strip() != "1":
                    raise FileNotFoundError
        except:
            print("System not properly configured. Running setup...")
            time.sleep(2)
            os.system(f"python3 {os.path.join(os.path.dirname(__file__), 'setup.py')}")
            sys.exit(0)
            
        if not self._login():
            sys.exit(1)
            
        self.version = "1.0-release"
        self.current_dir = os.getcwd()
        self.app_registry = self._load_app_registry()
        self.command_history = []
        self.history_index = -1
        
        self.commands = {
            'help': self.show_help,
            'dir': self.list_directory,
            'cd': self.change_directory,
            'cls': self.clear_screen,
            'ver': self.show_version,
            'exit': self.exit_system,
            'time': self.show_time,
            'update': self.check_updates,
            'crash': self.simulate_crash,
            'install': self.install_cdos,
            'apps': self.list_apps,
            'sysinfo': self.show_system_info,
            'history': self.show_history,
            'uptime': self.show_uptime,
            'clear': self.clear_screen  # Alias for cls
        }
        # Add registered apps to commands
        self.commands.update(self.app_registry)
        self.start_time = datetime.datetime.now()

    def _load_app_registry(self):
        try:
            with open("System/Apps/registry.json", 'r') as f:
                registry = json.load(f)
            # Create execution functions for each app
            app_commands = {}
            for app_name in registry:
                app_commands[app_name] = self.create_app_executor(app_name)
            return app_commands
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print("Warning: App registry corrupted. Rebuilding...")
            self._rebuild_app_registry()
            return {}

    def _rebuild_app_registry(self):
        """Rebuild app registry from installed apps"""
        try:
            apps_dir = "System/Apps"
            if not os.path.exists(apps_dir):
                return
            
            registry = {}
            for app_name in os.listdir(apps_dir):
                app_path = os.path.join(apps_dir, app_name)
                if os.path.isdir(app_path):
                    cdos_file = os.path.join(app_path, f"{app_name}.cdos")
                    if os.path.exists(cdos_file):
                        registry[app_name] = f"app_{app_name}"
            
            os.makedirs(apps_dir, exist_ok=True)
            with open("System/Apps/registry.json", "w") as f:
                json.dump(registry, f, indent=2)
                
        except Exception as e:
            print(f"Error rebuilding registry: {e}")

    def create_app_executor(self, app_name):
        def app_runner(*args):
            try:
                app_file = f"System/Apps/{app_name}/{app_name}.cdos"
                if not os.path.exists(app_file):
                    print(f"App file not found: {app_file}")
                    return 1
                
                # Execute the .cdos file as Python code
                with open(app_file, 'r') as f:
                    code = f.read()
                
                # Validate app before execution
                if not self._validate_app_code(code, app_name):
                    return 1
                
                # Create a secure namespace for the app
                app_namespace = {
                    '__builtins__': __builtins__,
                    'APP_NAME': app_name,
                    'SYSTEM_VERSION': self.version
                }
                
                try:
                    exec(code, app_namespace)
                except Exception as e:
                    print(f"Error loading {app_name}: {e}")
                    return 1
                
                # Check if run function exists and call it
                if 'run' in app_namespace:
                    try:
                        return app_namespace['run'](list(args))
                    except Exception as e:
                        print(f"Error running {app_name}: {e}")
                        return 1
                else:
                    print(f"No run() function found in {app_name}")
                    return 1
                    
            except Exception as e:
                print(f"Critical error running {app_name}: {str(e)}")
                return 1
        return app_runner

    def _validate_app_code(self, code, app_name):
        """Validate app code for security and correctness"""
        try:
            # Check for required elements
            if 'APP_INFO' not in code:
                print(f"Error: {app_name} missing APP_INFO")
                return False
            
            if 'def run(' not in code:
                print(f"Error: {app_name} missing run() function")
                return False
            
            # Basic security check - prevent dangerous imports
            dangerous_imports = ['subprocess', 'eval', 'exec', '__import__']
            for danger in dangerous_imports:
                if danger in code and 'import' in code:
                    print(f"Warning: {app_name} contains potentially dangerous code")
                    choice = input("Continue anyway? (y/n): ").lower()
                    if choice != 'y':
                        return False
            
            return True
        except Exception:
            return False

    def show_help(self, *args):
        """Show available commands with optional detailed help"""
        if args and args[0] in self.commands:
            # Show detailed help for specific command
            cmd = args[0]
            help_text = {
                'dir': 'dir [path] - List directory contents',
                'cd': 'cd <path> - Change current directory',
                'cls': 'cls - Clear screen',
                'ver': 'ver - Show system version and information',
                'time': 'time - Display current time',
                'update': 'update - Check for system updates',
                'install': 'install <path> - Install app from .cdos file\ninstall -d <app> - Uninstall app',
                'apps': 'apps - List all installed applications',
                'sysinfo': 'sysinfo - Show detailed system information',
                'history': 'history - Show command history',
                'uptime': 'uptime - Show system uptime'
            }
            print(f"\n{help_text.get(cmd, f'{cmd} - No detailed help available')}")
            return
        
        print("\nCommanDOS Command Reference:")
        print("="*40)
        show_hidden = len(args) > 0 and args[0] == "-a"
        
        # Group commands by category
        system_cmds = ['help', 'ver', 'cls', 'clear', 'exit', 'time', 'uptime', 'sysinfo']
        file_cmds = ['dir', 'cd']
        app_cmds = ['apps', 'install']
        other_cmds = ['update', 'history']
        
        print("\nSystem Commands:")
        for cmd in system_cmds:
            if cmd in self.commands and (cmd != 'crash' or show_hidden):
                print(f"  {cmd:<12} - {self._get_command_desc(cmd)}")
        
        print("\nFile Commands:")
        for cmd in file_cmds:
            if cmd in self.commands:
                print(f"  {cmd:<12} - {self._get_command_desc(cmd)}")
        
        print("\nApp Management:")
        for cmd in app_cmds:
            if cmd in self.commands:
                print(f"  {cmd:<12} - {self._get_command_desc(cmd)}")
        
        if self.app_registry:
            print("\nInstalled Apps:")
            for app in sorted(self.app_registry.keys()):
                print(f"  {app:<12} - {self._get_app_desc(app)}")
        
        print("\nOther Commands:")
        for cmd in other_cmds:
            if cmd in self.commands:
                print(f"  {cmd:<12} - {self._get_command_desc(cmd)}")
        
        if show_hidden and 'crash' in self.commands:
            print("\nHidden Commands:")
            print(f"  {'crash':<12} - Simulate system crash")
        
        print(f"\nType 'help <command>' for detailed information.")
        print(f"Use 'help -a' to show all commands including hidden ones.")

    def _get_command_desc(self, cmd):
        """Get command description"""
        descriptions = {
            'help': 'Show this help message',
            'dir': 'List directory contents',
            'cd': 'Change directory',
            'cls': 'Clear screen',
            'clear': 'Clear screen',
            'ver': 'Show version information',
            'exit': 'Exit and reboot system',
            'time': 'Display current time',
            'update': 'Check for updates',
            'install': 'Install/uninstall apps',
            'apps': 'List installed apps',
            'sysinfo': 'Show system information',
            'history': 'Show command history',
            'uptime': 'Show system uptime'
        }
        return descriptions.get(cmd, 'No description available')

    def _get_app_desc(self, app_name):
        """Get app description from APP_INFO"""
        try:
            app_file = f"System/Apps/{app_name}/{app_name}.cdos"
            with open(app_file, 'r') as f:
                code = f.read()
            
            # Extract description from APP_INFO
            if 'APP_INFO' in code:
                namespace = {}
                exec(code, namespace)
                if 'APP_INFO' in namespace:
                    return namespace['APP_INFO'].get('description', 'No description')
        except:
            pass
        return 'No description available'

    def list_directory(self, *args):
        """Enhanced directory listing"""
        path = args[0] if args else self.current_dir
        try:
            if not os.path.exists(path):
                print(f"Directory not found: {path}")
                return 1
            
            files = os.listdir(path)
            abs_path = os.path.abspath(path)
            
            print(f"\nDirectory of {abs_path}")
            print("="*len(abs_path) + 12)
            
            if not files:
                print("  <empty directory>")
                return 0
            
            # Separate directories and files
            dirs = []
            file_list = []
            
            for item in files:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    dirs.append(item)
                else:
                    try:
                        size = os.path.getsize(item_path)
                        modified = datetime.datetime.fromtimestamp(os.path.getmtime(item_path))
                        file_list.append((item, size, modified))
                    except:
                        file_list.append((item, 0, datetime.datetime.now()))
            
            # Display directories first
            for d in sorted(dirs):
                print(f"  📁 {d}/")
            
            # Display files with size and date
            for filename, size, modified in sorted(file_list):
                size_str = self._format_size(size)
                date_str = modified.strftime("%Y-%m-%d %H:%M")
                print(f"  📄 {filename:<30} {size_str:>10} {date_str}")
            
            print(f"\n  {len(dirs)} directories, {len(file_list)} files")
            return 0
            
        except PermissionError:
            print(f"Access denied: {path}")
            return 1
        except Exception as e:
            print(f"Error listing directory: {e}")
            return 1

    def _format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"

    def change_directory(self, *args):
        """Enhanced directory change with validation"""
        if not args:
            print(self.current_dir)
            return 0
        
        target = args[0]
        
        # Handle special cases
        if target == "..":
            target = os.path.dirname(self.current_dir)
        elif target == "~":
            target = os.path.expanduser("~")
        
        try:
            if not os.path.exists(target):
                print(f"Directory not found: {target}")
                return 1
            
            if not os.path.isdir(target):
                print(f"Not a directory: {target}")
                return 1
            
            os.chdir(target)
            self.current_dir = os.getcwd()
            return 0
            
        except PermissionError:
            print(f"Access denied: {target}")
            return 1
        except Exception as e:
            print(f"Error changing directory: {e}")
            return 1

    def clear_screen(self, *args):
        os.system('cls' if platform.system() == 'Windows' else 'clear')

    def show_version(self, *args):
        print("\nCommanDOS Version " + self.version)
        print("RELEASE-GRADE SOFTWARE - May contain bugs or be incomplete")
        print(f"Build date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
        print(f"Running on {platform.system()} {platform.release()}")
        print(f"Python version: {platform.python_version()}")

    def exit_system(self, *args):
        print("\nRebooting CommanDOS...")
        os.system(f"python3 {os.path.join(os.path.dirname(__file__), 'boot.py')}")
        sys.exit(0)

    def show_time(self, *args):
        print(datetime.datetime.now().strftime("%H:%M:%S"))

    def check_updates(self, *args):
        print("Checking for updates...")
        try:
            response = requests.get("http://thatoneamiho.cc/commandos-newest.txt")
            newest_version = response.text.strip()
            
            if newest_version != self.version:
                print(f"New version available: {newest_version}")
                choice = input("Download and install update? (y/n): ").lower()
                if choice == 'y':
                    return self.download_and_install_update()
                else:
                    print("Update cancelled.")
                    return False
            else:
                print("You are using the latest version.")
                return False
        except Exception as e:
            print(f"Could not check for updates: {str(e)}")
            return False

    def download_and_install_update(self):
        try:
            print("Downloading update...")
            
            # Download the update
            response = requests.get("http://thatoneamiho.cc/CommanDOS.zip", stream=True)
            response.raise_for_status()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                zip_path = tmp_file.name
            
            print("Installing update...")
            
            # Create backup of current system
            current_dir = os.getcwd()
            backup_dir = f"{current_dir}_backup"
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            
            # Backup critical files
            backup_files = ["System/Credentials/credentials.txt", "System/USER_SETUP_COMPLETED", "System/SHOW_USER_ON_LOGON"]
            temp_backup = {}
            
            for file_path in backup_files:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        temp_backup[file_path] = f.read()
            
            # Extract update
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall('.')
            
            # Restore backed up files
            for file_path, content in temp_backup.items():
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content)
            
            # Cleanup
            os.unlink(zip_path)
            
            print("Update installed successfully!")
            print("Rebooting CommanDOS...")
            
            # Reboot
            os.system(f"python3 {os.path.join(os.path.dirname(__file__), 'boot.py')}")
            sys.exit(0)
            
        except Exception as e:
            print(f"Update failed: {str(e)}")
            print("System may be in an unstable state. Please reinstall manually.")
            return False

    def list_apps(self, *args):
        if not self.app_registry:
            print("No apps installed")
            return
        print("\nInstalled apps:")
        for app in self.app_registry:
            print(f"  {app}")

    def _login(self):
        try:
            with open("System/Credentials/credentials.txt", "r") as f:
                credentials = json.load(f)
        except FileNotFoundError:
            print("Error: Credentials file not found")
            return False
        except json.JSONDecodeError:
            print("Error: Invalid credentials file format")
            return False

        attempts = 3
        while attempts > 0:
            username = input("Username: ")
            password = getpass("Password: ")

            if username in credentials and credentials[username] == password:
                print(f"\nWelcome, {username}!")
                return True

            attempts -= 1
            print(f"Invalid credentials. {attempts} attempts remaining.")

        print("Too many failed attempts. System locked.")
        return False

    def simulate_crash(self, *args):
        print("\nERROR: Critical system failure detected!")
        print("System unresponsive... Press Ctrl+C to force quit")
        try:
            while True:
                # Infinite loop to simulate freeze
                pass
        except KeyboardInterrupt:
            print("\nSystem recovered. Normal operation resumed.")

    def install_cdos(self, *args):
        # Check for uninstall flag
        if args and args[0] == "-d":
            if len(args) < 2:
                print("Usage: install -d <app_name>")
                return
            self.uninstall_app(args[1])
            return
            
        # Check if path provided
        if not args:
            print("Usage: install <path>")
            return

        path = " ".join(args)  # Handle paths with spaces
        
        # Handle directory input
        if os.path.isdir(path):
            cdos_files = [f for f in os.listdir(path) if f.endswith('.cdos')]
            if not cdos_files:
                print("No .cdos files found in directory")
                return
                
            print("\nAvailable .cdos files:")
            for i, file in enumerate(cdos_files, 1):
                print(f"{i}. {file}")
                
            try:
                choice = int(input("\nSelect number to install: "))
                if not 1 <= choice <= len(cdos_files):
                    print("Invalid selection")
                    return
                file_path = os.path.join(path, cdos_files[choice-1])
            except ValueError:
                print("Invalid input")
                return
        else:
            file_path = path
            if not os.path.exists(file_path) or not file_path.endswith('.cdos'):
                print("Invalid file path or not a .cdos file")
                return

        # Install the app
        try:
            app_name = os.path.basename(file_path).replace('.cdos', '')
            app_dir = f"System/Apps/{app_name}"
            os.makedirs(app_dir, exist_ok=True)

            # Copy the .cdos file
            shutil.copy2(file_path, f"{app_dir}/{app_name}.cdos")
            
            # Update registry
            os.makedirs("System/Apps", exist_ok=True)
            try:
                with open("System/Apps/registry.json", "r") as f:
                    registry = json.load(f)
            except FileNotFoundError:
                registry = {}

            # Add to command registry
            registry[app_name] = f"app_{app_name}"
            with open("System/Apps/registry.json", "w") as f:
                json.dump(registry, f)

            print(f"Successfully installed {app_name}")
            
        except Exception as e:
            print(f"Error installing app: {str(e)}")

    def uninstall_app(self, app_name):
        # Check if app exists
        app_dir = f"System/Apps/{app_name}"
        if not os.path.exists(app_dir):
            print(f"App '{app_name}' not found")
            return
            
        # Confirmation
        confirm = input(f"Are you sure you want to uninstall '{app_name}'? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Uninstall cancelled")
            return
            
        try:
            # Remove app directory
            shutil.rmtree(app_dir)
            
            # Update registry
            try:
                with open("System/Apps/registry.json", "r") as f:
                    registry = json.load(f)
                    
                if app_name in registry:
                    del registry[app_name]
                    
                with open("System/Apps/registry.json", "w") as f:
                    json.dump(registry, f)
                    
            except FileNotFoundError:
                pass  # Registry doesn't exist
                
            print(f"Successfully uninstalled '{app_name}'")
            
        except Exception as e:
            print(f"Error uninstalling app: {str(e)}")

    def show_system_info(self, *args):
        """Show detailed system information"""
        print("\nSystem Information")
        print("="*30)
        
        # CommanDOS info
        print(f"CommanDOS Version: {self.version}")
        print(f"Uptime: {self._get_uptime()}")
        print(f"Current Directory: {self.current_dir}")
        
        # System info
        print(f"\nHost System:")
        print(f"  OS: {platform.system()} {platform.release()}")
        print(f"  Architecture: {platform.machine()}")
        print(f"  Python: {platform.python_version()}")
        
        try:
            # Hardware info
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(os.getcwd())
            
            print(f"\nHardware:")
            print(f"  CPU Cores: {psutil.cpu_count()}")
            print(f"  Memory: {self._format_size(memory.available)} available / {self._format_size(memory.total)} total")
            print(f"  Disk: {self._format_size(disk.free)} free / {self._format_size(disk.total)} total")
            
        except Exception:
            print(f"\nHardware: Information unavailable")
        
        # App info
        print(f"\nApplications:")
        print(f"  Installed Apps: {len(self.app_registry)}")
        print(f"  Total Commands: {len(self.commands)}")

    def show_history(self, *args):
        """Show command history"""
        if not self.command_history:
            print("No command history available")
            return 0
        
        print("\nCommand History:")
        print("-"*20)
        
        # Show last 20 commands
        start_idx = max(0, len(self.command_history) - 20)
        for i, cmd in enumerate(self.command_history[start_idx:], start_idx + 1):
            print(f"{i:3d}: {cmd}")
        
        if len(self.command_history) > 20:
            print(f"\n... and {len(self.command_history) - 20} more commands")

    def show_uptime(self, *args):
        """Show system uptime"""
        uptime = self._get_uptime()
        print(f"System uptime: {uptime}")

    def _get_uptime(self):
        """Calculate system uptime"""
        delta = datetime.datetime.now() - self.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if not parts:  # Less than a minute
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
        return ", ".join(parts)

    def run(self):
        self.clear_screen()
        print(f"CommanDOS v{self.version}")
        print("Type 'help' for available commands.")
        print(f"Welcome! System ready at {datetime.datetime.now().strftime('%H:%M:%S')}")
        
        while True:
            try:
                prompt = f"{os.path.basename(self.current_dir)}>"
                command_line = input(prompt).strip()
                
                if not command_line:
                    continue
                
                # Add to history
                self.command_history.append(command_line)
                self.history_index = len(self.command_history)
                
                # Parse command
                command = command_line.lower().split()
                cmd_name = command[0]
                args = command[1:]
                
                if cmd_name in self.commands:
                    try:
                        exit_code = self.commands[cmd_name](*args)
                        if exit_code and exit_code != 0:
                            print(f"Command exited with code {exit_code}")
                    except Exception as e:
                        print(f"Error executing {cmd_name}: {e}")
                else:
                    print(f"'{cmd_name}' is not recognized as a command.")
                    print("Type 'help' to see available commands.")
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' command to quit CommanDOS.")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                print("System recovered. Use 'help' for commands.")

if __name__ == "__main__":
    try:
        print("CommanDOS Login")
        print("="*20)
        dos = CommanDOS()
        dos.run()
    except Exception as e:
        print(f"Critical system error: {e}")
        print("Please run recovery mode or reinstall CommanDOS.")
        sys.exit(1)