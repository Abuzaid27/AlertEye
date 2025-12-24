from db import add_user

# Create admin user (username: admin, password: admin123)
if add_user("admin", "admin123", is_admin=1):
    print("✅ Admin account created successfully!")
else:
    print("⚠️ Admin user already exists.")
