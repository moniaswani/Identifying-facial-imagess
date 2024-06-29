import sys
import os
import pandas as pd


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions import extracting_genes
from functions import match_genes_in_text
#from .functions import genes_in_text

# Paths to the input and output files
extracted_genes_file = 'extracted_genes.csv'
merged_results_file = 'merged_results.csv'
output_file = 'merged_faces_and_genes.csv'

# try:
#     genes = extracting_genes(extracted_genes_file)
# except Exception as e:
#     print(f"Error processing extracted_genes_file: {e}")

try:
    match_genes_in_text(extracted_genes_file, merged_results_file, 'hgnc_complete_set.txt', output_file)
except Exception as e: 
    print(f"Error merging files: {e}")

