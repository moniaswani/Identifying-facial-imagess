import os
import tarfile
import re
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
def unzip_file(file_path, destination_path):
    """
    Unzips a specified .tar.gz file to a given destination directory.

    Parameters:
    file_path (str): The path to the .tar.gz file to be unzipped.
    destination_path (str): The path to the directory where the contents will be extracted.

    Returns:
    None
    """
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        # Check if destination directory exists and is not empty
        if os.path.exists(destination_path) and os.listdir(destination_path):
            print(f"The directory {destination_path} already exists and is not empty. Skipping extraction.")
            return

        # Create destination directory if it does not exist
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        # Unzip the file
        with tarfile.open(file_path, 'r:gz') as tar_ref:
            tar_ref.extractall(destination_path)
            print(f"File {file_path} successfully unzipped to {destination_path}.")

    except tarfile.ReadError:
        print(f"The file {file_path} is not a tar.gz file or it is corrupted.")
    except FileNotFoundError as fnf_error:
        print(fnf_error)
    except Exception as e:
        print(f"An error occurred: {e}")



def extracting_genes(output_csv):
    # Regular expression pattern to match potential gene symbols with at least 5 characters, excluding exactly three digits
    gene_pattern = re.compile(r'\b(?!\d{3}\b)[A-Z0-9]{2,}\b')

    generev = []

    # Path to the directory containing the unzipped XML files
    xml_path = Path('gene_NBK1116/gene_NBK1116')
    xml_list = [xml_path / e.name for e in xml_path.rglob('*.nxml')]

    for xml in xml_list:
        try:
            with open(xml, 'rb') as f:
                soup = BeautifulSoup(f, 'lxml-xml')
                title = soup.title.get_text() if soup.title else "No Title Found"
                
                # Skip retired chapters and specific content
                if 'RETIRED CHAPTER, FOR HISTORICAL REFERENCE ONLY' not in title:
                    if 'Resources for Genetics Professionals' not in title:
                        ref_list = soup.find_all('ref-list')
                        for ref in ref_list:
                            pmids = [i.get_text() for i in ref.find_all('pub-id')]
                            
                            # Attempt to find a section header that likely represents the diagnosis section
                            diagnosis_header = None
                            possible_titles = soup.find_all('title', string=re.compile(r'Diagnosis/testing', re.I))
                            
                            genes_in_diagnosis = []

                            if possible_titles:
                                for title_tag in possible_titles:
                                    # Check if the title is part of the relevant content
                                    if 'diagnosis/testing' in title_tag.get_text().lower():
                                        diagnosis_header = title_tag
                                        break
                            
                            if diagnosis_header:
                                # Get the next sibling elements until the next title or section header
                                diagnosis_section = []
                                next_sibling = diagnosis_header.find_next_sibling()
                                while next_sibling and next_sibling.name != 'title':
                                    diagnosis_section.append(next_sibling)
                                    next_sibling = next_sibling.find_next_sibling()

                                # Extract potential gene names from the diagnosis section
                                for element in diagnosis_section:
                                    for text in element.stripped_strings:
                                        for match in gene_pattern.findall(text):
                                            genes_in_diagnosis.append(match)
                                
                                # Remove duplicates
                                genes_in_diagnosis = list(set(genes_in_diagnosis))
                            
                            genes_str = ', '.join(genes_in_diagnosis)
                            for pmid in pmids:
                                generev.append({'title': title, 'pmid': pmid, 'genes': genes_str})
                        
        except Exception as e:
            print(f"Error processing {xml}: {e}")

    # Create a DataFrame
    genes = pd.DataFrame(generev, columns=['title', 'pmid', 'genes'])

    # Save the DataFrame to a CSV file
    genes.to_csv(output_csv, index=False)
    print(f"Gene information saved to {output_csv}")

import pandas as pd

