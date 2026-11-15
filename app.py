
from pathlib import Path
import hashlib
import pandas as pd
import streamlit as st

from analysis.upload_pipeline import process_uploaded_dataset

from components.metrics import render_metric_cards
from components.charts import (
    make_bar_chart,
    make_line_chart,
    make_donut_chart
)


# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent
REPORT_FOLDER = PROJECT_ROOT / "reports"
DATA_FOLDER = PROJECT_ROOT / "data" / "processed"

st.set_page_config(
    page_title="Online Retail Business Analytics",
    page_icon="📊",
    layout="wide"
)


# ==================================================
# 2. LOAD CSS
# ==================================================

def load_css():
    css_file = PROJECT_ROOT / "assets" / "style.css"

    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as file:
            st.markdown(
                f"<style>{file.read()}</style>",
                unsafe_allow_html=True
            )


load_css()


# ==================================================
# 3. DATASET UPLOAD
# ==================================================

st.sidebar.title("📊 Business Analytics")

st.sidebar.write("Upload a retail dataset to begin.")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel Dataset",
    type=["csv", "xlsx"],
    help="Required columns: InvoiceNo, StockCode, Description, "
         "Quantity, InvoiceDate, UnitPrice, CustomerID and Country."
)

if uploaded_file is not None:

    file_hash = hashlib.sha256(
        uploaded_file.getvalue()
    ).hexdigest()

    already_processed = (
        st.session_state.get("processed_file_hash") == file_hash
    )

    if not already_processed:

        with st.spinner(
            "Processing dataset and generating all business reports..."
        ):
            try:
                result = process_uploaded_dataset(uploaded_file)

                st.session_state["processed_file_hash"] = file_hash
                st.session_state["uploaded_filename"] = uploaded_file.name
                st.session_state["upload_result"] = result

                st.success(
                    "Dataset analysed successfully! "
                    "All dashboard reports have been generated."
                )

            except Exception as error:
                st.error(f"Dataset processing failed: {error}")

    else:
        st.sidebar.success("Dataset analysed and ready.")

elif "processed_file_hash" in st.session_state:
    st.sidebar.info(
        "The last analysed dataset is still being displayed. "
        "Upload another file to replace it."
    )

st.sidebar.divider()

st.sidebar.caption("CCW331 Business Analytics Mini Project")


# ==================================================
# 4. LOAD REPORTS
# ==================================================

def load_report(filename):
    path = REPORT_FOLDER / filename

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def load_cleaned_data():
    path = DATA_FOLDER / "cleaned_sales.csv"

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


sales_summary = load_report("sales_summary.csv")
monthly_sales = load_report("monthly_sales.csv")
daily_sales = load_report("daily_sales.csv")
invoice_sales = load_report("invoice_sales.csv")

product_summary = load_report("product_summary.csv")
top_products_revenue = load_report("top_products_by_revenue.csv")
top_products_quantity = load_report("top_products_by_quantity.csv")
least_selling_products = load_report("least_selling_products.csv")
product_metrics = load_report("product_metrics.csv")

customer_summary = load_report("customer_summary.csv")
top_customers_revenue = load_report("top_customers_by_revenue.csv")
top_customers_orders = load_report("top_customers_by_orders.csv")
repeat_customers = load_report("repeat_customers.csv")
customer_metrics = load_report("customer_metrics.csv")

country_summary = load_report("country_summary.csv")
top_countries_revenue = load_report("top_countries_by_revenue.csv")
top_countries_orders = load_report("top_countries_by_orders.csv")
top_countries_quantity = load_report("top_countries_by_quantity.csv")
country_metrics = load_report("country_metrics.csv")


# ==================================================
# 5. HELPER FUNCTIONS
# ==================================================

def find_column(data, names):
    for name in names:
        if name in data.columns:
            return name
    return None


def get_metric(data, names, default=0):
    if data.empty:
        return default

    if "Metric" not in data.columns or "Value" not in data.columns:
        return default

    for _, row in data.iterrows():
        metric_name = str(row["Metric"]).strip().lower()

        if metric_name in [name.lower() for name in names]:
            return row["Value"]

    return default


def number(value):
    try:
        result = pd.to_numeric(value, errors="coerce")
        return 0 if pd.isna(result) else float(result)
    except (TypeError, ValueError):
        return 0


def currency(value):
    return f"£{number(value):,.2f}"


def formatted_number(value):
    return f"{number(value):,.0f}"


def show_table(data, title):
    st.subheader(title)

    if data.empty:
        st.info("No report data is available.")
    else:
        st.dataframe(
            data,
            use_container_width=True,
            hide_index=True
        )


def show_bar(data, category, value, title, horizontal=False):
    if (
        data.empty
        or category not in data.columns
        or value not in data.columns
    ):
        st.info("Chart data is not available.")
        return

    chart_data = data.copy()

    if horizontal:
        figure = make_bar_chart(
            chart_data,
            value,
            category,
            title,
            horizontal=True
        )
    else:
        figure = make_bar_chart(
            chart_data,
            category,
            value,
            title
        )

    st.plotly_chart(
        figure,
        use_container_width=True
    )


