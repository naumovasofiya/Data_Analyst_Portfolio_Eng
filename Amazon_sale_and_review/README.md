# Analysis of Amazon Product Sales and Reviews Data

**Notebook link:** `amazon_sales_and_review-Copy1.ipynb`

## Research Objective

Conduct a comprehensive analysis of Amazon product data to identify relationships between product categories, prices, reviews, time, and shipping directions.

## Research Tasks

1.  Analyze price distribution across product categories
2.  Investigate the relationship between price and number of reviews
3.  Identify the most popular shipping destinations
4.  Study temporal trends and seasonality in order activity
5.  Examine the influence of brand on price and number of reviews
6.  Test main hypotheses about relationships within the data

## Libraries Used

- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `datetime`

## Research Results

### 1. Data Preparation
Data loading and initial analysis were performed (89,082 records). Outliers in prices and number of reviews were identified and processed. Logarithmic transformation was applied to normalize distributions. Temporal features (year, month) were added for analysis.

### 2. Price Analysis
Clear price segments were identified:
-   **Premium:** Laptops (~$507), Cameras (~$132)
-   **Mid-range:** Men's Shoes (~$95), Auto Accessories (~$64)
-   **Budget:** Audio/Video (~$54), Men's Clothing (~$51), Toys (~$31)

### 3. Review Analysis
An inverse relationship was found between price and user activity. Budget categories (Toys, Mobile Devices) receive significantly more reviews than premium ones (Laptops, Cameras).

### 4. Correlation Analysis
A weak negative correlation (-0.15) between the logarithm of price and the logarithm of the number of reviews was confirmed.

### 5. Shipping Analysis
98.9% of orders use standard shipping. A paradox was discovered: free shipping is more often applied to cheaper items, while express shipping is used for premium ones.

### 6. Temporal Analysis
A pronounced seasonal trend was identified, with sales peaks in November-December (holiday season) and dips in January-February. Overall sales growth was observed in 2020-2021.

### 7. Hypothesis Testing
-   Hypothesis **"Expensive items receive fewer reviews"** — **confirmed** (weak negative correlation)
-   Hypothesis **"Some product categories have higher average prices"** — **confirmed** (premium, mid-range, and budget segments identified)
-   Hypothesis **"There are seasonal fluctuations in the number of orders"** — **confirmed** (clear annual seasonality)

**Conclusion:** The research revealed key patterns in Amazon data that can be used to optimize pricing strategy, marketing activities, and logistics.