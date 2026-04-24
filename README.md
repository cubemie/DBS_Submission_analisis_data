# Proyek Analisis Data: E-Commerce Public Dataset ✨

## 📋 Informasi Submitter
- **Nama:** MUTIA SANIYA RAHMA
- **Email:** cdcc001d6x2018@student.devacademy.id
- **ID Dicoding:** cdcc001d6x2018

---

## 📊 Tentang Proyek
Proyek ini menganalisis **E-Commerce Public Dataset** dari platform Olist Brasil untuk menjawab dua pertanyaan bisnis utama:

1. **Kategori produk apa yang paling banyak terjual dan menghasilkan pendapatan terbesar?**
2. **Bagaimana tren jumlah pesanan bulanan dari waktu ke waktu, dan apakah ada pola pertumbuhan yang terlihat?**

Dataset berisi 8 tabel terhubung dengan lebih dari 99,000 pesanan dari September 2016 hingga Oktober 2018.

---

## 🛠️ Setup Environment

### Menggunakan Anaconda
```bash

### Menggunakan Shell/Terminal (venv)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📦 Dependencies
- pandas
- numpy
- matplotlib
- seaborn

---

## 🚀 Cara Menjalankan

### Streamlit Dashboard (jika tersedia)
```bash
streamlit run dashboard.py
```

---

## 📁 Struktur File
```
.
├── README.md
├── requirements.txt
├── Proyek_Analisis_Data e- comarce.ipynb
├── E-commerce-public-dataset.zip
└── data/
    ├── orders_dataset.csv
    ├── order_items_dataset.csv
    ├── order_payments_dataset.csv
    ├── order_reviews_dataset.csv
    ├── products_dataset.csv
    ├── product_category_name_translation.csv
    ├── customers_dataset.csv
    ├── sellers_dataset.csv
    └── geolocation_dataset.csv
```

---

## 📈 Key Findings
- **Kategori Terlaris:** bed_bath_table (volume tertinggi)
- **Kategori Pendapatan Terbesar:** health_beauty
- **Pertumbuhan:** Volume pesanan meningkat 17x lipat dalam 2 tahun
- **Peak Sales:** November 2017 (kemungkinan Black Friday)

---

## 📝 Author
MUTIA SANIYA RAHMA - DBS Coding Camp Submission
