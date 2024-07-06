import pandas as pd
import fitz  # PyMuPDF
import os

def extract_images_from_pmid_list(csv_file, pdf_folder, image_output_folder):
    """
    This function reads pmid values from a CSV file and extracts images from
    the corresponding PDF files. The extracted images are saved to a specified
    output folder.

    Parameters:
    - csv_file: str, path to the CSV file containing pmid values.
    - pdf_folder: str, path to the folder containing the PDF files.
    - image_output_folder: str, path to the folder where extracted images will be saved.
    """

    # Read the CSV file into a dataframe
    df = pd.read_csv(csv_file)

    # Ensure 'pmid' column exists in the dataframe
    if 'index' not in df.columns:
        raise ValueError("CSV file must contain 'index' column")

    # Create the output folder if it doesn't exist
    os.makedirs(image_output_folder, exist_ok=True)

    # Iterate through each pmid in the dataframe
    for index in df['index']:
        pdf_path = os.path.join(pdf_folder, f"{index}.pdf")
        if os.path.exists(pdf_path):
            extract_images_from_pdf(pdf_path, image_output_folder, index)
        else:
            print(f"PDF file for index {index} does not exist in the specified folder.")

def extract_images_from_pdf(pdf_path, image_output_folder, index):
    """
    Extract images from a PDF file and save them to a specified output folder.

    Parameters:
    - pdf_path: str, path to the PDF file.
    - image_output_folder: str, path to the folder where extracted images will be saved.
    - pmid: str, PubMed ID to be used as a prefix for the image filenames.
    """
    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        for img in doc.get_page_images(i):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = os.path.join(image_output_folder, f"{index}_page{i+1}_img{xref}.{image_ext}")
            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)

import os
import cv2
from yoloface import face_analysis

face_yolo = face_analysis()


def detect_faces_yolo_in_directory(image_dir, save_dir):
    """
    Detect faces in all images within a directory using the YOLO model and save each detected face individually.

    Parameters:
    - image_dir: str, path to the directory containing the input images.
    - save_dir: str, path to the directory where the output images will be saved.
    """
    # Ensure the save directory exists
    os.makedirs(save_dir, exist_ok=True)

    # Iterate over each file in the image directory
    for filename in os.listdir(image_dir):
        image_path = os.path.join(image_dir, filename)

        # Check if the file is an image (you can add more extensions if needed)
        if os.path.isfile(image_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            print(f"Processing {image_path}")
            face_count = detect_faces_yolo(image_path, save_dir)
            print(f"Number of faces detected in {filename}: {face_count}")

def detect_faces_yolo(image_path, save_dir):
    """
    Detect faces in an image using the YOLO model and save each detected face individually.

    Parameters:
    - image_path: str, path to the input image.
    - save_dir: str, path to the directory where the output image will be saved.

    Returns:
    - face_count: int, number of faces detected in the image.
    """
    # Ensure the image exists
    if not os.path.exists(image_path):
        print(f"Error: Image file {image_path} does not exist.")
        return 0

    # Perform face detection
    try:
        img, box, conf = face_yolo.face_detection(image_path=image_path, model='full')
    except Exception as e:
        print(f"Error during face detection: {e}")
        return 0
    
    face_count = 0
    
    if len(box) > 0:
        # Load the image using OpenCV
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"Error: Unable to load image at {image_path}")
            return face_count
        
        for i, (x, y, w, h) in enumerate(box):
            # Expand the bounding box to include more area around the face
            expand_ratio = 0.4  # 50% expansion
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
    else:
        print(f"No faces detected in {image_path}")
    
    return face_count