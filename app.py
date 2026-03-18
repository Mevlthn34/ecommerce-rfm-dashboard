import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_csv("data/Online Retail.csv", sep=";")
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], dayfirst=True)

    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")

    df = df.dropna()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], dayfirst=True)
    df["StockCode"] = df["StockCode"].astype(str)
    return df

st.title("🛒 E-Commerce Dashboard")

st.write("Veri yükleniyor...")

try:
    df = load_data()

    st.success("Veri yüklendi ✅")

    st.subheader("İlk 5 satır")
    st.dataframe(df.head())

    st.write("Satır sayısı:", df.shape[0])
    st.write("Sütun sayısı:", df.shape[1])

except Exception as e:
    st.error(f"Hata oluştu: {e}")

# RFM ANALİZİ
st.subheader("🧠 RFM Analizi")

df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

rfm = df.groupby("CustomerID").agg({
    "InvoiceDate": lambda x: (df["InvoiceDate"].max() - x.max()).days,
    "InvoiceNo": "nunique",
    "TotalPrice": "sum"
})

rfm.columns = ["Recency", "Frequency", "Monetary"]

# RFM SKOR
rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5,4,3,2,1])
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1,2,3,4,5])
rfm["M_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1,2,3,4,5])

rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str)

def segment(row):
    r = int(row["R_Score"])
    f = int(row["F_Score"])

    if r >= 4 and f >= 4:
        return "Champions"
    elif r >= 3 and f >= 4:
        return "Loyal Customers"
    elif r >= 4 and f <= 2:
        return "New Customers"
    elif r <= 2 and f >= 4:
        return "At Risk"
    else:
        return "Hibernating"

rfm["Segment"] = rfm.apply(segment, axis=1)

col1, col2, col3 = st.columns(3)

col1.metric("Toplam Müşteri", rfm.shape[0])
col2.metric("Toplam Gelir", round(rfm["Monetary"].sum(), 2))
col3.metric("Ortalama Sepet", round(rfm["Monetary"].mean(), 2))

st.subheader("🏆 En Değerli Müşteriler")

top_customers = rfm.sort_values("Monetary", ascending=False).head(10)

st.dataframe(top_customers)

st.dataframe(rfm.head())

st.subheader("🎯 Segment Bazlı Filtreleme")

selected_segment = st.selectbox(
    "Segment seç:",
    rfm["Segment"].unique()
)

filtered_data = rfm[rfm["Segment"] == selected_segment]

st.write(f"{selected_segment} segmentindeki müşteriler:")
st.dataframe(filtered_data.head(20))

import matplotlib.pyplot as plt

st.subheader("📈 Frequency vs Monetary")

fig, ax = plt.subplots()

ax.scatter(rfm["Frequency"], rfm["Monetary"])

ax.set_xlabel("Frequency")
ax.set_ylabel("Monetary")

st.pyplot(fig)

# Segment dağılımı
st.subheader("📊 Segment Dağılımı")
segment_counts = rfm["Segment"].value_counts()
st.bar_chart(segment_counts)


st.subheader("🎯 Müşteri Analizi")

# müşteri seç
customer_list = rfm.index.tolist()
selected_customer = st.selectbox("Müşteri ID seç:", customer_list)

if st.button("Analiz Et"):

    customer = rfm.loc[selected_customer]

    st.write("### 📊 Müşteri Bilgileri")
    st.write(customer)

    # 🧠 YORUM KISMI
    st.subheader("🧠 Yorum")

    if customer["Segment"] == "Champions":
        st.success(f"""
Bu müşteri en değerli segmentte yer alıyor çünkü:
- Son alışverişi yakın (Recency: {customer["Recency"]})
- Sık alışveriş yapıyor (Frequency: {customer["Frequency"]})
- Yüksek harcama yapmış (Monetary: {customer["Monetary"]})

➡️ Bu müşteriye özel kampanya yapılmalı ve sadakati korunmalıdır.
""")

    elif customer["Segment"] == "Loyal Customers":
        st.info(f"""
Bu müşteri sadık bir müşteridir:
- Düzenli alışveriş yapmaktadır

➡️ İlişki güçlendirilmelidir.
""")

    elif customer["Segment"] == "New Customers":
        st.info(f"""
Bu müşteri yeni kazanılmıştır:
➡️ Doğru strateji ile sadık müşteriye dönüştürülebilir.
""")

    elif customer["Segment"] == "At Risk":
        st.warning(f"""
Bu müşteri kaybedilmek üzere:
➡️ Yeniden kazanmak için kampanya yapılmalıdır.
""")

    else:
        st.error(f"""
Bu müşteri pasif durumdadır:
➡️ Tekrar kazanmak zor olabilir.
""")

























