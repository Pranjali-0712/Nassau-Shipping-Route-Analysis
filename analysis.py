import pandas as pd
import numpy as np
import pgeocode

# ==================================================
# 1. LOAD DATA
# ==================================================

df = pd.read_csv("data/Nassau Candy Distributor (1).csv")

print("Total orders/rows:", len(df))


# ==================================================
# 2. CLEAN POSTAL CODES
# ==================================================

df["Postal Code"] = df["Postal Code"].astype(str).str.strip()

# Restore leading zeros for U.S. ZIP codes
us_mask = df["Country/Region"] == "United States"

df.loc[us_mask, "Postal Code"] = (
    df.loc[us_mask, "Postal Code"]
    .str.replace(r"\.0$", "", regex=True)
    .str.zfill(5)
)


# ==================================================
# 3. PRODUCT → FACTORY MAPPING
# ==================================================

factory_mapping = {

    "Lot's O' Nuts": [
        "Wonka Bar - Nutty Crunch Surprise",
        "Wonka Bar - Fudge Mallows",
        "Wonka Bar -Scrumdiddlyumptious"
    ],

    "Wicked Choccy's": [
        "Wonka Bar - Milk Chocolate",
        "Wonka Bar - Triple Dazzle Caramel"
    ],

    "Sugar Shack": [
        "Laffy Taffy",
        "SweeTARTS",
        "Nerds",
        "Fun Dip",
        "Fizzy Lifting Drinks"
    ],

    "Secret Factory": [
        "Everlasting Gobstopper",
        "Lickable Wallpaper",
        "Wonka Gum"
    ],

    "The Other Factory": [
        "Hair Toffee",
        "Kazookles"
    ]
}


# Create reverse mapping:
# Product → Factory

product_to_factory = {}

for factory, products in factory_mapping.items():

    for product in products:
        product_to_factory[product] = factory


df["Factory"] = df["Product Name"].map(product_to_factory)


# ==================================================
# 4. CHECK FACTORY MAPPING
# ==================================================

print("\nFactory mapping check:")

print(
    "Unmapped products:",
    df["Factory"].isna().sum()
)

print("\nFactory counts:")

print(
    df["Factory"].value_counts()
)


# ==================================================
# 5. FACTORY COORDINATES
# ==================================================

factory_coordinates = {

    "Lot's O' Nuts": {
        "Latitude": 32.881893,
        "Longitude": -111.768036
    },

    "Wicked Choccy's": {
        "Latitude": 32.076176,
        "Longitude": -81.088371
    },

    "Sugar Shack": {
        "Latitude": 48.119140,
        "Longitude": -96.181150
    },

    "Secret Factory": {
        "Latitude": 41.446333,
        "Longitude": -90.565487
    },

    "The Other Factory": {
        "Latitude": 35.117500,
        "Longitude": -89.971107
    }
}


df["Factory Latitude"] = df["Factory"].map(
    lambda x: factory_coordinates.get(x, {}).get("Latitude")
)

df["Factory Longitude"] = df["Factory"].map(
    lambda x: factory_coordinates.get(x, {}).get("Longitude")
)


# ==================================================
# 6. CUSTOMER GEOGRAPHIC COORDINATES
# ==================================================

us_geo = pgeocode.Nominatim("US")
ca_geo = pgeocode.Nominatim("CA")


locations = df[
    ["Country/Region", "Postal Code"]
].drop_duplicates().reset_index(drop=True)


locations["Customer Latitude"] = None
locations["Customer Longitude"] = None
locations["Customer City"] = None
locations["Customer State"] = None


for i, row in locations.iterrows():

    country = row["Country/Region"]
    postal_code = row["Postal Code"]

    if country == "United States":

        result = us_geo.query_postal_code(postal_code)

    elif country == "Canada":

        result = ca_geo.query_postal_code(postal_code)

    else:

        continue

    locations.at[i, "Customer Latitude"] = result["latitude"]
    locations.at[i, "Customer Longitude"] = result["longitude"]
    locations.at[i, "Customer City"] = result["place_name"]
    locations.at[i, "Customer State"] = result["state_name"]


# ==================================================
# 7. MERGE CUSTOMER COORDINATES INTO MAIN DATA
# ==================================================

df = df.merge(
    locations,
    on=["Country/Region", "Postal Code"],
    how="left"
)


# ==================================================
# 8. CREATE ROUTE
# ==================================================

df["Route"] = (
    df["Factory"]
    + " → "
    + df["State/Province"]
)


# ==================================================
# 9. DISPLAY RESULTS
# ==================================================

print("\nSample enriched data:")

