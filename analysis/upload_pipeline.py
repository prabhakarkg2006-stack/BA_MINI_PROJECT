
from pathlib import Path
from io import BytesIO
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"
REPORT_FOLDER = PROJECT_ROOT / "reports"

REQUIRED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country"
]



def read_uploaded_dataset(uploaded_file):
    """Read CSV/Excel files and standardize Online Retail II column names."""

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    elif file_name.endswith((".xlsx", ".xls")):
        data = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Please upload a CSV or Excel file.")

    # Remove extra spaces from column names
    data.columns = data.columns.astype(str).str.strip()

    # Standardize Online Retail II column names
    column_mapping = {
        "Invoice": "InvoiceNo",
        "Price": "UnitPrice",
        "Customer ID": "CustomerID"
    }

    data = data.rename(columns=column_mapping)

    # Check required columns
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "The uploaded dataset is missing these required columns: "
            + ", ".join(missing_columns)
        )

    return data



def clean_uploaded_data(data):
    """Clean the uploaded retail transaction dataset."""

    original_count = len(data)

    data = data.copy()

    # Remove duplicate rows.
    data = data.drop_duplicates()

    # Clean text fields.
    for column in ["InvoiceNo", "StockCode", "Description", "Country"]:
        data[column] = data[column].astype("string").str.strip()

    # Convert numeric columns.
    data["Quantity"] = pd.to_numeric(
        data["Quantity"], errors="coerce"
    )

    data["UnitPrice"] = pd.to_numeric(
        data["UnitPrice"], errors="coerce"
    )

    data["CustomerID"] = pd.to_numeric(
        data["CustomerID"], errors="coerce"
    )

    # Parse dates.
    data["InvoiceDate"] = pd.to_datetime(
        data["InvoiceDate"],
        errors="coerce",
        dayfirst=True
    )

    # Remove rows with essential missing values.
    essential_columns = [
        "InvoiceNo",
        "StockCode",
        "Quantity",
        "UnitPrice",
        "InvoiceDate"
    ]

    invalid_records = data[
        data[essential_columns].isna().any(axis=1)
    ].copy()

    data = data.dropna(
        subset=essential_columns
    ).copy()

    # Separate cancelled invoices.
    cancelled_mask = (
        data["InvoiceNo"].astype(str).str.startswith("C")
    )

    cancelled_transactions = data[
        cancelled_mask
    ].copy()

    data = data[~cancelled_mask].copy()

    # Separate returns.
    returns = data[data["Quantity"] < 0].copy()

    if not returns.empty:
        returns["ReturnQuantity"] = returns["Quantity"].abs()
        returns["ReturnValue"] = (
            returns["Quantity"].abs() * returns["UnitPrice"]
        )

    # Keep valid positive sales for business analysis.
    sales = data[
        (data["Quantity"] > 0) &
        (data["UnitPrice"] > 0)
    ].copy()

    sales["Description"] = (
        sales["Description"]
        .fillna("Unknown Product")
    )

    sales["Country"] = (
        sales["Country"]
        .fillna("Unknown Country")
    )

    sales["Revenue"] = (
        sales["Quantity"] * sales["UnitPrice"]
    )

    sales["Year"] = sales["InvoiceDate"].dt.year
    sales["Month"] = sales["InvoiceDate"].dt.to_period("M").astype(str)
    sales["MonthName"] = sales["InvoiceDate"].dt.month_name()
    sales["Day"] = sales["InvoiceDate"].dt.day
    sales["DayName"] = sales["InvoiceDate"].dt.day_name()

    sales = sales.sort_values("InvoiceDate")

    cleaning_summary = pd.DataFrame({
        "Metric": [
            "Original Rows",
            "Duplicate Rows Removed",
            "Invalid Rows",
            "Cancelled Transactions",
            "Return Transactions",
            "Valid Sales Rows"
        ],
        "Value": [
            original_count,
            original_count - len(data) - len(invalid_records),
            len(invalid_records),
            len(cancelled_transactions),
            len(returns),
            len(sales)
        ]
    })

    return (
        sales,
        returns,
        cancelled_transactions,
        invalid_records,
        cleaning_summary
    )


