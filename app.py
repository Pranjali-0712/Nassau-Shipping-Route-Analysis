import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Nassau Candy Shipping Route Analysis",
    page_icon="🚚",
    layout="wide"
)

# ============================================================
# LOAD CUSTOM CSS
# ============================================================

with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv("data/enriched_shipping_data.csv")
# ============================================================
# FILTERS
# ============================================================

st.sidebar.header("🔎 Dashboard Filters")

# Region filter
regions = sorted(df["Region"].dropna().unique())

selected_regions = st.sidebar.multiselect(
    "Select Region",
    options=regions,
    default=regions
)

# State filter
states = sorted(df["State/Province"].dropna().unique())

selected_states = st.sidebar.multiselect(
    "Select State / Province",
    options=states,
    default=states
)

# Ship Mode filter
ship_modes = sorted(df["Ship Mode"].dropna().unique())

selected_ship_modes = st.sidebar.multiselect(
    "Select Ship Mode",
    options=ship_modes,
    default=ship_modes
)

# Date filter
df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    errors="coerce"
)

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    (df["Region"].isin(selected_regions)) &
    (df["State/Province"].isin(selected_states)) &
    (df["Ship Mode"].isin(selected_ship_modes))
].copy()

if len(selected_dates) == 2:

    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        (filtered_df["Order Date"].dt.date >= start_date) &
        (filtered_df["Order Date"].dt.date <= end_date)
    ]

st.sidebar.markdown("---")

st.sidebar.write(
    f"**Filtered Shipments:** {len(filtered_df):,}"
)

factory_locations = pd.read_csv(
    "data/factory_locations.csv"
)

# ============================================================
# TITLE
# ============================================================

st.title("🚚 Factory-to-Customer Shipping Route Efficiency Analysis")

st.markdown(
    """
    ### Nassau Candy Distributor

    This dashboard analyzes factory-to-customer shipping routes,
    geographic distribution, shipment volume, cost, sales and profit.
    """
)

# ============================================================
# DATA QUALITY NOTICE
# ============================================================

st.warning(
    """
    **Data Quality Notice:** The source Order Date and Ship Date
    produce unusually large date differences. Therefore, source-date
    differences are treated as a data-quality diagnostic and not as
    actual delivery duration.
    """
)

# ============================================================
# KPI SECTION
# ============================================================

total_shipments = len(filtered_df)

total_sales = filtered_df["Sales"].sum()

total_cost = filtered_df["Cost"].sum()

total_profit = filtered_df["Gross Profit"].sum()

if total_sales > 0:
    profit_margin = (total_profit / total_sales) * 100
else:
    profit_margin = 0

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "📦 Shipments",
        f"{total_shipments:,}"
    )

with col2:
    st.metric(
        "💰 Sales",
        f"${total_sales:,.2f}"
    )

with col3:
    st.metric(
        "💸 Cost",
        f"${total_cost:,.2f}"
    )

with col4:
    st.metric(
        "📈 Gross Profit",
        f"${total_profit:,.2f}"
    )

with col5:
    st.metric(
        "📊 Profit Margin",
        f"{profit_margin:.2f}%"
    )

# ============================================================
# FACTORY PERFORMANCE
# ============================================================

st.markdown("---")

st.header("🏭 Factory Performance")

factory_summary = (
    filtered_df
    .groupby("Factory")
    .agg(
        Shipments=("Order ID", "count"),
        Units=("Units", "sum"),
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum")
    )
    .reset_index()
)

factory_summary["Profit Margin"] = (
    factory_summary["Gross_Profit"]
    / factory_summary["Sales"]
    * 100
).fillna(0)

# ------------------------------------------------------------
# FACTORY CHARTS
# ------------------------------------------------------------

chart1, chart2 = st.columns(2)

with chart1:

    factory_shipments = (
        factory_summary
        .sort_values("Shipments", ascending=False)
    )

    fig_shipments = px.bar(
        factory_shipments,
        x="Factory",
        y="Shipments",
        text="Shipments",
        title="📦 Shipment Volume by Factory"
    )

    fig_shipments.update_traces(
        textposition="outside"
    )

    fig_shipments.update_layout(
        height=400,
        xaxis_title="",
        yaxis_title="Shipments",
        showlegend=False
    )

    st.plotly_chart(
        fig_shipments,
        use_container_width=True
    )


