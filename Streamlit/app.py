import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

st.set_page_config(page_title="Visualisasi Penjualan", layout="wide")
st.title("🛍️ Dashboard Visualisasi Penjualan & Statistik")

csv_path = "https://raw.githubusercontent.com/LilFloppa69/SIM/refs/heads/main/Streamlit/polished_df_final.csv"

def clean_dataframe(df):
    """
    Membersihkan DataFrame untuk menghindari ArrowTypeError dan Git conflicts
    """
    # Convert semua ke string dulu untuk cleaning
    df_clean = df.copy()
    
    # Remove Git merge conflict markers dari semua cells
    git_patterns = ['<<<<<<< HEAD', '=======', '>>>>>>> ', '<<<<<<< ', '>>>>>>> ']
    for pattern in git_patterns:
        df_clean = df_clean.replace(pattern, '', regex=False)
    
    # Ganti string kosong atau whitespace dengan NaN
    df = df.replace(r'^\s*$', np.nan, regex=True)
    
    # Hapus baris yang seluruh kolomnya kosong (NaN semua)
    df.dropna(how='all', inplace=True)

try:
    # Read CSV dengan parameter khusus untuk handle mixed types
    df = pd.read_csv(csv_path, low_memory=False, dtype=str)
    
    # CRITICAL: Fix Git merge conflict
    # Remove rows that contain Git merge markers
    git_markers = ['<<<<<<< HEAD', '=======', '>>>>>>> ']
    mask = df.astype(str).apply(lambda x: x.str.contains('|'.join(git_markers), na=False)).any(axis=1)
    if mask.any():
        st.warning(f"⚠️ Ditemukan {mask.sum()} baris dengan Git merge conflict - akan dihapus otomatis")
        df = df[~mask]
    
    # Remove completely empty rows
    df = df.dropna(how='all')
    
    # Reset index after cleaning
    df = df.reset_index(drop=True)
    
    # Clean dataframe untuk menghindari Arrow error
    df = clean_dataframe(df)
    
    if 'tanggal' in df.columns:
        try:
            df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        except:
            st.warning("Tidak dapat mengkonversi kolom tanggal")
    
    # ======================== SECTION 1: DATA PENJUALAN ========================
    st.header("📊 Data Penjualan")
    st.write(f"**Total rows:** {len(df):,} | **Total columns:** {len(df.columns)}")
    
    # Tampilkan kolom yang tersedia
    with st.expander("🔍 Lihat Kolom Yang Tersedia"):
        # Filter out Git conflict columns
        clean_columns = [col for col in df.columns if not any(marker in str(col) for marker in ['<<<<', '>>>>', '======'])]
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Daftar Kolom Bersih:**")
            for i, col in enumerate(clean_columns):
                st.write(f"{i+1}. `{col}` ({df[col].dtype})")
        with col2:
            st.write("**Sample Data (5 kolom pertama):**")
            try:
                sample_cols = clean_columns[:5] if len(clean_columns) >= 5 else clean_columns
                st.dataframe(df[sample_cols].head(3))
            except Exception as e:
                st.write(f"Error showing sample: {e}")
                
        # Show problematic columns if any
        problem_columns = [col for col in df.columns if any(marker in str(col) for marker in ['<<<<', '>>>>', '======'])]
        if problem_columns:
            st.error("⚠️ **Kolom bermasalah (Git conflict):**")
            for col in problem_columns:
                st.write(f"- `{col}`")
    
    # Display dataframe dengan error handling
    try:
        st.subheader("📋 Preview Data (100 rows pertama)")
        st.dataframe(df.head(100), use_container_width=True)
    except Exception as e:
        st.error(f"Error menampilkan dataframe lengkap: {str(e)}")
    
    st.divider()
    
    # ======================== SECTION 2: STATISTIK METODE PEMBAYARAN ========================
    st.header("💳 Statistik Metode Pembayaran")
    
    # Cari kolom yang mungkin payment related (lebih fleksibel)
    clean_columns = [col for col in df.columns if not any(marker in str(col) for marker in ['<<<<', '>>>>', '======'])]
    payment_columns = [col for col in clean_columns if any(keyword in col.lower() for keyword in ['payment', 'pay', 'method', 'type'])]
    
    if payment_columns:
        payment_col = payment_columns[0]  # ambil yang pertama
        st.success(f"Menggunakan kolom: `{payment_col}`")
        
        payment_stats = df[payment_col].value_counts().sort_values(ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            payment_df = pd.DataFrame({
                'Metode Pembayaran': payment_stats.index,
                'Jumlah Transaksi': payment_stats.values
            })
            st.dataframe(payment_df, use_container_width=True)
        
        with col2:
            fig1, ax1 = plt.subplots(figsize=(8, 6))
            ax1.pie(payment_stats.values, labels=payment_stats.index, autopct='%1.1f%%', startangle=90)
            ax1.set_title("Distribusi Metode Pembayaran")
            st.pyplot(fig1)
        
        # Charts
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("📊 Bar Chart")
            st.bar_chart(payment_stats)
        
        with col4:
            st.subheader("📈 Line Chart")
            st.line_chart(payment_stats)
            
    else:
        st.warning("❌ Tidak ada kolom payment yang ditemukan. Kolom yang tersedia:")
        st.write([col for col in clean_columns if col.strip() != ''])
    
    st.divider()
    
    # ======================== SECTION 3: STATISTIK PENGIRIMAN ========================
    st.header("🚚 Statistik Pengiriman")
    
    # Cari kolom yang delivery related
    delivery_columns = [col for col in clean_columns if any(keyword in col.lower() for keyword in ['deliver', 'ship', 'time', 'status', 'date'])]
    
    if delivery_columns:
        delivery_col = delivery_columns[0]
        st.success(f"Menggunakan kolom: `{delivery_col}`")
        
        delivery_stats = df[delivery_col].value_counts().sort_values(ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            delivery_df = pd.DataFrame({
                'Status Pengiriman': delivery_stats.index,
                'Jumlah': delivery_stats.values
            })
            st.dataframe(delivery_df, use_container_width=True)
        
        with col2:
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            ax2.pie(delivery_stats.values, labels=delivery_stats.index, autopct='%1.1f%%', startangle=90)
            ax2.set_title("Status Pengiriman")
            st.pyplot(fig2)
        
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("📊 Bar Chart")
            st.bar_chart(delivery_stats)
        
        with col4:
            st.subheader("📈 Line Chart")
            st.line_chart(delivery_stats)
            
    else:
        st.warning("❌ Tidak ada kolom delivery yang ditemukan")
    
    st.divider()
    
    # ======================== SECTION 4: KATEGORI PRODUK TERLARIS ========================
    st.header("🏆 Kategori Produk Terlaris")
    
    # Cari kolom produk/kategori
    product_columns = [col for col in clean_columns if any(keyword in col.lower() for keyword in ['product', 'category', 'item', 'name'])]
    
    if product_columns:
        product_col = product_columns[0]
        st.success(f"Menggunakan kolom: `{product_col}`")
        
        product_freq = df[product_col].value_counts()
        top10 = product_freq.head(10)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 Semua Kategori")
            product_df = pd.DataFrame({
                'Kategori Produk': product_freq.index,
                'Frekuensi': product_freq.values
            })
            st.dataframe(product_df, use_container_width=True)
        
        with col2:
            st.subheader("🥇 Top 10 Pie Chart")
            fig3, ax3 = plt.subplots(figsize=(10, 8))
            ax3.pie(top10.values, labels=top10.index, autopct='%1.1f%%', startangle=90)
            ax3.set_title("Top 10 Produk Terlaris")
            plt.tight_layout()
            st.pyplot(fig3)
        
        st.subheader("📊 Bar Chart - Semua Kategori")
        st.bar_chart(product_freq)
        
    else:
        st.warning("❌ Tidak ada kolom product/category yang ditemukan")
    
    st.divider()
    
    # ======================== SECTION 5: DAERAH PENGIRIMAN TERLARIS ========================
    st.header("🌍 Daerah Pengiriman Terlaris")
    
    # Cari kolom city/location
    city_columns = [col for col in clean_columns if any(keyword in col.lower() for keyword in ['city', 'location', 'address', 'region', 'state'])]
    
    if city_columns:
        city_col = city_columns[0]
        st.success(f"Menggunakan kolom: `{city_col}`")
        
        city_freq = df[city_col].value_counts()
        top10_cities = city_freq.head(10)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 Semua Kota")
            city_df = pd.DataFrame({
                'Kota': city_freq.index,
                'Frekuensi': city_freq.values
            })
            st.dataframe(city_df, use_container_width=True)
        
        with col2:
            st.subheader("🏙️ Top 10 Kota")
            fig4, ax4 = plt.subplots(figsize=(10, 8))
            ax4.pie(top10_cities.values, labels=top10_cities.index, autopct='%1.1f%%', startangle=90)
            ax4.set_title("Top 10 Kota Pengiriman")
            plt.tight_layout()
            st.pyplot(fig4)
        
        st.subheader("📊 Bar Chart - Semua Kota")
        st.bar_chart(city_freq)
        
    else:
        st.warning("❌ Tidak ada kolom city/location yang ditemukan")
    
    st.divider()
    
    # ======================== SECTION 6: ANALISIS RATA-RATA PENGELUARAN ========================
    st.header("💰 Analisis Rata-rata Pengeluaran Pelanggan")
    
    # Cari kolom price/amount
    price_columns = [col for col in clean_columns if any(keyword in col.lower() for keyword in ['price', 'amount', 'cost', 'total', 'value', 'money'])]
    
    if price_columns:
        price_col = price_columns[0]
        st.success(f"Menggunakan kolom: `{price_col}`")
        
        # Convert to numeric
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
        
        avg_spending_overall = df[price_col].mean()
        median_spending = df[price_col].median()
        max_spending = df[price_col].max()
        min_spending = df[price_col].min()
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💸 Rata-rata", f"{avg_spending_overall:.2f}")
        with col2:
            st.metric("📊 Median", f"{median_spending:.2f}")
        with col3:
            st.metric("📈 Maksimum", f"{max_spending:.2f}")
        with col4:
            st.metric("📉 Minimum", f"{min_spending:.2f}")
        
        # Analysis by city if available
        if city_columns:
            city_col = city_columns[0]
            avg_spending_by_city = df.groupby(city_col)[price_col].mean().sort_values(ascending=False)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🏙️ Rata-rata Pengeluaran per Kota")
                spending_df = pd.DataFrame({
                    'Kota': avg_spending_by_city.index,
                    'Rata-rata Pengeluaran': avg_spending_by_city.values
                })
                st.dataframe(spending_df, use_container_width=True)
            
            with col2:
                st.subheader("📊 Top 10 Kota - Pengeluaran Tertinggi")
                st.bar_chart(avg_spending_by_city.head(10))
            
            # Analysis insight
            st.subheader("🔍 Insight Geografis")
            if avg_spending_by_city.max() - avg_spending_by_city.min() > 0:
                st.success("✅ **Ada perbedaan pengeluaran antar lokasi geografis:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.info(f"🥇 **Tertinggi:** {avg_spending_by_city.index[0]} \n({avg_spending_by_city.iloc[0]:.2f})")
                with col2:
                    st.warning(f"🥉 **Terendah:** {avg_spending_by_city.index[-1]} \n({avg_spending_by_city.iloc[-1]:.2f})")
                with col3:
                    st.error(f"📊 **Selisih:** {(avg_spending_by_city.max() - avg_spending_by_city.min()):.2f}")
            else:
                st.info("ℹ️ Rata-rata pengeluaran pelanggan relatif sama di semua lokasi.")
        
    else:
        st.warning("❌ Tidak ada kolom price/amount yang ditemukan")
    
    st.divider()
    
    # ======================== FOOTER ========================
    st.success("🎉 **Dashboard berhasil dimuat!** Scroll ke atas untuk melihat semua analisis.")
    st.balloons()

except FileNotFoundError:
    st.error(f"❌ **File CSV tidak ditemukan:** `{csv_path}`")
    st.write("Pastikan file CSV ada di lokasi yang benar!")
except Exception as e:
    st.error(f"💥 **Error tidak terduga:** {str(e)}")
    st.write("**Kemungkinan penyebab:**")
    st.write("- Format CSV bermasalah")
    st.write("- Kolom mengandung data yang corrupt")
    st.write("- Memory tidak cukup untuk memproses file besar")
, '', regex=True)
    
    # Convert mixed types to string untuk kolom object
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            # Clean up the column
            df_clean[col] = df_clean[col].astype(str)
            df_clean[col] = df_clean[col].replace('nan', '')
            df_clean[col] = df_clean[col].replace('None', '')
    
    # Handle missing values
    df_clean = df_clean.fillna('')
    
    # Try to convert numeric columns properly
    for col in df_clean.columns:
        # Skip if column name looks like Git conflict
        if any(marker in str(col) for marker in ['<<<<', '>>>>', '======']):
            continue
            
        # Try to convert to numeric if it makes sense
        if df_clean[col].dtype == 'object':
            # Check if column contains mostly numbers
            try:
                # Remove empty strings and try conversion
                non_empty = df_clean[col][df_clean[col] != '']
                if len(non_empty) > 0:
                    numeric_converted = pd.to_numeric(non_empty, errors='coerce')
                    # If more than 70% can be converted to numbers, treat as numeric
                    if numeric_converted.notna().sum() / len(non_empty) > 0.7:
                        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            except:
                pass
    
    return df_clean

try:
    # Read CSV dengan parameter khusus untuk handle mixed types
    df = pd.read_csv(csv_path, low_memory=False, dtype=str)
    
    # CRITICAL: Fix Git merge conflict
    # Remove rows that contain Git merge markers
    git_markers = ['<<<<<<< HEAD', '=======', '>>>>>>> ']
    mask = df.astype(str).apply(lambda x: x.str.contains('|'.join(git_markers), na=False)).any(axis=1)
    if mask.any():
        st.warning(f"⚠️ Ditemukan {mask.sum()} baris dengan Git merge conflict - akan dihapus otomatis")
        df = df[~mask]
    
    # Remove completely empty rows
    df = df.dropna(how='all')
    
    # Reset index after cleaning
    df = df.reset_index(drop=True)
    
    # Clean dataframe untuk menghindari Arrow error
    df = clean_dataframe(df)
    
    if 'tanggal' in df.columns:
        try:
            df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        except:
            st.warning("Tidak dapat mengkonversi kolom tanggal")
    
    # ======================== SECTION 1: DATA PENJUALAN ========================
    st.header("📊 Data Penjualan")
    st.write(f"**Total rows:** {len(df):,} | **Total columns:** {len(df.columns)}")
    
    # Tampilkan kolom yang tersedia
    with st.expander("🔍 Lihat Kolom Yang Tersedia"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Daftar Kolom:**")
            for i, col in enumerate(df.columns):
                st.write(f"{i+1}. `{col}` ({df[col].dtype})")
        with col2:
            st.write("**Sample Data:**")
            try:
                st.dataframe(df.head(5))
            except:
                st.write("Error menampilkan sample data")
    
    # Display dataframe dengan error handling
    try:
        st.subheader("📋 Preview Data (100 rows pertama)")
        st.dataframe(df.head(100), use_container_width=True)
    except Exception as e:
        st.error(f"Error menampilkan dataframe lengkap: {str(e)}")
    
    st.divider()
    
    # ======================== SECTION 2: STATISTIK METODE PEMBAYARAN ========================
    st.header("💳 Statistik Metode Pembayaran")
    
    # Cari kolom yang mungkin payment related
    payment_columns = [col for col in df.columns if 'payment' in col.lower() or 'pay' in col.lower()]
    
    if payment_columns:
        payment_col = payment_columns[0]  # ambil yang pertama
        st.success(f"Menggunakan kolom: `{payment_col}`")
        
        payment_stats = df[payment_col].value_counts().sort_values(ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            payment_df = pd.DataFrame({
                'Metode Pembayaran': payment_stats.index,
                'Jumlah Transaksi': payment_stats.values
            })
            st.dataframe(payment_df, use_container_width=True)
        
        with col2:
            fig1, ax1 = plt.subplots(figsize=(8, 6))
            ax1.pie(payment_stats.values, labels=payment_stats.index, autopct='%1.1f%%', startangle=90)
            ax1.set_title("Distribusi Metode Pembayaran")
            st.pyplot(fig1)
        
        # Charts
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("📊 Bar Chart")
            st.bar_chart(payment_stats)
        
        with col4:
            st.subheader("📈 Line Chart")
            st.line_chart(payment_stats)
            
    else:
        st.warning("❌ Tidak ada kolom payment yang ditemukan. Kolom yang tersedia:")
        st.write(df.columns.tolist())
    
    st.divider()
    
    # ======================== SECTION 3: STATISTIK PENGIRIMAN ========================
    st.header("🚚 Statistik Pengiriman")
    
    # Cari kolom yang delivery related
    delivery_columns = [col for col in df.columns if 'deliver' in col.lower() or 'ship' in col.lower() or 'time' in col.lower()]
    
    if delivery_columns:
        delivery_col = delivery_columns[0]
        st.success(f"Menggunakan kolom: `{delivery_col}`")
        
        delivery_stats = df[delivery_col].value_counts().sort_values(ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            delivery_df = pd.DataFrame({
                'Status Pengiriman': delivery_stats.index,
                'Jumlah': delivery_stats.values
            })
            st.dataframe(delivery_df, use_container_width=True)
        
        with col2:
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            ax2.pie(delivery_stats.values, labels=delivery_stats.index, autopct='%1.1f%%', startangle=90)
            ax2.set_title("Status Pengiriman")
            st.pyplot(fig2)
        
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("📊 Bar Chart")
            st.bar_chart(delivery_stats)
        
        with col4:
            st.subheader("📈 Line Chart")
            st.line_chart(delivery_stats)
            
    else:
        st.warning("❌ Tidak ada kolom delivery yang ditemukan")
    
    st.divider()
    
    # ======================== SECTION 4: KATEGORI PRODUK TERLARIS ========================
    st.header("🏆 Kategori Produk Terlaris")
    
    # Cari kolom produk/kategori
    product_columns = [col for col in df.columns if 'product' in col.lower() or 'category' in col.lower() or 'item' in col.lower()]
    
    if product_columns:
        product_col = product_columns[0]
        st.success(f"Menggunakan kolom: `{product_col}`")
        
        product_freq = df[product_col].value_counts()
        top10 = product_freq.head(10)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 Semua Kategori")
            product_df = pd.DataFrame({
                'Kategori Produk': product_freq.index,
                'Frekuensi': product_freq.values
            })
            st.dataframe(product_df, use_container_width=True)
        
        with col2:
            st.subheader("🥇 Top 10 Pie Chart")
            fig3, ax3 = plt.subplots(figsize=(10, 8))
            ax3.pie(top10.values, labels=top10.index, autopct='%1.1f%%', startangle=90)
            ax3.set_title("Top 10 Produk Terlaris")
            plt.tight_layout()
            st.pyplot(fig3)
        
        st.subheader("📊 Bar Chart - Semua Kategori")
        st.bar_chart(product_freq)
        
    else:
        st.warning("❌ Tidak ada kolom product/category yang ditemukan")
    
    st.divider()
    
    # ======================== SECTION 5: DAERAH PENGIRIMAN TERLARIS ========================
    st.header("🌍 Daerah Pengiriman Terlaris")
    
    # Cari kolom city/location
    city_columns = [col for col in df.columns if 'city' in col.lower() or 'location' in col.lower() or 'address' in col.lower()]
    
    if city_columns:
        city_col = city_columns[0]
        st.success(f"Menggunakan kolom: `{city_col}`")
        
        city_freq = df[city_col].value_counts()
        top10_cities = city_freq.head(10)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 Semua Kota")
            city_df = pd.DataFrame({
                'Kota': city_freq.index,
                'Frekuensi': city_freq.values
            })
            st.dataframe(city_df, use_container_width=True)
        
        with col2:
            st.subheader("🏙️ Top 10 Kota")
            fig4, ax4 = plt.subplots(figsize=(10, 8))
            ax4.pie(top10_cities.values, labels=top10_cities.index, autopct='%1.1f%%', startangle=90)
            ax4.set_title("Top 10 Kota Pengiriman")
            plt.tight_layout()
            st.pyplot(fig4)
        
        st.subheader("📊 Bar Chart - Semua Kota")
        st.bar_chart(city_freq)
        
    else:
        st.warning("❌ Tidak ada kolom city/location yang ditemukan")
    
    st.divider()
    
    # ======================== SECTION 6: ANALISIS RATA-RATA PENGELUARAN ========================
    st.header("💰 Analisis Rata-rata Pengeluaran Pelanggan")
    
    # Cari kolom price/amount
    price_columns = [col for col in df.columns if 'price' in col.lower() or 'amount' in col.lower() or 'cost' in col.lower() or 'total' in col.lower()]
    
    if price_columns:
        price_col = price_columns[0]
        st.success(f"Menggunakan kolom: `{price_col}`")
        
        # Convert to numeric
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
        
        avg_spending_overall = df[price_col].mean()
        median_spending = df[price_col].median()
        max_spending = df[price_col].max()
        min_spending = df[price_col].min()
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💸 Rata-rata", f"{avg_spending_overall:.2f}")
        with col2:
            st.metric("📊 Median", f"{median_spending:.2f}")
        with col3:
            st.metric("📈 Maksimum", f"{max_spending:.2f}")
        with col4:
            st.metric("📉 Minimum", f"{min_spending:.2f}")
        
        # Analysis by city if available
        if city_columns:
            city_col = city_columns[0]
            avg_spending_by_city = df.groupby(city_col)[price_col].mean().sort_values(ascending=False)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🏙️ Rata-rata Pengeluaran per Kota")
                spending_df = pd.DataFrame({
                    'Kota': avg_spending_by_city.index,
                    'Rata-rata Pengeluaran': avg_spending_by_city.values
                })
                st.dataframe(spending_df, use_container_width=True)
            
            with col2:
                st.subheader("📊 Top 10 Kota - Pengeluaran Tertinggi")
                st.bar_chart(avg_spending_by_city.head(10))
            
            # Analysis insight
            st.subheader("🔍 Insight Geografis")
            if avg_spending_by_city.max() - avg_spending_by_city.min() > 0:
                st.success("✅ **Ada perbedaan pengeluaran antar lokasi geografis:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.info(f"🥇 **Tertinggi:** {avg_spending_by_city.index[0]} \n({avg_spending_by_city.iloc[0]:.2f})")
                with col2:
                    st.warning(f"🥉 **Terendah:** {avg_spending_by_city.index[-1]} \n({avg_spending_by_city.iloc[-1]:.2f})")
                with col3:
                    st.error(f"📊 **Selisih:** {(avg_spending_by_city.max() - avg_spending_by_city.min()):.2f}")
            else:
                st.info("ℹ️ Rata-rata pengeluaran pelanggan relatif sama di semua lokasi.")
        
    else:
        st.warning("❌ Tidak ada kolom price/amount yang ditemukan")
    
    st.divider()
    
    # ======================== FOOTER ========================
    st.success("🎉 **Dashboard berhasil dimuat!** Scroll ke atas untuk melihat semua analisis.")
    st.balloons()

except FileNotFoundError:
    st.error(f"❌ **File CSV tidak ditemukan:** `{csv_path}`")
    st.write("Pastikan file CSV ada di lokasi yang benar!")
except Exception as e:
    st.error(f"💥 **Error tidak terduga:** {str(e)}")
    st.write("**Kemungkinan penyebab:**")
    st.write("- Format CSV bermasalah")
    st.write("- Kolom mengandung data yang corrupt")
    st.write("- Memory tidak cukup untuk memproses file besar")
