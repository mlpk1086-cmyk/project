import os

file_path = r"c:\Users\USER\OneDrive\Desktop\gopal\src\components\Dashboard.js"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content[:15000])  # Print first 15000 chars
except Exception as e:
    print(f"Error: {e}")
