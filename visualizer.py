import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from db_utils import DatabaseManager

def histogram_page(selected_table, property):
    
    # Slider für Anzahl der Bins
    num_bins_price = st.slider(
        "Number of Bins",
        min_value=5,
        max_value=100,
        value=10,
        step=5,
        help="Change for adjusting the granularity",
        key=f"bin_slider_{property}_{selected_table}"
    )
    sold_data = st.toggle("Only sold items", False, key=f"sold_data_{property}_{selected_table}")
    
    df = data[selected_table]
    if sold_data:
        df = df["sold" == 1]
        
    # Daten in Bins einteilen
    df['bin'] = pd.cut(df[property], bins=num_bins_price)
    df['bin_mid'] = df['bin'].apply(lambda x: int(x.mid))
    bar_data = df.groupby('bin_mid', observed=False)[property].count()
    st.bar_chart(bar_data, x_label="Price in €" ,y_label="Number of sold items")
    
    expander = st.expander("Show statistic measures")
    with expander:
            st.table(df[property].describe().apply(lambda x: int(x)))
         

def main():
    st.title("Visualizer for Scraped Data")
    
    selected_table = st.selectbox("Select a table", table_names)
    tab_price, tab_durartion, tab_bivariate = st.tabs(["Price", "Duration", "Bivariate"])
    
    with tab_price:   
        histogram_page(selected_table, "price")

    with tab_durartion:   
        histogram_page(selected_table, "days_online")
        
    with tab_bivariate:
        df = data[selected_table][["price", "days_online"]]
        # range_price = (df["price"].max(),df["price"].min())
        # range_duration = (df["days_online"].max(),df["days_online"].min())
        covariance = df.cov()
        correlation = df.corr()
        
        st.scatter_chart(df, x="price", y="days_online", x_label="Price in €", y_label="Duration in days")
        
        expander = st.expander("Show statistic measures")
        with expander:
            st.write("Covariance Matrix")
            st.table(covariance)
            st.write(f"Correlation: {correlation.iloc[0, 1]}")
            
dbm = DatabaseManager("./data.db")
table_names = dbm.return_table_names()

data = {}
for table in table_names:
    data[table] = dbm.read_data(table)

main()