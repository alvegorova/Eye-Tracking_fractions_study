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
file_paths <- list.files(pattern = "*.csv", full.names = TRUE)

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
                   finalNumerator = col_double(),
                   finalDenominator = col_double(),
                   true_final_numerator = col_double(),
                   true_final_denominator = col_double(),
                   TaskGazeArray = col_character(),
                   Condition = col_character(),
                   trialElapsedTime = col_double(),
                   problem_Order = col_double(),
                   .default = col_double(),  # all other columns as double
                 ),
                 show_col_types = FALSE)

  # Round values in arousal and value columns
  df$arousal_Time_PrePre <- round(df$arousal_Time_PrePre, 1)
  df$arousal_Time_Pretest_3 <- round(df$arousal_Time_Pretest_3, 1)
  df$arousal_Time_Pretest_7 <- round(df$arousal_Time_Pretest_7, 1)
  df$arousal_Time_Pretest_12 <- round(df$arousal_Time_Pretest_12, 1)
  df$arousal_Time_Exp_2 <- round(df$arousal_Time_Exp_2, 1)
  df$arousal_Time_Exp_12 <- round(df$arousal_Time_Exp_12, 1)

  df$valence_Time_PrePre <- round(df$valence_Time_PrePre, 1)
  df$valence_Time_Pretest_3 <- round(df$valence_Time_Pretest_3, 1)
  df$valence_Time_Pretest_7 <- round(df$valence_Time_Pretest_7, 1)
  df$valence_Time_Pretest_12 <- round(df$valence_Time_Pretest_12, 1)
  df$valence_Time_Exp_2 <- round(df$valence_Time_Exp_2, 1)
  df$valence_Time_Exp_12 <- round(df$valence_Time_Exp_12, 1)
 
  ### Calculate mean math anxiety values

  ## General math anxiety
  MA <- df %>% select(
      MA_EM_1, MA_EM_2, MA_EM_3, MA_EM_4,
      MA_WO_1, MA_WO_2, MA_WO_3, MA_WO_4,
      MA_EV_1, MA_EV_2, MA_EV_3) %>% 
    unlist() %>%
    mean(na.rm = TRUE)

  # Assign value to a column
  df <- df %>% mutate(MA = round(MA, 1))

  ## Emotional 
  MA_EM_mean <- df %>% 
    select(MA_EM_1, MA_EM_2, MA_EM_3, MA_EM_4) %>% 
    unlist() %>%
    mean(na.rm = TRUE)

  # Assign value to a column
  df <- df %>% mutate(MA_EM_mean = round(MA_EM_mean, 1))

  ## Worry 
  MA_WO_mean <- df %>% 
    select(MA_WO_1, MA_WO_2, MA_WO_3, MA_WO_4) %>% 
    unlist() %>%
    mean(na.rm = TRUE)

  # Assign value to a column
  df <- df %>% mutate(MA_WO_mean = round(MA_WO_mean, 1))

  ## Evaluation 
  MA_EV_mean <- df %>% 
    select(MA_EV_1, MA_EV_2, MA_EV_3) %>% 
    unlist() %>%
    mean(na.rm = TRUE)

  # Assign value to a column
  df <- df %>% mutate(MA_EV_mean = round(MA_EV_mean, 1))

  # Cut extra columns
  df <- df %>% head(1)
  
  # Select only the relevant columns
  df <- df %>% select(pid, date, Condition, OS,
    age, gender, race_ethnicity,
    MA,
    MA_EM_1, MA_EM_2, MA_EM_3, MA_EM_4, MA_EM_mean,
    MA_WO_1, MA_WO_2, MA_WO_3, MA_WO_4, MA_WO_mean,
    MA_EV_1, MA_EV_2, MA_EV_3, MA_EV_mean,
    arousal_PrePre, arousal_Time_PrePre,
    arousal_Pretest_3, arousal_Time_Pretest_3,
    arousal_Pretest_7, arousal_Time_Pretest_7,
    arousal_Pretest_12, arousal_Time_Pretest_12,
    arousal_Exp_2, arousal_Time_Exp_2,
    arousal_Exp_12, arousal_Time_Exp_12,
    valence_PrePre, valence_Time_PrePre,
    valence_Pretest_3, valence_Time_Pretest_3,
    valence_Pretest_7, valence_Time_Pretest_7,
    valence_Pretest_12, valence_Time_Pretest_12,
    valence_Exp_2, valence_Time_Exp_2,
    valence_Exp_12, valence_Time_Exp_12
  )

  # Append to the combined data frame
  combined_data <- bind_rows(combined_data, df)
}

# Save the combined data to a new CSV file
setwd("~/Documents/Data_Analysis/Eye_tracking_fractions/Code/Output_files")
write_csv(combined_data, "MA_Demo_Student_data.csv")
