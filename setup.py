import os
import requests
from getpass import getpass
import json

VERSION = "1.0-release"

def print_welcome():
    print("="*50)
    print("Welcome to CommanDOS - MS-DOS Simulation")
    print("="*50)
    print("\nNOTICE: This is release-grade software.")
    print("It may contain bugs or be incomplete.")
    print("="*50)
    print("\n")

def accept_terms():
    print("Terms of Service:")
    print("1. This software is provided as-is")
    print("2. By using this software, you agree to our terms")
    print("3. Developer is not responsible for any data loss")
    
    while True:
        choice = input("\nDo you accept these terms? (yes/no): ").lower()
        if choice == 'yes':
            return True
        elif choice == 'no':
            return False
        print("Please enter 'yes' or 'no'")

def create_user():
    users = {}
    
    while True:
        username = input("Enter username: ")
        password = getpass("Enter password: ")
        
        # Create system directory if it doesn't exist
        os.makedirs("System/Credentials", exist_ok=True)
        
        # Load existing credentials if any
        try:
            with open("System/Credentials/credentials.txt", "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = {}
            
        users[username] = password
        
        # Save credentials
        with open("System/Credentials/credentials.txt", "w") as f:
            json.dump(users, f)
            
        # Add show user preference
        show_user = input("\nShow usernames on login screen? (y/n): ").lower() == 'y'
        os.makedirs("System", exist_ok=True)
        with open("System/SHOW_USER_ON_LOGON", "w") as f:
            f.write("1" if show_user else "0")
        
        choice = input("Do you want to create another user? (y/n): ").lower()
        if choice != 'y':
            break

def check_updates():
    try:
        response = requests.get("http://thatoneamiho.cc/commandos-newest.txt")
        newest_version = response.text.strip()
        
        if newest_version != VERSION:
            print(f"New version available: {newest_version}")
            print("Please download the newest version from our website.")
            return True
        return False
    except:
        print("Could not check for updates.")
        return False

def install_apps():
    apps_dir = "Apps"
    system_apps_dir = "System/Apps"
    os.makedirs(apps_dir, exist_ok=True)
    os.makedirs(system_apps_dir, exist_ok=True)

    while True:
        path = input("\nEnter path to .cdos file or directory (or 'q' to quit): ")
        if path.lower() == 'q':
            break

        if os.path.isdir(path):
            files = [f for f in os.listdir(path) if f.endswith('.cdos')]
            if not files:
                print("No .cdos files found in directory")
                continue
                
            print("\nAvailable files:")
            for i, file in enumerate(files, 1):
                print(f"{i}. {file}")
                
            choice = input("Select file number to install: ")
            try:
                file_path = os.path.join(path, files[int(choice)-1])
            except:
                print("Invalid selection")
                continue
        else:
            file_path = path

        if not os.path.exists(file_path) or not file_path.endswith('.cdos'):
            print("Invalid file path or not a .cdos file")
            continue

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            app_name = os.path.basename(file_path).replace('.cdos', '')
            app_dir = f"{system_apps_dir}/{app_name}"
            os.makedirs(app_dir, exist_ok=True)

            # Copy app file
            with open(f"{app_dir}/app.txt", 'w') as f:
                f.write(content)

            # Update registry
            registry_path = f"{system_apps_dir}/registry.json"
            try:
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
            except FileNotFoundError:
                registry = {}

            registry[app_name] = f"app_{app_name}"

            with open(registry_path, 'w') as f:
                json.dump(registry, f)

            print(f"Successfully installed {app_name}")

        except Exception as e:
            print(f"Error installing app: {str(e)}")

def mark_setup_complete():
    os.makedirs("System", exist_ok=True)
    with open("System/USER_SETUP_COMPLETED", "w") as f:
        f.write("1")

def main():
    print_welcome()
    
    if not accept_terms():
        print("You must accept the terms to continue.")
        return
    
    create_user()
    
    install_choice = input("Do you want to install apps from .cdos files? (y/n): ").lower()
    if install_choice == 'y':
        install_apps()
    
    check_update = input("Do you want to check for updates? (y/n): ").lower()
    if check_update == 'y':
        needs_update = check_updates()
        if needs_update:
            return
    
    start = input("Setup complete! Do you want to start CommanDOS? (y/n): ").lower()
    if start == 'y':
        mark_setup_complete()
        print("Starting CommanDOS...")
        os.system(f"python3 {os.path.join(os.path.dirname(__file__), 'boot.py')}")
    else:
        mark_setup_complete()
        print("Setup completed. You can run CommanDOS later.")

if __name__ == "__main__":
    main()