def create_sales_reports(sales, returns, cancelled):
    """Create sales, monthly, daily and invoice reports."""

    total_revenue = sales["Revenue"].sum()
    total_orders = sales["InvoiceNo"].nunique()
    total_quantity = sales["Quantity"].sum()

    average_order_value = (
        total_revenue / total_orders
        if total_orders else 0
    )

    sales_metrics = pd.DataFrame({
        "Metric": [
            "Total Revenue",
            "Total Orders",
            "Total Quantity Sold",
            "Unique Products",
            "Unique Customers",
            "Average Order Value",
            "Return Transactions",
            "Cancelled Transactions"
        ],
        "Value": [
            round(total_revenue, 2),
            total_orders,
            total_quantity,
            sales["StockCode"].nunique(),
            sales["CustomerID"].nunique(),
            round(average_order_value, 2),
            len(returns),
            len(cancelled)
        ]
    })

    monthly = (
        sales.groupby("Month")
        .agg(
            Revenue=("Revenue", "sum"),
            Orders=("InvoiceNo", "nunique"),
            QuantitySold=("Quantity", "sum")
        )
        .reset_index()
        .sort_values("Month")
    )

    monthly["AverageOrderValue"] = (
        monthly["Revenue"] / monthly["Orders"]
    )

    monthly["RevenueGrowthPercent"] = (
        monthly["Revenue"].pct_change() * 100
    ).fillna(0)

    daily = (
        sales.groupby(sales["InvoiceDate"].dt.date)
        .agg(
            Revenue=("Revenue", "sum"),
            Orders=("InvoiceNo", "nunique"),
            QuantitySold=("Quantity", "sum")
        )
        .reset_index()
        .rename(columns={"InvoiceDate": "Date"})
    )

    invoice = (
        sales.groupby("InvoiceNo")
        .agg(
            InvoiceDate=("InvoiceDate", "min"),
            Revenue=("Revenue", "sum"),
            Quantity=("Quantity", "sum")
        )
        .reset_index()
    )

    if "CustomerID" in sales.columns:
        invoice_customers = (
            sales.groupby("InvoiceNo")["CustomerID"]
            .first()
            .reset_index()
        )

        invoice = invoice.merge(
            invoice_customers,
            on="InvoiceNo",
            how="left"
        )

    return sales_metrics, monthly, daily, invoice


def create_product_reports(sales):
    """Create product performance reports."""

    summary = (
        sales.groupby(
            ["StockCode", "Description"],
            as_index=False
        )
        .agg(
            TotalRevenue=("Revenue", "sum"),
            TotalQuantitySold=("Quantity", "sum"),
            NumberOfTransactions=("InvoiceNo", "nunique"),
            AverageUnitPrice=("UnitPrice", "mean")
        )
        .sort_values("TotalRevenue", ascending=False)
    )

    top_revenue = summary.head(10).copy()

    top_quantity = (
        summary.sort_values(
            "TotalQuantitySold",
            ascending=False
        ).head(10).copy()
    )

    least_selling = (
        summary.sort_values(
            "TotalRevenue",
            ascending=True
        ).head(10).copy()
    )

    metrics = pd.DataFrame({
        "Metric": [
            "Total Unique Products",
            "Total Quantity Sold",
            "Total Product Revenue",
            "Average Revenue Per Product",
            "Highest Revenue Product",
            "Highest Product Revenue"
        ],
        "Value": [
            summary["StockCode"].nunique(),
            sales["Quantity"].sum(),
            round(sales["Revenue"].sum(), 2),
            round(summary["TotalRevenue"].mean(), 2),
            summary.iloc[0]["Description"] if not summary.empty else "None",
            round(summary.iloc[0]["TotalRevenue"], 2) if not summary.empty else 0
        ]
    })

    return summary, top_revenue, top_quantity, least_selling, metrics


