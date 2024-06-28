import pandas as pd


def merge_filtered_with_results(filtered_csv, merged_results_csv, output_csv):
    # Load the filtered results CSV
    try:
        filtered_df = pd.read_csv(filtered_csv)
        print("Filtered DataFrame loaded successfully.")
    except Exception as e:
        print(f"Error loading filtered CSV: {e}")
        return
    
    # Load the merged results CSV
    try:
        merged_results_df = pd.read_csv(merged_results_csv)
        print("Merged results DataFrame loaded successfully.")
    except FileNotFoundError:
        print(f"The merged results file at {merged_results_csv} does not exist.")
        return
    except pd.errors.ParserError:
        print(f"There was an error parsing the merged results file at {merged_results_csv}.")
        return
    except Exception as e:
        print(f"An error occurred while loading the merged results file: {e}")
        raise

    # Print column names and first few rows for debugging
    print("Filtered DataFrame columns:", filtered_df.columns.tolist())
    print("Merged Results DataFrame columns:", merged_results_df.columns.tolist())
    print("First few rows of the Filtered DataFrame:")
    print(filtered_df.head())
    print("First few rows of the Merged Results DataFrame:")
    print(merged_results_df.head())

    # Convert 'pmid' columns to strings
    filtered_df['pmid'] = filtered_df['pmid'].astype(str)
    merged_results_df['pmid'] = merged_results_df['pmid'].astype(str)

    # Merge the dataframes on pmid
    merged_df = pd.merge(filtered_df, merged_results_df, on='pmid', suffixes=('_filtered', '_merged'))
    print("DataFrames merged successfully.")

    # Save the merged DataFrame to a new CSV file
    merged_df.to_csv(output_csv, index=False)

    print(f"Merged results saved to '{output_csv}'")

# Example usage
filtered_csv = '/Users/Monishka/Identifying-facial-imagess/filtered_results_with_matching_genes.csv'
merged_results_csv = 'merged_results.csv'
output_csv = 'final_merged_filtered_results.csv'

merge_filtered_with_results(filtered_csv, merged_results_csv, output_csv)