with chart2:

    factory_profit = (
        factory_summary
        .sort_values("Gross_Profit", ascending=False)
    )

    fig_profit = px.bar(
        factory_profit,
        x="Factory",
        y="Gross_Profit",
        text="Gross_Profit",
        title="📈 Gross Profit by Factory"
    )

    fig_profit.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside"
    )

    fig_profit.update_layout(
        height=400,
        xaxis_title="",
        yaxis_title="Gross Profit ($)",
        showlegend=False
    )

    st.plotly_chart(
        fig_profit,
        use_container_width=True
    )

# ------------------------------------------------------------
# FACTORY PERFORMANCE TABLE
# ------------------------------------------------------------

st.subheader("📋 Factory Performance Details")

st.dataframe(
    factory_summary,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Shipments": st.column_config.NumberColumn(
            "Shipments",
            format="%d"
        ),
        "Units": st.column_config.NumberColumn(
            "Units",
            format="%d"
        ),
        "Sales": st.column_config.NumberColumn(
            "Sales",
            format="$%.2f"
        ),
        "Cost": st.column_config.NumberColumn(
            "Cost",
            format="$%.2f"
        ),
        "Gross_Profit": st.column_config.NumberColumn(
            "Gross Profit",
            format="$%.2f"
        ),
        "Profit Margin": st.column_config.NumberColumn(
            "Profit Margin",
            format="%.2f%%"
        )
    }
)
# ============================================================
# ROUTE PERFORMANCE OVERVIEW
# ============================================================

st.markdown("---")

st.header("📊 Route Performance Overview")

route_summary = (
    filtered_df
    .groupby(["Factory", "State/Province"])
    .agg(
        Shipments=("Order ID", "count"),
        Units=("Units", "sum"),
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum")
    )
    .reset_index()
)

route_summary["Profit Margin"] = (
    route_summary["Gross_Profit"]
    / route_summary["Sales"]
    * 100
).fillna(0)

# ------------------------------------------------------------
# TOP ROUTES
# ------------------------------------------------------------

top_routes = route_summary.sort_values(
    "Shipments",
    ascending=False
).head(10)

# ------------------------------------------------------------
# ROUTE CHARTS
# ------------------------------------------------------------

chart1, chart2 = st.columns(2)

with chart1:

    fig_volume = px.bar(
        top_routes.sort_values("Shipments"),
        x="Shipments",
        y="State/Province",
        color="Factory",
        orientation="h",
        title="📦 Top 10 Routes by Shipment Volume",
        text="Shipments"
    )

    fig_volume.update_traces(
        textposition="outside"
    )

    fig_volume.update_layout(
        height=450,
        xaxis_title="Shipments",
        yaxis_title="Destination",
        legend_title="Factory"
    )

    st.plotly_chart(
        fig_volume,
        use_container_width=True
    )


with chart2:

    fig_profit = px.bar(
        top_routes.sort_values("Gross_Profit"),
        x="Gross_Profit",
        y="State/Province",
        color="Factory",
        orientation="h",
        title="💰 Top 10 Routes by Gross Profit",
        text="Gross_Profit"
    )

    fig_profit.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside"
    )

    fig_profit.update_layout(
        height=450,
        xaxis_title="Gross Profit ($)",
        yaxis_title="Destination",
        legend_title="Factory"
    )

    st.plotly_chart(
        fig_profit,
        use_container_width=True
    )

# ------------------------------------------------------------
# ROUTE TABLE
# ------------------------------------------------------------

st.subheader("🏆 Top Performing Routes")

display_routes = top_routes.copy()

st.dataframe(
    display_routes,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Shipments": st.column_config.NumberColumn(
            "Shipments",
            format="%d"
        ),
        "Units": st.column_config.NumberColumn(
            "Units",
            format="%d"
        ),
        "Sales": st.column_config.NumberColumn(
            "Sales",
            format="$%.2f"
        ),
        "Cost": st.column_config.NumberColumn(
            "Cost",
            format="$%.2f"
        ),
        "Gross_Profit": st.column_config.NumberColumn(
            "Gross Profit",
            format="$%.2f"
        ),
        "Profit Margin": st.column_config.NumberColumn(
            "Profit Margin",
            format="%.2f%%"
        )
    }
)

# ============================================================
# GEOGRAPHIC SHIPPING NETWORK
# ============================================================