print(
    df[
        [
            "Order ID",
            "Product Name",
            "Factory",
            "State/Province",
            "Postal Code",
            "Customer City",
            "Customer State",
            "Factory Latitude",
            "Factory Longitude",
            "Customer Latitude",
            "Customer Longitude",
            "Route"
        ]
    ].head(10).to_string(index=False)
)


# ==================================================
# 10. FINAL CHECKS
# ==================================================

print("\nFINAL CHECKS")

print("Total rows:", len(df))

print(
    "Unmapped factories:",
    df["Factory"].isna().sum()
)

print(
    "Missing customer latitude:",
    df["Customer Latitude"].isna().sum()
)

print(
    "Missing customer longitude:",
    df["Customer Longitude"].isna().sum()
)

print(
    "Unique routes:",
    df["Route"].nunique()
)
# Save enriched dataset
output_file = "data/enriched_shipping_data.csv"
df.to_csv(output_file, index=False)

print(f"\nEnriched dataset saved to: {output_file}")
# ============================================================
# ROUTE EFFICIENCY ANALYSIS
# ============================================================
# Convert dates back to datetime before calculating date difference
df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    format="%d-%m-%Y",
    errors="coerce"
)

df["Ship Date"] = pd.to_datetime(
    df["Ship Date"],
    format="%d-%m-%Y",
    errors="coerce"
)

print("\n" + "=" * 60)
print("ROUTE EFFICIENCY ANALYSIS")
print("=" * 60)

# Calculate source date difference
df["Source Date Difference"] = (
    df["Ship Date"] - df["Order Date"]
).dt.days

# Route-level summary
route_summary = (
    df.groupby(["Factory", "State/Province"])
    .agg(
        Shipments=("Order ID", "count"),
        Unique_Orders=("Order ID", "nunique"),
        Units=("Units", "sum"),
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Average_Source_Date_Difference=("Source Date Difference", "mean"),
        Median_Source_Date_Difference=("Source Date Difference", "median"),
        Lead_Time_Std=("Source Date Difference", "std"),
        Min_Source_Date_Difference=("Source Date Difference", "min"),
        Max_Source_Date_Difference=("Source Date Difference", "max")
    )
    .reset_index()
)

# Round numerical values
route_summary["Average_Source_Date_Difference"] = (
    route_summary["Average_Source_Date_Difference"].round(2)
)

route_summary["Median_Source_Date_Difference"] = (
    route_summary["Median_Source_Date_Difference"].round(2)
)

route_summary["Lead_Time_Std"] = (
    route_summary["Lead_Time_Std"].round(2)
)

# Sort by shipment volume
route_summary = route_summary.sort_values(
    "Shipments",
    ascending=False
)

print("\nTop 10 routes by shipment volume:")
print(
    route_summary[
        [
            "Factory",
            "State/Province",
            "Shipments",
            "Unique_Orders",
            "Units",
            "Sales",
            "Cost",
            "Gross_Profit"
        ]
    ].head(10).to_string(index=False)
)

# Save route analysis
route_file = "data/route_summary.csv"
route_summary.to_csv(route_file, index=False)

print(f"\nRoute summary saved to: {route_file}")
print(f"Total routes analyzed: {len(route_summary)}")
# ============================================================
# ROUTE EFFICIENCY SCORE
# ============================================================

print("\n" + "=" * 60)
print("ROUTE EFFICIENCY SCORE")
print("=" * 60)

# Profit margin
route_summary["Profit_Margin"] = (
    route_summary["Gross_Profit"] /
    route_summary["Sales"].replace(0, np.nan)
) * 100

# Cost as percentage of sales
route_summary["Cost_Ratio"] = (
    route_summary["Cost"] /
    route_summary["Sales"].replace(0, np.nan)
) * 100

# Normalize metrics using min-max scaling
def min_max_score(series):
    min_value = series.min()
    max_value = series.max()

    if max_value == min_value:
        return pd.Series(100, index=series.index)

    return (
        (series - min_value) /
        (max_value - min_value)
    ) * 100


# Higher profit margin = better
route_summary["Profit_Score"] = min_max_score(
    route_summary["Profit_Margin"]
)

# Lower cost ratio = better
route_summary["Cost_Efficiency_Score"] = (
    100 - min_max_score(route_summary["Cost_Ratio"])
)

# Lower lead-time variability = better
route_summary["Consistency_Score"] = (
    100 - min_max_score(
        route_summary["Lead_Time_Std"].fillna(0)
    )
)

# Final analytical score
route_summary["Route_Efficiency_Score"] = (
    route_summary["Profit_Score"] * 0.40
    + route_summary["Cost_Efficiency_Score"] * 0.30
    + route_summary["Consistency_Score"] * 0.30
)

