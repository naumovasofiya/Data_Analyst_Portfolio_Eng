# Visual Snow Syndrome (VSS) Gamma Power Analysis
# Comprehensive script for analyzing gamma power and frequency changes

library(ggplot2)
library(dplyr)
library(broom)
library(nlme)
library(purrr)
library(tidyr)
library(segmented)

# =============================================
# Configuration and Data Loading
# =============================================

# Set paths and parameters
datapath <- '{path_to_data}'
filename <- 'gamma_all.csv'
file <- paste(datapath, filename, sep = "")
output_path <- datapath  # Change if different output location needed

# Analysis parameters
max_trials <- 137
min_trials <- 0
outlier_coeff <- 2  # IQR multiplier for outlier detection
excluded_subjects <- "S227"  # Subjects to exclude

# Color scheme for plots
vss_color <- '#FF6B6B'
control_color <- "#4CC9F0"

# Load and prepare data
load_and_prepare_data <- function(file_path) {
  data <- read.csv(file_path) %>%
    mutate(
      orderN = orderN + 1,  # Adjust trial numbering
      group = factor(group, levels = c(1, 2), labels = c("VSS", "Control")),
      stim_type = factor(stim_type)),
      
      return(data)
}

DATA <- load_and_prepare_data(file)

# =============================================
# Data Cleaning Functions
# =============================================

# Outlier handling function
replace_outliers_with_na <- function(x, coeff = 2) {
  q <- quantile(x, c(0.25, 0.75), na.rm = TRUE)
  iqr <- q[2] - q[1]
  bounds <- q + coeff * iqr * c(-1, 1)
  x[x < bounds[1] | x > bounds[2]] <- NA
  return(x)
}

# Function to remove outliers from dataset
clean_data <- function(df, response_vars = c("gamma_power", "gamma_freq")) {
  df %>%
    group_by(code, stim_type) %>%
    mutate(across(all_of(response_vars), ~replace_outliers_with_na(.x, outlier_coeff))) %>%
    ungroup() %>%
    filter(!is.na(gamma_power), !is.na(gamma_freq))  # Remove rows with NA in key variables
}

# Z-score normalization
z_score_normalize <- function(df) {
  df %>%
    group_by(code, stim_type) %>%
    mutate(
      z_gamma_power = scale(gamma_power),
      z_gamma_freq = scale(gamma_freq)
    ) %>%
    ungroup()
}

# =============================================
# Analysis Functions
# =============================================

# Function to analyze power changes across trials
analyze_power_changes <- function(z_data, group_name) {
  # Calculate mean power by trial for each stimulus type
  power_data <- map_dfc(sort(unique(z_data$stim_type)), ~{
    z_data %>%
      filter(stim_type == .x) %>%
      group_by(orderN) %>%
      summarize(!!paste0("pow_", .x) := mean(z_gamma_power, na.rm = TRUE)) %>%
      pull(paste0("pow_", .x))
  }) %>%
    mutate(orderN = 1:n())
  
  # Add average across all stimulus types
  power_data$average_power <- rowMeans(power_data[, -ncol(power_data)], na.rm = TRUE)
  power_data$group <- group_name
  
  return(power_data)
}

# Function to fit non-linear power model
fit_power_model <- function(power_data) {
  model_formula <- average_power ~ A * exp(-orderN / tau) + B * orderN + C
  nls(model_formula, 
      data = power_data,
      start = list(A = 1, tau = 10, B = 0.5, C = 1),
      control = nls.control(maxiter = 500))
}

# Function to analyze frequency changes
analyze_frequency_changes <- function(z_data, group_name) {
  # Calculate mean frequency by trial for each stimulus type
  freq_data <- map_dfc(sort(unique(z_data$stim_type)), ~{
    z_data %>%
      filter(stim_type == .x) %>%
      group_by(orderN) %>%
      summarize(!!paste0("freq_", .x) := mean(z_gamma_freq, na.rm = TRUE)) %>%
      pull(paste0("freq_", .x))
  }) %>%
    mutate(orderN = 1:n())
  
  # Add average across all stimulus types
  freq_data$average_freq <- rowMeans(freq_data[, -ncol(freq_data)], na.rm = TRUE)
  freq_data$group <- group_name
  
  return(freq_data)
}

# =============================================
# Block Analysis Functions
# =============================================

analyze_blocks <- function(clean_data) {
  # Assign blocks based on trial ranges
  block_data <- clean_data %>%
    group_by(stim_type, code) %>%
    arrange(orderN) %>%
    mutate(block = case_when(
      orderN >= 15 & orderN <= 55 ~ 1,
      orderN >= 56 & orderN <= 96 ~ 2,
      orderN >= 97 & orderN <= 137 ~ 3,
      TRUE ~ NA_real_
    )) %>%
    filter(!is.na(block))
  
  # Calculate summary statistics
  block_summary <- block_data %>%
    group_by(group, stim_type, block) %>%
    summarise(
      mean_power = mean(gamma_power, na.rm = TRUE),
      mean_freq = mean(gamma_freq, na.rm = TRUE),
      n = n(),
      se_power = sd(gamma_power, na.rm = TRUE) / sqrt(n),
      ci_power = 1.96 * se_power,
      se_freq = sd(gamma_freq, na.rm = TRUE) / sqrt(n),
      ci_freq = 1.96 * se_freq,
      .groups = "drop"
    )
  
  return(block_summary)
}