st.markdown("---")

st.header("🗺️ Geographic Shipping Network")

st.write(
    "Explore the distribution of customer destinations and "
    "the factories serving each market."
)

# ------------------------------------------------------------
# CUSTOMER LOCATIONS
# ------------------------------------------------------------

customer_map = (
    filtered_df[
        [
            "Customer City",
            "Customer State",
            "Customer Latitude",
            "Customer Longitude",
            "Factory",
            "Order ID"
        ]
    ]
    .dropna(
        subset=[
            "Customer Latitude",
            "Customer Longitude"
        ]
    )
)

customer_locations = (
    customer_map
    .groupby(
        [
            "Customer City",
            "Customer State",
            "Customer Latitude",
            "Customer Longitude",
            "Factory"
        ]
    )
    .agg(
        Shipments=("Order ID", "count")
    )
    .reset_index()
)

# ------------------------------------------------------------
# MAP
# ------------------------------------------------------------

fig_map = px.scatter_geo(
    customer_locations,
    lat="Customer Latitude",
    lon="Customer Longitude",
    size="Shipments",
    color="Factory",
    hover_name="Customer City",
    hover_data={
        "Customer State": True,
        "Factory": True,
        "Shipments": True,
        "Customer Latitude": False,
        "Customer Longitude": False
    },
    scope="usa",
    title="Customer Distribution by Factory"
)

fig_map.update_traces(
    marker=dict(
        opacity=0.65
    )
)

# ------------------------------------------------------------
# FACTORY MARKERS
# ------------------------------------------------------------

fig_map.add_scattergeo(
    lat=factory_locations["Factory Latitude"],
    lon=factory_locations["Factory Longitude"],
    text=factory_locations["Factory"],
    mode="markers+text",
    textposition="top center",
    marker=dict(
        size=16,
        symbol="star"
    ),
    name="Factories"
)

fig_map.update_geos(
    showcountries=True,
    showsubunits=True,
    showland=True,
    fitbounds="locations"
)

fig_map.update_layout(
    height=650,
    margin=dict(
        l=0,
        r=0,
        t=60,
        b=0
    ),
    legend_title="Factory"
)

st.plotly_chart(
    fig_map,
    use_container_width=True
)

# ------------------------------------------------------------
# FACTORY LOCATION TABLE
# ------------------------------------------------------------

st.subheader("🏭 Factory Locations")

st.dataframe(
    factory_locations,
    use_container_width=True,
    hide_index=True
)
# ============================================================
# ROUTE VOLUME
# ============================================================

st.header("📦 Top Shipping Routes")

route_summary = (
    filtered_df.groupby(
        ["Factory", "State/Province"]
    )
    .agg(
        Shipments=("Order ID", "count"),
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum")
    )
    .reset_index()
    .sort_values(
        "Shipments",
        ascending=False
    )
)

st.dataframe(
    route_summary.head(20),
    use_container_width=True
)
# ============================================================
# ROUTE EFFICIENCY ANALYSIS
# ============================================================

st.markdown("---")

st.header("🚚 Route Efficiency Analysis")

route_efficiency = pd.read_csv(
    "data/route_efficiency_scores.csv"
)

# Apply current state filter
route_efficiency = route_efficiency[
    route_efficiency["State/Province"].isin(selected_states)
].copy()

# Apply current factory filter if available
selected_factories = filtered_df["Factory"].dropna().unique()

route_efficiency = route_efficiency[
    route_efficiency["Factory"].isin(selected_factories)
].copy()

# ============================================================
# EFFICIENCY KPIs
# ============================================================

