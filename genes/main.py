import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions import extracting_genes
from functions import match_gene_data
from functions import extract_genes_from_csv
# from .functions import genes_in_text

# Paths to the input and output files
extracted_genes_file = 'extracted_genes.csv'
merged_results_file = 'results_4.csv'
output_file = 'results_7.csv'
filtered_output_file = 'filtered_results_7.csv'

def main():
    try:
        # Run the matching function
        match_gene_data(extracted_genes_file, merged_results_file, "hgnc_complete_set.txt", output_file)
        
        # Load the output CSV file
        df = pd.read_csv(output_file)
        
        # Normalize column names to handle case sensitivity and leading/trailing spaces
        df.columns = df.columns.str.strip().str.lower()

        # Filter out rows where 'number_of_faces' is 0
        if 'number_of_faces' not in df.columns:
            raise ValueError("Output file must contain 'number_of_faces' column")
        df = df[df['number_of_faces'] != 0]
        
        # Save the filtered dataframe to a new CSV file
        df.to_csv(filtered_output_file, index=False)

        print(f"Filtered matched data saved to {filtered_output_file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()