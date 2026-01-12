
import bcrypt
import streamlit_authenticator as stauth

password = "strikegoal2026"

# Method 1: Manual Bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print(f"Manual Hash: {hashed.decode()}")

# Verify
if bcrypt.checkpw(password.encode(), hashed):
    print("Manual Hash verification: SUCCESS")
else:
    print("Manual Hash verification: FAILED")

# Method 2: Library Hasher (for debugging)
try:
    # Try different signatures if 0.4.2 changed things
    h = stauth.Hasher([password])
    gen = h.generate()
    print(f"Library Hash: {gen[0]}")
except Exception as e:
    print(f"Library Hasher Error: {e}")