def match_gene_data(file1, file2, hgnc_file, output_file):
    """
    This function reads gene data from two input CSV files and an HGNC file,
    then matches and cross-references genes between the files. The matched data
    is saved to an output CSV file.

    Parameters:
    - file1: str, path to the first input CSV file.
    - file2: str, path to the second input CSV file.
    - hgnc_file: str, path to the HGNC text file.
    - output_file: str, path to the output CSV file where results will be saved.

    Returns:
    - output_file: str, path to the output CSV file.
    """

    # Read the CSV files into dataframes
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    hgnc_df = pd.read_csv(hgnc_file, delimiter="\t", low_memory=False)  # Reading HGNC text file

    # Ensure 'pmid' columns are of the same type
    df1['pmid'] = df1['pmid'].astype(str)
    df2['pmid'] = df2['pmid'].astype(str)

    # Check if required columns exist in the dataframes
    if 'pmid' not in df1.columns or 'genes' not in df1.columns:
        raise ValueError("Input file 1 must contain 'pmid' and 'genes' columns")
    if 'pmid' not in df2.columns or 'genes_found' not in df2.columns:
        raise ValueError("Input file 2 must contain 'pmid' and 'genes_found' columns")
    if 'symbol' not in hgnc_df.columns:
        raise ValueError("HGNC file must contain 'symbol' column")

    # Merge dataframes on 'pmid', keeping all rows from df2
    merged_df = pd.merge(df2, df1, on='pmid', how='left')

    # Initialize a list to store matched rows
    matched_rows = []

    # Get the set of symbols from the HGNC file
    hgnc_symbols = set(hgnc_df['symbol'])

    # Iterate through each row of the merged dataframe
    for index, row in merged_df.iterrows():
        genes_found = row['genes_found']

        # Skip rows with NaN values in 'genes_found'
        if pd.isna(genes_found):
            continue

        # Split the genes by comma to get a list of genes
        genes_found_list = [gene.strip() for gene in genes_found.split(',')]

        # Filter genes_found to only include those in HGNC symbols
        cross_referenced_genes = [gene for gene in genes_found_list if gene in hgnc_symbols]

        # Skip rows where no genes are left after filtering
        if not cross_referenced_genes:
            continue

        # Check for matching genes if 'genes' column is present in the row
        if 'genes' in row and not pd.isna(row['genes']):
            genes1 = [gene.strip() for gene in row['genes'].split(',')]
            matching_genes = [gene for gene in genes1 if gene in cross_referenced_genes]
        else:
            matching_genes = []

        # Create a new row with the relevant data
        new_row = row.drop(labels=['genes'] if 'genes' in row else []).to_dict()
        new_row['genes_in_pub_and_genereviews'] = ','.join(matching_genes)
        new_row['cross_referenced_genes'] = ','.join(cross_referenced_genes)
        matched_rows.append(new_row)

    # Convert the matched rows to a dataframe
    matched_df = pd.DataFrame(matched_rows)

    # Drop the 'pdf' column if it exists
    if 'pdf' in matched_df.columns:
        matched_df = matched_df.drop(columns=['pdf'])

    # Rename the columns
    matched_df = matched_df.rename(columns={
        'title_x': 'pub_title',
        'title_y': 'genereviews_title',
        'genes_found': 'genes_in_pub',
        'matching_genes': 'genes_in_pub_and_genereviews'
    })

    # Save the matched dataframe to a CSV file
    matched_df.to_csv(output_file, index=False)

    return output_file


import pandas as pd
import re

def extract_genes_from_csv(input_csv_path, output_csv_path):
    # Define the regex pattern for gene
    gene_pattern = re.compile(r'\b(?!\d{3}\b)[A-Z0-9]{3,5}\b')

    # Load the CSV file into a DataFrame
    df = pd.read_csv(input_csv_path)

    # Function to find genes in text
    def find_genes(text):
        if pd.isna(text):
            return set()
        matches = gene_pattern.findall(text)
        # Filter out patterns that are just numbers
        return {match for match in matches if not match.isdigit()}

    # Apply the function to 'title' and 'abstract' columns and create a new column 'genes_found'
    title_genes = df['title'].apply(find_genes)
    abstract_genes = df['abstract'].apply(find_genes)
    
    # Combine and remove duplicates
    df['genes_found'] = title_genes.combine(abstract_genes, lambda x, y: x.union(y)).apply(lambda x: ', '.join(x))

    # Save the modified DataFrame to a new CSV file
    df.to_csv(output_csv_path, index=False)

    print(f'New CSV file saved as {output_csv_path}')

# Example usage:
# extract_genes_from_csv('input_file.csv', 'output_file.csv')

