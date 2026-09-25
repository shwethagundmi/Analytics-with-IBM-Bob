import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc

# ── Load & Clean Data ────────────────────────────────────────────────────────
df = pd.read_csv("retail data .csv")
df.dropna(subset=["Sales Amount"], inplace=True)
df.reset_index(drop=True, inplace=True)

df["Sales Amount"]      = pd.to_numeric(df["Sales Amount"], errors="coerce")
df["Profit"]            = pd.to_numeric(df["Profit"],       errors="coerce")
df["Quantity"]          = pd.to_numeric(df["Quantity"],     errors="coerce")
df["Discount"]          = pd.to_numeric(df["Discount"],     errors="coerce")
df["Profit Margin (%)"] = pd.to_numeric(df["Profit Margin (%)"], errors="coerce")

df["Sales Date"]  = pd.to_datetime(df["Sales Date"],  errors="coerce")
df["Order Date"]  = pd.to_datetime(df["Order Date"],  errors="coerce")
df["Year"]        = df["Sales Date"].dt.year.astype("Int64").astype(str)
df["Year-Month"]  = df["Sales Date"].dt.to_period("M").astype(str)

for col in ["Category of Goods", "Region", "Segment", "Sales Channel",
            "Payment Mode", "Ship Mode", "City Type", "Delivery Mode",
            "State", "Product Name"]:
    df[col] = df[col].astype(str).str.strip()

# ── Colour palette ────────────────────────────────────────────────────────────
COLORS = ["#3b82d4", "#7c5cd8", "#16a34a", "#f59e0b",
          "#ef4444", "#06b6d4", "#ec4899", "#84cc16"]

CARD_STYLE = {
    "background": "#ffffff", "border": "1px solid #e5e7eb",
    "borderRadius": "8px",   "padding": "16px 20px",
    "marginBottom": "0"
}
KPI_LABEL = {"fontSize": "11px", "color": "#57606a",
             "textTransform": "uppercase", "letterSpacing": "0.05em",
             "fontWeight": "600", "marginBottom": "4px"}
KPI_VAL   = {"fontSize": "26px", "fontWeight": "700", "color": "#1f2328"}
KPI_SUB   = {"fontSize": "12px", "color": "#57606a", "marginTop": "2px"}

SECTION   = {"fontSize": "14px", "fontWeight": "700",
             "color": "#1f2328", "marginBottom": "10px", "marginTop": "22px"}

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt(n):
    if n >= 1e7:  return f"₹{n/1e7:.2f} Cr"
    if n >= 1e5:  return f"₹{n/1e5:.2f} L"
    if n >= 1e3:  return f"₹{n/1e3:.1f} K"
    return f"₹{n:.0f}"

def filter_df(cat, region, seg, channel, pay, year):
    d = df.copy()
    if cat:     d = d[d["Category of Goods"] == cat]
    if region:  d = d[d["Region"] == region]
    if seg:     d = d[d["Segment"] == seg]
    if channel: d = d[d["Sales Channel"] == channel]
    if pay:     d = d[d["Payment Mode"] == pay]
    if year:    d = d[d["Year"] == year]
    return d

CHART_LAYOUT = dict(
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="-apple-system,Segoe UI,system-ui,sans-serif", size=12, color="#1f2328"),
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11))
)

# ── App ────────────────────────────────────────────────────────────────────────
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Retail Sales Dashboard"

def make_dropdown(id_, label, options, placeholder):
    return html.Div([
        html.Label(label, style={"fontSize": "11px", "fontWeight": "600",
                                  "color": "#57606a", "textTransform": "uppercase",
                                  "letterSpacing": "0.04em", "marginBottom": "4px"}),
        dcc.Dropdown(id=id_, options=[{"label": o, "value": o} for o in options],
                     placeholder=placeholder, clearable=True,
                     style={"fontSize": "13px", "minWidth": "140px"})
    ], style={"display": "flex", "flexDirection": "column"})

# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div(style={"background": "#f7f8fa", "minHeight": "100vh",
                              "fontFamily": "-apple-system,Segoe UI,system-ui,sans-serif"}, children=[
    html.Div(style={"maxWidth": "1150px", "margin": "0 auto", "padding": "24px 16px"}, children=[

        # Header
        html.H1("🛒 Retail Sales Dashboard",
                style={"fontSize": "22px", "fontWeight": "700", "marginBottom": "4px"}),
        html.P("Dataset: 499 valid orders · 200 blank rows excluded · India · 2019–2023 · All figures in ₹",
               style={"color": "#57606a", "fontSize": "13px", "marginBottom": "22px"}),

        # ── Filters ──────────────────────────────────────────────────────────
        html.Div(style={**CARD_STYLE, "display": "flex", "flexWrap": "wrap",
                        "gap": "14px", "alignItems": "flex-end", "marginBottom": "20px"}, children=[
            make_dropdown("f-cat",    "Category",     sorted(df["Category of Goods"].unique()), "All Categories"),
            make_dropdown("f-region", "Region",       sorted(df["Region"].unique()),            "All Regions"),
            make_dropdown("f-seg",    "Segment",      sorted(df["Segment"].unique()),            "All Segments"),
            make_dropdown("f-chan",   "Sales Channel",sorted(df["Sales Channel"].unique()),      "All Channels"),
            make_dropdown("f-pay",    "Payment Mode", sorted(df["Payment Mode"].unique()),       "All Payment Modes"),
            make_dropdown("f-year",   "Year",         sorted(df["Year"].dropna().unique()),      "All Years"),
        ]),

        # ── KPI Row ───────────────────────────────────────────────────────────
        dbc.Row(id="kpi-row", className="g-3 mb-4"),

        # ── Category Table ────────────────────────────────────────────────────
        html.P("Sales by Category of Goods", style=SECTION),
        html.Div(id="cat-table-div", style={"marginBottom": "22px"}),

        # ── Charts Row 1: Category + Region ──────────────────────────────────
        dbc.Row([
            dbc.Col(html.Div(style=CARD_STYLE, children=[
                html.P("Sales by Category", style={**KPI_LABEL, "marginBottom": "10px"}),
                dcc.Graph(id="ch-cat", config={"displayModeBar": False}, style={"height": "280px"})
            ]), md=6),
            dbc.Col(html.Div(style=CARD_STYLE, children=[
                html.P("Sales by Region", style={**KPI_LABEL, "marginBottom": "10px"}),
                dcc.Graph(id="ch-region", config={"displayModeBar": False}, style={"height": "280px"})
            ]), md=6),
        ], className="g-3 mb-3"),

        # ── Charts Row 2: Channel + Segment ──────────────────────────────────
        dbc.Row([
            dbc.Col(html.Div(style=CARD_STYLE, children=[
                html.P("Sales Channel Breakdown", style={**KPI_LABEL, "marginBottom": "10px"}),
                dcc.Graph(id="ch-channel", config={"displayModeBar": False}, style={"height": "280px"})
            ]), md=6),
            dbc.Col(html.Div(style=CARD_STYLE, children=[
                html.P("Customer Segment Split", style={**KPI_LABEL, "marginBottom": "10px"}),
                dcc.Graph(id="ch-seg", config={"displayModeBar": False}, style={"height": "280px"})
            ]), md=6),
        ], className="g-3 mb-3"),

        # ── Monthly Trend (full width) ────────────────────────────────────────
        dbc.Row([
            dbc.Col(html.Div(style=CARD_STYLE, children=[
                html.P("Monthly Sales Trend (2019–2023)", style={**KPI_LABEL, "marginBottom": "10px"}),
                dcc.Graph(id="ch-monthly", config={"displayModeBar": False}, style={"height": "300px"})
            ]), md=12),
        ], className="g-3 mb-3"),

        # ── Charts Row 3: Products + States ──────────────────────────────────
        dbc.Row([
            dbc.Col(html.Div(style=CARD_STYLE, children=[
                html.P("Top 10 Products by Sales", style={**KPI_LABEL, "marginBottom": "10px"}),
                dcc.Graph(id="ch-products", config={"displayModeBar": False}, style={"height": "320px"})
            ]), md=6),
            dbc.Col(html.Div(style=CARD_STYLE, children=[
                html.P("Top 10 States by Sales", style={**KPI_LABEL, "marginBottom": "10px"}),
                dcc.Graph(id="ch-states", config={"displayModeBar": False}, style={"height": "320px"})
            ]), md=6),
        ], className="g-3 mb-3"),

        # ── Charts Row 4: Delivery + City ─────────────────────────────────────
        dbc.Row([
            dbc.Col(html.Div(style=CARD_STYLE, children=[
                html.P("Delivery Mode Distribution", style={**KPI_LABEL, "marginBottom": "10px"}),
                dcc.Graph(id="ch-delivery", config={"displayModeBar": False}, style={"height": "280px"})
            ]), md=6),
            dbc.Col(html.Div(style=CARD_STYLE, children=[
                html.P("Sales by City Tier", style={**KPI_LABEL, "marginBottom": "10px"}),
                dcc.Graph(id="ch-city", config={"displayModeBar": False}, style={"height": "280px"})
            ]), md=6),
        ], className="g-3 mb-3"),

        # ── Yearly Table ──────────────────────────────────────────────────────
        html.P("Year-on-Year Sales Performance", style=SECTION),
        html.Div(id="yr-table-div", style={"marginBottom": "22px"}),

        # ── Insights ──────────────────────────────────────────────────────────
        html.P("Key Business Insights", style=SECTION),
        dbc.Row([
            dbc.Col(html.Div(style={**CARD_STYLE, "borderLeft": "4px solid #16a34a"}, children=[
                html.P("📈 Electric Appliances Dominate Sales", style={"fontWeight": "700", "marginBottom": "4px"}),
                html.P("Electric Appliances account for 68.8% of total revenue (₹28.83L). Washing Machines and Fans alone contribute ₹19.73L — the most critical product lines.", style={"color": "#57606a", "fontSize": "13px"})
            ]), md=6),
            dbc.Col(html.Div(style={**CARD_STYLE, "borderLeft": "4px solid #3b82d4"}, children=[
                html.P("📱 Online Channel is King (96.6%)", style={"fontWeight": "700", "marginBottom": "4px"}),
                html.P("Online sales drive ₹40.47L (96.6%) of all revenue, exclusively via Credit Card. In-store and Retail Partner contribute just 3.4% — a strongly digital-first base.", style={"color": "#57606a", "fontSize": "13px"})
            ]), md=6),
        ], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(html.Div(style={**CARD_STYLE, "borderLeft": "4px solid #f59e0b"}, children=[
                html.P("⚠️ 200 Blank Rows Detected", style={"fontWeight": "700", "marginBottom": "4px"}),
                html.P("The raw CSV contains 200 completely empty rows (28.6% of the file). These were excluded from all calculations. The source file should be cleaned for reliable reporting.", style={"color": "#57606a", "fontSize": "13px"})
            ]), md=6),
            dbc.Col(html.Div(style={**CARD_STYLE, "borderLeft": "4px solid #7c5cd8"}, children=[
                html.P("📅 2021 Was the Peak Year", style={"fontWeight": "700", "marginBottom": "4px"}),
                html.P("2021 recorded ₹10.41L in sales — the highest of any year, up 59.5% vs 2020. Sales eased in 2022 (₹8.67L) and 2023 (₹8.60L), likely post-pandemic normalisation.", style={"color": "#57606a", "fontSize": "13px"})
            ]), md=6),
        ], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(html.Div(style={**CARD_STYLE, "borderLeft": "4px solid #16a34a"}, children=[
                html.P("💰 Stable & Healthy Profit Margins", style={"fontWeight": "700", "marginBottom": "4px"}),
                html.P("Average profit margin holds steady at 15.70% across all categories. Electric Appliances generate ₹4.68L absolute profit. Margins are consistent across years.", style={"color": "#57606a", "fontSize": "13px"})
            ]), md=6),
            dbc.Col(html.Div(style={**CARD_STYLE, "borderLeft": "4px solid #3b82d4"}, children=[
                html.P("🌍 South & West Lead Regionally", style={"fontWeight": "700", "marginBottom": "4px"}),
                html.P("South (₹11.85L) and West (₹11.23L) are the top two regions. Uttar Pradesh leads state-level sales at ₹5.32L, followed by Andhra Pradesh (₹4.92L) and Delhi (₹4.72L).", style={"color": "#57606a", "fontSize": "13px"})
            ]), md=6),
        ], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(html.Div(style={**CARD_STYLE, "borderLeft": "4px solid #f59e0b"}, children=[
                html.P("⚖️ Consumer vs Corporate Near-Parity", style={"fontWeight": "700", "marginBottom": "4px"}),
                html.P("Consumer (50.4%) and Corporate (49.6%) are almost evenly split. This presents a strategic choice: focus on one segment or use targeted campaigns to grow both.", style={"color": "#57606a", "fontSize": "13px"})
            ]), md=6),
            dbc.Col(html.Div(style={**CARD_STYLE, "borderLeft": "4px solid #7c5cd8"}, children=[
                html.P("🏭 Strong Demand Beyond Tier 1", style={"fontWeight": "700", "marginBottom": "4px"}),
                html.P("Tier 2 cities (₹13.58L) and Villages (₹13.03L) together contribute 63.5% of sales. Rural and semi-urban markets are a vital and often underestimated growth engine.", style={"color": "#57606a", "fontSize": "13px"})
            ]), md=6),
        ], className="g-3 mb-4"),

        html.Hr(style={"borderColor": "#e5e7eb"}),
        html.P("Made with IBM Bob", style={"textAlign": "center", "fontSize": "12px",
                                            "color": "#57606a", "padding": "12px 0"})
    ])
])

