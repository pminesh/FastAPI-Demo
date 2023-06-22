import os
from fastapi import UploadFile

# save file on specific location
def save_file(file: UploadFile) -> str:
    file_path = os.path.join("static/uploads", file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_path