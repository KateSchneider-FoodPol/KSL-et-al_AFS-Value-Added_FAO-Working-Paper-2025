################################################################################ 
## VALUE ADDED IN AGRIFOOD SYSTEMS SUPPLY USE TABLE DATA MANAGEMENT ############ 
## Created by: Kate Schneider
## Last revised: 
Sys.Date()
## Contact: Kate Schneider, kschne29@jhu.edu
## Input datasets (Main aggregates): https://unstats.un.org/unsd/snaama/Basic

################################################################################ 

################################################################################ 
# HOUSEKEEPING
################################################################################ 
setwd("C:\\Users\\Kate S\\OneDrive - Johns Hopkins\\AFS Value Added 2023\\Data")

# Install packages
# install.packages(c("httr", "jsonlite", "tidyverse", "haven", "janitor"))

# Load packages #############################################################
library(dplyr)
Packages <- c("tidyverse", "haven", "janitor", "httr", "jsonlite", "purrr", "Hmisc")
lapply(Packages, require, character.only = TRUE)
################################################################################ 

################################################################################ 
# DETERMINE AVAILABLE DATA VIA UNSTATS API
################################################################################ 

res = GET("https://unstats.un.org/unsd/amaapi/api/Series")
rawToChar(res$content)
series = fromJSON(rawToChar(res$content))

res = GET("https://unstats.un.org/unsd/amaapi/api/Country")
  rawToChar(res$content)
  countries = fromJSON(rawToChar(res$content))
  names(countries)
countries <- countries %>% select(countryCode, countryName) %>%
  mutate(M49_code = countryCode,
         country = countryName) %>%
  select(-c("countryCode", "countryName"))

# Remove aggregate groups and historical states that will not have data in the past 5 years (the only years called by the API)
countries$country
list_to_rm <- c("Former Ethiopia", "Former USSR", "Middle Africa", "Southern Asia", "Western Europe", "Yemen: Former Democratic Yemen", "Africa", "Americas",
                "Bosnia and Herzegovina", "Caribbean", "Central America", "Former Netherlands Antilles", "Former Yugoslavia", "South-Eastern Asia", "Oceania",
                "Southern Europe", "Western Africa", "World", "Yemen: Former Yemen Arab Republic", "Australia and New Zealand", "Eastern Asia", "Europe", "Polynesia",
                "Former Czechoslovakia", "Former Sudan", "Latin America and the Caribbean", "Northern Africa", "South America", "Southern Africa", "Western Asia",
                "Sub-Saharan Africa", "Central Asia", "Micronesia", "Melanesia", "Northern America", "Asia", "Eastern Africa", "Eastern Europe", "Northern Europe")
                
countries <- countries[!countries$country %in% list_to_rm, ]
countries$country

# Define elements for API pulls
base <- 'https://unstats.un.org/unsd/amaapi/api/Data/limited/'
code <- as.list(countries$M49_code)
################################################################################ 


################################################################################
## DEFINE CUSTOM FUNCTION TO ADD COLUMNS IF THEY DO NOT EXISTS
################################################################################ 
add_cols <- function(df, cols) {
      add <- cols[!cols %in% names(df)]
      if(length(add) !=0 ) df[add] <- NA
      return(df)
    }
################################################################################ 

################################################################################
##### MAIN AGGREGATES (Series = 22) ########################################################## 
################################################################################ 
series
# Create empty data frame
    df = data.frame()

# Define series
series_select <- '/22' ##  Value Added by Economic Activity, at current prices - US Dollars
        
