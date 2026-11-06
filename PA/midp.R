library(ggplot2)
library(dplyr)

data <- read.csv("diabetes.csv")

summary(data)

sum(is.na(data))

ggplot(data, aes(x = Age)) +
  geom_histogram(binwidth = 5, fill = "blue", color = "black") +
  labs(title = "Distribution of Age", x = "Age", y = "Frequency") +
  theme_minimal()

ggplot(data, aes(x = BMI)) +
  geom_histogram(binwidth = 1, fill = "green", color = "black") +
  labs(title = "Distribution of BMI", x = "BMI", y = "Frequency") +
  theme_minimal()

ggplot(data, aes(x = Glucose, y = Insulin)) +
  geom_point(aes(color = as.factor(Outcome)), alpha = 0.7) +
  labs(title = "Glucose vs Insulin Levels", x = "Glucose", y = "Insulin") +
  scale_color_manual(values = c("red", "blue"), labels = c("No Diabetes", "Diabetes")) +
  theme_minimal()

ggplot(data, aes(x = Age, y = BMI, color = as.factor(Outcome))) +
  geom_point(alpha = 0.6) +
  labs(title = "Age vs BMI Colored by Diabetes Outcome", x = "Age", y = "BMI") +
  scale_color_manual(values = c("red", "blue"), labels = c("No Diabetes", "Diabetes")) +
  theme_minimal()

ggplot(data, aes(x = as.factor(Outcome), y = Glucose, fill = as.factor(Outcome))) +
  geom_boxplot() +
  labs(title = "Boxplot of Glucose Levels by Diabetes Outcome", x = "Diabetes Outcome", y = "Glucose") +
  scale_fill_manual(values = c("red", "blue"), labels = c("No Diabetes", "Diabetes")) +
  theme_minimal()

ggsave("glucose_vs_insulin.png", width = 8, height = 6)

ggplot(data, aes(x = Age, y = Glucose, color = as.factor(Outcome))) +
  geom_point(alpha = 0.5) +
  geom_smooth(method = "lm") +
  labs(title = "Age vs Glucose with Trend Line", x = "Age", y = "Glucose") +
  scale_color_manual(values = c("red", "blue"), labels = c("No Diabetes", "Diabetes")) +
  theme_minimal()