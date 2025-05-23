import os
from pathlib import Path
import pandas as pd

def combine_aoi_hits():
    # Set up paths
    parent_path = str(Path(os.path.dirname(__file__)).parent)  # Go up one level to Code directory
    input_path = os.path.join(parent_path, 'Output_files', 'AOI_hit_per_image')
    output_file = os.path.join(parent_path, 'Output_files', 'AOI_hits_combined.csv')
    
    print("\nStarting to combine AOI hits data...")
    
    # Get list of CSV files
    csv_files = [f for f in os.listdir(input_path) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in the input directory")
        return
    
    # Initialize list to store all dataframes
    all_data = []
    
    # Process each file
    for file in csv_files:
        try:
            print(f"Processing {file}")
            
            # Read the CSV file
            file_path = os.path.join(input_path, file)
            df = pd.read_csv(file_path)
            
            # Add participant ID (filename without .csv extension)
            df['pid'] = os.path.splitext(file)[0]
            
            # Add to list
            all_data.append(df)
            
        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue
    
    if not all_data:
        print("No data was successfully processed")
        return
    
    try:
        # Combine all dataframes
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Reorder columns to put Participant_ID first
        cols = combined_df.columns.tolist()
        cols.remove('pid')
        cols = ['pid'] + cols
        combined_df = combined_df[cols]
        
        # Save combined data
        combined_df.to_csv(output_file, index=False)
        print(f"\nSuccessfully combined {len(csv_files)} files")
        print(f"Total rows in combined file: {len(combined_df)}")
        print(f"Saved combined data to: {os.path.basename(output_file)}")
        
    except Exception as e:
        print(f"Error combining data: {e}")

if __name__ == "__main__":
    combine_aoi_hits()
