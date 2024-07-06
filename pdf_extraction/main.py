import os
import cv2
import pandas as pd
from collections import defaultdict

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pdf_extraction.extract_images import extract_images_from_pdf
from pdf_extraction.face_detection import detect_faces
from pdf_extraction.unzip_files import unzip_pdfs

def ensure_directories(*directories):
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def save_image_without_conversion(image_path, output_path):
    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        print(f"Error loading image {image_path}")
        return False

    # Ensure output path has a valid extension
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    if not any(output_path.lower().endswith(ext) for ext in valid_extensions):
        print(f"Error: Output path {output_path} does not have a valid image extension.")
        return False

    # Save the image as is
    success = cv2.imwrite(output_path, image)
    if not success:
        print(f"Error: Could not write image to {output_path}")
        return False
    else:
        print(f"Saved image to {output_path}")
        return True

def process_pdfs(pdf_directory, image_directory, face_directory, detection_method):
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    results = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_directory, pdf_file)
        extract_images_from_pdf(pdf_path, image_directory)

        image_files = [f for f in os.listdir(image_directory) if f.startswith(os.path.splitext(pdf_file)[0])]
        total_faces = 0

        for image_file in image_files:
            image_path = os.path.join(image_directory, image_file)
            converted_image_path = os.path.join(image_directory, "converted_" + image_file)
            
            # Save image without conversion and check if successful
            if not save_image_without_conversion(image_path, converted_image_path):
                print(f"Skipping image {image_file} due to save error.")
                continue
            
            # Check if the converted image exists and can be read
            if not os.path.exists(converted_image_path):
                print(f"Converted image {converted_image_path} does not exist.")
                continue

            image = cv2.imread(converted_image_path)
            if image is None:
                print(f"Error reading converted image {converted_image_path}")
                continue
            
            # Detect faces in the converted image
            num_faces = detect_faces(converted_image_path, face_directory, method=detection_method)
            total_faces += num_faces

        results.append({"PDF_File": pdf_file, "Number_of_Faces": total_faces})
    
    return results

def create_and_save_dataframe(data, output_csv):
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    print(df)
    return df

def merge_dataframes(df1, df2_path, output_csv):
    df2 = pd.read_csv(df2_path, sep='\t')
    
    # Select only the desired columns from df2
    df2_selected = df2[['index', 'pmid', 'title', 'abstract', 'pub_date', 'pdf']]
    
    # Strip the '.pdf' extension from the 'PDF_File' column in df1
    df1['PDF_File'] = df1['PDF_File'].str.replace('.pdf', '', regex=False)

    # Merge DataFrames on 'PDF_File' and 'index'
    merged_df = df1.merge(df2_selected, left_on='PDF_File', right_on='index')
    
    # Drop the 'pdf' column
    merged_df.drop(columns=['PDF_File'], inplace=True)
    
    # Save the merged DataFrame to a new CSV file
    merged_df.to_csv(output_csv, index=False)
    print(merged_df)
    return merged_df

def main():
    zip_directory = 'unzip_pdfs/'
    pdf_directory = 'pdfs/'
    image_directory = 'images/'
    face_directory = 'faces/'
    output_csv = "results_1.csv"
    retrieved_df_path = "retrieved_df2.tsv"
    final_output_csv = "results_2.csv"
    detection_method = 'yolo'  # Change to 'mctnn' to switch to MTCNN

    ensure_directories(pdf_directory, image_directory, face_directory)
    
    # unzip_pdfs(zip_directory, pdf_directory)
    
    data = process_pdfs(pdf_directory, image_directory, face_directory, detection_method)
    
    df1 = create_and_save_dataframe(data, output_csv)
    
    merge_dataframes(df1, retrieved_df_path, final_output_csv)

if __name__ == "__main__":
    main()
