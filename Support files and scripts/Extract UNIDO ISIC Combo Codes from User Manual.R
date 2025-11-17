# This script extracts Annex III from [@unidoINDSTAT22020ISIC2020]
# Downloaded from https://stat.unido.org/pdf/Inst32-online-UserGuide_2402619451797638449.pdf - but this is no longer available online as of 31 May 2024

# Load libraries
library("pdftools")
library("tidyverse")
library("stringr")

# Load document 
pdf_file <- ("./Support files and scripts/INDSTAT_UGUIDE.pdf")
txt <- map(pdf_file, ~ pdftools::pdf_text(.x)[26:29])
txt <- unlist(txt)

# Remove the text components
rep_str = c('Annex III - ISIC Combination Code List'='',
            'Many countries report data as a combination of two or more 2-digit ISIC categories. The'='',
            'codes used to identify such ISIC combinations are listed below:'='',
            'Rev.3 Code'='',
            'ISIC Components'='')
txt <- str_replace_all(txt, rep_str)
print(txt)
class(txt)

# Extract data from table
table <- read.delim(text = txt, sep = "\t", header = FALSE)
class(table)

# Drop empty rows and page numbers
table <- table %>%  filter(!row_number() %in% c(1,2,3,37,38,75,76,113,114,127))

# Remove leading white space in first 33 rows
fix <- table %>% filter(row_number() %in% c(1:33)) %>%
  mutate(across(everything(),  trimws, which = "left"))

# Merge fixed rows with the rest of the table
table <- table %>% filter(!row_number() %in% c(1:33))
table <- rbind(fix, table)

# Now separate into multiple columns
table[c('isiccomb', 'Combined_Codes')] <- str_split_fixed(table$V1, ' ', 2)

# Drop the merged variable
table <- table %>% select(-c(V1))

# Trim leading white space from the Combined_Codes column
ComboCodes <- table %>% mutate(across(Combined_Codes,  trimws, which = "left"))

# Save data frame to project
save(table, file = "./Support files and scripts/INDSTAT_ISICComboCodes.RData")

# Export to excel
writexl::write_xlsx(table, path = "./Support files and scripts/INDSTAT_ISICComboCodes.xlsx")

# Remove intermediate dataframes
rm(txt, fix, table)

