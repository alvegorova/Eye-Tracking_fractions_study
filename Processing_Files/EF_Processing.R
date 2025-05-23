#install.packages("remotes")
#remotes::install_github("joaquinanguera/aceR")

#install.packages("devtools")
#devtools::install_github("joaquinanguera/aceR")

library(aceR)
library(dplyr)
library(stringr)

setwd("~/Documents/Data_Analysis/Eye_tracking_fractions/Code/")

path_data<-("Input_files/RawData:ACE")

# Remove problematic files before processing
file.remove(file.path(path_data, "None.csv"))

tryCatch({
  EF_data<-proc_ace_complete(path_in=path_data, path_out=NULL, data_type="explorer")
}, error = function(e) {
  print(paste("Error in processing:", e$message))
})

PID<-read.csv("Input_files/participant_ids.csv")

# Print debugging information
print("Structure of EF_data:")
print(str(EF_data))
print("Unique PIDs in EF_data:")
print(unique(EF_data$pid))
print("Structure of PID dataframe:")
print(str(PID))
print("Unique PIDs in PID dataframe:")
print(unique(PID$pid))

# Merge the data based on the "pid" column
merged_ACE_data <- EF_data %>%
  inner_join(PID, by = "pid")

# Write the merged data to a new file
write.csv(merged_ACE_data, "Output_files/EF_data_combined.csv", row.names = FALSE)

# Check file
EF_data_combined<-read.csv("Output_files/EF_data_combined.csv")
summary(EF_data_combined)