if len(route_efficiency) > 0:

    best_route = route_efficiency.loc[
        route_efficiency["Route_Efficiency_Score"].idxmax()
    ]

    worst_route = route_efficiency.loc[
        route_efficiency["Route_Efficiency_Score"].idxmin()
    ]

    average_efficiency = route_efficiency[
        "Route_Efficiency_Score"
    ].mean()

    total_routes = len(route_efficiency)

    eff_col1, eff_col2, eff_col3, eff_col4 = st.columns(4)

    with eff_col1:
        st.metric(
            "🛣️ Routes Analyzed",
            f"{total_routes:,}"
        )

    with eff_col2:
        st.metric(
            "⭐ Average Efficiency",
            f"{average_efficiency:.2f}"
        )

    with eff_col3:
        st.metric(
            "🏆 Best Efficiency",
            f"{best_route['Route_Efficiency_Score']:.2f}"
        )

    with eff_col4:
        st.metric(
            "📍 Best Destination",
            f"{best_route['State/Province']}"
        )

    # ========================================================
    # TOP AND LOW PERFORMING ROUTES
    # ========================================================

    top_routes = route_efficiency.sort_values(
        "Route_Efficiency_Score",
        ascending=False
    ).head(10)

    low_routes = route_efficiency.sort_values(
        "Route_Efficiency_Score",
        ascending=True
    ).head(10)

    chart1, chart2 = st.columns(2)

    with chart1:

        fig_top = px.bar(
            top_routes.sort_values(
                "Route_Efficiency_Score",
                ascending=True
            ),
            x="Route_Efficiency_Score",
            y="State/Province",
            color="Factory",
            orientation="h",
            title="🏆 Top 10 Most Efficient Routes",
            text="Route_Efficiency_Score"
        )

        fig_top.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )

        fig_top.update_layout(
            height=500,
            xaxis_title="Efficiency Score",
            yaxis_title="Destination",
            legend_title="Factory"
        )

        st.plotly_chart(
            fig_top,
            use_container_width=True
        )

    with chart2:

        fig_low = px.bar(
            low_routes.sort_values(
                "Route_Efficiency_Score",
                ascending=True
            ),
            x="Route_Efficiency_Score",
            y="State/Province",
            color="Factory",
            orientation="h",
            title="⚠️ Routes Requiring Attention",
            text="Route_Efficiency_Score"
        )

        fig_low.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )

        fig_low.update_layout(
            height=500,
            xaxis_title="Efficiency Score",
            yaxis_title="Destination",
            legend_title="Factory"
        )

        st.plotly_chart(
            fig_low,
            use_container_width=True
        )

    # ========================================================
    # EFFICIENCY DISTRIBUTION
    # ========================================================

    st.subheader("📊 Efficiency Score Distribution")

    fig_distribution = px.histogram(
        route_efficiency,
        x="Route_Efficiency_Score",
        nbins=20,
        title="Distribution of Route Efficiency Scores",
        labels={
            "Route_Efficiency_Score": "Efficiency Score"
        }
    )

    fig_distribution.update_layout(
        height=400,
        xaxis_title="Efficiency Score",
        yaxis_title="Number of Routes"
    )

    st.plotly_chart(
        fig_distribution,
        use_container_width=True
    )

    # ========================================================
    # DETAILED ROUTE TABLE
    # ========================================================

    st.subheader("📋 Route Efficiency Details")

    display_efficiency = route_efficiency.sort_values(
        "Route_Efficiency_Score",
        ascending=False
    )

    st.dataframe(
        display_efficiency,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Sales": st.column_config.NumberColumn(
                "Sales",
                format="$%.2f"
            ),
            "Cost": st.column_config.NumberColumn(
                "Cost",
                format="$%.2f"
            ),
            "Gross_Profit": st.column_config.NumberColumn(
                "Gross Profit",
                format="$%.2f"
            ),
            "Profit_Margin": st.column_config.NumberColumn(
                "Profit Margin",
                format="%.2f%%"
            ),
            "Cost_Ratio": st.column_config.NumberColumn(
                "Cost Ratio",
                format="%.2f%%"
            ),
            "Route_Efficiency_Score": st.column_config.NumberColumn(
                "Efficiency Score",
                format="%.2f"
            )
        }
    )

else:

    st.info(
        "No route efficiency data is available for the selected filters."
    )
    # ============================================================
# LEAD-TIME & DELAY ANALYSIS
# ============================================================

st.markdown("---")

st.header("⏱️ Shipping Lead-Time Analysis")

# ------------------------------------------------------------
# CALCULATE SHIPPING LEAD TIME
# ------------------------------------------------------------

lead_time_df = filtered_df.copy()

lead_time_df["Ship Date"] = pd.to_datetime(
    lead_time_df["Ship Date"],
    errors="coerce"
)

lead_time_df["Shipping Lead Time"] = (
    lead_time_df["Ship Date"] -
    lead_time_df["Order Date"]
).dt.days

# Remove invalid / negative lead times
lead_time_df = lead_time_df[
    lead_time_df["Shipping Lead Time"].notna() &
    (lead_time_df["Shipping Lead Time"] >= 0)
].copy()

