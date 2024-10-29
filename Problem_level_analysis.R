#library(dplyr)
#library(readr)
#library(tidyr)
#library(ggplot2)
#install.packages("hms")
#library(hms)


rm(list = ls())

### --- Uploading gaze datasets

# Download file
setwd("~/Documents/Data_Analysis/Eye_tracking_fractions/experiment")
file_paths <- list.files(pattern = "*.csv", full.names = TRUE)

# Initialize an empty data frame to store the combined data
combined_data <- data.frame()

# Iterate over each file and process
for (i in seq_along(file_paths)) {
  
  # Load the CSV file
  df <- read_csv(file_paths[i])
  
  # Filter rows where "anx_resp.keys" contains a number
  filtered_df <- df %>% filter(grepl("*.png", as.character(Image)))
  
  # Add the Part_ID column
  filtered_df <- filtered_df %>% mutate(Part_ID = i)
  
  # Convert finalNumerator and finalDenominator to numeric
  filtered_df <- filtered_df %>%
    mutate(finalNumerator = as.numeric(finalNumerator),
           finalDenominator = as.numeric(finalDenominator))
  
  # Select only the relevant columns
  filtered_df <- filtered_df %>% select(Part_ID, Image, finalNumerator, finalDenominator, trialElapsedTime)
  
  # Append to the combined data frame
  combined_data <- bind_rows(combined_data, filtered_df)
}

# Save the combined data to a new CSV file
setwd("~/Documents/Data_Analysis/Eye_tracking_fractions")
write_csv(combined_data, "combined_participant_data.csv")
setwd("~/Documents/Data_Analysis/Eye_tracking_fractions/experiment")

# Create a data frame mapping Image to true numerators and denominators
true_values <- data.frame(
  Image = c("P1.png", "P2.png", "P3.png", "P4.png", "P5.png", "P6.png", "P7.png", "P8.png", "P9.png", "P10.png", 
            "P11.png", "P12.png", "CC1.png", "CC2.png", "CC3.png", "CC4.png", "CC5.png", "CC6.png", 
            "CC7.png", "CC8.png", "CC9.png", "CC10.png", "CC11.png", "CC12.png", 
            "IC1.png", "IC2.png", "IC3.png", "IC4.png", "IC5.png", "IC6.png", 
            "IC7.png", "IC8.png", "IC9.png", "IC10.png", "IC11.png", "IC12.png"),
  true_final_numerator = c(31, 28, 21, 71, 31, 49, 67, 41, 33, 43, 23, 51,
                           29, 41, 89, 49, 29, 37, 19, 25, 47, 37, 19, 73,
                           29, 41, 89, 49, 29, 37, 19, 25, 47, 37, 19, 73),
  true_final_denominator = c(20, 15, 20, 12, 24, 24, 9, 20, 14, 12, 18, 28,
                             4, 21, 36, 16, 18, 30, 10, 21, 14, 16, 24, 12,
                             4, 21, 36, 16, 18, 30, 10, 21, 14, 16, 24, 12)
)

# Assuming your dataframe with participant data is called 'df'
# Merge true values into the participant dataframe
combined_data <- merge(combined_data, true_values, by = "Image", all.x = TRUE)

# Calculate 'Correct' column by comparing the divisions
combined_data$Correct <- with(combined_data, 
                   (finalNumerator / finalDenominator) == (true_final_numerator / true_final_denominator))

#### -- Correctness by problem type (pretest vs conditions)
# Step 1: Create a new column to classify image types (P, CC, IC)
combined_data$image_type <- ifelse(grepl("^P", combined_data$Image), "P",
                        ifelse(grepl("^CC", combined_data$Image), "CC", "IC"))

# Step 2: Calculate percentage of correct responses per image type per participant
# Group by Participant and Image Type, calculate percentage of correct responses
cor_by_condition <- combined_data %>%
  group_by(Part_ID, image_type) %>%
  summarise(percent_correct = mean(Correct) * 100) %>%
  ungroup()

