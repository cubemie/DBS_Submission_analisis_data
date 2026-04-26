import numpy as np
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from datetime import datetime

# Page config
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

sns.set_theme(style="whitegrid")

# Load & cache data 
@st.cache_data
def load_data():
    orders      = pd.read_csv("data/orders_dataset.csv")
    order_items = pd.read_csv("data/order_items_dataset.csv")
    payments    = pd.read_csv("data/order_payments_dataset.csv")
    reviews     = pd.read_csv("data/order_reviews_dataset.csv")
    products    = pd.read_csv("data/products_dataset.csv")
    category    = pd.read_csv("data/product_category_name_translation.csv")

    # Datetime conversion
    for col in ["order_purchase_timestamp", "order_delivered_customer_date",
                "order_estimated_delivery_date"]:
        orders[col] = pd.to_datetime(orders[col])

    # Filter delivered only
    orders = orders[orders["order_status"] == "delivered"].copy()

    # Merge items + products + category
    items = order_items.merge(
        products[["product_id", "product_category_name"]], on="product_id", how="left"
    ).merge(category, on="product_category_name", how="left")

    items = items.copy()
    items["product_category_name_english"] = items["product_category_name_english"].fillna("unknown")

    # Main merged dataframe
    main = orders[["order_id", "order_purchase_timestamp"]].merge(items, on="order_id", how="inner")
    main["order_month"] = main["order_purchase_timestamp"].dt.to_period("M")

    # Payments & reviews
    payments = payments[payments["payment_type"] != "not_defined"]

    return orders, main, payments, reviews

orders_df, main_df, payments_df, reviews_df = load_data()

# Sidebar 
st.sidebar.title("🛒 E-Commerce Dashboard")
st.sidebar.markdown("---")
st.sidebar.title("🔎 Filter Data")

min_date = orders_df["order_purchase_timestamp"].min().date()
max_date = orders_df["order_purchase_timestamp"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Rentang Tanggal",
    value=[datetime(2017, 1, 1).date(), max_date],
    min_value=min_date,
    max_value=max_date
)

# Category filter
all_cats = sorted(main_df["product_category_name_english"].dropna().unique())
selected_cats = st.sidebar.multiselect(
    "Filter Kategori (opsional)",
    options=all_cats,
    default=[]
)

st.sidebar.markdown("---")
st.sidebar.markdown("📊 **Proyek Analisis Data**\nDicoding — E-Commerce Public Dataset (Olist)")

# Apply filters 
mask_date = (
    (orders_df["order_purchase_timestamp"].dt.date >= start_date) &
    (orders_df["order_purchase_timestamp"].dt.date <= end_date)
)
filtered_orders = orders_df[mask_date]

mask_main = (
    (main_df["order_purchase_timestamp"].dt.date >= start_date) &
    (main_df["order_purchase_timestamp"].dt.date <= end_date)
)
filtered_main = main_df[mask_main]
if selected_cats:
    filtered_main = filtered_main[filtered_main["product_category_name_english"].isin(selected_cats)]

# Header 
st.title("🛒 E-Commerce Public Dataset Dashboard")
st.markdown(f"Menampilkan data dari **{start_date.strftime('%d %b %Y')}** hingga **{end_date.strftime('%d %b %Y')}**")
st.markdown("---")

# Metric Cards 
col1, col2, col3, col4 = st.columns(4)

total_orders   = filtered_orders["order_id"].nunique()
total_revenue  = filtered_main["price"].sum()
avg_review     = reviews_df[reviews_df["order_id"].isin(filtered_orders["order_id"])]["review_score"].mean()
total_items    = len(filtered_main)

col1.metric("📦 Total Pesanan",    f"{total_orders:,}")
col2.metric("💰 Total Revenue",    f"R${total_revenue:,.0f}")
col3.metric("🛍️ Total Item Terjual", f"{total_items:,}")
col4.metric("⭐ Rata-rata Ulasan",  f"{avg_review:.2f} / 5.00")

st.markdown("---")

# Pertanyaan 1: Top Kategori 
st.subheader("📌 Pertanyaan 1: Kategori produk apa yang menghasilkan volume penjualan tertinggi dan total pendapatan terbesar selama periode 2016–2018?")

cat_stats = filtered_main.groupby("product_category_name_english").agg(
    jumlah_item   =("order_id", "count"),
    total_revenue =("price", "sum")
).sort_values("jumlah_item", ascending=False)

