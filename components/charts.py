
import plotly.express as px


def make_bar_chart(
    data,
    x,
    y,
    title,
    horizontal=False
):
    """Create a reusable bar chart."""

    if horizontal:
        figure = px.bar(
            data,
            x=x,
            y=y,
            orientation="h",
            title=title,
            text=x
        )
    else:
        figure = px.bar(
            data,
            x=x,
            y=y,
            title=title,
            text=y
        )

    figure.update_layout(
        template="plotly_white",
        title_x=0.02,
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis_title=x,
        yaxis_title=y
    )

    return figure


def make_line_chart(
    data,
    x,
    y,
    title
):
    """Create a reusable line chart."""

    figure = px.line(
        data,
        x=x,
        y=y,
        markers=True,
        title=title
    )

    figure.update_layout(
        template="plotly_white",
        title_x=0.02,
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis_title=x,
        yaxis_title=y
    )

    return figure


def make_donut_chart(
    data,
    names,
    values,
    title
):
    """Create a reusable donut chart."""

    figure = px.pie(
        data,
        names=names,
        values=values,
        hole=0.55,
        title=title
    )

    figure.update_layout(
        template="plotly_white",
        title_x=0.02,
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title_text=names
    )

    return figure
