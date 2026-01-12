
import bcrypt
password = b"strikegoal2026"
# salt = bcrypt.gensalt()
# hashed = bcrypt.hashpw(password, salt)
# print(hashed.decode('utf-8'))
# Streamlit Authenticator expects a list of hashes usually, or just the string. 
# Let's just print the hash.
print(bcrypt.hashpw(password, bcrypt.gensalt()).decode())