def create_customer_reports(sales):
    """Create customer spending and repeat-purchase reports."""

    customer_data = sales.dropna(
        subset=["CustomerID"]
    ).copy()

    summary = (
        customer_data.groupby("CustomerID")
        .agg(
            TotalRevenue=("Revenue", "sum"),
            TotalQuantityPurchased=("Quantity", "sum"),
            TotalOrders=("InvoiceNo", "nunique"),
            AverageTransactionValue=("Revenue", "mean"),
            FirstPurchase=("InvoiceDate", "min"),
            LastPurchase=("InvoiceDate", "max")
        )
        .reset_index()
    )

    if not summary.empty:
        summary["AverageOrderValue"] = (
            summary["TotalRevenue"] / summary["TotalOrders"]
        )

        summary["CustomerType"] = summary["TotalOrders"].apply(
            lambda count: (
                "Repeat Customer"
                if count > 1
                else "One-time Customer"
            )
        )

    top_revenue = (
        summary.sort_values("TotalRevenue", ascending=False)
        .head(10)
    )

    top_orders = (
        summary.sort_values(
            ["TotalOrders", "TotalRevenue"],
            ascending=[False, False]
        ).head(10)
    )

    repeat = (
        summary[summary["TotalOrders"] > 1]
        .sort_values("TotalOrders", ascending=False)
    )

    total_customers = len(summary)
    repeat_count = len(repeat)
    one_time_count = (
        len(summary[summary["TotalOrders"] == 1])
        if not summary.empty else 0
    )

    total_customer_revenue = summary["TotalRevenue"].sum()
    total_customer_orders = summary["TotalOrders"].sum()

    repeat_percentage = (
        repeat_count / total_customers * 100
        if total_customers else 0
    )

    metrics = pd.DataFrame({
        "Metric": [
            "Total Identified Customers",
            "Repeat Customers",
            "One-time Customers",
            "Repeat Customer Percentage",
            "Total Customer Revenue",
            "Total Customer Orders",
            "Average Customer Spending",
            "Average Order Value"
        ],
        "Value": [
            total_customers,
            repeat_count,
            one_time_count,
            round(repeat_percentage, 2),
            round(total_customer_revenue, 2),
            total_customer_orders,
            round(summary["TotalRevenue"].mean(), 2) if total_customers else 0,
            round(
                total_customer_revenue / total_customer_orders, 2
            ) if total_customer_orders else 0
        ]
    })

    return summary, top_revenue, top_orders, repeat, metrics


def create_country_reports(sales):
    """Create country-wise performance reports."""

    summary = (
        sales.groupby("Country")
        .agg(
            TotalRevenue=("Revenue", "sum"),
            TotalQuantitySold=("Quantity", "sum"),
            TotalOrders=("InvoiceNo", "nunique"),
            TotalTransactions=("InvoiceNo", "count"),
            AverageUnitRevenue=("Revenue", "mean")
        )
        .reset_index()
    )

    summary["AverageOrderValue"] = (
        summary["TotalRevenue"] / summary["TotalOrders"]
    )

    total_revenue = summary["TotalRevenue"].sum()

    summary["RevenuePercentage"] = (
        summary["TotalRevenue"] / total_revenue * 100
        if total_revenue else 0
    )

    summary = summary.sort_values(
        "TotalRevenue",
        ascending=False
    )

    top_revenue = summary.head(10).copy()

    top_orders = (
        summary.sort_values(
            "TotalOrders",
            ascending=False
        ).head(10)
    )

    top_quantity = (
        summary.sort_values(
            "TotalQuantitySold",
            ascending=False
        ).head(10)
    )

    highest_order_country = (
        summary.sort_values(
            "TotalOrders",
            ascending=False
        ).iloc[0]["Country"]
        if not summary.empty else "None"
    )

    metrics = pd.DataFrame({
        "Metric": [
            "Total Countries",
            "Total Revenue",
            "Total Quantity Sold",
            "Total Unique Orders",
            "Highest Revenue Country",
            "Highest Country Revenue",
            "Highest Order Volume Country"
        ],
        "Value": [
            summary["Country"].nunique(),
            round(sales["Revenue"].sum(), 2),
            sales["Quantity"].sum(),
            sales["InvoiceNo"].nunique(),
            summary.iloc[0]["Country"] if not summary.empty else "None",
            round(summary.iloc[0]["TotalRevenue"], 2) if not summary.empty else 0,
            highest_order_country
        ]
    })

    return summary, top_revenue, top_orders, top_quantity, metrics


