import os
import sys
import time

def check_requirements():
    try:
        import requests
    except ImportError:
        print("Required packages not installed!")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("="*50)
    print("CommanDOS Boot Picker")
    print("="*50)
    print("\nSelect boot option:")
    print("1. Normal System")
    print("2. Recovery Mode")
    print("\nAutoboot in 5 seconds...")

def check_setup():
    try:
        with open("System/USER_SETUP_COMPLETED", "r") as f:
            return f.read().strip() == "1"
    except:
        return False

def boot_picker():
    if not check_setup():
        print("First-time setup required...")
        time.sleep(2)
        return "setup"
        
    clear_screen()
    print_header()
    
    timeout = 5
    while timeout > 0:
        if os.name != 'nt':
            import select
            if select.select([sys.stdin], [], [], 1)[0]:
                choice = sys.stdin.readline().strip()
            else:
                timeout -= 1
                continue
        else:
            import msvcrt
            if msvcrt.kbhit():
                choice = msvcrt.getch().decode()
            else:
                time.sleep(1)
                timeout -= 1
                continue
        
        if choice == "1":
            return "system"
        elif choice == "2":
            return "recovery"
    
    return "system"  # Default boot option

if __name__ == "__main__":
    check_requirements()
    print("Starting CommanDOS...")
    time.sleep(2)
    clear_screen()
    boot_option = boot_picker()
    clear_screen()  # Clear screen after selection
    if boot_option == "setup":
        os.system(f"python3 {os.path.join(os.path.dirname(__file__), 'setup.py')}")
    elif boot_option == "system":
        os.system(f"python3 {os.path.join(os.path.dirname(__file__), 'system.py')}")
    else:
        os.system(f"python3 {os.path.join(os.path.dirname(__file__), 'recovery.py')}")
