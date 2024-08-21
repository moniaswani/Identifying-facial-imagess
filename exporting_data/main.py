import os
import sys

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the necessary functions
from functions import extract_images_from_pmid_list
from functions import extract_images_from_pdf
from functions import detect_faces_yolo_in_directory

def main():

    try:
        # Attempt to extract images from the specified PMID list
        extract_images_from_pmid_list('filtered_results_7.csv', 'pdfs', 'images_2')
        print("Images extracted successfully.")
    except Exception as e:
        # Print any error that occurs during image extraction
        print(f"Error extracting images: {e}")

    try:
        # Attempt to detect faces in the extracted images
        detect_faces_yolo_in_directory('images_2', 'faces_2')
        print("Faces detected successfully.")
    except Exception as e:
        # Print any error that occurs during face detection
        print(f"Error detecting faces: {e}")

if __name__ == "__main__":
    main()
