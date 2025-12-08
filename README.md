Replication files for Schneider Lecy et al (2025) "Estimating output value added of the world's agrifood systems"

Replication Workflow Creator: Kate Schneider Lecy

Purpose: Replicate the workflow to create the dataset and analyses for Schneider et al (2024), "Estimating output value added of global agrifood systems" 

Last updated: 17 November 2025

License: CC-BY-4.0 (see https://creativecommons.org/licenses/by/4.0/  for terms)

Archived Dataset DOI: 

- "Classification and metadata" spreadsheet lists original source and download instructions for all raw datasets.
- Raw data saved in "Input data"
    - The Input-Output datasets in the "Eora_ExtractedData" subfolder of "Input Data" were created by the ASTAR-Labor project and provided as a collaboration for this paper. They were created by first balancing the Eora-26 harmonized input-output tables for 1995-2021. The specific data files created for this project were reshaped from the balanced IO tables using the Python code contained in the replication file "4a_Eora Extraction.Rmd".
- The R markdown files in the "Scripts" folder describe and code all the data management, data set creation, and analysis. Scripts 1-5 are the data management scripts to calculate value added in agrifood systems. Script 6 calculates value added per worker, bringing in the employmment dataset from Davis et al (2023). Replication files for the PNAS manuscript create the tables and figures in the paper starting from the final dataset created at the conclusion of Script 5. Replication files for the ESS Working Paper create the tables and figures in the ESS working paper and include value added per worker, starting from the final dataset created at the conclusion of Script 6.
- The "Output datasets" folder contains the resulting time series datasets created by this project.
- All ".bib" files contained in the root folder are Zotero .bib files with all literature saved to the public, curated literature folder also created for this project. The .bib files are part of the R project to allow for citation of sources within the R Markdown document to reference specific methodological steps and decisions.
    - The Zotero library can be found at https://www.zotero.org/groups/5027907/agrifood_value_added/library
- See the "Support files and scripts" folder for additional documentation about the data used in this project. Occassionaly files in this folder are specifically mentioned in the "Classification and metadata" spreadsheet as well as in the annotations to the R markdown file. 

Send any questions to: k.schneider.lecy {at} asu {dot} edu
