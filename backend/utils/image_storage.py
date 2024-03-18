from typing import BinaryIO
from azure.storage.blob import BlobServiceClient
from fastapi import UploadFile
from ..settings.config import AZURE_STORAGE_CONNECTION_STRING

def upload_to_azure(file: BinaryIO, filename: str, container_name: str) -> str:
    """
    Upload an image to Azure Blob Storage. 
    It overwrites an existing image with the same name.
    
    Args:
        file (BinaryIO): The image to be uploaded.
        filename (str): The name of the file.
        container_name (str): The name of the container to upload to.
        
    Returns:
        str: The URL of the uploaded image.
    """
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

    blob_client.upload_blob(file, overwrite=True)
    
    return blob_client.url