# ------------------------------------------------------------
# LEAD-TIME THRESHOLD
# ------------------------------------------------------------

threshold = st.slider(
    "🚨 Lead-Time Threshold (days)",
    min_value=1,
    max_value=30,
    value=5,
    step=1
)

# ------------------------------------------------------------
# DELAY CALCULATION
# ------------------------------------------------------------

lead_time_df["Delayed"] = (
    lead_time_df["Shipping Lead Time"] > threshold
)

total_valid_shipments = len(lead_time_df)

delayed_shipments = lead_time_df["Delayed"].sum()

if total_valid_shipments > 0:
    delay_frequency = (
        delayed_shipments /
        total_valid_shipments
    ) * 100
else:
    delay_frequency = 0

# ------------------------------------------------------------
# LEAD-TIME KPIs
# ------------------------------------------------------------

avg_lead_time = (
    lead_time_df["Shipping Lead Time"].mean()
    if total_valid_shipments > 0
    else 0
)

median_lead_time = (
    lead_time_df["Shipping Lead Time"].median()
    if total_valid_shipments > 0
    else 0
)

lead_time_std = (
    lead_time_df["Shipping Lead Time"].std()
    if total_valid_shipments > 1
    else 0
)

max_lead_time = (
    lead_time_df["Shipping Lead Time"].max()
    if total_valid_shipments > 0
    else 0
)

# ------------------------------------------------------------
# KPI CARDS
# ------------------------------------------------------------

lt1, lt2, lt3, lt4, lt5 = st.columns(5)

with lt1:
    st.metric(
        "⏱️ Average Lead Time",
        f"{avg_lead_time:.2f} days"
    )

with lt2:
    st.metric(
        "📊 Median Lead Time",
        f"{median_lead_time:.2f} days"
    )

with lt3:
    st.metric(
        "⚠️ Delayed Shipments",
        f"{delayed_shipments:,}"
    )

with lt4:
    st.metric(
        "🚨 Delay Frequency",
        f"{delay_frequency:.2f}%"
    )

with lt5:
    st.metric(
        "📈 Lead-Time Variability",
        f"{lead_time_std:.2f} days"
    )

# ------------------------------------------------------------
# LEAD-TIME DISTRIBUTION
# ------------------------------------------------------------

chart1, chart2 = st.columns(2)

with chart1:

    fig_lead_distribution = px.histogram(
        lead_time_df,
        x="Shipping Lead Time",
        nbins=20,
        title="📊 Shipping Lead-Time Distribution",
        labels={
            "Shipping Lead Time": "Lead Time (Days)"
        }
    )

    fig_lead_distribution.add_vline(
        x=threshold,
        line_dash="dash",
        annotation_text=f"Threshold: {threshold} days"
    )

    fig_lead_distribution.update_layout(
        height=420,
        xaxis_title="Lead Time (Days)",
        yaxis_title="Number of Shipments"
    )

    st.plotly_chart(
        fig_lead_distribution,
        use_container_width=True
    )

with chart2:

    delay_summary = pd.DataFrame({
        "Status": ["On Time", "Delayed"],
        "Shipments": [
            total_valid_shipments - delayed_shipments,
            delayed_shipments
        ]
    })

    fig_delay = px.pie(
        delay_summary,
        names="Status",
        values="Shipments",
        hole=0.55,
        title="🚨 Shipment Delay Status"
    )

    fig_delay.update_layout(
        height=420
    )

    st.plotly_chart(
        fig_delay,
        use_container_width=True
    )

# ------------------------------------------------------------
# AVERAGE LEAD TIME BY ROUTE
# ------------------------------------------------------------

st.subheader("🚚 Average Lead Time by Factory → State")

route_lead_time = (
    lead_time_df
    .groupby(
        ["Factory", "State/Province"]
    )
    .agg(
        Shipments=("Order ID", "count"),
        Average_Lead_Time=("Shipping Lead Time", "mean"),
        Lead_Time_Std=("Shipping Lead Time", "std"),
        Delayed_Shipments=("Delayed", "sum")
    )
    .reset_index()
)

route_lead_time["Delay Frequency"] = (
    route_lead_time["Delayed_Shipments"] /
    route_lead_time["Shipments"] *
    100
).fillna(0)

