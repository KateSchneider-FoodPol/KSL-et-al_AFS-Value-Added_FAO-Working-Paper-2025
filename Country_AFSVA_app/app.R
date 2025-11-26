# ============================================================
# ValueAdded_Shiny.R  —  Shiny app to explore results by country
# ============================================================

library(shiny)
library(tidyverse)
library(flextable)
library(officer)
library(rsconnect)

# Run once to create directory
# dir.create("Country_AFSVA_app")
# dir.create("Country_AFSVA_app/data")
# file.copy("Output Datasets/AFS_ValueAdded.RData", "Country_AFSVA_app/data/AFS_ValueAdded.RData")


# ================================================================
# LOAD DATA
# ================================================================
# self-contained dataset
AFS_ValueAdded <- get(load("data/AFS_ValueAdded.RData"))

# Rename aggregate manufacturing for clarity
AFS_ValueAdded <- AFS_ValueAdded %>%
  mutate(ISIC_Item = case_when(ISIC_Item == "Manufacturing" ~ "Manufacturing, Total (not disaggregable)",
         TRUE ~ ISIC_Item))

years_available <- sort(unique(AFS_ValueAdded$Year))
isic_items      <- sort(unique(AFS_ValueAdded$ISIC_Item))

# ================================================================
# TABLE-BUILDING FUNCTION
# ================================================================
make_country_table <- function(data, country_name, year_sel,
                               isic_filter = NULL,
                               show_continent_col = TRUE) {
  
  # Filter to selected year
  dat_year <- data %>%
    filter(Year == year_sel,
           !is.na(ISIC_Item),
           !is.na(country))
  
  # Determine continent for the selected country
  continent_name <- dat_year %>%
    filter(country == country_name) %>%
    distinct(UN_continental_region) %>%
    pull() %>%
    .[1]
  
  # ISIC filter
  if (!is.null(isic_filter) && length(isic_filter) > 0) {
    dat_year <- dat_year %>%
      filter(ISIC_Item %in% isic_filter)
  }
  
  # Build table:
  # - Country value
  # - Global total
  tabledata <- dat_year %>%
    group_by(ISIC_Item) %>%
    summarise(
      Country = sum(if_else(country == country_name,
                            ValueAdded_cUSD, 0),
                    na.rm = TRUE),
      Global  = sum(ValueAdded_cUSD, na.rm = TRUE),
      .groups = "drop"
    )
  
  # Remove all-zero rows
  tabledata <- tabledata %>%
    filter(Country != 0 | Global != 0)
  
  # Convert to billions
  tabledata <- tabledata %>%
    mutate(
      Country = Country / 1e9,
      Global  = Global  / 1e9
    )
  
  # Rename
  tabledata <- tabledata %>%
    rename("ISIC Category" = ISIC_Item)
  
  # Add continent column
  if (show_continent_col && !is.na(continent_name)) {
    tabledata <- tabledata %>%
      mutate(Continent = continent_name) %>%
      select(`ISIC Category`, Country, Continent, Global)
  } else {
    tabledata <- tabledata %>%
      select(`ISIC Category`, Country, Global)
  }
  
  # TOTAL row
  numeric_cols <- sapply(tabledata, is.numeric)
  
  totals_row <- tabledata %>%
    summarise(across(where(is.numeric), ~ sum(.x, na.rm = TRUE))) %>%
    mutate(`ISIC Category` = "Total")
  
  if ("Continent" %in% names(tabledata)) {
    totals_row <- totals_row %>%
      mutate(Continent = continent_name) %>%
      select(names(tabledata))
  } else {
    totals_row <- totals_row %>%
      select(any_of(names(tabledata)))
  }
  
  tabledata <- bind_rows(tabledata, totals_row)
  
  # Round + clean NA
  tabledata <- tabledata %>%
    mutate(across(where(is.numeric), ~ round(.x, 2))) %>%
    mutate(across(everything(), ~ ifelse(is.na(.x), "--", as.character(.x))))
  
  # Make flextable
  flextable(tabledata) %>% autofit()
}

# ================================================================
# UI
# ================================================================
ui <- fluidPage(
  titlePanel("Country Agrifood System Value Added Explorer"),
  
  sidebarLayout(
    sidebarPanel(
      selectInput("year", "Year:",
                  choices = years_available,
                  selected = max(years_available)),
      
      selectInput("ctry", "Country:",
                  choices = sort(unique(AFS_ValueAdded$country))),
      
      selectizeInput(
        "isic", "Filter ISIC categories:",
        choices  = isic_items,
        selected = isic_items,
        multiple = TRUE,
        options = list(placeholder = "All")
      ),
      
      checkboxInput("show_continent",
                    "Show continent column", TRUE),
      
      downloadButton("download_docx", "Download DOCX")
    ),
    
    mainPanel(
      h3(textOutput("caption")),
      uiOutput("va_table")
    )
  )
)

# ================================================================
# SERVER
# ================================================================
server <- function(input, output, session) {
  
  # Update country list when year changes
  observeEvent(input$year, {
    ctries <- AFS_ValueAdded %>%
      filter(Year == input$year) %>%
      distinct(country) %>%
      arrange(country) %>%
      pull()
    
    selected_ctry <- if (input$ctry %in% ctries) input$ctry else ctries[1]
    updateSelectInput(session, "ctry",
                      choices = ctries,
                      selected = selected_ctry)
  })
  
  # Reactive table
  country_table <- reactive({
    make_country_table(
      data = AFS_ValueAdded,
      country_name = input$ctry,
      year_sel = input$year,
      isic_filter = input$isic,
      show_continent_col = isTRUE(input$show_continent)
    )
  })
  
  # Caption
  output$caption <- renderText({
    paste0("Value added in agrifood systems (billions of constant USD), ",
           input$ctry, ", ", input$year)
  })
  
  # Render flextable
  output$va_table <- renderUI({
    flextable::htmltools_value(country_table())
  })
  
  # DOCX download
  output$download_docx <- downloadHandler(
    filename = function() {
      paste0("AFSVA_", gsub(" ", "_", input$ctry),
             "_", input$year, ".docx")
    },
    content = function(file) {
      save_as_docx(country_table(), path = file)
    }
  )
}

# ================================================================
# RUN APP
# ================================================================
shinyApp(ui, server)
