# 🚚 Factory-to-Customer Shipping Route Efficiency Analysis

## Nassau Candy Distributor

An interactive data analytics and visualization project designed to analyze factory-to-customer shipping routes, shipping lead time, delays, route efficiency, geographic distribution, and shipping-mode performance for Nassau Candy Distributor.

The project transforms shipment-level transactional data into an interactive logistics decision-support dashboard using **Python, Pandas, Plotly, and Streamlit**.

---

## 📌 Project Overview

Efficient logistics operations require clear visibility into shipment volumes, route performance, delays, geographic bottlenecks, and shipping-mode behavior.

This project analyzes the shipping network of Nassau Candy Distributor by connecting factories with customer destinations and evaluating route-level operational and financial indicators.

The interactive dashboard enables users to explore:

- Factory performance
- Factory-to-customer routes
- Shipping volume
- Sales and cost
- Gross profit and profit margin
- Shipping lead time
- Delay frequency
- Lead-time variability
- Route efficiency scores
- Geographic customer distribution
- Shipping-mode performance

The goal is to help identify routes that may require further operational investigation and provide a centralized view of logistics performance.

---

## 🎯 Objectives

The main objectives of this project are:

1. Clean and validate shipment-level logistics data.
2. Analyze factory-to-customer shipping routes.
3. Calculate shipping lead-time indicators.
4. Identify potentially delayed shipments.
5. Compare route performance across states and regions.
6. Benchmark routes using efficiency scores.
7. Analyze geographic shipment distribution.
8. Compare different shipping modes.
9. Provide interactive filtering and visualization.
10. Develop a deployable logistics analytics dashboard.

---

## 🗂️ Dataset

The project uses an enriched Nassau Candy shipping dataset containing shipment, customer, product, geographic, and financial information.

### Main Fields

| Field | Description |
|---|---|
| Row ID | Unique row identifier |
| Order ID | Shipment/order identifier |
| Order Date | Date associated with the order |
| Ship Date | Date associated with shipment |
| Ship Mode | Shipping method |
| Customer ID | Customer identifier |
| Country/Region | Customer country or region |
| City | Customer city |
| State/Province | Customer state |
| Postal Code | Customer postal code |
| Division | Business division |
| Region | Geographic region |
| Product ID | Product identifier |
| Product Name | Product name |
| Sales | Sales value |
| Units | Number of units |
| Gross Profit | Gross profit |
| Cost | Cost value |

Additional enriched fields are used for factory assignment, customer coordinates, and route-efficiency analysis.

---

## 🏭 Factory Locations

The project analyzes five factory locations:

| Factory | Latitude | Longitude |
|---|---:|---:|
| Lot's O' Nuts | 32.881893 | -111.768036 |
| Wicked Choccy's | 32.076176 | -81.088371 |
| Sugar Shack | 48.119140 | -96.181150 |
| Secret Factory | 41.446333 | -90.565487 |
| The Other Factory | 35.117500 | -89.971107 |

These locations are displayed together with customer locations in the geographic shipping network visualization.

---

# 🔬 Methodology

## 1. Data Cleaning and Validation

The dataset is loaded and validated using Pandas.

The preprocessing stage includes:

- Date conversion
- Numerical field validation
- Missing-value handling
- Geographic coordinate validation
- Negative lead-time removal
- Route-level aggregation

---

## 2. Shipping Lead Time

Shipping lead time is calculated using:

```text
Shipping Lead Time = Ship Date − Order Date