route_summary["Route_Efficiency_Score"] = (
    route_summary["Route_Efficiency_Score"].round(2)
)

# Sort by analytical score
route_score = route_summary.sort_values(
    "Route_Efficiency_Score",
    ascending=False
)

print("\nRoute efficiency score calculated.")

print("\nSample route scores:")
print(
    route_score[
        [
            "Factory",
            "State/Province",
            "Shipments",
            "Sales",
            "Cost",
            "Gross_Profit",
            "Profit_Margin",
            "Cost_Ratio",
            "Route_Efficiency_Score"
        ]
    ].head(10).to_string(index=False)
)

# Save scored routes
score_file = "data/route_efficiency_scores.csv"

route_score.to_csv(
    score_file,
    index=False
)

print(f"\nRoute efficiency scores saved to: {score_file}")
# ============================================================
# DELAY FREQUENCY ANALYSIS
# ============================================================

print("\n" + "=" * 60)
print("DELAY FREQUENCY ANALYSIS")
print("=" * 60)

# Threshold used for analysis
delay_threshold = 30

# Identify records above the threshold
df["Above_Threshold"] = (
    df["Source Date Difference"] > delay_threshold
)

# Calculate route-level delay frequency
delay_summary = (
    df.groupby(["Factory", "State/Province"])
    .agg(
        Total_Shipments=("Order ID", "count"),
        Records_Above_Threshold=("Above_Threshold", "sum")
    )
    .reset_index()
)

# Calculate percentage
delay_summary["Delay_Frequency_Percent"] = (
    delay_summary["Records_Above_Threshold"]
    / delay_summary["Total_Shipments"]
    * 100
).round(2)

# Sort by delay frequency
delay_summary = delay_summary.sort_values(
    "Delay_Frequency_Percent",
    ascending=False
)

print(f"\nSource date difference threshold: {delay_threshold} days")

print("\nDelay frequency by route:")
print(
    delay_summary.head(10).to_string(index=False)
)

# Save results
delay_file = "data/route_delay_frequency.csv"

delay_summary.to_csv(
    delay_file,
    index=False
)

print(f"\nDelay frequency saved to: {delay_file}")
# ============================================================
# SHIP MODE COMPARISON
# ============================================================

print("\n" + "=" * 60)
print("SHIP MODE COMPARISON")
print("=" * 60)

ship_mode_summary = (
    df.groupby("Ship Mode")
    .agg(
        Shipments=("Order ID", "count"),
        Unique_Orders=("Order ID", "nunique"),
        Units=("Units", "sum"),
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Average_Source_Date_Difference=(
            "Source Date Difference",
            "mean"
        ),
        Median_Source_Date_Difference=(
            "Source Date Difference",
            "median"
        )
    )
    .reset_index()
)

# Calculate profit margin
ship_mode_summary["Profit_Margin"] = (
    ship_mode_summary["Gross_Profit"]
    / ship_mode_summary["Sales"]
    * 100
).round(2)

ship_mode_summary["Average_Source_Date_Difference"] = (
    ship_mode_summary["Average_Source_Date_Difference"]
    .round(2)
)

ship_mode_summary["Median_Source_Date_Difference"] = (
    ship_mode_summary["Median_Source_Date_Difference"]
    .round(2)
)

print("\nShip mode comparison:")
print(
    ship_mode_summary.to_string(index=False)
)

# Save ship mode analysis
ship_mode_file = "data/ship_mode_summary.csv"

ship_mode_summary.to_csv(
    ship_mode_file,
    index=False
)

print(f"\nShip mode summary saved to: {ship_mode_file}")
# ============================================================
# GEOGRAPHIC SHIPPING MAP DATA
# ============================================================

print("\n" + "=" * 60)
print("GEOGRAPHIC SHIPPING MAP DATA")
print("=" * 60)

# Factory-level geographic summary
factory_locations = df[
    [
        "Factory",
        "Factory Latitude",
        "Factory Longitude"
    ]
].drop_duplicates()

print("\nFactory locations:")
print(factory_locations.to_string(index=False))

# Customer-level geographic summary
customer_locations = (
    df[
        [
            "Customer ID",
            "Customer City",
            "Customer State",
            "Customer Latitude",
            "Customer Longitude"
        ]
    ]
    .drop_duplicates()
)

print("\nCustomer locations:")
print(f"Unique customer locations: {len(customer_locations)}")

# Save factory locations
factory_locations.to_csv(
    "data/factory_locations.csv",
    index=False
)

# Save customer locations
customer_locations.to_csv(
    "data/customer_locations.csv",
    index=False
)

print("\nGeographic data saved:")
print("Factory locations: data/factory_locations.csv")
print("Customer locations: data/customer_locations.csv")