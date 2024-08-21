import os
import cv2
import pandas as pd
from collections import defaultdict
import zipfile
import cv2
from yoloface import face_analysis
from mtcnn import MTCNN
import fitz  # PyMuPDF


import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



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

def extract_images_from_pdf(pdf_path, output_folder):
    pdf_document = fitz.open(pdf_path)
    for page_number in range(len(pdf_document)):
        for img_index, img in enumerate(pdf_document.get_page_images(page_number)):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_name = f"{os.path.basename(pdf_path).split('.')[0]}_page{page_number + 1}_{img_index}.{image_ext}"
            with open(os.path.join(output_folder, image_name), "wb") as image_file:
                image_file.write(image_bytes)
    pdf_document.close()



# Initialize YOLO face analysis
face_yolo = face_analysis()  # Auto Download a large weight files from Google Drive.

def detect_faces_yolo(image_path, save_dir):
    img, box, conf = face_yolo.face_detection(image_path=image_path, model='full')
    face_count = 0
    if len(box) > 0:
        # Load the image using OpenCV
        image = cv2.imread(image_path)
        for i, (x, y, w, h) in enumerate(box):
            # Expand the bounding box to include more area around the face
            expand_ratio = 0.2  # 20% expansion
            x = max(0, int(x - w * expand_ratio))
            y = max(0, int(y - h * expand_ratio))
            w = min(int(w * (1 + 2 * expand_ratio)), image.shape[1] - x)
            h = min(int(h * (1 + 2 * expand_ratio)), image.shape[0] - y)
            
            # Extract the face from the image
            face_img = image[y:y+h, x:x+w]
            if face_img.size > 0:
                # Save the face image to the save directory
                face_filename = os.path.join(save_dir, f"{os.path.splitext(os.path.basename(image_path))[0]}_face_{i+1}.jpg")
                cv2.imwrite(face_filename, face_img)
                face_count += 1
            else:
                print(f"Skipped empty face image from {image_path} at coordinates {x, y, w, h}")
    return face_count

def detect_faces_mctnn(image_path, save_dir):
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Skipping: Unable to load image at {image_path}")
            return 0

        detector = MTCNN()
        faces = detector.detect_faces(image)
        face_count = 0
        expansion_ratio = 0.2  # Adjust this value to control the amount of expansion

        for i, face in enumerate(faces):
            x, y, w, h = face['box']
            
            # Calculate the amount to expand
            expand_w = int(w * expansion_ratio)
            expand_h = int(h * expansion_ratio)
            
            # Expand the bounding box
            x = max(0, x - expand_w)
            y = max(0, y - expand_h)
            w = min(w + 2 * expand_w, image.shape[1] - x)
            h = min(h + 2 * expand_h, image.shape[0] - y)
            
            # Extract the face from the image
            face_img = image[y:y+h, x:x+w]
            if face_img.size > 0:
                # Save the face image to the save directory
                face_filename = os.path.join(save_dir, f"{os.path.splitext(os.path.basename(image_path))[0]}_face_{i+1}.jpg")
                cv2.imwrite(face_filename, face_img)
                face_count += 1
            else:
                print(f"Skipped empty face image from {image_path} at coordinates {x, y, w, h}")
        
        return face_count
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return 0

def detect_faces(image_path, save_dir, method='yolo'):
    if method == 'yolo':
        return detect_faces_yolo(image_path, save_dir)
    elif method == 'mctnn':
        return detect_faces_mctnn(image_path, save_dir)
    else:
        raise ValueError(f"Unknown detection method: {method}")

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