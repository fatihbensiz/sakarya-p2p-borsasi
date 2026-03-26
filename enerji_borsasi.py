import streamlit as st
import pandas as pd
import numpy as np

# 1. BAŞLIK VE AYARLAR
st.set_page_config(page_title="Sakarya P2P Borsası", layout="wide")
st.title("⚡ Sakarya Enerji Kooperatifi P2P Platformu")
st.sidebar.header("⚙️ Senaryo Ayarları")

# 2. TASARIM RAPORUNDAKİ VERİLER
kurulu_guc = 100  # 100 kWp GES [cite: 2120]
toplam_tuketim_tepe = 55  # 55 kW Toplam Aktif Yük [cite: 2141]

# 3. VERİ ÜRETİCİ (Haziran ayı Sakarya verileri baz alınmıştır)
saatler = np.arange(0, 24, 1)
# Güneş üretimi çan eğrisi
uretim = kurulu_guc * np.maximum(0, np.sin((saatler - 6) * np.pi / 12)) * 0.8 
# Tüketim eğrisi (Akşam pikli)
tuketim = np.array([30,25,22,20,20,25,35,40,45,40,35,30,30,35,40,45,50,55,55,50,45,40,35,30])

df = pd.DataFrame({
    'Saat': saatler,
    'GES Üretimi (kW)': uretim,
    'Hane Tüketimi (kW)': tuketim
})

# 4. BORSA MANTIĞI
df['Fark'] = df['GES Üretimi (kW)'] - df['Hane Tüketimi (kW)']
df['Durum'] = df['Fark'].apply(lambda x: "P2P Satış" if x > 0 else "Şebekeden Alım")

# 5. ARAYÜZ TASARIMI (Dashboard)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Anlık Üretim", f"{df['GES Üretimi (kW)'].max():.1f} kW", "Haziran Zirve")
with col2:
    st.metric("Toplam Tüketim", f"{toplam_tuketim_tepe} kW", "Tepe Yük")
with col3:
    st.metric("P2P Potansiyeli", f"{df[df['Fark'] > 0]['Fark'].sum():.1f} kWh", "Günlük")

# Duck Curve Görseli 
st.subheader("📊 Günlük Enerji Dengesi (Duck Curve Analizi)")
st.line_chart(df.set_index('Saat')[['GES Üretimi (kW)', 'Hane Tüketimi (kW)']])

st.subheader("📋 Anlık Takas Kayıtları")
st.dataframe(df)
import streamlit as st
import pandas as pd
import numpy as np

# 1. SAYFA AYARLARI VE GİRİŞ PANELİ
st.set_page_config(page_title="Sakarya P2P Borsası", layout="wide")
st.sidebar.title("👤 Kullanıcı Girişi")
rol = st.sidebar.selectbox("Rolünüzü Seçiniz:", ["Fatih (Üretici)", "Kaan (Tüketici)"])

# 2. SABİT VERİLER (Tasarım Raporu Bazlı)
kurulu_guc = 100  # 100 kWp GES [cite: 2120]
tuketim_tepe = 55 # kW [cite: 2141]
sebeke_fiyat = 2.40 # TL/kWh (Örnek)
p2p_fiyat = 1.80    # TL/kWh (Örnek)

# 3. VERİ SİMÜLASYONU
saatler = np.arange(0, 24, 1)
uretim = kurulu_guc * np.maximum(0, np.sin((saatler - 6) * np.pi / 12)) * 0.8
tuketim = np.array([30,25,22,20,20,25,35,40,45,40,35,30,30,35,40,45,50,55,55,50,45,40,35,30])

# --- ÜRETİCİ PANELİ (FATİH) ---
if rol == "Fatih (Üretici)":
    st.header("🏢 Üretici İzleme Paneli")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Anlık Üretim", f"{uretim[12]:.1f} kW", "Zirve Saat")
    with col2:
        gelir = (uretim.sum() * p2p_fiyat)
        st.metric("Tahmini Günlük Gelir", f"{gelir:,.0f} TL")
    
    st.subheader("📊 Santral Performans Verileri")
    st.line_chart(uretim)

# --- TÜKETİCİ PANELİ (KAAN) ---
else:
    st.header("🏠 Tüketici Kontrol Paneli")
    st.subheader("🚗 Elektrikli Araç (EV) Yönetimi")
    
    acil_durum = st.toggle("🚨 Uçak Yolculuğu / Acil Şarj Modu")
    
    if acil_durum:
        st.error("⚠️ ACİL MOD AKTİF: Araç fiyata bakılmaksızın tam kapasite şarj ediliyor.")
        st.info(f"Şu anki Birim Maliyet: {sebeke_fiyat} TL (Şebeke Takviyeli)")
    else:
        st.success("✅ EKONOMİK MOD: Araç şarjı için P2P ucuz enerji saatleri bekleniyor.")
        st.info(f"Beklenen Birim Maliyet: {p2p_fiyat} TL (Kooperatif İçi)")

    st.subheader("📉 Kişisel Tasarruf Grafiğiniz")
    st.bar_chart(tuketim)
    