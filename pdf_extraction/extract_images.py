import fitz  # PyMuPDF
import os

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

    