import dash
from dash import dcc, html
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

# Load dataset
df = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2009-2010")  # Adjust if multiple sheets!

# Preprocessing
df = df.dropna(subset=["Customer ID"])  # Remove missing customers
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["Month"] = df["InvoiceDate"].dt.to_period("M").dt.to_timestamp().astype(str)  # Convert to string for JSON serialization

# Figures
# 1. Demographics - Customers per country
fig_demographics = px.bar(
    df["Country"].value_counts().head(10),
    labels={"value": "Number of Customers", "index": "Country"},
    title="Top 10 Countries by Number of Customers"
)

)

# 3. Customer Segmentation - RFM Analysis (example)
rfm = df.groupby("Customer ID").agg({
    "InvoiceDate": lambda x: (df["InvoiceDate"].max() - x.max()).days,
    "Invoice": "nunique",
    "Price": "sum"
}).rename(columns={"InvoiceDate": "Recency", "Invoice": "Frequency", "Price": "MonetaryValue"})
fig_segmentation = px.scatter(
    rfm, x="Recency", y="MonetaryValue", size="Frequency",
    title="Customer Segmentation (RFM)",
    hover_name=rfm.index
)



# 5. Returns Insight - Returns by Country (Improved)
returns = df[df["Quantity"] < 0]
returns_by_country = returns["Country"].value_counts()
# Group countries with less than 2% into "Others"
threshold = returns_by_country.sum() * 0.02
top_countries = returns_by_country[returns_by_country >= threshold]
others = returns_by_country[returns_by_country < threshold].sum()
returns_by_country_adjusted = pd.concat([
    top_countries,
    pd.Series(others, index=["Others"])
])
fig_returns = px.pie(
    returns_by_country_adjusted,
    names=returns_by_country_adjusted.index,
    values=returns_by_country_adjusted,
    title="Returns Distribution by Country",
    hole=0.3,  # Add a donut hole for better aesthetics
)

# 6. Correlation Heatmap
# Select numerical columns for correlation
numerical_cols = ["Quantity", "Price", "Customer ID"]
corr_matrix = df[numerical_cols].corr()
# Create annotated heatmap with a visible colorscale
fig_correlation = ff.create_annotated_heatmap(
    z=corr_matrix.values,
    x=numerical_cols,
    y=numerical_cols,
    colorscale="Viridis",  # Changed to Viridis for better visibility
    showscale=True,
    zmin=-1,
    zmax=1,
    annotation_text=corr_matrix.round(2).values,
    textfont={"size": 12, "color": "black"},  # Ensure text is visible
    hoverinfo="z"
)
fig_correlation.update_layout(
    title="Correlation Heatmap of Numerical Features",
    height=400,  # Adjust height for better fit
    margin=dict(l=50, r=50, t=100, b=50),  # Adjust margins
)

# Dash App
app = dash.Dash(__name__)

app.layout = dmc.MantineProvider(
    inherit=True,
    theme={
        "colorScheme": "dark",
        "primaryColor": "teal",  # Change tab color to teal
        "colors": {
            "teal": ["#E6FFFA", "#B2F5EA", "#81E6D9", "#4FD1C5", "#38B2AC", "#319795", "#2C7A7B", "#285E61", "#233E5F", "#1A2E44"]
        }
    },
    children=[
        dmc.Container(
            [
                dmc.Title("🛍️ Decoding Retail Dynamics Dashboard", order=2, align="center", mb=20),
                dmc.Text("An interactive dashboard for analyzing retail customer behavior, trends, and returns.", align="center", size="md", color="dimmed"),
                dmc.Tabs(
                    value="tab1",
                    children=[
                        dmc.TabsList(
                            [
                                dmc.Tab("Demographics", value="tab1"),
                                dmc.Tab("Trends", value="tab2"),
                                dmc.Tab("Customer Segmentation", value="tab3"),
                                dmc.Tab("Seasonality", value="tab4"),
                                dmc.Tab("Returns Insight", value="tab5"),
                                dmc.Tab("Correlation", value="tab6"),
                            ],
                            grow=True,
                            mb=20,
                        ),
                        dmc.TabsPanel(dcc.Loading(dcc.Graph(figure=fig_demographics), type="default"), value="tab1"),
                        dmc.TabsPanel(dcc.Loading(dcc.Graph(figure=fig_trends), type="default"), value="tab2"),
                        dmc.TabsPanel(dcc.Loading(dcc.Graph(figure=fig_segmentation), type="default"), value="tab3"),
                        dmc.TabsPanel(dcc.Loading(dcc.Graph(figure=fig_seasonality), type="default"), value="tab4"),
                        dmc.TabsPanel(dcc.Loading(dcc.Graph(figure=fig_returns), type="default"), value="tab5"),
                        dmc.TabsPanel(dcc.Loading(dcc.Graph(figure=fig_correlation), type="default"), value="tab6"),
                    ],
                ),
            ],
            style={"padding": "2rem"},
        )
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
