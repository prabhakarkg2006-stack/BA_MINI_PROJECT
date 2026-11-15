
import html
import streamlit as st


def render_metric_cards(metrics):
    """
    Display KPI cards.

    metrics format:
    [
        ("Total Revenue", "£100,000"),
        ("Total Orders", "5,000")
    ]
    """

    if not metrics:
        return

    columns = st.columns(len(metrics))

    for column, metric in zip(columns, metrics):
        label, value = metric[0], metric[1]

        safe_label = html.escape(str(label))
        safe_value = html.escape(str(value))

        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{safe_label}</div>
                    <div class="metric-value">{safe_value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
