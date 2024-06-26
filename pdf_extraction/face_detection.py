import cv2
from yoloface import face_analysis
from mtcnn import MTCNN
import os

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
