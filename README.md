# 🚚 Factory-to-Customer Shipping Route Efficiency Analysis

### Nassau Candy Distributor

## 📌 Overview

This project analyzes factory-to-customer shipping data to identify efficient and inefficient routes, shipping delays, geographic bottlenecks, factory performance, and shipping-mode performance.

An interactive **Streamlit dashboard** is developed to help users explore logistics performance through charts, KPIs, filters, and geographic visualization.

## 🎯 Objectives

- Analyze factory and route performance
- Calculate shipping lead time
- Identify delayed shipments
- Compare shipping modes
- Identify high and low-performing routes
- Analyze geographic shipping patterns
- Develop route efficiency scores
- Provide interactive logistics insights

## 📊 Key Features

- 📈 Factory Performance Analysis
- 🛣️ Route Efficiency Analysis
- 🌎 Geographic Shipping Map
- 🚚 Ship Mode Comparison
- ⏱️ Shipping Lead-Time Analysis
- 🚨 Delay Analysis
- 📊 Interactive KPI Dashboard
- 🔍 Date, Region, State, and Ship Mode Filters

## 🛠️ Technology Stack

- **Python**
- **Pandas**
- **Plotly**
- **Streamlit**
- **CSV Dataset**

## 📁 Project Structure

```text
Nassau-Shipping-Route-Analysis/
│
├── app.py
├── analysis.py
├── style.css
├── requirements.txt
├── README.md
│
└── data/
    ├── enriched_shipping_data.csv
    ├── factory_locations.csv
    └── route_efficiency_scores.csv
```
### File Description

- `app.py` — Main Streamlit dashboard application
- `analysis.py` — Data analysis and preprocessing
- `style.css` — Custom dashboard styling
- `requirements.txt` — Python dependencies
- `enriched_shipping_data.csv` — Processed shipment dataset
- `factory_locations.csv` — Factory coordinates
- `route_efficiency_scores.csv` — Route efficiency metrics

---

## 💻 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Pranjali-0712/Nassau-Shipping-Route-Analysis.git
```
### 2. Navigate to the Project
```
cd Nassau-Shipping-Route-Analysis
```
### 3. Install Dependencies
```
pip install -r requirements.txt
```
### 4. Run the Application
```
streamlit run app.py
```
The dashboard will open in your browser at:
```
http://localhost:8501
```
