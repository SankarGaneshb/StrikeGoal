
import bcrypt
import yaml
from yaml.loader import SafeLoader
import sys
import getpass

def set_password():
    print("--- StrikeGoal Password Manager ---")
    username = input("Enter username to update (default: student): ").strip() or "student"
    
    # Securely get password
    password = getpass.getpass(f"Enter new password for '{username}': ")
    confirm = getpass.getpass("Confirm password: ")
    
    if password != confirm:
        print("Error: Passwords do not match!")
        return

    # Generate Hash
    print("Generating hash...")
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    # Update Config
    yaml_path = 'auth_config.yaml'
    try:
        with open(yaml_path) as f:
            config = yaml.load(f, Loader=SafeLoader)
        
        # Ensure structure exists
        if 'credentials' not in config: config['credentials'] = {}
        if 'usernames' not in config['credentials']: config['credentials']['usernames'] = {}
        
        # Update or Create User
        if username not in config['credentials']['usernames']:
            print(f"Creating new user '{username}'...")
            config['credentials']['usernames'][username] = {
                'email': f"{username}@strikegoal.app",
                'name': username.capitalize(),
                'password': hashed
            }
        else:
            print(f"Updating password for '{username}'...")
            config['credentials']['usernames'][username]['password'] = hashed
            
        with open(yaml_path, 'w') as f:
            yaml.dump(config, f)
            
        print("✅ Successfully updated auth_config.yaml")
        print("Restart the Streamlit app to apply changes.")
        
    except Exception as e:
        print(f"Error accessing config file: {e}")

if __name__ == "__main__":
    set_password()
