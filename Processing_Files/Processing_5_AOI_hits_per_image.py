import os
from pathlib import Path
import pandas as pd
from collections import defaultdict

def get_all_possible_aois():
    """Get all possible AOIs from the AOIs.csv file"""
    parent_path = str(Path().resolve())
    aois_path = os.path.join(parent_path + '/Input_files', 'AOIs.csv')
    aois_df = pd.read_csv(aois_path)
    all_aois = sorted(aois_df['AOI'].unique())
    # Add Outside_of_AOIs as a possible option
    all_aois = sorted(all_aois + ['Outside_of_AOIs', 'Outside_of_Screen'])
    return all_aois

def calculate_aoi_hits(df, all_possible_aois):
    """
    Calculate AOI hits and first/new hits for a single image viewing.
    
    Args:
        df: DataFrame containing gaze data for one image viewing
        all_possible_aois: List of all possible AOIs from AOIs.csv
    
    Returns:
        result_dict: Dictionary with total and new hits for each AOI
    """
    # Initialize counters
    total_hits = defaultdict(int)
    new_hits = defaultdict(int)
    
    # Define denominator and numerator AOIs
    denominator_aois = ['H_D1', 'H_D2']
    numerator_aois = ['H_N1', 'H_N2']
    
    # Initialize tracking variables
    last_aoi = None
    last_valid_aoi = None
    last_fraction_part = None  # Track if we were last in numerator or denominator
    num_denom_transitions = 0   # Counter for transitions between numerator and denominator
    
    # Sort by time_point to ensure chronological order
    df = df.sort_values('time_point')
    
    for _, row in df.iterrows():
        current_aoi = row['AOI']
        
        # Count total hits
        total_hits[current_aoi] += 1
        
        # Count new hits (first occurrence or different from previous AOI)
        # If it's the first gaze point AND it's on an actual AOI, count it
        if last_aoi is None and current_aoi not in ['Outside_of_AOIs', 'Outside_of_Screen']:
            new_hits[current_aoi] += 1

        # If transitioning between two different valid AOIs, count it
        elif last_aoi not in ['Outside_of_AOIs', 'Outside_of_Screen'] and \
            current_aoi not in ['Outside_of_AOIs', 'Outside_of_Screen'] and \
            last_aoi != current_aoi:
            new_hits[current_aoi] += 1

        # If coming from an ignored AOI into a valid AOI (first valid AOI after an ignored one), count it
        elif last_valid_aoi != current_aoi and \
            last_aoi in ['Outside_of_AOIs', 'Outside_of_Screen'] and \
            current_aoi not in ['Outside_of_AOIs', 'Outside_of_Screen']:
            new_hits[current_aoi] += 1

        # Update last valid AOI if current AOI is valid
        if current_aoi not in ['Outside_of_AOIs', 'Outside_of_Screen']:
            last_valid_aoi = current_aoi
        
        # Track transitions between numerator and denominator
        current_fraction_part = None
        if current_aoi in numerator_aois:
            current_fraction_part = 'numerator'
        elif current_aoi in denominator_aois:
            current_fraction_part = 'denominator'
            
        # Count transition if we moved between numerator and denominator
        if (current_fraction_part is not None and 
            last_fraction_part is not None and 
            current_fraction_part != last_fraction_part):
            num_denom_transitions += 1
            
        # Update last fraction part if we're in numerator or denominator
        if current_fraction_part is not None:
            last_fraction_part = current_fraction_part
            
        last_aoi = current_aoi
    
    # Create result dictionary with separate columns for each AOI
    result_dict = {
        'Image': df['Image'].iloc[0],
        'HOO_Position': df['HOO_Position'].iloc[0],
        'Numerator_Denominator_Transitions': num_denom_transitions
    }
    
    # Add total hits columns for all possible AOIs (0 if no hits)
    for aoi in all_possible_aois:
        result_dict[f'Total_Hits_{aoi}'] = total_hits.get(aoi, 0)
    
    # Add new hits columns for all possible AOIs (0 if no hits)
    for aoi in all_possible_aois:
        result_dict[f'New_Hits_{aoi}'] = new_hits.get(aoi, 0)
    
    # Calculate total hits across all AOIs 
    total_aoi_hits = sum(total_hits[aoi] for aoi in all_possible_aois)
    total_new_aoi_hits = sum(new_hits[aoi] for aoi in all_possible_aois )
    
    # Add the total columns
    result_dict['Total_AOI_Hits_All'] = total_aoi_hits
    result_dict['New_AOI_Hits_All'] = total_new_aoi_hits
    
    return result_dict

def process_aoi_hits():
    # Set up paths
    parent_path = str(Path().resolve())
    input_path = os.path.join(parent_path + '/Processing_files', 'AOI_hit')
    output_path = os.path.join(parent_path + '/Output_files', 'AOI_hit_per_image')
    
    print("\nStarting AOI hits analysis...")
    
    # Get all possible AOIs
    try:
        all_possible_aois = get_all_possible_aois()
        print(f"Found {len(all_possible_aois)} possible AOIs")
    except Exception as e:
        print(f"Error reading AOIs file: {e}")
        return

    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Get list of CSV files
    csv_files = [f for f in os.listdir(input_path) if f.endswith('.csv')]
    
    # Process each participant's file
    for file in csv_files:
        try:
            print(f"\nProcessing {file}")
            input_file = os.path.join(input_path, file)
            output_file = os.path.join(output_path, file)
            
            # Read input CSV
            df = pd.read_csv(input_file)
            
            # Group by Image
            image_groups = df.groupby('Image')
            
            # Process each image
            results = []
            for _, image_df in image_groups:
                # Calculate hits and add to results
                result_dict = calculate_aoi_hits(image_df, all_possible_aois)
                results.append(result_dict)
            
            # Create output DataFrame
            output_df = pd.DataFrame(results)
            
            # Save to CSV
            output_df.to_csv(output_file, index=False)
            print(f"Saved results to {os.path.basename(output_file)}")
            
        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue

if __name__ == "__main__":
    process_aoi_hits()
