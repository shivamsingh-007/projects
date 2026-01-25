"""
Quick Fix Script - Copy Missing Static Files
Fixes 404 errors for CSS and JS files
"""

import os
import shutil

print("\n" + "="*70)
print(" FIXING STATIC FILE 404 ERRORS")
print("="*70)

# Get project root
project_root = os.path.dirname(os.path.abspath(__file__))

print(f"\nProject Root: {project_root}")

# Files that should exist
required_files = {
    'static/css/style.css': 'Main stylesheet',
    'static/js/landing.js': 'Landing page JavaScript',
    'static/js/auth.js': 'Authentication JavaScript',
    'frontend/index.html': 'Landing page',
    'frontend/login.html': 'Login page',
    'frontend/register.html': 'Register page',
    'frontend/dashboard.html': 'Dashboard page'
}

print("\n" + "="*70)
print(" CHECKING FILES")
print("="*70)

missing_files = []
existing_files = []

for file_path, description in required_files.items():
    full_path = os.path.join(project_root, file_path)
    
    if os.path.exists(full_path):
        size = os.path.getsize(full_path)
        print(f"✓ {description:30s} ({size:,} bytes)")
        existing_files.append(file_path)
    else:
        print(f"✗ {description:30s} MISSING!")
        print(f"  Expected at: {full_path}")
        missing_files.append((file_path, full_path))

print()

if not missing_files:
    print("="*70)
    print(" ALL FILES PRESENT!")
    print("="*70)
    print("\nThe issue might be with Flask routing.")
    print("\nNext steps:")
    print("1. Make sure you're using app_working.py")
    print("2. Restart the server")
    print("3. Check browser console (F12) for errors")
else:
    print("="*70)
    print(f" MISSING {len(missing_files)} FILES")
    print("="*70)
    print("\nMissing files:")
    for file_path, full_path in missing_files:
        print(f"  • {file_path}")
    
    print("\nThese files need to be created or copied from the package.")

# Check directory structure
print("\n" + "="*70)
print(" DIRECTORY STRUCTURE")
print("="*70)

dirs_to_check = ['static', 'static/css', 'static/js', 'frontend', 'backend', 'models']

for dir_name in dirs_to_check:
    dir_path = os.path.join(project_root, dir_name)
    
    if os.path.exists(dir_path):
        files_count = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
        print(f"✓ {dir_name:20s} ({files_count} files)")
    else:
        print(f"✗ {dir_name:20s} MISSING - Creating...")
        os.makedirs(dir_path, exist_ok=True)
        print(f"  Created: {dir_path}")

print("\n" + "="*70)
print(" RECOMMENDATIONS")
print("="*70)

if missing_files:
    print("\n1. Download the complete package again")
    print("2. Extract all files")
    print("3. Make sure static/css/style.css exists")
    print("4. Make sure static/js/landing.js exists")
else:
    print("\n1. Files are present, issue is with Flask routing")
    print("2. Use app_working.py backend")
    print("3. Check file paths in HTML files")
    
print("\n" + "="*70)

input("\nPress Enter to exit...")
