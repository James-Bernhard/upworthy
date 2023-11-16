# Analysis of Upworthy Archive data
# for the paper:
# Using a Mixed Effects Model of Multiple A/B Tests to Understand How
#   Different Pronouns in Online News Headlines Affect Click-Through Rate
#
# by James Bernhard
# 2023-11-16

library(tidyverse)
library(lme4)
library(knitr)
library(kableExtra)

# should we load the fitted model from the .Rdata file fitted_model_filename?
load_fitted_model <- FALSE

# should we save the fitted model to the .Rdata file fitted_model_filename?
save_fitted_model <- FALSE

# filename for data that has been output from preprocessing.py
input_filename <- "df_sentiments.csv"

# filename for the fitted model, if the fitted model is to be loaded or saved
fitted_model_filename <- "fitted_model.Rdata"


df <- read.csv(input_filename)

n_clicks <- sum(df$clicks)
n_impressions <- sum(df$impressions)

rescale <- function(x) {
  (x - min(x)) / (max(x) - min(x))
}

df <-
  df %>% mutate(
    headline_length_rescaled = rescale(headline_length),
    test_week_rescaled = rescale(test_week)
  )

n_variants <- nrow(df)

# make a normal quantile plot of mean CTP to verify that this mixed effects model is appropriate
quantile_df <- df %>%
  group_by(clickability_test_id) %>%
  summarize(mean_logit_ctr = mean(car::logit(ctr)), n = n())

min_test_count <- min(quantile_df$n)
max_test_count <- max(quantile_df$n)

n_ab_tests <- nrow(quantile_df)

# this plot is Figure 1 in the paper
ctr_normal_quantile_plot <- quantile_df %>%
  ggplot(aes(sample = mean_logit_ctr)) +
  geom_qq() +
  xlab("Theoretical standard normal quantile") +
  ylab("Sample quantile")


fit_model <-
  function(df,
           trial_id,
           n_successes,
           n_trials,
           variables_of_interest,
           covariates,
           family = binomial(link = "logit"),
           ...) {
    model_formula = as.formula(
      paste0(
        "cbind(",
        n_successes,
        ", ",
        n_trials,
        " - ",
        n_successes,
        ") ~ ",
        paste(covariates, collapse = " + "),
        " + ",
        paste(variables_of_interest, collapse = " + "),
        " + (1 | ",
        trial_id,
        ")"
      )
    )
    model <-
      glmer(formula = model_formula,
            data = df,
            family = family,
            ...)
    return(model)
  }


if (load_fitted_model) {
  load(fitted_model_filename)
} else {
  model <- fit_model(
    df = df,
    trial_id = "clickability_test_id",
    n_successes = "clicks",
    n_trials = "impressions",
    variables_of_interest = c(
      "exclamation",
      "question",
      "caps",
      "these",
      "this",
      "that",
      "those",
      "i",
      "me",
      "we",
      "us",
      "you",
      "he_she",
      "her_him",
      "it",
      "they",
      "them"
    ),
    covariates = c(
      "nltk_sentiment",
      "headline_length_rescaled",
      "test_week_rescaled"
    ),
    control = glmerControl(optimizer = "bobyqa")
  )
}

if (save_fitted_model) {
  save(model, file = fitted_model_filename)
}

# make data frame for Table 1 in paper
coefficients_table <-
  as.data.frame(summary(model)$coefficients) %>% rownames_to_column("Parameter")

# since we aren't testing for the intercept, we subtract 1 from the number of parameters in the coefficients table
n_hypothesis_tests <- nrow(coefficients_table) - 1

# make the names in Table 1 easier to read
coefficients_table <-
  coefficients_table %>% mutate(
    Parameter = case_match(
      Parameter,
      "(Intercept)" ~ "Intercept",
      "nltk_sentiment" ~ "Sentiment",
      "exclamationTrue" ~ "Exclamation",
      "headline_length_rescaled" ~ "Length",
      "test_week_rescaled" ~ "Week",
      "questionTrue" ~ "Question",
      "capsTrue" ~ "Caps",
      "theseTrue" ~ "These",
      "thisTrue" ~ "This",
      "thatTrue" ~ "That",
      "thoseTrue" ~ "Those",
      "iTrue" ~ "I",
      "meTrue" ~ "Me",
      "weTrue" ~ "We",
      "usTrue" ~ "Us",
      "youTrue" ~ "You",
      "he_sheTrue" ~ "He/She",
      "her_himTrue" ~ "Her/Him",
      "itTrue" ~ "It",
      "theyTrue" ~ "They",
      "themTrue" ~ "Them",
      .default = Parameter
    )
  ) %>%
  rename(SE = "Std. Error", z = "z value", p = "Pr(>|z|)") %>%
  mutate(`Adjusted p` = pmin(p * n_hypothesis_tests, 1))

summary(model)
