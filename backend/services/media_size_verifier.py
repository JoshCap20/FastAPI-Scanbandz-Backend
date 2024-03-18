"""
This is used to check file size without loading the entire file into memory. 
It reads the file in chunks and keeps track of the total size. 
If the file exceeds the maximum allowed size, it raises an HTTPException with status code 413 (Payload Too Large).

This is done to prevent potential denial-of-service (DoS) attacks where an attacker tries to overload the server by uploading very large files.
"""

from fastapi import UploadFile, HTTPException

async def verify_file_size(
    file: UploadFile, max_size: int = 10 * 1024 * 1024
) -> UploadFile:
    """
    Verifies that the file size does not exceed the maximum allowed size.

    Args:
        file (UploadFile): The uploaded file.
        max_size (int): Maximum allowed file size in bytes. (default is 10MB)

    Returns:
        UploadFile: The verified file if it doesn't exceed the max size.

    Raises:
        HTTPException: If the file exceeds the maximum allowed size.
    """
    size = 0
    while True:
        chunk = await file.read(1024 * 1024)  # Read in chunks of 1MB
        if not chunk:
            break
        size += len(chunk)
        if size > max_size:
            await file.close()
            raise HTTPException(status_code=413, detail="File too large")

    await file.seek(0)  # Reset file pointer to the beginning
    return file
