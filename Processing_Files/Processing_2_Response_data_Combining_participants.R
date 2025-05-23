# Install required packages if not already installed
if (!require("dplyr")) install.packages("dplyr")
if (!require("readr")) install.packages("readr")
if (!require("tidyr")) install.packages("tidyr")
if (!require("ggplot2")) install.packages("ggplot2")
if (!require("hms")) install.packages("hms")

# Load required libraries
library(dplyr)
library(readr)
library(tidyr)
library(ggplot2)
library(hms)

rm(list = ls())

### --- Uploading gaze datasets

# Download file
setwd("~/Documents/Data_Analysis/Eye_tracking_fractions/Code/Processing_files/Pavlovia_Data")

# Define files to exclude
files_to_exclude <- c("wpi6172z971436g3640.csv", "wpi61740524s9759r04.csv",
                      "wpi61746552e98473o3.csv", "wpi617m4630v4861669.csv",
                      "wpi6o1d733879690572.csv", "wpi6r1745874r291842.csv")

# Get all CSV files except the excluded ones
file_paths <- list.files(pattern = "[.]csv$", full.names = TRUE) %>%
  subset(!basename(.) %in% files_to_exclude)

# Initialize an empty data frame to store the combined data
combined_data <- data.frame()

# Iterate over each file and process
for (i in seq_along(file_paths)) {

  # Load the CSV file with specified column types
  df <- read_csv(file_paths[i], 
                 col_types = cols(
                 pid = col_character(),
                 date = col_character(),
                 OS = col_character(),
                 frameRate = col_double(),
                 Image = col_character(),
                 HOO_Position = col_factor(),
                 Simplification = col_factor(),
                 finalNumerator = col_character(),
                 finalDenominator = col_character(),
                 true_final_numerator = col_double(),
                 true_final_denominator = col_double(),
                 TaskGazeArray = col_character(),
                 Condition = col_character(),
                 trialElapsedTime = col_double(),
                 problem_Order = col_double(),
                 .default = col_double()  # all other columns as double
                 ),
                 show_col_types = FALSE)

  # Correct the finalNumerator and finalDenominator columns in specific images in specific participants
  df <- df %>%
    mutate(
      finalNumerator = ifelse(pid == "wpi6174493xg0886649" & Image == "P7.png", as.numeric(67),
                            ifelse(pid == "wpi6174b6550g984996" & Image == "CC8.png", as.numeric(25), 
                                   ifelse (pid == "wpi617n3308449928h0" & Image == "CC7.png", as.numeric(38), finalNumerator))),
      finalDenominator = ifelse(pid == "wpi6174493xg0886649" & Image == "P7.png", as.numeric(9), 
                              ifelse(pid == "wpi617n3308449928h0" & Image == "CC7.png", as.numeric(20), finalDenominator)))

  # Compare only simple numeric values, NA for expressions or non-numeric
  df <- df %>%
    mutate(
      Correct = ifelse(
      !grepl("[^0-9.-]", finalNumerator) & !grepl("[^0-9.-]", finalDenominator),
      as.numeric(finalNumerator)/as.numeric(finalDenominator) == true_final_numerator/true_final_denominator,
      FALSE
    )
  ) %>%
    # Replace any remaining NA values in Correct with FALSE
    mutate(
      Correct = replace_na(Correct, FALSE) # as some 0s and NAs in finalNumerators gave as NAs in "Correct"
    )

  # Select only the relevant columns
  df <- df %>% select(pid, date, Condition, Image, problem_Order,
                    HOO_Position, Simplification, trialElapsedTime,
                    finalNumerator, finalDenominator,
                    true_final_numerator, true_final_denominator,
                    Correct
                    )

  # Append to the combined data frame
  combined_data <- bind_rows(combined_data, df)
}

# Save the combined data to a new CSV file
setwd("~/Documents/Data_Analysis/Eye_tracking_fractions/Code/Output_files")
write_csv(combined_data, "Response_data.csv")