# Get all countries in a loop and create master dataset
    for(i in 1:length(code)) {
      print(code[[i]])
      # Build the API URL with the country code for series 22 (value added by economic activity, current dollars)
      API_URL <- paste0(base,code[[i]],series_select)
      # Store the raw and processed API results in temporary objects
      temp_raw <- GET(API_URL)
      temp_list <- fromJSON(rawToChar(temp_raw$content), flatten = TRUE)
      # Convert to dataframe
      # Select and reshape
      temp_list <- temp_list %>% select(-c(serieCode, itemId, observationNote, unit)) %>% 
        rename(year = fiscalYear,
               M49_code = countryCode,
               country = countryName)
      temp_list$itemName <- as.factor(temp_list$itemName)
      temp_list <- temp_list %>%
        pivot_wider(names_from = itemName, values_from = observationValue)
      
      # Add columns if they don't already exist
      temp_list <- add_cols(temp_list, c("Agriculture, hunting, forestry, fishing (ISIC A-B)", "Construction (ISIC F)",                                    
                                         "Manufacturing (ISIC D)", "Mining, Manufacturing, Utilities (ISIC C-E)",               
                                         "Other Activities (ISIC J-P)", "Total Value Added",                                        
                                         "Transport, storage and communication (ISIC I)", "Wholesale, retail trade, restaurants and hotels (ISIC G-H)"))
      
      # Reorder
      col_order <- c("M49_code", "serieName", "country", "year",
                     "Agriculture, hunting, forestry, fishing (ISIC A-B)", "Construction (ISIC F)",                                    
                     "Manufacturing (ISIC D)", "Mining, Manufacturing, Utilities (ISIC C-E)",               
                     "Other Activities (ISIC J-P)", "Total Value Added",                                        
                     "Transport, storage and communication (ISIC I)", "Wholesale, retail trade, restaurants and hotels (ISIC G-H)")
      temp_list <- temp_list[, col_order]
      
      # Add to dataframe
      df <- rbind(df, temp_list)
    }
      ValAdded_data <- df %>% rename("Value Added_Agriculture, hunting, forestry, fishing" = "Agriculture, hunting, forestry, fishing (ISIC A-B)", 
                                     "Value Added_Construction" = "Construction (ISIC F)",                                    
                                     "Value Added_Manufacturing" = "Manufacturing (ISIC D)",
                                     "Value Added_Mining, Manufacturing, Utilities" = "Mining, Manufacturing, Utilities (ISIC C-E)",               
                                     "Value Added_Other" = "Other Activities (ISIC J-P)", 
                                     "Value Added_Total" = "Total Value Added",                                        
                                     "Value Added_Transport, storage, Comms" = "Transport, storage and communication (ISIC I)", 
                                     "Value Added_Trade, restaurants, hotels" = "Wholesale, retail trade, restaurants and hotels (ISIC G-H)")
      label(ValAdded_data$`Value Added_Agriculture, hunting, forestry, fishing`) <- "Value Added by Economic Activity, at current prices - US Dollars"
      label(ValAdded_data$`Value Added_Construction`) <- "Value Added by Economic Activity, at current prices - US Dollars"
      label(ValAdded_data$`Value Added_Manufacturing`) <- "Value Added by Economic Activity, at current prices - US Dollars"
      label(ValAdded_data$`Value Added_Mining, Manufacturing, Utilities`) <- "Value Added by Economic Activity, at current prices - US Dollars"
      label(ValAdded_data$`Value Added_Other`) <- "Value Added by Economic Activity, at current prices - US Dollars"
      label(ValAdded_data$`Value Added_Total`) <- "Value Added by Economic Activity, at current prices - US Dollars"
      label(ValAdded_data$`Value Added_Transport, storage, Comms`) <- "Value Added by Economic Activity, at current prices - US Dollars"
      label(ValAdded_data$`Value Added_Trade, restaurants, hotels`) <- "Value Added by Economic Activity, at current prices - US Dollars"
      ValAdded_data <- ValAdded_data %>% select(-c(serieName))
      
################################################################################ 
    
################################################################################
##### GDP (Series = 2) ########################################################## 
################################################################################ 
series
# Create empty data frame
df = data.frame()

# Define series
series_select <- '/2' ##  GDP, at current prices - US Dollars

# Get all countries in a loop and create master dataset
for(i in 1:length(code)) {
  print(code[[i]])
  # Build the API URL with the country code for series 2
  API_URL <- paste0(base,code[[i]],series_select)
  # Store the raw and processed API results in temporary objects
  temp_raw <- GET(API_URL)
  temp_list <- fromJSON(rawToChar(temp_raw$content), flatten = TRUE)
  # Convert to dataframe
  # Select and reshape
  temp_list <- temp_list %>% select(-c(serieCode, itemId, observationNote, unit)) %>% 
    rename(year = fiscalYear,
           M49_code = countryCode,
           country = countryName)
  temp_list$itemName <- as.factor(temp_list$itemName)
  temp_list <- temp_list %>%
    rename(GDP = observationValue)

  # Add to dataframe
  df <- rbind(df, temp_list)
}

GDP_data <- df %>% select(-c(itemName, serieName))
label(GDP_data$GDP) <- "GDP, at current prices - US Dollars"

################################################################################ 

################################################################################
##### Population (Series = 42) ########################################################## 
################################################################################ 
series
# Create empty data frame
df = data.frame()

# Define series
series_select <- '/42' ##  Population

# Get all countries in a loop and create master dataset
for(i in 1:length(code)) {
  print(code[[i]])
  # Build the API URL with the country code for series 42
  API_URL <- paste0(base,code[[i]],series_select)
  # Store the raw and processed API results in temporary objects
  temp_raw <- GET(API_URL)
  temp_list <- fromJSON(rawToChar(temp_raw$content), flatten = TRUE)
  # Convert to dataframe
  # Select and reshape
  temp_list <- temp_list %>% select(-c(serieCode, itemId, observationNote, unit)) %>% 
    rename(year = fiscalYear,
           M49_code = countryCode,
           country = countryName)
  temp_list$itemName <- as.factor(temp_list$itemName)
  temp_list <- temp_list %>%
    rename(Population = observationValue)
  
  # Add to dataframe
  df <- rbind(df, temp_list)
}

Pop_data <- df %>% select(-c(itemName, serieName))
label(Pop_data$Population) <- "Population (number of persons)"

################################################################################

################################################################################ 
## COMBINE DATASETS ############################################################
################################################################################ 

VA_data_all <- merge(Pop_data, GDP_data, by=c("country", "year", "M49_code"))
VA_data_all <- merge(VA_data_all, ValAdded_data, by=c("country", "year", "M49_code"))
VA_data_all <- VA_data_all %>% relocate(`Value Added_Total`, .after = GDP)

# Dataset characterstics
table(VA_data_all$year)
table(VA_data_all$country)