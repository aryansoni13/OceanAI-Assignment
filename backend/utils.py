import os

def save_uploaded_file(uploaded_file, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    file_path = os.path.join(dest_folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def read_file_content(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
