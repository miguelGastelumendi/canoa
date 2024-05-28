import os

def remove_pycache(path):
  for root, dirs, files in os.walk(path):
    for dir in dirs:
      if dir == "__pycache__":
        for filename in files:
            file = os.path.join(root, dir, filename)
            print(file)
            #os.remove(file)

# Replace "path/to/your/project" with your actual project directory
remove_pycache("D:\Projects\AdaptaBrasil\canoa\carranca")