route_lead_time = route_lead_time.sort_values(
    "Average_Lead_Time",
    ascending=False
)

# ------------------------------------------------------------
# ROUTE LEAD-TIME CHART
# ------------------------------------------------------------

top_slowest_routes = route_lead_time.head(10)

fig_route_lead = px.bar(
    top_slowest_routes.sort_values(
        "Average_Lead_Time"
    ),
    x="Average_Lead_Time",
    y="State/Province",
    color="Factory",
    orientation="h",
    text="Average_Lead_Time",
    title="⚠️ 10 Routes with Highest Average Lead Time"
)

fig_route_lead.update_traces(
    texttemplate="%{text:.1f} days",
    textposition="outside"
)

fig_route_lead.update_layout(
    height=500,
    xaxis_title="Average Lead Time (Days)",
    yaxis_title="Destination",
    legend_title="Factory"
)

st.plotly_chart(
    fig_route_lead,
    use_container_width=True
)

# ------------------------------------------------------------
# ROUTE LEAD-TIME TABLE
# ------------------------------------------------------------

st.subheader("📋 Route Lead-Time Details")

st.dataframe(
    route_lead_time,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Shipments": st.column_config.NumberColumn(
            "Shipments",
            format="%d"
        ),
        "Average_Lead_Time": st.column_config.NumberColumn(
            "Average Lead Time",
            format="%.2f days"
        ),
        "Lead_Time_Std": st.column_config.NumberColumn(
            "Lead-Time Variability",
            format="%.2f days"
        ),
        "Delayed_Shipments": st.column_config.NumberColumn(
            "Delayed Shipments",
            format="%d"
        ),
        "Delay Frequency": st.column_config.NumberColumn(
            "Delay Frequency",
            format="%.2f%%"
        )
    }
)

# ------------------------------------------------------------
# ORDER-LEVEL SHIPMENT DETAILS
# ------------------------------------------------------------

st.subheader("🔎 Order-Level Shipment Details")

display_orders = lead_time_df[
    [
        "Order ID",
        "Order Date",
        "Ship Date",
        "Shipping Lead Time",
        "Ship Mode",
        "Factory",
        "State/Province",
        "Sales",
        "Cost",
        "Gross Profit",
        "Delayed"
    ]
].sort_values(
    "Shipping Lead Time",
    ascending=False
)

st.dataframe(
    display_orders.head(100),
    use_container_width=True,
    hide_index=True
)
# ============================================================
# SHIP MODE PERFORMANCE COMPARISON
# ============================================================

st.markdown("---")

st.header("🚚 Ship Mode Performance Comparison")

# ------------------------------------------------------------
# SHIP MODE SUMMARY
# ------------------------------------------------------------

ship_mode_summary = (
    lead_time_df
    .groupby("Ship Mode")
    .agg(
        Shipments=("Order ID", "count"),
        Average_Lead_Time=("Shipping Lead Time", "mean"),
        Median_Lead_Time=("Shipping Lead Time", "median"),
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Delayed_Shipments=("Delayed", "sum")
    )
    .reset_index()
)

# Calculate delay frequency correctly
ship_mode_summary["Delay Frequency"] = (
    ship_mode_summary["Delayed_Shipments"]
    / ship_mode_summary["Shipments"]
    * 100
).fillna(0)

# ------------------------------------------------------------
# SHIP MODE CHARTS
# ------------------------------------------------------------

chart1, chart2 = st.columns(2)

with chart1:

    fig_ship_mode = px.bar(
        ship_mode_summary.sort_values(
            "Average_Lead_Time"
        ),
        x="Ship Mode",
        y="Average_Lead_Time",
        text="Average_Lead_Time",
        title="⏱️ Average Lead Time by Ship Mode"
    )

    fig_ship_mode.update_traces(
        texttemplate="%{text:.1f} days",
        textposition="outside"
    )

    fig_ship_mode.update_layout(
        height=450,
        xaxis_title="Ship Mode",
        yaxis_title="Average Lead Time (Days)",
        showlegend=False
    )

    st.plotly_chart(
        fig_ship_mode,
        use_container_width=True
    )


