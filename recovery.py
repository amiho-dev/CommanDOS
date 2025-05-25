import os
import json
import sys
import shutil
from getpass import getpass

class RecoveryMode:
    def __init__(self):
        self.system_version = self._get_current_version()
        self.commands = {
            'help': self.show_help,
            'forgot': self.show_credentials,
            'factory': self.factory_reset,
            'update': self.manual_update,
            'exit': self.exit_recovery
        }

    def _get_current_version(self):
        try:
            with open("system.py", "r") as f:
                for line in f:
                    if "self.version =" in line:
                        return line.split('"')[1]
        except:
            return "1.0-release"

    def show_help(self):
        print("\nRecovery Mode Commands:")
        print("  forgot  - Show all usernames and passwords")
        print("  factory - Factory reset (delete all apps and credentials)")
        print("  update  - Manual system update")
        print("  exit    - Exit recovery mode")

    def show_credentials(self):
        try:
            with open("System/Credentials/credentials.txt", "r") as f:
                creds = json.load(f)
            print("\nAll credentials:")
            for user, pwd in creds.items():
                print(f"Username: {user}, Password: {pwd}")
        except:
            print("No credentials file found")

    def factory_reset(self):
        confirm = input("WARNING: This will delete all apps and credentials. Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Factory reset cancelled")
            return

        try:
            # Delete credentials
            if os.path.exists("System/Credentials/credentials.txt"):
                os.remove("System/Credentials/credentials.txt")
            
            # Delete apps
            if os.path.exists("System/Apps"):
                shutil.rmtree("System/Apps")
            
            # Reset setup completion
            if os.path.exists("System/USER_SETUP_COMPLETED"):
                with open("System/USER_SETUP_COMPLETED", "w") as f:
                    f.write("0")

            print("Factory reset complete. Setup will run on next boot.")
        except Exception as e:
            print(f"Error during factory reset: {e}")

    def manual_update(self):
        print("\nManual System Update")
        print("Current version:", self.system_version)
        
        file_path = input("Drag new system.py file here: ").strip().replace("'", "").replace('"', '')
        
        if not os.path.exists(file_path):
            print("File not found")
            return

        try:
            # Check version of new file
            with open(file_path, "r") as f:
                content = f.read()
                if 'self.version = "' not in content:
                    print("Invalid system file")
                    return
                new_version = content.split('self.version = "')[1].split('"')[0]

            if new_version <= self.system_version:
                print(f"New version ({new_version}) is not newer than current version ({self.system_version})")
                return

            # Backup current system
            if os.path.exists("system.py"):
                os.rename("system.py", "system_old.py")

            # Copy new system file
            shutil.copy2(file_path, "system.py")
            print(f"Successfully updated to version {new_version}")
            print("Old system backed up as system_old.py")
            
        except Exception as e:
            print(f"Error during update: {e}")

    def exit_recovery(self):
        print("Exiting recovery mode...")
        sys.exit(0)

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*50)
        print("CommanDOS Recovery Mode")
        print("="*50)
        print("Type 'help' for available commands")

        while True:
            try:
                command = input("\nrecovery> ").strip().lower()
                if command in self.commands:
                    self.commands[command]()
                else:
                    print("Unknown command")
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit recovery mode")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    recovery = RecoveryMode()
    recovery.run()
