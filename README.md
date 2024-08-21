# Identifying-facial-imagess
This git repisotory is a product of "Leveraging Machine Learning and Facial
Recognition Models to Improve Rare Disease
Diagnosis: A Data Pipeline for Clinician
Support" paper. It aims to create a dataframe with useful data for clincians to help them with diagnosis process for patients with rare diseases. 

The repository consist of 3 modules the order to run this is as follows:

# PDF Image Extraction and Face Detection Pipeline

## Overview

This script automates the process of extracting images from PDF files, detecting faces in the extracted images, and managing the results in CSV files. It is designed to handle a batch of PDFs, perform face detection using either the YOLO or MTCNN method, and output structured data for further analysis.

## Features

- **Directory Management**: Ensures that necessary directories exist before processing.
- **PDF Processing**: Extracts images from PDFs and applies face detection to those images.
- **Face Detection**: Supports YOLO and MTCNN methods for face detection.
- **Data Handling**: Saves the processed results in CSV files and merges them with existing data.

## Requirements

- Python 3.x
- Required Python libraries:
  - `os`
  - `cv2` (OpenCV)
  - `pandas`
  - Any additional libraries required by the `pdf_extraction.functions` module (e.g., PyPDF2, torch for YOLO)

## Usage

1. **Set Up Directories**:
   - Ensure the following directories are set up:
     - `unzip_pdfs/`: (Optional) Directory containing PDFs that need to be unzipped.
     - `pdfs/`: Directory containing PDF files to be processed.
     - `images/`: Directory where extracted images will be saved.
     - `faces/`: Directory where images with detected faces will be saved.

2. **Processing PDFs**:
   - The script processes PDFs in the `pdfs/` directory, extracts images, detects faces, and saves the results.

3. **Running the Script**:
   - To run the script, use the following command:
     ```bash
     python main.py
     ```
   - The script will ensure directories, process the PDFs, and save the results in CSV files (`results_1.csv` and `results_2.csv`).

4. **Customizing Face Detection**:
   - The face detection method can be changed by modifying the `detection_method` variable:
     - `'yolo'`: Uses YOLO for face detection (default).
     - `'mctnn'`: Uses MTCNN for face detection.

## Error Handling

- The script includes error handling for each major step. If an error occurs, it prints an appropriate error message and exits gracefully.

## Output

- **results_1.csv**: A CSV file containing the initial results of the PDF processing.
- **results_2.csv**: A CSV file with the merged data, combining the initial results with pre-existing data (`retrieved_df2.tsv`).

# Gene Data Matching and Filtering Script

## Overview

This script processes gene-related data by matching gene information from different sources, filtering the results based on specific criteria, and saving the filtered data to a CSV file. The primary goal is to identify relevant gene data that also has associated features, such as the presence of faces.

## Features

- **Gene Data Matching**: Matches gene data from extracted gene files and merged result files.
- **Data Filtering**: Filters the data to include only entries with non-zero detected faces.
- **CSV Output**: Saves the processed and filtered data to a CSV file.

## Requirements

- Python 3.x
- Required Python libraries:
  - `pandas` for data manipulation and processing.

## Usage

1. **Set Up Input Files**:
   - Ensure you have the following files:
     - `extracted_genes.csv`: The CSV file containing extracted gene data.
     - `results_4.csv`: The CSV file with merged gene data.
     - `hgnc_complete_set.txt`: A reference text file for gene data matching.

2. **Running the Script**:
   - The script will match gene data, filter the results based on the presence of faces, and save the final filtered data to a new CSV file.
   - Run the script using the following command:
     ```bash
     python main.py
     ```

3. **Output**:
   - **results_7.csv**: The output CSV file with matched gene data.
   - **filtered_results_7.csv**: The final CSV file with filtered data, containing only entries with non-zero detected faces.