with chart2:

    fig_ship_volume = px.bar(
        ship_mode_summary.sort_values(
            "Shipments"
        ),
        x="Shipments",
        y="Ship Mode",
        orientation="h",
        text="Shipments",
        title="📦 Shipment Volume by Ship Mode"
    )

    fig_ship_volume.update_traces(
        textposition="outside"
    )

    fig_ship_volume.update_layout(
        height=450,
        xaxis_title="Shipments",
        yaxis_title="Ship Mode",
        showlegend=False
    )

    st.plotly_chart(
        fig_ship_volume,
        use_container_width=True
    )

# ------------------------------------------------------------
# DELAY FREQUENCY BY SHIP MODE
# ------------------------------------------------------------

st.subheader("🚨 Delay Frequency by Ship Mode")

fig_delay_mode = px.bar(
    ship_mode_summary.sort_values(
        "Delay Frequency"
    ),
    x="Ship Mode",
    y="Delay Frequency",
    text="Delay Frequency",
    title="Delay Frequency by Shipping Method"
)

fig_delay_mode.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig_delay_mode.update_layout(
    height=400,
    xaxis_title="Ship Mode",
    yaxis_title="Delay Frequency (%)",
    showlegend=False
)

st.plotly_chart(
    fig_delay_mode,
    use_container_width=True
)

# ------------------------------------------------------------
# SHIP MODE TABLE
# ------------------------------------------------------------

st.subheader("📋 Ship Mode Performance Details")

st.dataframe(
    ship_mode_summary,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Shipments": st.column_config.NumberColumn(
            "Shipments",
            format="%d"
        ),
        "Average_Lead_Time": st.column_config.NumberColumn(
            "Average Lead Time",
            format="%.2f days"
        ),
        "Median_Lead_Time": st.column_config.NumberColumn(
            "Median Lead Time",
            format="%.2f days"
        ),
        "Delayed_Shipments": st.column_config.NumberColumn(
            "Delayed Shipments",
            format="%d"
        ),
        "Delay Frequency": st.column_config.NumberColumn(
            "Delay Frequency",
            format="%.2f%%"
        ),
        "Sales": st.column_config.NumberColumn(
            "Sales",
            format="$%.2f"
        ),
        "Cost": st.column_config.NumberColumn(
            "Cost",
            format="$%.2f"
        )
    }
)
# ============================================================
# GEOGRAPHIC BOTTLENECK ANALYSIS
# ============================================================

st.markdown("---")

st.header("🗺️ Geographic Bottleneck Analysis")

st.write(
    "Identify states and regions with high shipping volume, "
    "long lead times, and frequent delays."
)

# ------------------------------------------------------------
# STATE-LEVEL BOTTLENECK SUMMARY
# ------------------------------------------------------------

state_bottleneck = (
    lead_time_df
    .groupby(["State/Province", "Region"])
    .agg(
        Shipments=("Order ID", "count"),
        Average_Lead_Time=("Shipping Lead Time", "mean"),
        Lead_Time_Variability=("Shipping Lead Time", "std"),
        Delayed_Shipments=("Delayed", "sum")
    )
    .reset_index()
)

state_bottleneck["Delay Frequency"] = (
    state_bottleneck["Delayed_Shipments"]
    / state_bottleneck["Shipments"]
    * 100
).fillna(0)

state_bottleneck["Lead_Time_Variability"] = (
    state_bottleneck["Lead_Time_Variability"]
).fillna(0)

# ------------------------------------------------------------
# BOTTLENECK SCORE
# ------------------------------------------------------------

state_bottleneck["Bottleneck Score"] = (
    state_bottleneck["Average_Lead_Time"]
    * (1 + state_bottleneck["Delay Frequency"] / 100)
)

# ------------------------------------------------------------
# BOTTLENECK KPIs
# ------------------------------------------------------------

highest_lead_state = state_bottleneck.loc[
    state_bottleneck["Average_Lead_Time"].idxmax()
]

highest_delay_state = state_bottleneck.loc[
    state_bottleneck["Delay Frequency"].idxmax()
]

highest_volume_state = state_bottleneck.loc[
    state_bottleneck["Shipments"].idxmax()
]

b1, b2, b3, b4 = st.columns(4)

with b1:
    st.metric(
        "📦 Highest Volume State",
        highest_volume_state["State/Province"]
    )

with b2:
    st.metric(
        "⏱️ Highest Avg Lead Time",
        f"{highest_lead_state['Average_Lead_Time']:.2f} days"
    )

