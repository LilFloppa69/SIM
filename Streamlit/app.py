import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import pyarrow as pa

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

csv_path = "./Streamlit/polished_df_final.csv"

try:
    df = pd.read_csv(csv_path)

    # Safely parse 'tanggal' column (if exists)
    if 'tanggal' in df.columns:
        try:
            df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        except Exception:
            df['tanggal'] = df['tanggal'].astype(str)

    # Sanitasi kolom agar aman untuk PyArrow
    for col in df.columns:
        try:
            _ = pa.array(df[col])  # test PyArrow compatibility
        except Exception:
            st.warning(f"Kolom '{col}' tidak kompatibel dengan PyArrow. Akan dikonversi ke string.")
            df[col] = df[col].astype(str)

    # Deteksi kolom object yang masih nyangkut dan paksa jadi string
    object_cols = df.select_dtypes(include=['object']).columns
    for col in object_cols:
        try:
            df[col] = df[col].astype(str)
        except Exception:
            st.warning(f"Gagal konversi kolom '{col}' ke string. Akan dilewati.")

    # Output Streamlit
    st.subheader("Cek Struktur DataFrame")
    st.write("Tipe data per kolom:")
    st.write(df.dtypes)

    st.write("Sample 5 baris pertama:")
    st.write(df.head())

    st.dataframe(df)

except FileNotFoundError:
    st.error(f"File CSV tidak ditemukan: {csv_path}")


    if selected_insight == "Statistik Metode Pembayaran":
        if 'payment_type' in df.columns:
            st.header("Statistik Metode Pembayaran")
            payment_stats = df['payment_type'].value_counts().sort_values(ascending=False)
            st.dataframe(payment_stats.rename("Jumlah Transaksi"))
            st.subheader("Bar Chart")
            st.bar_chart(payment_stats)
            st.subheader("Line Chart")
            st.line_chart(payment_stats)
            st.subheader("Scatter Plot")
            fig1, ax1 = plt.subplots()
            ax1.scatter(x=payment_stats.index, y=payment_stats.values, color='green', s=100)
            ax1.set_xlabel("Metode Pembayaran")
            ax1.set_ylabel("Jumlah Transaksi")
            ax1.set_title("Scatter Plot: Metode Pembayaran")
            plt.xticks(rotation=45)
            st.pyplot(fig1)
        else:
            st.warning("Kolom 'payment_type' tidak ditemukan.")

    elif selected_insight == "Statistik Pengiriman":
        if 'delivered_on_time' in df.columns:
            st.header("Statistik Pengiriman")
            delivery_stats = df['delivered_on_time'].value_counts().sort_values(ascending=False)
            st.dataframe(delivery_stats.rename("Jumlah"))
            st.subheader("Bar Chart")
            st.bar_chart(delivery_stats)
            st.subheader("Line Chart")
            st.line_chart(delivery_stats)
            st.subheader("Scatter Plot")
            fig2, ax2 = plt.subplots()
            ax2.scatter(x=delivery_stats.index, y=delivery_stats.values, color='orange', s=100)
            ax2.set_xlabel("Status Pengiriman")
            ax2.set_ylabel("Jumlah")
            ax2.set_title("Scatter Plot: Status Pengiriman")
            st.pyplot(fig2)
            st.subheader("Pie Chart")
            fig_pie2, ax_pie2 = plt.subplots()
            ax_pie2.pie(delivery_stats, labels=delivery_stats.index, autopct='%1.1f%%', startangle=90)
            ax_pie2.axis('equal')
            st.pyplot(fig_pie2)
        else:
            st.warning("Kolom 'delivered_on_time' tidak ditemukan.")

    elif selected_insight == "Kategori Produk Terlaris":
        if 'product_category_name_english' in df.columns:
            st.header("Kategori Produk Terlaris")
            product_freq = df['product_category_name_english'].value_counts()
            top5 = product_freq.head(5)
            st.dataframe(product_freq.rename("Frekuensi"))
            st.subheader("Bar Chart")
            st.bar_chart(product_freq)
            st.subheader("Line Chart")
            st.line_chart(product_freq)
            st.subheader("Top 5 Produk Terlaris - Scatter Plot")
            fig3, ax3 = plt.subplots()
            ax3.scatter(x=top5.index, y=top5.values, color='blue', s=100)
            ax3.set_xlabel("Kategori Produk")
            ax3.set_ylabel("Frekuensi")
            ax3.set_title("Scatter Plot")
            plt.xticks(rotation=45)
            st.pyplot(fig3)
            st.subheader("Top 5 Produk Terlaris - Pie Chart")
            fig_pie, ax_pie = plt.subplots()
            ax_pie.pie(top5, labels=top5.index, autopct='%1.1f%%', startangle=90)
            ax_pie.axis('equal')
            st.pyplot(fig_pie)
        else:
            st.warning("Kolom 'product_category_name_english' tidak ditemukan.")

    elif selected_insight == "Daerah Pengiriman Terlaris":
        if 'seller_city' in df.columns:
            st.header("Statistik Pengiriman per Kota")
            city_freq = df['seller_city'].value_counts()
            top5 = city_freq.head(5)
            st.dataframe(city_freq.rename("Frekuensi"))
            st.subheader("Bar Chart")
            st.bar_chart(city_freq)
            st.subheader("Line Chart")
            st.line_chart(city_freq)
            st.subheader("Top 5 Pengiriman per Kota - Scatter Plot")
            fig3, ax3 = plt.subplots()
            ax3.scatter(x=top5.index, y=top5.values, color='blue', s=100)
            ax3.set_xlabel("Kota Penjual")
            ax3.set_ylabel("Frekuensi Pengiriman")
            ax3.set_title("Scatter Plot Pengiriman per Kota")
            plt.xticks(rotation=90)
            st.pyplot(fig3)
            st.subheader("Top 5 Pengiriman per Kota - Pie Chart")
            fig_pie, ax_pie = plt.subplots()
            ax_pie.pie(top5, labels=top5.index, autopct='%1.1f%%', startangle=90)
            ax_pie.axis('equal')
            st.pyplot(fig_pie)
        else:
            st.warning("Kolom 'seller_city' tidak ditemukan.")

    elif selected_insight == "Analisis Rata-rata Pengeluaran Pelanggan":
        st.header("Analisis Rata-rata Pengeluaran Pelanggan")
        if 'price' in df.columns:
            avg_spending_overall = df['price'].mean()
            st.write(f"Rata-rata pengeluaran pelanggan secara keseluruhan: **{avg_spending_overall:.2f}**")
            if 'seller_city' in df.columns:
                avg_spending_by_city = df.groupby('seller_city')['price'].mean().sort_values(ascending=False)
                st.subheader("Rata-rata Pengeluaran per Kota")
                st.dataframe(avg_spending_by_city.rename("Rata-rata Pengeluaran"))
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
