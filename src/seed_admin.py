import os
import sys
import secrets
# ensure src is on path
sys.path.insert(0, os.path.dirname(__file__))

from AssetManagement import InventorySystem
from werkzeug.security import generate_password_hash

username = 'admin'
email = 'admin@example.com'
password = secrets.token_urlsafe(10)

s = InventorySystem()
# create Admin group if not exists
s.add_group('Admin', 'Administrator group')
# add user (password stored as hash)
pw_hash = generate_password_hash(password)
s.add_user(username, email, pw_hash)
# assign to group
s.assign_user_to_group(username, 'Admin')

print('CREATED_ADMIN')
print('username:', username)
print('email:', email)
print('password:', password)