with b3:
    st.metric(
        "🚨 Highest Delay Frequency",
        f"{highest_delay_state['Delay Frequency']:.2f}%"
    )

with b4:
    st.metric(
        "⚠️ States Analyzed",
        f"{len(state_bottleneck):,}"
    )

# ------------------------------------------------------------
# HIGH LEAD-TIME STATES
# ------------------------------------------------------------

chart1, chart2 = st.columns(2)

with chart1:

    slowest_states = state_bottleneck.sort_values(
        "Average_Lead_Time",
        ascending=False
    ).head(10)

    fig_slow_states = px.bar(
        slowest_states.sort_values(
            "Average_Lead_Time"
        ),
        x="Average_Lead_Time",
        y="State/Province",
        color="Region",
        orientation="h",
        text="Average_Lead_Time",
        title="⏱️ States with Highest Average Lead Time"
    )

    fig_slow_states.update_traces(
        texttemplate="%{text:.1f} days",
        textposition="outside"
    )

    fig_slow_states.update_layout(
        height=500,
        xaxis_title="Average Lead Time (Days)",
        yaxis_title="State / Province"
    )

    st.plotly_chart(
        fig_slow_states,
        use_container_width=True
    )

# ------------------------------------------------------------
# HIGH DELAY STATES
# ------------------------------------------------------------

with chart2:

    delay_states = state_bottleneck.sort_values(
        "Delay Frequency",
        ascending=False
    ).head(10)

    fig_delay_states = px.bar(
        delay_states.sort_values(
            "Delay Frequency"
        ),
        x="Delay Frequency",
        y="State/Province",
        color="Region",
        orientation="h",
        text="Delay Frequency",
        title="🚨 States with Highest Delay Frequency"
    )

    fig_delay_states.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_delay_states.update_layout(
        height=500,
        xaxis_title="Delay Frequency (%)",
        yaxis_title="State / Province"
    )

    st.plotly_chart(
        fig_delay_states,
        use_container_width=True
    )

# ------------------------------------------------------------
# HIGH VOLUME + POOR PERFORMANCE
# ------------------------------------------------------------

st.subheader("⚠️ High-Volume & Poor-Performance States")

volume_threshold = state_bottleneck["Shipments"].median()
lead_threshold = state_bottleneck["Average_Lead_Time"].median()

congestion_states = state_bottleneck[
    (state_bottleneck["Shipments"] >= volume_threshold) &
    (state_bottleneck["Average_Lead_Time"] >= lead_threshold)
].copy()

if len(congestion_states) > 0:

    fig_congestion = px.scatter(
        congestion_states,
        x="Shipments",
        y="Average_Lead_Time",
        size="Delay Frequency",
        color="Region",
        hover_name="State/Province",
        hover_data={
            "Shipments": True,
            "Average_Lead_Time": ":.2f",
            "Delay Frequency": ":.2f",
            "Region": True
        },
        title="📍 High Shipment Volume vs Poor Shipping Performance"
    )

    fig_congestion.update_layout(
        height=500,
        xaxis_title="Shipment Volume",
        yaxis_title="Average Lead Time (Days)"
    )

    st.plotly_chart(
        fig_congestion,
        use_container_width=True
    )

else:

    st.info(
        "No high-volume states with above-median lead time "
        "were identified for the current filters."
    )

# ------------------------------------------------------------
# BOTTLENECK DETAILS
# ------------------------------------------------------------

st.subheader("📋 Geographic Bottleneck Details")

display_bottlenecks = state_bottleneck.sort_values(
    "Bottleneck Score",
    ascending=False
)

st.dataframe(
    display_bottlenecks,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Shipments": st.column_config.NumberColumn(
            "Shipments",
            format="%d"
        ),
        "Average_Lead_Time": st.column_config.NumberColumn(
            "Average Lead Time",
            format="%.2f days"
        ),
        "Lead_Time_Variability": st.column_config.NumberColumn(
            "Lead-Time Variability",
            format="%.2f days"
        ),
        "Delayed_Shipments": st.column_config.NumberColumn(
            "Delayed Shipments",
            format="%d"
        ),
        "Delay Frequency": st.column_config.NumberColumn(
            "Delay Frequency",
            format="%.2f%%"
        ),
        "Bottleneck Score": st.column_config.NumberColumn(
            "Bottleneck Score",
            format="%.2f"
        )
    }
)