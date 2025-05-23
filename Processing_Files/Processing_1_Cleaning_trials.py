import os
from pathlib import Path
import pandas as pd
import numpy as np

def generate_eye_tracking_data():
    # Generate gaze dataset 
    parent_path = str(Path(__file__).resolve().parent.parent)  # get the Code directory path
    
    input_path = os.path.join(parent_path, 'Input_files/Raw_di-data')

    output_path = os.path.join(parent_path, 'Processing_files/Pavlovia_Data')

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Get IDs
    IDs_path = os.path.join(parent_path, 'Input_files/participant_ids.csv')
    
    IDs_df = pd.read_csv(IDs_path)
    all_IDs = IDs_df['pid'].tolist()

    for filename in os.listdir(input_path):
        # Skip non-CSV files
        if not filename.endswith('.csv'):
            continue

        file_path = os.path.join(input_path, filename)
        print(f"\nProcessing file: {filename}")
        
        try:
            df = pd.read_csv(file_path, encoding='latin-1')  # Use latin-1 encoding to handle special characters
            print(f"Successfully read file, shape: {df.shape}")
        except Exception as e:
            print(f"Error reading file {filename}: {str(e)}")
            continue
            
        PID = str(df.at[1,'pid']).strip()  # Add strip() to remove any whitespace
        
        if PID not in all_IDs:
            print(f"PID {PID} not in participant_ids.csv, skipping...")
            continue

        # Assign win sizes values
        win_height = df['win_height'].dropna().iloc[0]
        win_width = df['win_width'].dropna().iloc[0]

        # Assign condition value
        if df['Image'].astype(str).str.contains('CC', na=False).any():
            Condition = "Congruent"  
        else:
            Condition = "Incongruent"

        # Assign math anxiety values
        MA_EM_1 = df['key_MA.keys'].dropna().iloc[0]
        MA_EM_2 = df['key_MA.keys'].dropna().iloc[1]
        MA_EM_3 = df['key_MA.keys'].dropna().iloc[2]
        MA_EM_4 = df['key_MA.keys'].dropna().iloc[3]
        MA_WO_1 = df['key_MA.keys'].dropna().iloc[4]
        MA_WO_2 = df['key_MA.keys'].dropna().iloc[5]
        MA_WO_3 = df['key_MA.keys'].dropna().iloc[6]
        MA_WO_4 = df['key_MA.keys'].dropna().iloc[7]
        MA_EV_1 = df['key_MA.keys'].dropna().iloc[8]
        MA_EV_2 = df['key_MA.keys'].dropna().iloc[9]
        MA_EV_3 = df['key_MA.keys'].dropna().iloc[10]

        # Assign pre pretest arousal values and response times
        arousal_PrePre = df['key_Pretest_Arousal.keys'].dropna().iloc[0]
        arousal_Time_PrePre = df['key_Pretest_Arousal.rt'].dropna().iloc[0]

        # Assign pretest and experimental arousal values and response times
        arousal_Pretest_3 = df['key_Arousal.keys'].dropna().iloc[0]
        arousal_Time_Pretest_3 = df['key_Arousal.rt'].dropna().iloc[0]
        
        arousal_Pretest_7 = df['key_Arousal.keys'].dropna().iloc[1]
        arousal_Time_Pretest_7 = df['key_Arousal.rt'].dropna().iloc[1]

        arousal_Pretest_12 = df['key_Arousal.keys'].dropna().iloc[2]
        arousal_Time_Pretest_12 = df['key_Arousal.rt'].dropna().iloc[2]
        
        arousal_Exp_2 = df['key_Arousal.keys'].dropna().iloc[3]
        arousal_Time_Exp_2 = df['key_Arousal.rt'].dropna().iloc[3]
        
        arousal_Exp_12 = df['key_Arousal.keys'].dropna().iloc[4]
        arousal_Time_Exp_12 = df['key_Arousal.rt'].dropna().iloc[4]

        # Assign pre pretest valence values and response times
        valence_PrePre = df['key_Pretest_Valence.keys'].dropna().iloc[0]
        valence_Time_PrePre = df['key_Pretest_Valence.rt'].dropna().iloc[0]

        # Assign pretest and experimental valence values and response times
        valence_Pretest_3 = df['key_Valence.keys'].dropna().iloc[0]
        valence_Time_Pretest_3 = df['key_Valence.rt'].dropna().iloc[0]
        
        valence_Pretest_7 = df['key_Valence.keys'].dropna().iloc[1]
        valence_Time_Pretest_7 = df['key_Valence.rt'].dropna().iloc[1]

        valence_Pretest_12 = df['key_Valence.keys'].dropna().iloc[2]
        valence_Time_Pretest_12 = df['key_Valence.rt'].dropna().iloc[2]
        
        valence_Exp_2 = df['key_Valence.keys'].dropna().iloc[3]
        valence_Time_Exp_2 = df['key_Valence.rt'].dropna().iloc[3]
        
        valence_Exp_12 = df['key_Valence.keys'].dropna().iloc[4]
        valence_Time_Exp_12 = df['key_Valence.rt'].dropna().iloc[4]

        # Assign demographics values
        age = df['DemoResp'].dropna().iloc[0]
        gender = df['DemoResp'].dropna().iloc[1]
        race_ethnicity = df['DemoResp'].dropna().iloc[2]

        # Search for rows with trials information
        png_rows = df[df['Image'].astype(str).str.contains('png', na=False)]
        
        if len(png_rows) == 0:
            continue  # Skip to next file
            
        Image_first = png_rows.index.min()
        Image_last = png_rows.index.max()
        
        # Check if indices are valid integers
        if not isinstance(Image_first, (int, np.integer)) or not isinstance(Image_last, (int, np.integer)):
            continue  # Skip to next file

        # Make dataframe only for rows with math problems
        Question_df = df.iloc[Image_first:Image_last+1].copy()

        # Add student-level variables to each row
        Question_df.loc[Image_first:Image_last+1,'win_height'] = win_height
        Question_df.loc[Image_first:Image_last+1,'win_width'] = win_width
        Question_df.loc[Image_first:Image_last+1,'Condition'] = Condition

        # Add math anxiety into dataframe
        Question_df.loc[Image_first:Image_last+1,'MA_EM_1'] = MA_EM_1
        Question_df.loc[Image_first:Image_last+1,'MA_EM_2'] = MA_EM_2
        Question_df.loc[Image_first:Image_last+1,'MA_EM_3'] = MA_EM_3
        Question_df.loc[Image_first:Image_last+1,'MA_EM_4'] = MA_EM_4
        Question_df.loc[Image_first:Image_last+1,'MA_WO_1'] = MA_WO_1
        Question_df.loc[Image_first:Image_last+1,'MA_WO_2'] = MA_WO_2
        Question_df.loc[Image_first:Image_last+1,'MA_WO_3'] = MA_WO_3
        Question_df.loc[Image_first:Image_last+1,'MA_WO_4'] = MA_WO_4
        Question_df.loc[Image_first:Image_last+1,'MA_EV_1'] = MA_EV_1
        Question_df.loc[Image_first:Image_last+1,'MA_EV_2'] = MA_EV_2
        Question_df.loc[Image_first:Image_last+1,'MA_EV_3'] = MA_EV_3

        # Add arousal and valence data into dataframe
        Question_df.loc[Image_first:Image_last+1,'arousal_PrePre'] = arousal_PrePre
        Question_df.loc[Image_first:Image_last+1,'arousal_Time_PrePre'] = arousal_Time_PrePre
        Question_df.loc[Image_first:Image_last+1,'arousal_Pretest_3'] = arousal_Pretest_3
        Question_df.loc[Image_first:Image_last+1,'arousal_Time_Pretest_3'] = arousal_Time_Pretest_3
        Question_df.loc[Image_first:Image_last+1,'arousal_Pretest_7'] = arousal_Pretest_7
        Question_df.loc[Image_first:Image_last+1,'arousal_Time_Pretest_7'] = arousal_Time_Pretest_7
        Question_df.loc[Image_first:Image_last+1,'arousal_Pretest_12'] = arousal_Pretest_12
        Question_df.loc[Image_first:Image_last+1,'arousal_Time_Pretest_12'] = arousal_Time_Pretest_12
        Question_df.loc[Image_first:Image_last+1,'arousal_Exp_2'] = arousal_Exp_2
        Question_df.loc[Image_first:Image_last+1,'arousal_Time_Exp_2'] = arousal_Time_Exp_2
        Question_df.loc[Image_first:Image_last+1,'arousal_Exp_12'] = arousal_Exp_12
        Question_df.loc[Image_first:Image_last+1,'arousal_Time_Exp_12'] = arousal_Time_Exp_12

        Question_df.loc[Image_first:Image_last+1,'valence_PrePre'] = valence_PrePre
        Question_df.loc[Image_first:Image_last+1,'valence_Time_PrePre'] = valence_Time_PrePre
        Question_df.loc[Image_first:Image_last+1,'valence_Pretest_3'] = valence_Pretest_3
        Question_df.loc[Image_first:Image_last+1,'valence_Time_Pretest_3'] = valence_Time_Pretest_3
        Question_df.loc[Image_first:Image_last+1,'valence_Pretest_7'] = valence_Pretest_7
        Question_df.loc[Image_first:Image_last+1,'valence_Time_Pretest_7'] = valence_Time_Pretest_7
        Question_df.loc[Image_first:Image_last+1,'valence_Pretest_12'] = valence_Pretest_12
        Question_df.loc[Image_first:Image_last+1,'valence_Time_Pretest_12'] = valence_Time_Pretest_12
        Question_df.loc[Image_first:Image_last+1,'valence_Exp_2'] = valence_Exp_2
        Question_df.loc[Image_first:Image_last+1,'valence_Time_Exp_2'] = valence_Time_Exp_2
        Question_df.loc[Image_first:Image_last+1,'valence_Exp_12'] = valence_Exp_12
        Question_df.loc[Image_first:Image_last+1,'valence_Time_Exp_12'] = valence_Time_Exp_12

        # Add demo into dataframe
        Question_df.loc[Image_first:Image_last+1,'age'] = age
        Question_df.loc[Image_first:Image_last+1,'gender'] = gender
        Question_df.loc[Image_first:Image_last+1,'race_ethnicity'] = race_ethnicity

        # Create a copy for processing
        df_noNA = Question_df.copy()
        
        # Process the data
        df_noNA = df_noNA[df_noNA['Image'].notna()]
        
        # Define base columns that are always present
        columns_to_keep = [
            # Basic Info
            'pid', 'date', 'OS', 'frameRate',
            # Trial Data
            'Image', 'finalNumerator', 'finalDenominator', 'trialElapsedTime', 
            'TaskGazeArray', 
            'Condition',
            # Math Anxiety
            "MA_EM_1", "MA_EM_2", "MA_EM_3", "MA_EM_4",
            "MA_WO_1", "MA_WO_2", "MA_WO_3", "MA_WO_4",
            "MA_EV_1", "MA_EV_2", "MA_EV_3",
            # Demo
            "age", "gender", "race_ethnicity",
            # Window Info
            'win_height', 'win_width',
            # Arousal Data
            'arousal_PrePre', 'arousal_Time_PrePre',
            'arousal_Pretest_3', 'arousal_Time_Pretest_3',
            'arousal_Pretest_7', 'arousal_Time_Pretest_7',
            'arousal_Pretest_12', 'arousal_Time_Pretest_12',
            'arousal_Exp_2', 'arousal_Time_Exp_2',
            'arousal_Exp_12', 'arousal_Time_Exp_12',
            # Valence Data
            'valence_PrePre', 'valence_Time_PrePre',
            'valence_Pretest_3', 'valence_Time_Pretest_3',
            'valence_Pretest_7', 'valence_Time_Pretest_7',
            'valence_Pretest_12', 'valence_Time_Pretest_12',
            'valence_Exp_2', 'valence_Time_Exp_2',
            'valence_Exp_12', 'valence_Time_Exp_12'
        ]
            
        ### Keep only the specified columns
        df_noNA = df_noNA[columns_to_keep]

        ### Add trial number (1-based indexing)
        df_noNA['problem_Order'] = np.arange(1, len(df_noNA) + 1)
        
        # Create a data frame mapping Image to true numerators and denominators

        # Create dictionary for true values
        true_values = {
            'Image': ["P1.png", "P2.png", "P3.png", "P4.png", "P5.png", "P6.png", "P7.png", "P8.png", "P9.png", "P10.png", 
                "P11.png", "P12.png", "CC1.png", "CC2.png", "CC3.png", "CC4.png", "CC5.png", "CC6.png", 
                "CC7.png", "CC8.png", "CC9.png", "CC10.png", "CC11.png", "CC12.png", 
                "IC1.png", "IC2.png", "IC3.png", "IC4.png", "IC5.png", "IC6.png", 
                "IC7.png", "IC8.png", "IC9.png", "IC10.png", "IC11.png", "IC12.png"],
            'true_final_numerator': [31, 28, 21, 71, 31, 49, 67, 41, 33, 43, 23, 51,
                           29, 41, 89, 49, 29, 37, 19, 25, 43, 37, 19, 73,
                           29, 41, 89, 49, 29, 37, 19, 25, 43, 37, 19, 73],
            'true_final_denominator': [20, 15, 20, 12, 24, 24, 9, 20, 14, 12, 18, 28,
                             4, 21, 36, 16, 18, 30, 10, 21, 14, 16, 24, 12,
                             4, 21, 36, 16, 18, 30, 10, 21, 14, 16, 24, 12]
        }
        true_values_df = pd.DataFrame(true_values)
        
        # Merge with original dataframe
        df_noNA = df_noNA.merge(true_values_df, on='Image', how='left')
        
        def is_numeric(x):
            try:
                float(x)
                return True
            except ValueError:
                return False
        
        ### Add HOO position column
        # Create a data frame mapping Image to HOO positions
        HOO_Positions = {
            'Image': ["P1.png", "P2.png", "P3.png", "P4.png", "P5.png", "P6.png", 
                "P7.png", "P8.png", "P9.png", "P10.png", "P11.png", "P12.png", 
                "CC1.png", "CC2.png", "CC3.png", "CC4.png", "CC5.png", "CC6.png", 
                "CC7.png", "CC8.png", "CC9.png", "CC10.png", "CC11.png", "CC12.png", 
                "IC1.png", "IC2.png", "IC3.png", "IC4.png", "IC5.png", "IC6.png", 
                "IC7.png", "IC8.png", "IC9.png", "IC10.png", "IC11.png", "IC12.png"],
            'HOO_Position': ["Left", "Left", "Left", "Left", "Left", "Left", 
                "Right", "Right", "Right", "Right", "Right", "Right",
                "Left", "Left", "Left", "Left", "Left", "Left", 
                "Right", "Right", "Right", "Right", "Right", "Right",
                "Left", "Left", "Left", "Left", "Left", "Left", 
                "Right", "Right", "Right", "Right", "Right", "Right"]
        }
        HOO_Positions = pd.DataFrame(HOO_Positions)
        
        # Merge with original dataframe
        df_noNA = df_noNA.merge(HOO_Positions, on='Image', how='left')
        
        ### Add variable showing if problem could be simplified or not
        # Create a data frame mapping Image to Simplification Possibility
        Simplifications = {
            'Image': ["P1.png", "P2.png", "P3.png", "P4.png", "P5.png", "P6.png", 
                "P7.png", "P8.png", "P9.png", "P10.png", "P11.png", "P12.png", 
                "CC1.png", "CC2.png", "CC3.png", "CC4.png", "CC5.png", "CC6.png", 
                "CC7.png", "CC8.png", "CC9.png", "CC10.png", "CC11.png", "CC12.png", 
                "IC1.png", "IC2.png", "IC3.png", "IC4.png", "IC5.png", "IC6.png", 
                "IC7.png", "IC8.png", "IC9.png", "IC10.png", "IC11.png", "IC12.png"],
            'Simplification': ["Yes", "Yes", "Yes", "No", "No", "No", 
                "Yes", "Yes", "Yes", "No", "No", "No", 
                "Yes", "Yes", "Yes", "No", "No", "No", 
                "Yes", "Yes", "Yes", "No", "No", "No", 
                "Yes", "Yes", "Yes", "No", "No", "No",
                "Yes", "Yes", "Yes", "No", "No", "No"]
        }
        Simplifications = pd.DataFrame(Simplifications)
        
        # Merge with original dataframe
        df_noNA = df_noNA.merge(Simplifications, on='Image', how='left')
        
        # Print the output path and PID for debugging
        print(f"Output Path: {output_path}")
        
        # Save the processed DataFrame
        df_noNA.to_csv(output_path + '/' + PID + '.csv', index=False)

generate_eye_tracking_data()
