import os
import cv2
import pandas as pd
from collections import defaultdict

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pdf_extraction.functions import extract_images_from_pdf
from pdf_extraction.functions import detect_faces
from pdf_extraction.functions import unzip_pdfs
from pdf_extraction.functions import ensure_directories
from pdf_extraction.functions import save_image_without_conversion
from pdf_extraction.functions import process_pdfs, create_and_save_dataframe, merge_dataframes, save_image_without_conversion, ensure_directories, extract_images_from_pdf, detect_faces


def main():
    try:
        zip_directory = 'unzip_pdfs/'
        pdf_directory = 'pdfs/'
        image_directory = 'images/'
        face_directory = 'faces/'
        output_csv = "results_1.csv"
        retrieved_df_path = "retrieved_df2.tsv"
        final_output_csv = "results_2.csv"
        detection_method = 'yolo'  # Change to 'mctnn' to switch to MTCNN

        try:
            ensure_directories(pdf_directory, image_directory, face_directory)
            print("Directories ensured.")
        except Exception as e:
            print(f"Error ensuring directories: {e}")
            return  # Exit if directories cannot be ensured

        try:
            # unzip_pdfs(zip_directory, pdf_directory)
            print("Skipped unzipping PDFs (uncomment if needed).")
        except Exception as e:
            print(f"Error unzipping PDFs: {e}")
            return  # Exit if there is an error unzipping PDFs

        try:
            data = process_pdfs(pdf_directory, image_directory, face_directory, detection_method)
            print("PDFs processed successfully.")
        except Exception as e:
            print(f"Error processing PDFs: {e}")
            return  # Exit if there is an error processing PDFs

        try:
            df1 = create_and_save_dataframe(data, output_csv)
            print(f"Dataframe created and saved to {output_csv}.")
        except Exception as e:
            print(f"Error creating or saving dataframe: {e}")
            return  # Exit if there is an error creating or saving the dataframe

        try:
            merge_dataframes(df1, retrieved_df_path, final_output_csv)
            print(f"Dataframes merged and saved to {final_output_csv}.")
        except Exception as e:
            print(f"Error merging dataframes: {e}")
            return  # Exit if there is an error merging dataframes

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
