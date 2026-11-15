# Online Retail Business Analytics Dashboard

## Project Overview

The **Online Retail Business Analytics Dashboard** is a data analytics application developed using Python and Streamlit. It allows users to upload retail transaction datasets in CSV or Excel format and automatically performs data cleaning, processing, analysis, and visualization.

The dashboard provides insights into sales performance, product performance, customer purchasing behaviour, and country-wise sales distribution through interactive charts, key performance indicators (KPIs), and downloadable reports.

## Objectives

- Analyze online retail transaction data.
- Automatically clean and preprocess uploaded datasets.
- Calculate important business performance metrics.
- Identify top-performing and least-selling products.
- Analyze customer purchasing behaviour.
- Compare sales performance across countries.
- Display analytical results through interactive visualizations.
- Generate downloadable reports for business decision-making.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data manipulation and analysis |
| NumPy | Numerical operations |
| Matplotlib | Data visualization |
| Seaborn | Statistical visualization |
| Plotly | Interactive charts |
| Streamlit | Web dashboard development |
| OpenPyXL | Excel file processing |

## Dataset

The application supports retail transaction datasets in CSV and Excel formats.

Tested datasets:

1. **Online Retail Dataset** – UCI Machine Learning Repository  
   https://archive.ics.uci.edu/dataset/352/online+retail

2. **Online Retail II Dataset** – UCI Machine Learning Repository  
   https://archive.ics.uci.edu/dataset/502/online+retail+ii

The application expects these columns:

- InvoiceNo
- StockCode
- Description
- Quantity
- InvoiceDate
- UnitPrice
- CustomerID
- Country

The application automatically standardizes common Online Retail II column names during upload.

## Main Modules

### 1. Dataset Upload and Processing
- Upload CSV and Excel datasets.
- Validate required columns.
- Standardize supported column names.
- Automatically process newly uploaded datasets.

### 2. Data Cleaning
- Remove duplicate records.
- Handle missing values.
- Convert columns into appropriate data types.
- Identify invalid transactions.
- Separate cancelled invoices and returned products.
- Calculate revenue and date-related fields.

### 3. Sales Analysis
- Total revenue.
- Total orders.
- Total products sold.
- Monthly sales trends.
- Daily sales trends.
- Invoice-level analysis.

### 4. Product Analysis
- Top-selling products.
- Top products by revenue.
- Product quantity analysis.
- Least-selling products.

### 5. Customer Analysis
- Customer purchase history.
- Top customers by revenue.
- Top customers by number of orders.
- Repeat customer analysis.

### 6. Country Analysis
- Country-wise revenue.
- Country-wise orders.
- Country-wise product quantities.
- Top-performing countries.

### 7. Interactive Dashboard
- KPI cards.
- Interactive charts.
- Data tables.
- Multiple analysis pages.
- Downloadable reports.

## Project Structure

```text
Business-Analytics-Mini-Project/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── analysis/
│   ├── load_data.py
│   ├── cleaning.py
│   ├── sales_analysis.py
│   ├── product_analysis.py
│   ├── customer_analysis.py
│   ├── country_analysis.py
│   └── upload_pipeline.py
│
├── components/
│   ├── charts.py
│   └── metrics.py
│
├── assets/
│   └── style.css
│
├── data/
│   ├── raw/
│   └── processed/
│
└── reports/
```

## Installation and Setup

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### Step 2: Navigate to the Project Folder

```bash
cd Business-Analytics-Mini-Project
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 5: Install Required Libraries

```bash
pip install -r requirements.txt
```

### Step 6: Run the Application

```bash
python -m streamlit run app.py
```

### Step 7: Open the Dashboard

Open the following URL in your browser:

```text
http://localhost:8501
```

## How to Use

1. Start the Streamlit application.
2. Upload a retail dataset using the sidebar.
3. Wait for automatic dataset processing.
4. Explore the Overview dashboard.
5. Navigate through Sales, Product, Customer, and Country Analysis.
6. View charts, KPIs, and analytical tables.
7. Download the cleaned dataset and generated reports.

## Expected Outcomes

- Improved understanding of retail business performance.
- Identification of profitable products and important customers.
- Better understanding of sales trends.
- Country-wise business performance insights.
- Automated processing of supported retail datasets.
- Data-driven business decision support.

## Future Enhancements

- Support for more retail dataset formats and column structures.
- Predictive sales forecasting using machine learning.
- Customer segmentation using clustering algorithms.
- Interactive date and country filters.
- Automated PDF report generation.
- Deployment to a cloud hosting platform.

## Academic Information

**Course:** CCW331 – Business Analytics  
**Project Title:** Online Retail Business Analytics Dashboard  
**Project Type:** Mini Project  
**Domain:** Business Analytics and Data Visualization

## Author

Developed as part of the CCW331 Business Analytics Mini Project.

---

**Note:** This project is developed for academic and educational purposes.