# Step 3: Reshape the data to have participants as rows and image types (P, CC, IC) as columns
cor_by_condition <- cor_by_condition %>%
  pivot_wider(names_from = Part_ID, values_from = percent_correct, values_fill = list(percent_correct = 0))

#### -- Correct by problem (CC and IC separately)
# Step 1: Reshape the data to combine rows by Image and create columns for each participant's correctness
cor_by_prob_in_cond <- combined_data %>%
  group_by(Part_ID, Image) %>%
  summarise(percent_correct = Correct) %>%
  ungroup()

# Step 2: Reshape the data to have participants as rows and image types (P, CC, IC) as columns
cor_by_prob_in_cond <- cor_by_prob_in_cond %>%
  pivot_wider(names_from = Part_ID, values_from = percent_correct, values_fill = list(percent_correct = 0))

# Step 3: Calculate mean correctness across participants for each image
cor_by_prob_in_cond <- cor_by_prob_in_cond %>%
  rowwise() %>%
  mutate(mean_correct = mean(c_across(where(is.logical))) * 100)

#### -- Correct by problem (CC and IC combined)
# Step 1: Create a new column that merges the corresponding CC and IC problems into Cond
combined_data <- combined_data %>%
  mutate(Raw_problem = case_when(
    grepl("CC1.png|IC1.png", Image) ~ "Cond1",
    grepl("CC2.png|IC2.png", Image) ~ "Cond2",
    grepl("CC3.png|IC3.png", Image) ~ "Cond3",
    grepl("CC4.png|IC4.png", Image) ~ "Cond4",
    grepl("CC5.png|IC5.png", Image) ~ "Cond5",
    grepl("CC6.png|IC6.png", Image) ~ "Cond6",
    grepl("CC7.png|IC7.png", Image) ~ "Cond7",
    grepl("CC8.png|IC8.png", Image) ~ "Cond8",
    grepl("CC9.png|IC9.png", Image) ~ "Cond9",
    grepl("CC10.png|IC10.png", Image) ~ "Cond10",
    grepl("CC11.png|IC11.png", Image) ~ "Cond11",
    grepl("CC12.png|IC12.png", Image) ~ "Cond12",
    TRUE ~ Image  # Keep other problems as they are
  ))

# Step 2: Group by Raw_problem and calculate the number of participants who solved each problem correctly
cor_by_prob <- combined_data %>%
  group_by(Raw_problem) %>%
  summarise(
    total_responses = n(),                    # Total number of responses per problem
    correct_responses = sum(Correct == 1),    # Total number of correct responses
    percent_correct = (correct_responses / total_responses) * 100  # Percentage of correct responses
  )

#### -- Time by problem type (pretest vs conditions)
# Step 2: Calculate percentage of correct responses per image type per participant
# Group by Participant and Image Type, calculate percentage of correct responses
# Convert the time columns to 'hms' format
#combined_data$trialElapsedTimeFormatted <- as_hms(combined_data$trialElapsedTimeFormatted)

time_by_condition <- combined_data %>%
  group_by(Part_ID, image_type) %>%
  summarise(mean_time = mean(trialElapsedTime)) %>%
  ungroup()

#### -- Time by problem
# Step 1: Reshape the data to combine rows by Image and create columns for each participant's correctness
time_by_prob_raw <- combined_data %>%
  group_by(Part_ID, Image) %>%
  summarise(time = trialElapsedTime) %>%
  ungroup()

# Step 2: Reshape the data to have participants as rows and image types (P, CC, IC) as columns
time_by_prob <- time_by_prob_raw %>%
  pivot_wider(names_from = Part_ID, values_from = time, values_fill = list(time = 0))

time_by_prob <- time_by_prob %>%
  mutate(across(everything(), ~ ifelse(. == "00:00:00", NA, .)))

# Step 3: Calculate mean correctness across participants for each image
time_by_prob <- time_by_prob %>%
  rowwise() %>%
  mutate(mean_time = mean(c_across(where(is.numeric)), na.rm = TRUE) * 100)

time_by_prob <- time_by_prob_raw %>%
  group_by(Image) %>%
  summarise(time = time, na.rm = TRUE) %>%
  ungroup()


