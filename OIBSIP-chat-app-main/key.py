from cryptography.fernet import Fernet

# Generate and print a new key
key = Fernet.generate_key()
print(f"Generated key: {key.decode()}")
