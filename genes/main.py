import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions import unzip_file
from functions import genes_in_text
from functions import extracting_genes
#from .functions import genes_in_text


unzip_file('gene_NBK1116.tar.gz', 'gene_NBK1116')

extracting_genes('extracted_genes.csv')

import pandas as pd

# Define the function to extract and filter genes
def extract_and_filter_genes(extracted_genes_csv, hgnc_file, output_csv):
    # Load the extracted genes CSV
    df = pd.read_csv(extracted_genes_csv)

    # Load the HGNC file with error handling
    try:
        hgnc_df = pd.read_csv(hgnc_file, sep='\t')  # Load the HGNC file with tab separator
    except FileNotFoundError:
        print(f"The HGNC file at {hgnc_file} does not exist.")
        return
    except pd.errors.ParserError:
        print(f"There was an error parsing the HGNC file at {hgnc_file}.")
        return
    except Exception as e:
        print(f"An error occurred while loading the HGNC file: {e}")
        raise

    # Extract the set of verified gene symbols from the HGNC file
    verified_genes = set(hgnc_df['symbol'])

    # Define the function to check for genes in the text and return matching genes
    def genes_in_text(row):
        if pd.isna(row['genes']):
            return ""
        genes = [gene.strip() for gene in row['genes'].split(',')]  # Assuming genes are comma-separated
        # Filter genes to include only verified genes
        verified_genes_in_row = [gene for gene in genes if gene in verified_genes]
        text = f"{row['title']}"  # Assuming 'title' column exists
        matching_genes = [gene for gene in verified_genes_in_row if gene in text]
        return ', '.join(matching_genes)

    # Apply the function to create a new column with matching genes
    df['matching_genes'] = df.apply(genes_in_text, axis=1)

    # Filter the DataFrame to keep only rows with matching genes
    filtered_df = df[df['matching_genes'] != ""]

    # Save the filtered DataFrame to a new CSV file
    filtered_df.to_csv(output_csv, index=False)

    print(f"Filtered rows with matching genes saved to '{output_csv}'")

# Example of how to call this function
if __name__ == "__main__":
    extracted_genes_csv = 'extracted_genes.csv'
    hgnc_file = 'hgnc_complete_set.txt'
    output_csv = 'filtered_results_with_matching_genes.csv'
    
    extract_and_filter_genes(extracted_genes_csv, hgnc_file, output_csv)
