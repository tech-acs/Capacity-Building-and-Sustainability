# Track 2 reference dashboard (Modules 5-6), R/Shiny version.
#
# Run from the repo root, after running data/make_sample_data.py:
#
#   Rscript -e "shiny::runApp('apps/shiny_app.R')"
#
# Two filters (province, district), one trend chart, one district-average
# bar chart, and one AI-assisted summary built strictly to the schema-only /
# local-execution / summary-only pattern from Module 6 (see the notebook for
# the fuller walkthrough — call_llm() here is the same kind of stand-in).

library(shiny)
library(tidyverse)

df <- read_csv("data/processed/track2_dataset.csv", show_col_types = FALSE)

call_llm <- function(prompt) {
  # Stand-in for a real LLM call, see Module 6. Only the schema in `prompt`
  # would ever reach a real provider; this fixed reply keeps the demo
  # runnable with no API key.
  "result <- frame |> group_by(district) |> summarise(value = mean(value)) |> arrange(desc(value)) |> head(3)"
}

ui <- fluidPage(
  titlePanel("Regional Analytic Hub — Prototype"),
  tags$p(em("Synthetic data. See data/README.md before treating any number here as real.")),
  sidebarLayout(
    sidebarPanel(
      selectInput("province", "Province", sort(unique(df$province))),
      uiOutput("district_ui"),
      actionButton("summarize", "Generate summary")
    ),
    mainPanel(
      fluidRow(
        column(8, h4("Trend"), plotOutput("trend")),
        column(4, h4("By district"), plotOutput("by_district"))
      ),
      h4("AI-assisted summary (schema-only pattern)"),
      tableOutput("ai_summary")
    )
  )
)

server <- function(input, output, session) {
  output$district_ui <- renderUI({
    choices <- df |> filter(province == input$province) |> pull(district) |> unique() |> sort()
    checkboxGroupInput("district", "District", choices = choices, selected = choices)
  })

  filtered <- reactive({
    req(input$district)
    df |> filter(province == input$province, district %in% input$district)
  })

  output$trend <- renderPlot({
    filtered() |>
      group_by(date) |>
      summarise(value = mean(value), .groups = "drop") |>
      ggplot(aes(date, value)) +
      geom_line(color = "#1D6E73", linewidth = 1) +
      theme_minimal()
  })

  output$by_district <- renderPlot({
    filtered() |>
      group_by(district) |>
      summarise(value = mean(value), .groups = "drop") |>
      ggplot(aes(x = fct_reorder(district, value), y = value)) +
      geom_col(fill = "#1D6E73") +
      coord_flip() +
      labs(x = NULL) +
      theme_minimal()
  })

  observeEvent(input$summarize, {
    frame <- filtered()
    schema <- sapply(frame, class)
    prompt <- paste0("Schema only: ", toString(schema), ". Return code for the top 3 districts by mean value.")
    generated_code <- call_llm(prompt)
    eval(parse(text = generated_code))
    output$ai_summary <- renderTable(result)
  })
}

shinyApp(ui, server)
