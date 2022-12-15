import hashlib
import os

def hash_three(username, password, salt):
    # Concatenate the username and password
    combined = username + password + str(salt)

    # Hash the combined username and password using SHA256
    hashed = hashlib.sha256(combined.encode('utf-8')).hexdigest()
    return hashed


def generate_salt():
    # Generate a random salt value using os.urandom()
    salt = os.urandom(8)
    return salt


def verified(username, password, salt, hashpass):
    # Concatenate the username and password
    combined = username + password + salt

    # Hash the combined username and password using SHA256
    hashed = hashlib.sha256(combined.encode('utf-8')).hexdigest()

    # Compare the hashed password with the stored hashed password
    return hashed == hashpass