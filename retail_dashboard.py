# retail_dashboard.py
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_mantine_components as dmc

# Load dataset
xls = pd.ExcelFile('online_retail_II.xlsx')
df = pd.concat([xls.parse('Year 2009-2010'), xls.parse('Year 2010-2011')], ignore_index=True)

# Data Preprocessing
df = df.dropna(subset=['Customer ID'])
df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['TotalPrice'] = df['Quantity'] * df['Price']
df['Year'] = df['InvoiceDate'].dt.year


# RFM Analysis
rfm = df.groupby('Customer ID').agg({
    'InvoiceDate': lambda x: (df['InvoiceDate'].max() - x.max()).days,
    'Invoice': 'nunique',
    'TotalPrice': 'sum'
}).rename(columns={
    'InvoiceDate': 'Recency',
    'Invoice': 'Frequency',
    'TotalPrice': 'Monetary'
})

# Dash App


app.layout = dmc.MantineProvider(
    theme={"colorScheme": "dark"},
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=dmc.Container([
        dmc.Paper([
            dmc.Title("🛍️ Decoding Retail Dynamics Dashboard", align="center", weight=800, size="h1", mb="lg"),
            dmc.Text("An interactive dashboard for analyzing retail customer behavior, trends, and returns.", align="center", size="md", color="gray.4"),
        ], shadow="xl", radius="xl", p="md", withBorder=True, mt=20, mb=30),

        dmc.Tabs(value="tab1", variant="pills", color="cyan", orientation="horizontal", children=[
            dmc.TabsList(position="center", grow=True, children=[
                dmc.Tab("Demographics", value="tab1"),
                dmc.Tab("Trends", value="tab2"),
                dmc.Tab("Customer Segmentation", value="tab3"),
                dmc.Tab("Seasonality", value="tab4"),
                dmc.Tab("Returns Insight", value="tab5")
            ]),

            dmc.TabsPanel(value="tab1", children=[
                dmc.Card([
                    dmc.Title("Revenue by Country", order=3, mb="md"),
                    dcc.Graph(
                        figure=px.treemap(
                            df.groupby('Country').agg({'Customer ID': 'nunique', 'TotalPrice': 'sum'}).reset_index(),
                            path=['Country'], values='TotalPrice',
                            title=''
                        )
                    )
                ], shadow="sm", radius="lg", withBorder=True, p="md")
            ]),

            dmc.TabsPanel(value="tab2", children=[
                dmc.Grid([
                    dmc.Col(span=6, children=dmc.Card([
                        dmc.Title("Monthly Revenue Trends", order=4),
                        dcc.Graph(
                            figure=px.line(
                                df.groupby(['Year', 'Month'])['TotalPrice'].sum().reset_index(),
                                x='Month', y='TotalPrice', color='Year'
                            )
                        )
                    ], shadow="sm", radius="lg", withBorder=True, p="md")),
                    dmc.Col(span=6, children=dmc.Card([
                        dmc.Title("Sales Heatmap by Hour & Month", order=4),
                        dcc.Graph(
                            figure=px.density_heatmap(
                                df, x='Hour', y='Month', z='TotalPrice',
                                histfunc='sum', nbinsx=24, nbinsy=12
                            )
                        )
                    ], shadow="sm", radius="lg", withBorder=True, p="md"))
                ])
            ]),

            dmc.TabsPanel(value="tab3", children=[
                dmc.Card([
                    dmc.Title("RFM Customer Segmentation", order=3, mb="md"),
                    dcc.Graph(
                        figure=px.scatter(
                            rfm, x='Recency', y='Monetary', size='Frequency'
                        )
                    )
                ], shadow="sm", radius="lg", withBorder=True, p="md")
            ]),

            dmc.TabsPanel(value="tab4", children=[
                dmc.Card([
                    dmc.Title("Monthly Sales Distribution - Seasonality", order=3, mb="md"),
                    dcc.Graph(
                        figure=px.box(
                            df, x='Month', y='TotalPrice'
                        )
                    )
                ], shadow="sm", radius="lg", withBorder=True, p="md")
            ]),

            dmc.TabsPanel(value="tab5", children=[
                dmc.Card([
                    dmc.Title("Top 10 Returned Products", order=3, mb="md"),
                    dcc.Graph(
                        figure=px.bar(
                            df[df['Invoice'].astype(str).str.startswith('C')]
                            .groupby('Description')['TotalPrice'].sum()
                            .nlargest(10).reset_index(),
                            x='Description', y='TotalPrice'
                        )
                    )
                ], shadow="sm", radius="lg", withBorder=True, p="md")
            ])
        ])
    ], size="lg")
)

if __name__ == '__main__':
    app.run(debug=True)
