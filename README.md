# 🏠 Tehran Real Estate Price Prediction (End-to-End Data Science Project)

## 📌 Overview
This is my **first fully completed end-to-end Data Science project**, built using real estate listings scraped from **Divar** (a major Persian classifieds platform).  
The goal is to predict **house total price** using a complete workflow:

✔ Web Scraping  
✔ SQL Data Cleaning  
✔ EDA & Feature Insights  
✔ Preprocessing  
✔ Machine Learning Modeling  

This project marks the **4th project in my learning journey**, and the first one where I combine everything I’ve learned into one unified pipeline.

---
## 📂 Project Structure
 ### divar_scraping.py         
 Scrapes real-estate listings from Divar
 ### divar_project.sql         
 Cleans & processes scraped data using SQL
 ### divar_ml_project.py      
 EDA, preprocessing, modeling, insights

 ## 🧵 Data Pipeline Summary

### 1️⃣ Web Scraping — divar_scraping.py
Collected Tehran real-estate ads from Divar.

Extracted key features such as:
- rooms
- house_size
- manufacture_year
- total_price
- price_per_meter

Saved the dataset for SQL processing.

### 2️⃣ SQL Processing — divar_project.sql
Cleaned the raw scraped dataset using SQL.

Performed the following steps:
- Removed duplicate records
- Handled missing or inconsistent values
- Normalized data for analysis
- Queried insights such as average prices by year and neighborhood

Exported the cleaned dataset for machine learning.

### 3️⃣ EDA & Insights — divar_ml_project.py

Explored patterns and relationships inside the cleaned dataset:

🔹 Year Binning & Feature Engineering
``` python
    dataframe['year_bins'] = (dataframe['manufacture_year'] // 5) * 5
    dataframe['total_price_bilion'] = dataframe['total_price'] / 1e9
```

🔹 Major Insights from EDA
- Most listed houses were built in 1403–1404
- Houses sized 50–110 m² dominate Tehran’s listings
- Strong positive correlation between:
  - total_price ↔ house_size
  - house_size ↔ rooms
- Newer houses tend to be both larger and more expensive

🔹 Visualizations Included
- Room count distribution by build year
- House size distribution by build year
- Feature distributions
- Correlation heatmap
- Scatterplots:
  - price vs size
  - rooms vs size
  - price_per_meter vs total_price
  - manufacture_year vs price


### 🧪 Modeling & Evaluation

#### Features Used for Model Training
``` python
X = dataframe.drop(columns=['total_price', 'price_per_meter', 'year_bins', 'total_price_bilion'])
y = dataframe['total_price']
```
#### Preprocessing
Applied `StandardScaler` to numeric features:
- `house_size`
- `manufacture_year`

#### Models Trained
- Linear Regression
- Random Forest Regressor

#### Metrics Evaluated
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- Mean Absolute Percentage Error (MAPE)
- R² Score

Random Forest performed significantly better due to:
- Nonlinear relationships
- Interactions between house size, rooms, and year

## 🎯 Key Achievements

This project helped me to:

- Build my  **first fully operational ML pipeline** 
- Use **web scraping**, **SQL**, and **Python ML** together  
- Extract real insights from Tehran’s real estate market  
- Understand real-world challenges in:
  - noisy data  
  - inconsistent user input  
  - feature engineering  
  - non-linear price behaviors  


## 📚 Dataset
The dataset is self-collected from Divar using web scraping.
Due to Divar's terms of service, the dataset is **not uploaded** and must be recreated using the scraping script.
