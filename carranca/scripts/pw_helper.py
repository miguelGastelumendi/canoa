# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
#cSpell: ignore urandom pwdhash hexlify


import os
import hashlib
import binascii
from flask_login import current_user, logout_user


# Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/


def hash_pass(password: str) -> str:
    # Hash a password for storing.
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    pwdhash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return salt + pwdhash  # return bytes


def verify_pass(provided_password: str, stored_password: str) -> bool:
    # Verify a stored password against one provided by user
    stored_password = stored_password.decode("ascii")
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac(
        "sha512", provided_password.encode("utf-8"), salt.encode("ascii"), 100000
    )
    pwdhash = binascii.hexlify(pwdhash).decode("ascii")
    return pwdhash == stored_password


def is_user_logged():
    # mgd:
    # in some context, current_user is an 'invalid pointer'
    # see models.py:request_loader
    logged = False
    try:
        logged = None if not current_user else current_user.is_authenticated and (current_user.id > 0)
    except:
        logged = False

    return logged


def internal_logout():
    logout_user()
    return

#eof
