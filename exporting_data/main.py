import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions import extract_images_from_pmid_list
from functions import extract_images_from_pdf
from functions import detect_faces_yolo_in_directory


# try:
#     extract_images_from_pmid_list('filtered_results_7.csv', 'pdfs', 'images_2')
#     print("Images extracted successfully.")
# except Exception as e:
#     print(f"Error: {e}")    



try:
    detect_faces_yolo_in_directory('images_2', 'faces_2' )
    print("Faces detected successfully.")
except Exception as e:  
    print(f"Error: {e}")