def save_report(filename, dataframe):
    """Save a generated report."""

    REPORT_FOLDER.mkdir(parents=True, exist_ok=True)

    dataframe.to_csv(
        REPORT_FOLDER / filename,
        index=False,
        encoding="utf-8-sig"
    )


def process_uploaded_dataset(uploaded_file):
    """Run the complete business analytics pipeline."""

    PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
    REPORT_FOLDER.mkdir(parents=True, exist_ok=True)

    raw_data = read_uploaded_dataset(uploaded_file)

    (
        sales,
        returns,
        cancelled,
        invalid,
        cleaning_summary
    ) = clean_uploaded_data(raw_data)

    if sales.empty:
        raise ValueError(
            "No valid sales transactions were found in this dataset."
        )

    # Save cleaned and supporting datasets.
    sales.to_csv(
        PROCESSED_FOLDER / "cleaned_sales.csv",
        index=False,
        encoding="utf-8-sig"
    )

    returns.to_csv(
        PROCESSED_FOLDER / "returns.csv",
        index=False,
        encoding="utf-8-sig"
    )

    cancelled.to_csv(
        PROCESSED_FOLDER / "cancelled_transactions.csv",
        index=False,
        encoding="utf-8-sig"
    )

    invalid.to_csv(
        PROCESSED_FOLDER / "invalid_records.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Sales reports.
    sales_reports = create_sales_reports(
        sales, returns, cancelled
    )

    sales_filenames = [
        "sales_summary.csv",
        "monthly_sales.csv",
        "daily_sales.csv",
        "invoice_sales.csv"
    ]

    for filename, report in zip(
        sales_filenames, sales_reports
    ):
        save_report(filename, report)

    # Product reports.
    product_reports = create_product_reports(sales)

    product_filenames = [
        "product_summary.csv",
        "top_products_by_revenue.csv",
        "top_products_by_quantity.csv",
        "least_selling_products.csv",
        "product_metrics.csv"
    ]

    for filename, report in zip(
        product_filenames, product_reports
    ):
        save_report(filename, report)

    # Customer reports.
    customer_reports = create_customer_reports(sales)

    customer_filenames = [
        "customer_summary.csv",
        "top_customers_by_revenue.csv",
        "top_customers_by_orders.csv",
        "repeat_customers.csv",
        "customer_metrics.csv"
    ]

    for filename, report in zip(
        customer_filenames, customer_reports
    ):
        save_report(filename, report)

    # Country reports.
    country_reports = create_country_reports(sales)

    country_filenames = [
        "country_summary.csv",
        "top_countries_by_revenue.csv",
        "top_countries_by_orders.csv",
        "top_countries_by_quantity.csv",
        "country_metrics.csv"
    ]

    for filename, report in zip(
        country_filenames, country_reports
    ):
        save_report(filename, report)

    save_report("cleaning_report.csv", cleaning_summary)

    return {
        "rows_uploaded": len(raw_data),
        "valid_sales_rows": len(sales),
        "products": sales["StockCode"].nunique(),
        "customers": sales["CustomerID"].nunique(),
        "countries": sales["Country"].nunique(),
        "revenue": round(sales["Revenue"].sum(), 2)
    }