def show_monthly_chart():
    if monthly_sales.empty:
        st.info("Monthly sales data is not available.")
        return

    date_column = find_column(
        monthly_sales,
        ["Month", "Period", "InvoiceMonth"]
    )

    revenue_column = find_column(
        monthly_sales,
        ["Revenue", "TotalRevenue"]
    )

    if not date_column or not revenue_column:
        st.info("Monthly chart columns are unavailable.")
        return

    figure = make_line_chart(
        monthly_sales,
        date_column,
        revenue_column,
        "Monthly Revenue Trend"
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )


# ==================================================
# 6. DASHBOARD NAVIGATION
# ==================================================

page = st.sidebar.radio(
    "Dashboard Pages",
    [
        "Overview",
        "Sales Analysis",
        "Product Analysis",
        "Customer Analysis",
        "Country Analysis"
    ]
)


# ==================================================
# 7. CHECK WHETHER DATA EXISTS
# ==================================================

if sales_summary.empty:

    st.title("📊 Online Retail Business Analytics")

    st.info(
        "Welcome! Upload a CSV or Excel retail dataset "
        "using the sidebar to generate your dashboard."
    )

    st.markdown(
        """
        ### How to use this application

        1. Click **Browse files** in the sidebar.
        2. Select a retail CSV or Excel dataset.
        3. Wait while the application cleans and analyses the data.
        4. Explore the Overview, Sales, Product, Customer and Country pages.

        **Required dataset columns**

        - InvoiceNo
        - StockCode
        - Description
        - Quantity
        - InvoiceDate
        - UnitPrice
        - CustomerID
        - Country
        """
    )

    st.stop()


# ==================================================
# 8. OVERVIEW PAGE
# ==================================================

def show_overview():

    st.title("📊 Online Retail Business Analytics")

    filename = st.session_state.get(
        "uploaded_filename",
        "Previously generated dataset"
    )

    st.caption(f"Currently analysed dataset: {filename}")

    revenue = get_metric(
        sales_summary,
        ["Total Revenue"]
    )

    orders = get_metric(
        sales_summary,
        ["Total Orders"]
    )

    quantity = get_metric(
        sales_summary,
        ["Total Quantity Sold"]
    )

    average_order = get_metric(
        sales_summary,
        ["Average Order Value"]
    )

    products = get_metric(
        product_metrics,
        ["Total Unique Products"]
    )

    customers = get_metric(
        customer_metrics,
        ["Total Identified Customers"]
    )

    countries = get_metric(
        country_metrics,
        ["Total Countries"]
    )

    render_metric_cards([
        ("Total Revenue", currency(revenue)),
        ("Total Orders", formatted_number(orders)),
        ("Quantity Sold", formatted_number(quantity)),
        ("Average Order Value", currency(average_order))
    ])

    render_metric_cards([
        ("Products", formatted_number(products)),
        ("Customers", formatted_number(customers)),
        ("Countries", formatted_number(countries))
    ])

    st.divider()

    st.subheader("Monthly Revenue Trend")
    show_monthly_chart()

    left, right = st.columns(2)

    with left:
        st.subheader("Top Products")

        show_bar(
            top_products_revenue.head(10),
            "Description",
            "TotalRevenue",
            "Top Products by Revenue",
            horizontal=True
        )

    with right:
        st.subheader("Top Countries")

        show_bar(
            top_countries_revenue.head(10),
            "Country",
            "TotalRevenue",
            "Top Countries by Revenue"
        )


# ==================================================
# 9. SALES ANALYSIS
# ==================================================

def show_sales():

    st.title("💰 Sales Analysis")

    render_metric_cards([
        (
            "Total Revenue",
            currency(get_metric(sales_summary, ["Total Revenue"]))
        ),
        (
            "Total Orders",
            formatted_number(get_metric(sales_summary, ["Total Orders"]))
        ),
        (
            "Quantity Sold",
            formatted_number(
                get_metric(sales_summary, ["Total Quantity Sold"])
            )
        ),
        (
            "Average Order Value",
            currency(
                get_metric(sales_summary, ["Average Order Value"])
            )
        )
    ])

    st.divider()

    st.subheader("Monthly Revenue")
    show_monthly_chart()

    show_table(monthly_sales, "Monthly Sales Report")
    show_table(daily_sales, "Daily Sales Report")
    show_table(invoice_sales.head(100), "Invoice Sales Report")


# ==================================================
# 10. PRODUCT ANALYSIS
# ==================================================

def show_products():

    st.title("📦 Product Analysis")

    render_metric_cards([
        (
            "Total Products",
            formatted_number(
                get_metric(product_metrics, ["Total Unique Products"])
            )
        ),
        (
            "Product Revenue",
            currency(
                get_metric(product_metrics, ["Total Product Revenue"])
            )
        ),
        (
            "Average Revenue Per Product",
            currency(
                get_metric(
                    product_metrics,
                    ["Average Revenue Per Product"]
                )
            )
        ),
        (
            "Highest Revenue Product",
            str(
                get_metric(
                    product_metrics,
                    ["Highest Revenue Product"],
                    "Not available"
                )
            )
        )
    ])

    st.divider()

    count = st.slider(
        "Number of products to display",
        5,
        10,
        10
    )

    left, right = st.columns(2)

    with left:
        show_bar(
            top_products_revenue.head(count),
            "Description",
            "TotalRevenue",
            "Top Products by Revenue",
            horizontal=True
        )

    with right:
        show_bar(
            top_products_quantity.head(count),
            "Description",
            "TotalQuantitySold",
            "Top Products by Quantity"
        )

    show_table(product_summary, "Complete Product Summary")
    show_table(least_selling_products, "Lowest 10 Products by Revenue")


