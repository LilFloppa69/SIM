import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

st.set_page_config(page_title="Visualisasi Penjualan", layout="centered")
st.title("Visualisasi Penjualan & Statistik")

# Navigasi
st.sidebar.title("Navigasi")
insight_options = [
    "Data Penjualan",
    "Statistik Metode Pembayaran",
    "Statistik Pengiriman",
    "Kategori Produk Terlaris",
    "Daerah Pengiriman Terlaris",
    "Analisis Rata-rata Pengeluaran Pelanggan"
]
selected_insight = st.sidebar.selectbox("Pilih Analisis", insight_options)

csv_path = "https://raw.githubusercontent.com/LilFloppa69/SIM/refs/heads/main/Streamlit/polished_df_final.csv"

def clean_dataframe(df):
    """
    Membersihkan DataFrame untuk menghindari ArrowTypeError
    """
    # Convert mixed types to string untuk kolom object
    for col in df.columns:
        if df[col].dtype == 'object':
            # Cek apakah ada mixed types
            types = df[col].apply(type).unique()
            if len(types) > 1:
                df[col] = df[col].astype(str)
    
    # Handle missing values
    df = df.fillna('')
    
    # Convert numeric columns yang mungkin bermasalah
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].dtype == 'int64':
            # Convert ke int32 atau float64 untuk menghindari masalah Arrow
            try:
                df[col] = df[col].astype('int32')
            except:
                df[col] = df[col].astype('float64')
    
    return df

