import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(page_title="Tire Market Dashboard", layout="wide")

# Load dataset
df = pd.read_csv("Dataset/2024dataset_2countries_3tiresizes.csv")

# Sidebar Filters with Icons
st.sidebar.header("🔍 Filters")
selected_countries = st.sidebar.selectbox("🌍 Select Countries", df["COUNTRY_OR_TERRITORY"].unique())
selected_tire_size = st.sidebar.selectbox("📏 Select Tire Size", df["TIRE_SIZE"].unique())

# Filtered Data
df_filtered = df[
    (df["COUNTRY_OR_TERRITORY"] == (selected_countries)) & 
    (df["TIRE_SIZE"] == selected_tire_size)
]

# ---- Main Layout ----
st.title("🚗 Tire Market Dashboard")
st.markdown("##### 📊 Market insights and competitor analysis")

# ---- Industry & Goodyear Sales (Bar Chart) ----
st.subheader("📊 Industry & Goodyear Sales")

# Drop duplicates to ensure correct values
sales_data = df_filtered[["TOTAL_INDUSTRY_SALES", "GOODYEAR_SALES"]].drop_duplicates().melt(var_name="Sales Type", value_name="Sales Value")

fig_sales = px.bar(
    sales_data,
    x="Sales Type",
    y="Sales Value",
    title="Industry & Goodyear Sales",
    text_auto=True,
    color="Sales Type",
    color_discrete_map={
        "TOTAL_INDUSTRY_SALES": "#1f77b4",  # Blue
        "GOODYEAR_SALES": "#ffcc00"  # Yellow
    }
)

st.plotly_chart(fig_sales, use_container_width=True)

# ---- Market Share ----
st.subheader("📊 Market Share of Goodyear")

# Drop duplicates to avoid miscalculations
market_share = df_filtered[["SOM_OF_BRAND"]].drop_duplicates()["SOM_OF_BRAND"].mean()

st.metric("Market Share (%)", f"{market_share * 100:.2f}%", help="Calculated based on SOM of the selected brand.")

# ---- Competitor Sales ----
st.subheader("🏆 Competitor Sales Comparison")

# Drop duplicates to prevent incorrect bar lengths
df_competitor_sales = (
    df_filtered[["COMPETITOR_BRAND", "COMPETITOR_BRAND_SALES"]]
    .drop_duplicates()
    .groupby("COMPETITOR_BRAND", as_index=False)
    .sum()
    .sort_values(by="COMPETITOR_BRAND_SALES", ascending=False)
    .head(35)  # Limit to top 35 competitors
)


fig_comp = px.bar(
    df_competitor_sales, 
    x="COMPETITOR_BRAND", 
    y="COMPETITOR_BRAND_SALES", 
    title="Top Competitor Sales", 
    text_auto=True,
    color_discrete_sequence=["#00CC96"]
)
st.plotly_chart(fig_comp, use_container_width=True)

# ---- Market Share Distribution (Brand Name Only) ----
st.subheader("📊 Market Share Distribution")

# Filter dataset to exclude missing brand names
df_valid_brands = df_filtered.dropna(subset=["BRAND_NAME"])

# Count occurrences of each brand
brand_counts = df_valid_brands["BRAND_NAME"].value_counts().reset_index()
brand_counts.columns = ["BRAND_NAME", "COUNT"]

# Calculate percentage share
total_brands = brand_counts["COUNT"].sum()
brand_counts["PERCENTAGE"] = (brand_counts["COUNT"] / total_brands) * 100

# Create pie chart with updated values
fig_pie = px.pie(
    brand_counts, 
    names="BRAND_NAME", 
    values="PERCENTAGE", 
    title="Market Share Distribution",
    color_discrete_sequence=px.colors.qualitative.Pastel
)

# Show percentage on hover
fig_pie.update_traces(
    textinfo="label",  # Show only brand names on chart
    hovertemplate="<b>%{label}</b><br>Market Share: %{value:.2f}%"  # Show name & percentage on hover
)

st.plotly_chart(fig_pie, use_container_width=True)

# ---- Top 10 Competitors ----
st.subheader("🥇 Top 10 Competitors")

# Drop duplicates before aggregation
df_top_competitors = df_filtered[["COMPETITOR_BRAND", "COMPETITOR_BRAND_SALES", "COMPETITOR_SOM"]].drop_duplicates().groupby("COMPETITOR_BRAND", as_index=False).agg({
    "COMPETITOR_BRAND_SALES": "max",
    "COMPETITOR_SOM": "mean"
})

# Convert SOM to percentage and format to 4 decimal places
df_top_competitors["COMPETITOR_SOM"] = df_top_competitors["COMPETITOR_SOM"] * 100
df_top_competitors["COMPETITOR_SOM"] = df_top_competitors["COMPETITOR_SOM"].apply(lambda x: f"{x:.4f}%")

# Sort and select top 10 competitors
df_top_competitors = df_top_competitors.sort_values(by="COMPETITOR_BRAND_SALES", ascending=False).head(10)

# Format dataframe to look modern
st.dataframe(
    df_top_competitors.style.set_properties(**{
        'background-color': '#f8f9fa',
        'border': '1px solid black',
        'text-align': 'left'
    }).bar(subset=["COMPETITOR_BRAND_SALES"], color="#3498DB")
)

# ---- Top Competitor Name & Market Share ----
if not df_top_competitors.empty:
    top_competitor = df_top_competitors.iloc[0]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h4>🏆 Top Competitor</h3>", unsafe_allow_html=True)
        st.markdown(f"<h5>{top_competitor['COMPETITOR_BRAND']}</h5>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h4>📊 Top Competitor SOM (%)</h3>", unsafe_allow_html=True)
        st.markdown(f"<h5>{top_competitor['COMPETITOR_SOM']}</h5>", unsafe_allow_html=True)


# ---- Competitor Pattern Pie Chart ----
st.subheader("📊 Competitor Pattern Analysis")

# Competitor selection filter from top 10 competitors
selected_competitor = st.selectbox("Select Competitor", df_top_competitors["COMPETITOR_BRAND"].unique())

# Filter dataset for selected competitor
df_competitor_pattern = df_filtered[df_filtered["COMPETITOR_BRAND"] == selected_competitor]

# Drop duplicates to ensure correct values
df_pattern_sales = df_competitor_pattern[["COMPETITOR_PATTERN", "COMPETITOR_PATTERN_SALES"]].drop_duplicates()

# Generate pie chart with correct values
fig_pattern_pie = px.pie(
    df_pattern_sales, 
    names="COMPETITOR_PATTERN", 
    values="COMPETITOR_PATTERN_SALES", 
    title=f"Sales Distribution by Pattern for {selected_competitor}",
    color_discrete_sequence=px.colors.qualitative.Set3
)

st.plotly_chart(fig_pattern_pie, use_container_width=True)

# ---- Top 5 Fitments ----
st.subheader("🛞 Top 5 Fitments")
fitments = df_filtered["TOP_5_FITMENTS"].dropna().unique()
for fitment in fitments[:5]:
    st.write(f"✅ {fitment}")

# ---- Footer ----
st.markdown("***")
