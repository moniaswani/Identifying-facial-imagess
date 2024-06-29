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



def genes_in_text(row):
    if pd.isna(row['genes']):
        return ""
    # Split the genes and strip any extra whitespace
    genes = [gene.strip() for gene in row['genes'].split(',')]
    # Combine title and abstract into a single text
    text = f"{row['abstract']} {row['title_y']}".lower()
    # Find genes that are present in the text
    matching_genes = [gene for gene in genes if gene.lower() in text]
    return ', '.join(matching_genes)

def match_genes_in_text(csv1_path, csv2_path, output_path):
    # Read the CSV files
    csv1 = pd.read_csv(csv1_path)
    csv2 = pd.read_csv(csv2_path)

    # Print the column names for debugging
    print("CSV 1 columns:", csv1.columns)
    print("CSV 2 columns:", csv2.columns)

    # Print the first few rows of each DataFrame for debugging
    print("CSV 1 preview:")
    print(csv1.head())
    print("CSV 2 preview:")
    print(csv2.head())

    # Ensure 'pmid' columns are of the same data type (convert to string)
    csv1['pmid'] = csv1['pmid'].astype(str)
    csv2['pmid'] = csv2['pmid'].astype(str)

    # Merge the DataFrames on the PMID column
    merged_df = pd.merge(csv1, csv2, on='pmid')

    # Print the merged DataFrame columns and preview
    print("Merged DataFrame columns:", merged_df.columns)
    print("Merged DataFrame preview:")
    print(merged_df.head())

    # Check if 'title_y' and 'abstract' columns exist in the merged DataFrame
    if 'title_y' not in merged_df.columns or 'abstract' not in merged_df.columns:
        raise ValueError("The merged DataFrame does not contain 'title_y' and/or 'abstract' columns.")

    # Apply the genes_in_text function to the merged DataFrame
    merged_df['matching_genes'] = merged_df.apply(genes_in_text, axis=1)

    # Filter the DataFrame to keep only the rows where there are matching genes
    matched_df = merged_df[merged_df['matching_genes'] != ""]

    # Drop the original 'genes' column
    matched_df = matched_df.drop(columns=['genes'])

    # Output the results to a new CSV file, without the index
    matched_df.to_csv(output_path, index=False)
    print(f'Matched results saved to {output_path}')
