import zipfile, os

async def extract_zip_async(zip_path: str, dest_path: str):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(dest_path)
        top_level = {member.filename.split("/")[0] for member in zip_ref.infolist() if "/" in member.filename}

    if len(top_level) == 1:
        return os.path.join(dest_path, list(top_level)[0])
    return None