top_n = st.slider("Tampilkan Top N Kategori", min_value=5, max_value=20, value=10)
top_vol = cat_stats.sort_values("jumlah_item", ascending=False).head(top_n)
top_rev = cat_stats.sort_values("total_revenue", ascending=False).head(top_n)

fig1, axes1 = plt.subplots(1, 2, figsize=(14, 5))
fig1.suptitle(f"Top {top_n} Kategori Produk", fontsize=13, fontweight="bold")

# Volume
c_vol = ["#1E90FF" if i == 0 else "#AED6F1" for i in range(top_n)]
b1 = axes1[0].barh(top_vol.index[::-1], top_vol["jumlah_item"][::-1],
                   color=c_vol[::-1], edgecolor="white")
axes1[0].set_title("Berdasarkan Jumlah Item Terjual")
axes1[0].set_xlabel("Jumlah Item")
axes1[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
for bar, val in zip(b1, top_vol["jumlah_item"][::-1]):
    axes1[0].text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2,
                  f"{val:,}", va="center", fontsize=8)

# Revenue
c_rev = ["#1E90FF" if i == 0 else "#AED6F1" for i in range(top_n)]
b2 = axes1[1].barh(top_rev.index[::-1], top_rev["total_revenue"][::-1],
                   color=c_rev[::-1], edgecolor="white")
