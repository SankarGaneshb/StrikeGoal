
import bcrypt
import yaml
from yaml.loader import SafeLoader

# 1. Generate new hash
password = "strikegoal2026"
new_hash_bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
new_hash_str = new_hash_bytes.decode()
print(f"Generated New Hash: {new_hash_str}")

# 2. Verify immediately
if bcrypt.checkpw(password.encode(), new_hash_bytes):
    print("Verification: SUCCESS")
else:
    print("Verification: FAILED")
    exit(1)

# 3. Update Yaml directly using Python to avoid Copy-Paste errors
yaml_path = 'auth_config.yaml'
try:
    with open(yaml_path) as f:
        config = yaml.load(f, Loader=SafeLoader)
    
    old_hash = config['credentials']['usernames']['student']['password']
    print(f"Old Hash: {old_hash}")
    
    config['credentials']['usernames']['student']['password'] = new_hash_str
    
    with open(yaml_path, 'w') as f:
        yaml.dump(config, f)
    print("Updated auth_config.yaml successfully.")
    
except Exception as e:
    print(f"Error updating yaml: {e}")
