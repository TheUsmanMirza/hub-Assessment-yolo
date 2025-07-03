from google.cloud import storage
import os

def upload_to_gcs(folder: str, bucket_folder: str, bucket_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    for root, _, files in os.walk(folder):
        for file in files:
            blob = bucket.blob(os.path.join(bucket_folder, os.path.relpath(os.path.join(root, file), folder)))
            blob.upload_from_filename(os.path.join(root, file))
    return f"gs://{bucket_name}/{bucket_folder}/"