axes1[1].set_title("Berdasarkan Total Pendapatan R($)")
axes1[1].set_xlabel("Total Pendapatan R($)")
axes1[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R${x/1e6:.1f}M"))
for bar, val in zip(b2, top_rev["total_revenue"][::-1]):
    axes1[1].text(bar.get_width() + 500, bar.get_y() + bar.get_height()/2,
                  fR"R${val/1e6:.2f}M", va="center", fontsize=8)

plt.tight_layout()
st.pyplot(fig1)

with st.expander("💡 Insight Pertanyaan 1"):
    st.markdown("""
    - **bed_bath_table** konsisten menjadi kategori dengan volume item terjual tertinggi.
    - **health_beauty** unggul dari sisi total pendapatan karena harga satuan produknya lebih tinggi.
    - Ada *mismatch* antara volume dan revenue — strategi bisnis perlu membedakan produk *high volume* vs *high margin*.
    """)

st.markdown("---")

# Pertanyaan 2: Tren Bulanan 
st.subheader("📌 Pertanyaan 2: Bagaimana tren jumlah pesanan bulanan dari tahun 2017 hingga 2018, dan bagaimana pola pertumbuhannya?")

monthly_orders = (
    filtered_orders
    .groupby(filtered_orders["order_purchase_timestamp"].dt.to_period("M"))["order_id"]
    .nunique()
    .reset_index()
)
monthly_orders.columns = ["bulan", "jumlah_pesanan"]
monthly_orders["bulan"] = monthly_orders["bulan"].astype(str)

monthly_revenue = (
    filtered_main
    .groupby("order_month")["price"]
    .sum()
    .reset_index()
)
monthly_revenue.columns = ["bulan", "total_revenue"]
monthly_revenue["bulan"] = monthly_revenue["bulan"].astype(str)

fig2, axes2 = plt.subplots(2, 1, figsize=(13, 8))
fig2.suptitle("Tren Penjualan E-Commerce Bulanan", fontsize=13, fontweight="bold")

# Orders
axes2[0].plot(monthly_orders["bulan"], monthly_orders["jumlah_pesanan"],
              marker="o", color="#1E90FF", linewidth=2, markersize=5)
axes2[0].fill_between(range(len(monthly_orders)), monthly_orders["jumlah_pesanan"],
                      alpha=0.15, color="#1E90FF")
if len(monthly_orders) > 0:
    peak = monthly_orders["jumlah_pesanan"].idxmax()
    axes2[0].annotate(
        f"Puncak\n{monthly_orders.loc[peak, 'bulan']}\n({monthly_orders.loc[peak, 'jumlah_pesanan']:,})",
        xy=(peak, monthly_orders.loc[peak, "jumlah_pesanan"]),
        xytext=(max(0, peak - 3), monthly_orders.loc[peak, "jumlah_pesanan"] * 0.75),
        arrowprops=dict(arrowstyle="->", color="crimson"),
        color="crimson", fontsize=8.5, fontweight="bold"
    )
axes2[0].set_title("Jumlah Pesanan per Bulan")
axes2[0].set_ylabel("Jumlah Pesanan")
axes2[0].set_xticks(range(len(monthly_orders)))
axes2[0].set_xticklabels(monthly_orders["bulan"], rotation=45, ha="right", fontsize=7.5)
axes2[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

# Revenue
bar_c = ["#1E90FF" if v == monthly_revenue["total_revenue"].max() else "#AED6F1"
         for v in monthly_revenue["total_revenue"]]
axes2[1].bar(range(len(monthly_revenue)), monthly_revenue["total_revenue"],
             color=bar_c, edgecolor="white")
axes2[1].plot(range(len(monthly_revenue)), monthly_revenue["total_revenue"],
              color="#154360", linewidth=1.5, marker="o", markersize=4)
axes2[1].set_title("Total Revenue per Bulan R($)")
axes2[1].set_ylabel("Revenue R($)")
axes2[1].set_xticks(range(len(monthly_revenue)))
axes2[1].set_xticklabels(monthly_revenue["bulan"], rotation=45, ha="right", fontsize=7.5)
axes2[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R${x/1e6:.1f}M"))

plt.tight_layout()
st.pyplot(fig2)

with st.expander("💡 Insight Pertanyaan 2"):
    st.markdown("""
    - Tren pesanan dan revenue menunjukkan **pertumbuhan konsisten** sepanjang 2016–2018.
    - **November 2017** mencatat lonjakan tertinggi, kemungkinan dipicu kampanye **Black Friday**.
    - Volume bulanan tumbuh lebih dari **17x lipat** dalam dua tahun — pertumbuhan bisnis yang sangat kuat.
    """)

st.markdown("---")

# Bonus: Ulasan & Pembayaran 
st.subheader("🔍 Analisis Tambahan: Ulasan & Metode Pembayaran")

filtered_reviews = reviews_df[reviews_df["order_id"].isin(filtered_orders["order_id"])]
filtered_pay     = payments_df[payments_df["order_id"].isin(filtered_orders["order_id"])]

col_a, col_b = st.columns(2)

with col_a:
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    score_counts = filtered_reviews["review_score"].value_counts().sort_index()
    colors_s = ["#1E90FF" if s == 5 else "#AED6F1" for s in score_counts.index]
    ax3.bar(score_counts.index, score_counts.values, color=colors_s, edgecolor="white", width=0.6)
    ax3.set_title("Distribusi Skor Ulasan Pelanggan", fontsize=11)
    ax3.set_xlabel("Skor Ulasan")
    ax3.set_ylabel("Jumlah Ulasan")
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    for s, v in zip(score_counts.index, score_counts.values):
        ax3.text(s, v + 100, f"{v:,}", ha="center", fontsize=8.5)
    plt.tight_layout()
    st.pyplot(fig3)

with col_b:
    fig4, ax4 = plt.subplots(figsize=(6, 5))
    pay_counts = filtered_pay["payment_type"].value_counts()
    payment_labels = {
        "credit_card": "Kartu Kredit",
        "boleto"     : "Boleto",
        "voucher"    : "Voucher",
        "debit_card" : "Kartu Debit"
    }
    pay_counts.index = [payment_labels.get(p, p) for p in pay_counts.index]
    colors_p = ["#1E90FF", "#5DADE2", "#AED6F1", "#D6EAF8"][:len(pay_counts)]

    wedges, texts, autotexts = ax4.pie(
        pay_counts,
        autopct="%1.1f%%",
        colors=colors_p,
        startangle=140,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        pctdistance=0.6,
        labeldistance=1.25
    )

    for autotext in autotexts:
        autotext.set_visible(False)

    bbox_props = dict(boxstyle="square,pad=0.2", fc="white", ec="none")
    kw = dict(arrowprops=dict(arrowstyle="-", color="red"),
              bbox=bbox_props, zorder=0, va="center")

    for i, (wedge, pct) in enumerate(zip(wedges, autotexts)):
        ang = (wedge.theta2 - wedge.theta1) / 2.0 + wedge.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = "left" if x > 0 else "right"
        label = f"{pay_counts.index[i]}\n{pay_counts.values[i]/pay_counts.sum()*100:.1f}%"
        ax4.annotate(
            label,
            xy=(x * 0.75, y * 0.75),
            xytext=(x * 1.2, y * 1.2),
            horizontalalignment=horizontalalignment,
            fontsize=8.5,
            **kw
        )

    ax4.set_title("Distribusi Metode Pembayaran", fontsize=11, pad=15)
    plt.tight_layout()
    st.pyplot(fig4)

st.markdown("---")
st.caption("Dashboard Proyek Analisis Data")