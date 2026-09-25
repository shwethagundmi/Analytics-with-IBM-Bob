# Analytics-with-IBM-Bob
 📊 Dataset Overview

| Property | Detail |
|----------|--------|
| Source File | `retail data .csv` |
| Raw Rows | 699 (includes 200 blank rows) |
| Valid Data Rows | **499 orders** |
| Columns | 25 |
| Time Period | 2019 – 2023 |
| Geography | India (multiple states & regions) |

### Columns Covered
`Order ID` · `Order Date` · `Ship Mode` · `Customer ID` · `Customer Name` · `Segment` · `Country` · `State` · `Region` · `City Type` · `Product ID` · `Category of Goods` · `Product Name` · `Sales Date` · `Sales Amount` · `Quantity` · `Discount` · `Profit` · `Profit per Unit` · `Profit Margin (%)` · `Sales per Unit` · `Discounted Price per Unit` · `Sales Channel` · `Payment Mode` · `Delivery Mode`

---

## 💰 Key Metrics

| Metric | Value |
|--------|-------|
| Total Sales | ₹41,89,958 |
| Total Profit | ₹6,89,767 |
| Avg Profit Margin | 15.70% |
| Total Orders | 499 |
| Total Units Sold | 2,648 |
| Avg Discount | 15.04% |
| Date Range | Jan 2019 – Dec 2023 |

---

## 🔍 Key Insights

1. **Electric Appliances dominate** — 68.8% of total revenue (₹28.83L). Washing Machines and Fans are the top two products.
2. **Online is the only real channel** — 96.6% of sales come from the Online channel, all paid via Credit Card.
3. **2021 was the peak year** — ₹10.41L in sales, up 59.5% over 2020 (COVID recovery effect).
4. **Consumer vs Corporate near-parity** — 50.4% Consumer vs 49.6% Corporate, a well-diversified revenue base.
5. **Rural demand is strong** — Tier 2 cities + Villages contribute 63.5% of sales, outperforming Tier 1.
6. **Stable margins** — Profit margins are consistent at ~15.7% across all categories and years.
7. **Top state: Uttar Pradesh** — ₹5.32L, followed by Andhra Pradesh (₹4.92L) and Delhi (₹4.72L).
8. **Data quality issue** — 200 completely blank rows (28.6% of raw file) were found and excluded.

---

## 🛠️ Technologies Used

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.x | Core programming language |
| **pandas** | Latest | Data loading, cleaning, type conversion, aggregation |
| **Plotly** | Latest | Interactive chart rendering (donut, bar, area line charts) |
| **Dash** | Latest | Web application framework, live filter callbacks |
| **dash-bootstrap-components** | Latest | Responsive grid layout |


## 📈 Dashboard Features

| Feature | Details |
|---------|---------|
| **Filters** | Category · Region · Segment · Sales Channel · Payment Mode · Year |
| **KPI Cards** | Total Sales · Total Profit + Margin · Quantity · Avg Discount |
| **Charts** | 9 interactive charts (donut, bar, area line with zoom) |
| **Tables** | Category breakdown · Year-on-Year performance |
| **Insights** | 8 pre-written business insight cards |

### Charts Included
1. Sales by Category (Donut)
2. Sales by Region (Bar)
3. Sales Channel Breakdown (Donut)
4. Customer Segment Split (Donut)
5. Monthly Sales Trend 2019–2023 (Area Line with zoom)
6. Top 10 Products by Sales (Horizontal Bar)
7. Top 10 States by Sales (Horizontal Bar)
8. Delivery Mode Distribution (Donut)
9. Sales by City Tier (Donut)