# ==================================================
# 11. CUSTOMER ANALYSIS
# ==================================================

def show_customers():

    st.title("👥 Customer Analysis")

    repeat_percentage = get_metric(
        customer_metrics,
        ["Repeat Customer Percentage"]
    )

    render_metric_cards([
        (
            "Identified Customers",
            formatted_number(
                get_metric(
                    customer_metrics,
                    ["Total Identified Customers"]
                )
            )
        ),
        (
            "Repeat Customers",
            formatted_number(
                get_metric(customer_metrics, ["Repeat Customers"])
            )
        ),
        (
            "One-time Customers",
            formatted_number(
                get_metric(customer_metrics, ["One-time Customers"])
            )
        ),
        (
            "Repeat Customer %",
            f"{number(repeat_percentage):.2f}%"
        )
    ])

    st.divider()

    left, right = st.columns(2)

    with left:
        show_bar(
            top_customers_revenue.head(10),
            "CustomerID",
            "TotalRevenue",
            "Top Customers by Revenue",
            horizontal=True
        )

    with right:
        if (
            not customer_summary.empty
            and "CustomerType" in customer_summary.columns
        ):
            types = (
                customer_summary["CustomerType"]
                .value_counts()
                .rename_axis("Customer Type")
                .reset_index(name="Customer Count")
            )

            figure = make_donut_chart(
                types,
                "Customer Type",
                "Customer Count",
                "Customer Purchase Type"
            )

            st.plotly_chart(
                figure,
                use_container_width=True
            )
        else:
            st.info("Customer type information is unavailable.")

    show_table(top_customers_orders, "Top Customers by Orders")
    show_table(repeat_customers, "Repeat Customers")
    show_table(customer_summary, "Complete Customer Summary")


# ==================================================
# 12. COUNTRY ANALYSIS
# ==================================================

def show_countries():

    st.title("🌍 Country Analysis")

    render_metric_cards([
        (
            "Countries",
            formatted_number(
                get_metric(country_metrics, ["Total Countries"])
            )
        ),
        (
            "Total Revenue",
            currency(
                get_metric(country_metrics, ["Total Revenue"])
            )
        ),
        (
            "Total Orders",
            formatted_number(
                get_metric(country_metrics, ["Total Unique Orders"])
            )
        ),
        (
            "Top Revenue Country",
            str(
                get_metric(
                    country_metrics,
                    ["Highest Revenue Country"],
                    "Not available"
                )
            )
        )
    ])

    st.divider()

    count = st.slider(
        "Number of countries to display",
        5,
        10,
        10
    )

    left, right = st.columns(2)

    with left:
        show_bar(
            top_countries_revenue.head(count),
            "Country",
            "TotalRevenue",
            "Revenue by Country"
        )

    with right:
        show_bar(
            top_countries_orders.head(count),
            "Country",
            "TotalOrders",
            "Orders by Country"
        )

    show_table(
        top_countries_quantity,
        "Top Countries by Quantity Sold"
    )

    show_table(
        country_summary,
        "Complete Country Summary"
    )


# ==================================================
# 13. DOWNLOAD REPORTS
# ==================================================

st.sidebar.divider()
st.sidebar.subheader("Download Reports")

cleaned_file = DATA_FOLDER / "cleaned_sales.csv"

if cleaned_file.exists():
    with open(cleaned_file, "rb") as file:
        st.sidebar.download_button(
            "Download Cleaned Dataset",
            data=file.read(),
            file_name="cleaned_sales.csv",
            mime="text/csv"
        )

download_files = [
    "sales_summary.csv",
    "product_summary.csv",
    "customer_summary.csv",
    "country_summary.csv",
    "monthly_sales.csv"
]

for filename in download_files:
    file_path = REPORT_FOLDER / filename

    if file_path.exists():
        with open(file_path, "rb") as file:
            st.sidebar.download_button(
                f"Download {filename}",
                data=file.read(),
                file_name=filename,
                mime="text/csv",
                key=f"download_{filename}"
            )


# ==================================================
# 14. DISPLAY SELECTED PAGE
# ==================================================

if page == "Overview":
    show_overview()

elif page == "Sales Analysis":
    show_sales()

elif page == "Product Analysis":
    show_products()

elif page == "Customer Analysis":
    show_customers()

elif page == "Country Analysis":
    show_countries()


# ==================================================
# 15. FOOTER
# ==================================================

st.markdown(
    """
    <div class="dashboard-footer">
        CCW331 Business Analytics |
        Online Retail Business Analytics Dashboard
    </div>
    """,
    unsafe_allow_html=True
)