# =============================================
# Plotting Functions
# =============================================

plot_power_changes <- function(power_data, models) {
  ggplot(power_data, aes(x = orderN, y = average_power, color = group)) +
    geom_point(alpha = 0.6, size = 2) +
    geom_smooth(method = "nls", 
                formula = y ~ A * exp(-x / tau) + B * x + C,
                method.args = list(start = coef(models[[1]])),
                se = FALSE, size = 1.5) +
    scale_color_manual(values = c("VSS" = vss_color, "Control" = control_color)) +
    labs(title = "Gamma Power Changes Across Trials",
         x = "Trial Number",
         y = "Normalized Gamma Power (z-score)",
         color = "Group") +
    theme_minimal() +
    theme(legend.position = "bottom")
}

plot_frequency_changes <- function(freq_data) {
  ggplot(freq_data, aes(x = orderN, y = average_freq, color = group)) +
    geom_point(alpha = 0.6, size = 2) +
    geom_smooth(method = "lm", se = FALSE, size = 1.5) +
    scale_color_manual(values = c("VSS" = vss_color, "Control" = control_color)) +
    labs(title = "Gamma Frequency Changes Across Trials",
         x = "Trial Number",
         y = "Normalized Gamma Frequency (z-score)",
         color = "Group") +
    theme_minimal() +
    theme(legend.position = "bottom")
}

plot_block_results <- function(block_summary, variable = "power") {
  if (variable == "power") {
    y_var <- "mean_power"
    y_lab <- "Gamma Power"
    ci_var <- "ci_power"
  } else {
    y_var <- "mean_freq"
    y_lab <- "Gamma Frequency (Hz)"
    ci_var <- "ci_freq"
  }
  
  ggplot(block_summary, aes(x = factor(block), y = !!sym(y_var), fill = group)) +
    geom_bar(stat = "identity", position = position_dodge()) +
    geom_errorbar(aes(ymin = !!sym(y_var) - !!sym(ci_var), 
                      ymax = !!sym(y_var) + !!sym(ci_var)),
                  position = position_dodge(0.9), width = 0.2) +
    facet_wrap(~stim_type, labeller = labeller(stim_type = c("1" = "0°/s", "2" = "0.6°/s", 
                                                             "3" = "1.2°/s", "4" = "3.6°/s", 
                                                             "5" = "6.0°/s"))) +
    scale_fill_manual(values = c("VSS" = vss_color, "Control" = control_color)) +
    labs(title = paste("Gamma", y_lab, "by Block and Stimulus Type"),
         x = "Block",
         y = y_lab,
         fill = "Group") +
    theme_minimal() +
    theme(legend.position = "bottom")
}

# =============================================
# Main Analysis Pipeline
# =============================================

# 1. Clean and prepare data
clean_data <- DATA %>%
  filter(block_num == 1, 
         orderN >= min_trials, 
         orderN <= max_trials,
         !code %in% excluded_subjects) %>%
  clean_data() %>%
  z_score_normalize()

# 2. Split by group
vss_data <- clean_data %>% filter(group == "VSS")
control_data <- clean_data %>% filter(group == "Control")

# 3. Analyze power changes
vss_power <- analyze_power_changes(vss_data, "VSS")
control_power <- analyze_power_changes(control_data, "Control")
combined_power <- bind_rows(vss_power, control_power)

# Fit models
power_models <- list(
  vss = fit_power_model(vss_power),
  control = fit_power_model(control_power)
)

# 4. Analyze frequency changes
vss_freq <- analyze_frequency_changes(vss_data, "VSS")
control_freq <- analyze_frequency_changes(control_data, "Control")
combined_freq <- bind_rows(vss_freq, control_freq)

# 5. Block analysis
block_results <- analyze_blocks(clean_data)

# =============================================
# Generate Plots
# =============================================

# Power changes plot
power_plot <- plot_power_changes(combined_power, power_models)
print(power_plot)

# Frequency changes plot
freq_plot <- plot_frequency_changes(combined_freq)
print(freq_plot)

# Block analysis plots
power_block_plot <- plot_block_results(block_results, "power")
print(power_block_plot)

freq_block_plot <- plot_block_results(block_results, "frequency")
print(freq_block_plot)

# =============================================
# Save Results
# =============================================

# Save plots
ggsave(paste0(output_path, "gamma_power_changes.png"), power_plot, width = 10, height = 6)
ggsave(paste0(output_path, "gamma_frequency_changes.png"), freq_plot, width = 10, height = 6)
ggsave(paste0(output_path, "gamma_power_by_block.png"), power_block_plot, width = 12, height = 6)
ggsave(paste0(output_path, "gamma_frequency_by_block.png"), freq_block_plot, width = 12, height = 6)

# Save model summaries
capture.output(
  summary(power_models$vss),
  summary(power_models$control),
  file = paste0(output_path, "power_model_summaries.txt")
)

# Save processed data
write.csv(combined_power, paste0(output_path, "processed_power_data.csv"), row.names = FALSE)
write.csv(combined_freq, paste0(output_path, "processed_frequency_data.csv"), row.names = FALSE)
write.csv(block_results, paste0(output_path, "block_analysis_results.csv"), row.names = FALSE)
