
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import bcrypt

print("1. Loading Config...")
try:
    with open('auth_config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    print("   Config loaded successfully.")
except Exception as e:
    print(f"   Error loading config: {e}")
    exit()

print("\n2. Checking Data Structure:")
creds = config['credentials']
print(f"   Usernames found: {list(creds['usernames'].keys())}")
stored_hash = creds['usernames']['student']['password']
print(f"   Stored Hash for 'student': {stored_hash}")

print("\n3. Verifying Password 'strikegoal2026' against Stored Hash...")
# Manual Check
if bcrypt.checkpw(b"strikegoal2026", stored_hash.encode()):
    print("   [Manual bcrypt] MATCH: Password is correct.")
else:
    print("   [Manual bcrypt] MISMATCH: Password does not match hash.")

print("\n4. Instantiating Authenticator (Dry Run)...")
try:
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        pre_authorized=config['pre-authorized']
    )
    print("   Authenticator instantiated.")
    
    # Internal check simulation if possible (depending on version internals)
    # Most versions store creds in self.credentials
    if authenticator.credentials['usernames']['student']['password'] == stored_hash:
        print("   Authenticator has the correct hash in memory.")
    else:
        print("   Authenticator memory mismatch!")

except Exception as e:
    print(f"   Error instantiating authenticator: {e}")
