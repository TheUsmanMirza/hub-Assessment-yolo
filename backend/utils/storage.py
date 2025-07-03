from google.cloud import storage
import os

def upload_to_gcs(folder: str, bucket_folder: str, bucket_name: str):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    for root, _, files in os.walk(folder):
        for file in files:
            local_file_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_file_path, folder)
            gcs_path = os.path.join(bucket_folder, rel_path)
            blob = bucket.blob(gcs_path)
            blob.upload_from_filename(local_file_path)

    return f"gs://{bucket_name}/{bucket_folder}/"