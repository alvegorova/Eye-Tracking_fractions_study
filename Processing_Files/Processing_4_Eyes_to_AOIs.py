import os
import pandas as pd
import ast
import traceback
from pathlib import Path

def pixels_to_height_units(x, y, screen_width, screen_height):
    """
    Convert pixel coordinates to PsychoPy height units.
    In PsychoPy height units:
    - Height ranges from -1 to 1 (total height = 2)
    - (0,0) is at screen center
    - Y increases upward
    """
    # Calculate conversion factors
    pixels_per_height_unit = screen_height / 2.0  # Since height range is 2 (-1 to 1)
    
    # Convert to centered coordinates (0,0 at center)
    x_centered = x - (screen_width / 2)
    y_centered = y - (screen_height / 2)
    
    # Convert to height units
    x_height_units = x_centered / pixels_per_height_unit
    y_height_units = -y_centered / pixels_per_height_unit  # Negative because y increases upward in PsychoPy
    
    return x_height_units, y_height_units

def is_point_in_screen(x, y, win_width, win_height):
    """
    Check if a point falls within the screen boundaries.
    x, y: gaze coordinates in participant's screen pixels
    win_width, win_height: participant's screen dimensions
    """
    return (0 <= x <= win_width) and (0 <= y <= win_height)

def is_point_in_aoi(x, y, aoi_row, win_width, win_height):
    """
    Check if a point falls within an AOI's boundaries.
    x, y: gaze coordinates in participant's screen pixels
    aoi_row: AOI coordinates in original screen pixels (3456x2156)
    win_width, win_height: participant's screen dimensions
    """
    try:
        # Convert gaze point to height units
        x_gaze_units, y_gaze_units = pixels_to_height_units(x, y, win_width, win_height)
        
        # Convert AOI boundaries to height units using original screen size
        aoi_left_units, _ = pixels_to_height_units(
            float(aoi_row['left_x_min']), 0, 3456, 2156)
        aoi_right_units, _ = pixels_to_height_units(
            float(aoi_row['right_x_max']), 0, 3456, 2156)
        _, aoi_top_units = pixels_to_height_units(
            0, float(aoi_row['top_y_min']), 3456, 2156)
        _, aoi_bottom_units = pixels_to_height_units(
            0, float(aoi_row['bottom_y_max']), 3456, 2156)
        
        # Check if point is within boundaries in height units
        return (aoi_left_units <= x_gaze_units <= aoi_right_units) and \
               (aoi_bottom_units <= y_gaze_units <= aoi_top_units)
    except Exception as e:
        raise

def find_aoi_for_point(x, y, aois_df, win_width, win_height, hoo_position):
    """
    Find which AOI contains the given point.
    All coordinates are in screen pixels.
    Returns:
    - AOI name if point is in an AOI
    - "Outside_of_Screen" if point is outside screen boundaries
    - "Outside_of_AOIs" if point is inside screen but not in any AOI
    """
    try:
        # First check if point is within screen boundaries
        if not is_point_in_screen(x, y, win_width, win_height):
            return "Outside_of_Screen"
            
        # Case-insensitive position matching
        relevant_aois = aois_df[aois_df['HOO_position'].str.lower() == hoo_position.lower()]
        
        # Check each relevant AOI
        for _, aoi in relevant_aois.iterrows():
            if is_point_in_aoi(x, y, aoi, win_width, win_height):
                return aoi['AOI']
        
        return "Outside_of_AOIs"
    except Exception as e:
        raise

def process_gaze_data():
    # Set up paths
    parent_path = str(Path().resolve())
    input_path = os.path.join(parent_path, 'Processing_files/Pavlovia_Data')
    output_path = os.path.join(parent_path, 'Processing_files/AOI_hit')
    aois_path = os.path.join(parent_path, 'Input_files/AOIs.csv')
    
    print("\nStarting gaze data processing...")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Read AOIs data
    try:
        aois_df = pd.read_csv(aois_path)
        aois_df.columns = aois_df.columns.str.strip()
        print(f"Successfully loaded AOIs file with {len(aois_df)} AOIs")
    except Exception as e:
        print(f"Error reading AOIs file: {e}")
        return
        
    # Get list of CSV files
    csv_files = [f for f in os.listdir(input_path) if f.endswith('.csv') and f not in output_path] 

    total_files = len(csv_files)
    print(f"\nFound {total_files} files to process")
    
    # Initialize counters
    processed_files = 0
    failed_files = 0
    total_points_processed = 0
    points_outside_aoi = 0
    points_outside_screen = 0
    
    # Process each file
    for file in csv_files:  # Process all files
        try:
            input_file = os.path.join(input_path, file)
            output_file = os.path.join(output_path, file)
            
            print(f"\nProcessing file: {file}")
            
            # Read input CSV
            df = pd.read_csv(input_file)
            print(f"  Loaded {len(df)} rows")
            
            # Process each row
            processed_rows = []
            file_points = 0
            file_outside_aoi = 0
            file_outside_screen = 0
            
            for _, row in df.iterrows():
                try:
                    # Clean and parse the TaskGazeArray string
                    gaze_array_str = str(row['TaskGazeArray']).strip('"')  # Convert to string and remove outer quotes
                    gaze_points = ast.literal_eval(gaze_array_str)
                    
                    # Process each gaze point
                    for time_point, x, y in gaze_points:
                        new_row = row.copy()
                        new_row['time_point'] = time_point
                        new_row['x'] = x
                        new_row['y'] = y
                        aoi = find_aoi_for_point(
                            x, y, 
                            aois_df, 
                            row['win_width'], row['win_height'],
                            row['HOO_Position']
                        )
                        new_row['AOI'] = aoi
                        processed_rows.append(new_row)
                        
                        file_points += 1
                        if aoi == "Outside_of_AOIs":
                            file_outside_aoi += 1
                        elif aoi == "Outside_of_Screen":
                            file_outside_screen += 1
                except Exception as e:
                    print(f"  Error processing row: {e}")
                    continue
            
            # Create processed dataframe
            processed_df = pd.DataFrame(processed_rows)
            
            # Drop the TaskGazeArray column as it's no longer needed
            processed_df = processed_df.drop('TaskGazeArray', axis=1)
            
            # Save processed data
            processed_df.to_csv(output_file, index=False)
            
            # Update counters
            processed_files += 1
            total_points_processed += file_points
            points_outside_aoi += file_outside_aoi
            points_outside_screen += file_outside_screen
            
            print(f"  Processed {file_points} points:")
            print(f"    - {file_outside_aoi} inside screen but outside AOIs")
            print(f"    - {file_outside_screen} outside screen")
            print(f"  Saved to {os.path.basename(output_file)}")
            
        except Exception as e:
            failed_files += 1
            print(f"  Error processing file: {e}")
            continue
    
    # Print summary
    print("\n=== Processing Summary ===")
    print(f"Total files processed: {processed_files}/{total_files}")
    print(f"Failed files: {failed_files}")
    print(f"Total points processed: {total_points_processed}")
    print(f"Points inside screen but outside AOIs: {points_outside_aoi} ({points_outside_aoi/total_points_processed*100:.1f}%)")
    print(f"Points outside screen: {points_outside_screen} ({points_outside_screen/total_points_processed*100:.1f}%)")
    print("=========================")

if __name__ == "__main__":
    process_gaze_data()