try:
    df = pd.read_csv(csv_path)
    
    # Clean dataframe untuk menghindari Arrow error
    df = clean_dataframe(df)
    
    if 'tanggal' in df.columns:
        try:
            df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        except:
            st.warning("Tidak dapat mengkonversi kolom tanggal")
    
    if selected_insight == "Data Penjualan":
        st.subheader("Data Penjualan")
        
        # Display basic info
        st.write(f"Total rows: {len(df)}")
        st.write(f"Total columns: {len(df.columns)}")
        
        # Display sample data with error handling
        try:
            st.dataframe(df.head(100))  # Batasi hanya 100 rows pertama untuk preview
        except Exception as e:
            st.error(f"Error menampilkan dataframe: {str(e)}")
            # Alternative: show basic statistics
            st.subheader("Informasi Dataset")
            st.write("Kolom-kolom dalam dataset:")
            for i, col in enumerate(df.columns):
                st.write(f"{i+1}. {col} ({df[col].dtype})")

    elif selected_insight == "Statistik Metode Pembayaran":
        if 'payment_type' in df.columns:
            st.header("Statistik Metode Pembayaran")
            payment_stats = df['payment_type'].value_counts().sort_values(ascending=False)
            
            # Convert to DataFrame untuk menghindari error
            payment_df = pd.DataFrame({
                'Metode Pembayaran': payment_stats.index,
                'Jumlah Transaksi': payment_stats.values
            })
            st.dataframe(payment_df)
            
            st.subheader("Bar Chart")
            st.bar_chart(payment_stats)
            
            st.subheader("Line Chart")
            st.line_chart(payment_stats)
            
            st.subheader("Scatter Plot")
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            ax1.scatter(x=range(len(payment_stats)), y=payment_stats.values, color='green', s=100)
            ax1.set_xlabel("Metode Pembayaran")
            ax1.set_ylabel("Jumlah Transaksi")
            ax1.set_title("Scatter Plot: Metode Pembayaran")
            ax1.set_xticks(range(len(payment_stats)))
            ax1.set_xticklabels(payment_stats.index, rotation=45)
            plt.tight_layout()
            st.pyplot(fig1)
        else:
            st.warning("Kolom 'payment_type' tidak ditemukan.")

    elif selected_insight == "Statistik Pengiriman":
        if 'delivered_on_time' in df.columns:
            st.header("Statistik Pengiriman")
            delivery_stats = df['delivered_on_time'].value_counts().sort_values(ascending=False)
            
            # Convert to DataFrame
            delivery_df = pd.DataFrame({
                'Status Pengiriman': delivery_stats.index,
                'Jumlah': delivery_stats.values
            })
            st.dataframe(delivery_df)
            
            st.subheader("Bar Chart")
            st.bar_chart(delivery_stats)
            
            st.subheader("Line Chart")
            st.line_chart(delivery_stats)
            
            st.subheader("Scatter Plot")
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            ax2.scatter(x=range(len(delivery_stats)), y=delivery_stats.values, color='orange', s=100)
            ax2.set_xlabel("Status Pengiriman")
            ax2.set_ylabel("Jumlah")
            ax2.set_title("Scatter Plot: Status Pengiriman")
            ax2.set_xticks(range(len(delivery_stats)))
            ax2.set_xticklabels(delivery_stats.index)
            plt.tight_layout()
            st.pyplot(fig2)
            
            st.subheader("Pie Chart")
            fig_pie2, ax_pie2 = plt.subplots(figsize=(8, 8))
            ax_pie2.pie(delivery_stats.values, labels=delivery_stats.index, autopct='%1.1f%%', startangle=90)
            ax_pie2.axis('equal')
            st.pyplot(fig_pie2)
        else:
            st.warning("Kolom 'delivered_on_time' tidak ditemukan.")

    elif selected_insight == "Kategori Produk Terlaris":
        if 'product_category_name_english' in df.columns:
            st.header("Kategori Produk Terlaris")
            product_freq = df['product_category_name_english'].value_counts()
            top5 = product_freq.head(5)
            
            # Convert to DataFrame
            product_df = pd.DataFrame({
                'Kategori Produk': product_freq.index,
                'Frekuensi': product_freq.values
            })
            st.dataframe(product_df)
            
            st.subheader("Bar Chart")
            st.bar_chart(product_freq)
            
            st.subheader("Line Chart")
            st.line_chart(product_freq)
            
            st.subheader("Top 5 Produk Terlaris - Scatter Plot")
            fig3, ax3 = plt.subplots(figsize=(12, 6))
            ax3.scatter(x=range(len(top5)), y=top5.values, color='blue', s=100)
            ax3.set_xlabel("Kategori Produk")
            ax3.set_ylabel("Frekuensi")
            ax3.set_title("Scatter Plot - Top 5 Produk Terlaris")
            ax3.set_xticks(range(len(top5)))
            ax3.set_xticklabels(top5.index, rotation=45)
            plt.tight_layout()
            st.pyplot(fig3)
            
            st.subheader("Top 5 Produk Terlaris - Pie Chart")
            fig_pie, ax_pie = plt.subplots(figsize=(10, 10))
            ax_pie.pie(top5.values, labels=top5.index, autopct='%1.1f%%', startangle=90)
            ax_pie.axis('equal')
            st.pyplot(fig_pie)
        else:
            st.warning("Kolom 'product_category_name_english' tidak ditemukan.")
            
    elif selected_insight == "Daerah Pengiriman Terlaris":
        if 'seller_city' in df.columns:
            st.header("Statistik Pengiriman per Kota")
            city_freq = df['seller_city'].value_counts()
            top5 = city_freq.head(5)
            
            # Convert to DataFrame
            city_df = pd.DataFrame({
                'Kota': city_freq.index,
                'Frekuensi': city_freq.values
            })
            st.dataframe(city_df)
            
            st.subheader("Bar Chart")
            st.bar_chart(city_freq)
            
            st.subheader("Line Chart")
            st.line_chart(city_freq)
            
            st.subheader("Top 5 Pengiriman per Kota - Scatter Plot")
            fig3, ax3 = plt.subplots(figsize=(12, 6))
            ax3.scatter(x=range(len(top5)), y=top5.values, color='blue', s=100)
            ax3.set_xlabel("Kota Penjual")
            ax3.set_ylabel("Frekuensi Pengiriman")
            ax3.set_title("Scatter Plot Pengiriman per Kota")
            ax3.set_xticks(range(len(top5)))
            ax3.set_xticklabels(top5.index, rotation=90)
            plt.tight_layout()
            st.pyplot(fig3)
            
            st.subheader("Top 5 Pengiriman per Kota - Pie Chart")
            fig_pie, ax_pie = plt.subplots(figsize=(10, 10))
            ax_pie.pie(top5.values, labels=top5.index, autopct='%1.1f%%', startangle=90)
            ax_pie.axis('equal')
            st.pyplot(fig_pie)
        else:
            st.warning("Kolom 'seller_city' tidak ditemukan.")
            
    elif selected_insight == "Analisis Rata-rata Pengeluaran Pelanggan":
        st.header("Analisis Rata-rata Pengeluaran Pelanggan")
        if 'price' in df.columns:
            # Convert price to numeric if needed
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
            
            avg_spending_overall = df['price'].mean()
            st.write(f"Rata-rata pengeluaran pelanggan secara keseluruhan: **{avg_spending_overall:.2f}**")
            
            if 'seller_city' in df.columns:
                avg_spending_by_city = df.groupby('seller_city')['price'].mean().sort_values(ascending=False)
                
                st.subheader("Rata-rata Pengeluaran per Kota")
                spending_df = pd.DataFrame({
                    'Kota': avg_spending_by_city.index,
                    'Rata-rata Pengeluaran': avg_spending_by_city.values
                })
                st.dataframe(spending_df)
                
                st.subheader("Bar Chart: Rata-rata Pengeluaran per Kota")
                st.bar_chart(avg_spending_by_city)
                
                st.subheader("Apakah Ada Perbedaan Pengeluaran Antar Lokasi?")
                if avg_spending_by_city.max() - avg_spending_by_city.min() > 0:
                    st.write("**Ya**, ada perbedaan pengeluaran antar lokasi geografis. Berikut detailnya:")
                    st.write(f"- Kota tertinggi: **{avg_spending_by_city.index[0]}** ({avg_spending_by_city.iloc[0]:.2f})")
                    st.write(f"- Kota terendah: **{avg_spending_by_city.index[-1]}** ({avg_spending_by_city.iloc[-1]:.2f})")
                    st.write(f"- Selisih: **{(avg_spending_by_city.max() - avg_spending_by_city.min()):.2f}**")
                else:
                    st.write("**Tidak**, rata-rata pengeluaran pelanggan sama di semua lokasi.")
            else:
                st.warning("Kolom 'seller_city' tidak ditemukan.")
        else:
            st.warning("Kolom 'price' tidak ditemukan.")

except FileNotFoundError:
    st.error(f"File CSV tidak ditemukan: {csv_path}")
except Exception as e:
    st.error(f"Error tidak terduga: {str(e)}")
    st.write("Silakan periksa format data CSV Anda.")