# ── Callbacks ─────────────────────────────────────────────────────────────────
@app.callback(
    Output("kpi-row",       "children"),
    Output("cat-table-div", "children"),
    Output("yr-table-div",  "children"),
    Output("ch-cat",        "figure"),
    Output("ch-region",     "figure"),
    Output("ch-channel",    "figure"),
    Output("ch-seg",        "figure"),
    Output("ch-monthly",    "figure"),
    Output("ch-products",   "figure"),
    Output("ch-states",     "figure"),
    Output("ch-delivery",   "figure"),
    Output("ch-city",       "figure"),
    Input("f-cat",    "value"),
    Input("f-region", "value"),
    Input("f-seg",    "value"),
    Input("f-chan",   "value"),
    Input("f-pay",    "value"),
    Input("f-year",   "value"),
)
def update_all(cat, region, seg, channel, pay, year):
    d = filter_df(cat, region, seg, channel, pay, year)

    total_sales  = d["Sales Amount"].sum()
    total_profit = d["Profit"].sum()
    total_qty    = int(d["Quantity"].sum())
    avg_disc     = d["Discount"].mean() * 100
    margin       = (total_profit / total_sales * 100) if total_sales else 0

    # KPIs
    def kpi_card(label, value, sub, color="#1f2328"):
        return dbc.Col(html.Div(style=CARD_STYLE, children=[
            html.P(label, style=KPI_LABEL),
            html.P(value, style={**KPI_VAL, "color": color}),
            html.P(sub,   style=KPI_SUB),
        ]), md=3)

    kpi_cards = [
        kpi_card("Total Sales",    fmt(total_sales),  f"{len(d):,} orders",      "#3b82d4"),
        kpi_card("Total Profit",   fmt(total_profit), f"Margin: {margin:.2f}%",  "#16a34a"),
        kpi_card("Total Quantity", f"{total_qty:,}",  "units sold"),
        kpi_card("Avg Discount",   f"{avg_disc:.2f}%","per order"),
    ]

    # ── Category Table ────────────────────────────────────────────────────────
    cat_grp = d.groupby("Category of Goods").agg(
        Sales=("Sales Amount", "sum"),
        Profit=("Profit", "sum")
    ).reset_index().sort_values("Sales", ascending=False)
    cat_grp["Share (%)"]  = (cat_grp["Sales"] / cat_grp["Sales"].sum() * 100).round(1)
    cat_grp["Margin (%)"] = (cat_grp["Profit"] / cat_grp["Sales"] * 100).round(1)
    cat_grp["Sales (₹)"]  = cat_grp["Sales"].apply(lambda x: f"₹{x:,.0f}")
    cat_grp["Profit (₹)"] = cat_grp["Profit"].apply(lambda x: f"₹{x:,.0f}")

    cat_table = dash_table.DataTable(
        data=cat_grp[["Category of Goods", "Sales (₹)", "Share (%)", "Profit (₹)", "Margin (%)"]].to_dict("records"),
        columns=[{"name": c, "id": c} for c in ["Category of Goods", "Sales (₹)", "Share (%)", "Profit (₹)", "Margin (%)"]],
        style_table={"overflowX": "auto"},
        style_header={"background": "#f7f8fa", "fontWeight": "600", "fontSize": "11px",
                      "color": "#57606a", "textTransform": "uppercase", "letterSpacing": "0.04em",
                      "border": "1px solid #e5e7eb", "padding": "9px 14px"},
        style_cell={"fontFamily": "-apple-system,Segoe UI,system-ui,sans-serif",
                    "fontSize": "13px", "padding": "9px 14px",
                    "border": "1px solid #f0f1f3", "color": "#1f2328"},
        style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#f7f8fa"}],
        page_action="none", sort_action="native",
    )

    # ── Yearly Table ──────────────────────────────────────────────────────────
    yr_grp = df.groupby("Year")["Sales Amount"].sum().reset_index().sort_values("Year")
    yr_grp["Sales (₹)"] = yr_grp["Sales Amount"].apply(lambda x: f"₹{x:,.0f}")
    yr_grp["YoY Growth"] = yr_grp["Sales Amount"].pct_change().mul(100).round(1)
    yr_grp["Growth"]     = yr_grp["YoY Growth"].apply(
        lambda x: "Base Year" if pd.isna(x) else (f"+{x}%" if x >= 0 else f"{x}%"))
    yr_table = dash_table.DataTable(
        data=yr_grp[["Year", "Sales (₹)", "Growth"]].to_dict("records"),
        columns=[{"name": c, "id": c} for c in ["Year", "Sales (₹)", "Growth"]],
        style_table={"overflowX": "auto"},
        style_header={"background": "#f7f8fa", "fontWeight": "600", "fontSize": "11px",
                      "color": "#57606a", "textTransform": "uppercase", "letterSpacing": "0.04em",
                      "border": "1px solid #e5e7eb", "padding": "9px 14px"},
        style_cell={"fontFamily": "-apple-system,Segoe UI,system-ui,sans-serif",
                    "fontSize": "13px", "padding": "9px 14px",
                    "border": "1px solid #f0f1f3", "color": "#1f2328"},
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#f7f8fa"},
            {"if": {"filter_query": '{Growth} contains "+"', "column_id": "Growth"},
             "color": "#15803d", "fontWeight": "600"},
            {"if": {"filter_query": '{Growth} contains "-"', "column_id": "Growth"},
             "color": "#c2410c", "fontWeight": "600"},
        ],
        page_action="none",
    )

    # ── Chart: Category Donut ─────────────────────────────────────────────────
    cat_fig = px.pie(cat_grp, names="Category of Goods", values="Sales",
                     hole=0.4, color_discrete_sequence=COLORS)
    cat_fig.update_traces(textinfo="percent+label", textfont_size=11)
    cat_fig.update_layout(**CHART_LAYOUT)

    # ── Chart: Region Bar ─────────────────────────────────────────────────────
    reg_grp = d.groupby("Region")["Sales Amount"].sum().reset_index().sort_values("Sales Amount", ascending=False)
    reg_fig = px.bar(reg_grp, x="Region", y="Sales Amount",
                     color="Region", color_discrete_sequence=COLORS,
                     text=reg_grp["Sales Amount"].apply(fmt))
    reg_fig.update_traces(textposition="outside")
    reg_fig.update_layout(**CHART_LAYOUT, showlegend=False,
                          yaxis=dict(tickformat=",.0f", title=""),
                          xaxis=dict(title=""))

    # ── Chart: Channel Donut ──────────────────────────────────────────────────
    chan_grp = d.groupby("Sales Channel")["Sales Amount"].sum().reset_index()
    chan_fig = px.pie(chan_grp, names="Sales Channel", values="Sales Amount",
                     hole=0.4, color_discrete_sequence=COLORS)
    chan_fig.update_traces(textinfo="percent+label", textfont_size=11)
    chan_fig.update_layout(**CHART_LAYOUT)

    # ── Chart: Segment Donut ─────────────────────────────────────────────────
    seg_grp = d.groupby("Segment")["Sales Amount"].sum().reset_index()
    seg_fig = px.pie(seg_grp, names="Segment", values="Sales Amount",
                     hole=0.4, color_discrete_sequence=["#3b82d4", "#7c5cd8"])
    seg_fig.update_traces(textinfo="percent+label", textfont_size=12)
    seg_fig.update_layout(**CHART_LAYOUT)

    # ── Chart: Monthly Trend ──────────────────────────────────────────────────
    mon_grp = d.groupby("Year-Month")["Sales Amount"].sum().reset_index().sort_values("Year-Month")
    mon_fig = go.Figure(go.Scatter(
        x=mon_grp["Year-Month"], y=mon_grp["Sales Amount"],
        mode="lines", fill="tozeroy", line=dict(color="#3b82d4", width=2),
        fillcolor="rgba(59,130,212,0.15)",
        hovertemplate="%{x}<br>Sales: ₹%{y:,.0f}<extra></extra>"
    ))
    mon_fig.update_layout(**CHART_LAYOUT,
                          xaxis=dict(tickangle=45, title=""),
                          yaxis=dict(title="", tickformat=",.0f"))

    # ── Chart: Top Products ───────────────────────────────────────────────────
    prod_grp = d.groupby("Product Name")["Sales Amount"].sum().nlargest(10).reset_index()
    prod_grp = prod_grp.sort_values("Sales Amount")
    prod_fig = px.bar(prod_grp, y="Product Name", x="Sales Amount",
                      orientation="h", color="Product Name",
                      color_discrete_sequence=COLORS,
                      text=prod_grp["Sales Amount"].apply(fmt))
    prod_fig.update_traces(textposition="outside")
    prod_fig.update_layout(**CHART_LAYOUT, showlegend=False,
                           xaxis=dict(title="", tickformat=",.0f"),
                           yaxis=dict(title=""))

    # ── Chart: Top States ────────────────────────────────────────────────────
    state_grp = d.groupby("State")["Sales Amount"].sum().nlargest(10).reset_index()
    state_grp = state_grp.sort_values("Sales Amount")
    state_fig = px.bar(state_grp, y="State", x="Sales Amount",
                       orientation="h", color_discrete_sequence=["#7c5cd8"],
                       text=state_grp["Sales Amount"].apply(fmt))
    state_fig.update_traces(textposition="outside", marker_color="#7c5cd8")
    state_fig.update_layout(**CHART_LAYOUT, showlegend=False,
                            xaxis=dict(title="", tickformat=",.0f"),
                            yaxis=dict(title=""))

    # ── Chart: Delivery Donut ────────────────────────────────────────────────
    del_grp = d.groupby("Delivery Mode")["Sales Amount"].sum().reset_index()
    del_fig = px.pie(del_grp, names="Delivery Mode", values="Sales Amount",
                     hole=0.4, color_discrete_sequence=["#3b82d4", "#7c5cd8", "#16a34a"])
    del_fig.update_traces(textinfo="percent+label", textfont_size=11)
    del_fig.update_layout(**CHART_LAYOUT)

    # ── Chart: City Tier Donut ───────────────────────────────────────────────
    city_grp = d.groupby("City Type")["Sales Amount"].sum().reset_index()
    city_fig = px.pie(city_grp, names="City Type", values="Sales Amount",
                      hole=0.4, color_discrete_sequence=["#f59e0b", "#3b82d4", "#16a34a"])
    city_fig.update_traces(textinfo="percent+label", textfont_size=11)
    city_fig.update_layout(**CHART_LAYOUT)

    return (kpi_cards, cat_table, yr_table,
            cat_fig, reg_fig, chan_fig, seg_fig, mon_fig,
            prod_fig, state_fig, del_fig, city_fig)


if __name__ == "__main__":
    print("\n✅ Retail Dashboard running at: http://127.0.0.1:8050\n")
    app.run(debug=False, port=8050)
