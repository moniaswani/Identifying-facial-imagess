import zipfile
import os

def unzip_pdfs(zip_directory, extract_to_directory):
    zip_files = [f for f in os.listdir(zip_directory) if f.endswith('.zip')]

    for zip_file in zip_files:
        zip_path = os.path.join(zip_directory, zip_file)
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to_directory)
            print(f"Extracted {zip_file} to {extract_to_directory}")
        except zipfile.BadZipFile:
            print(f"Bad zip file: {zip_file}, skipping.")
        except Exception as e:
            print(f"Error extracting {zip_file}: {e}")