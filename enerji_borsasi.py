import streamlit as st
import pandas as pd
import numpy as np

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Sakarya P2P Borsası", layout="wide")

# 2. GİRİŞ PANELİ (SOL MENÜ)
st.sidebar.title("👤 Kullanıcı Girişi")
rol = st.sidebar.selectbox("Rolünüzü Seçiniz:", ["Genel Dashboard", "Fatih (Üretici)", "Kaan (Tüketici)"])

# 3. TASARIM RAPORU VERİLERİ (SABİTLER)
kurulu_guc = 100  # 100 kWp GES
tuketim_tepe = 55 # 55 kW Toplam Aktif Yük
sebeke_fiyat = 2.40 # TL/kWh (Örnek Şebeke Tarifesi)
p2p_fiyat = 1.80    # TL/kWh (Kooperatif İçi Avantajlı Fiyat)

# 4. VERİ SİMÜLASYONU (SAKARYA HAZİRAN AYI VERİLERİ)
saatler = np.arange(0, 24, 1)
# Güneş üretimi çan eğrisi (100 kWp bazlı)
uretim = kurulu_guc * np.maximum(0, np.sin((saatler - 6) * np.pi / 12)) * 0.8 
# Tüketim eğrisi (Akşam pik yapan 55 kW'lık profil)
tuketim = np.array([30,25,22,20,20,25,35,40,45,40,35,30,30,35,40,45,50,55,55,50,45,40,35,30])

df = pd.DataFrame({
    'Saat': saatler,
    'GES Üretimi (kW)': uretim,
    'Hane Tüketimi (kW)': tuketim
})
df['Fark'] = df['GES Üretimi (kW)'] - df['Hane Tüketimi (kW)']

# --- 5. PANEL GÖRÜNÜMLERİ ---

# A) GENEL DASHBOARD
if rol == "Genel Dashboard":
    st.title("⚡ Sakarya Enerji Kooperatifi Genel Durumu")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Kurulu Güç", f"{kurulu_guc} kWp", "Sakarya Merkez")
    with col2:
        st.metric("Anlık Toplam Yük", f"{tuketim_tepe} kW", "7 Üye Toplamı")
    with col3:
        st.metric("Geri Ödeme Süresi", "5.11 Yıl", "ROI Analizi")

    st.subheader("📊 Günlük Enerji Dengesi (Duck Curve)")
    st.line_chart(df.set_index('Saat')[['GES Üretimi (kW)', 'Hane Tüketimi (kW)']])

# B) ÜRETİCİ PANELİ (FATİH)
elif rol == "Fatih (Üretici)":
    st.title("🏢 Üretici İzleme Paneli")
    st.info("Bu panelde GES üretim verimliliği ve satış gelirleri takip edilir.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Günlük Toplam Üretim", f"{uretim.sum():.1f} kWh")
    with col2:
        gelir = (df[df['Fark'] > 0]['Fark'].sum() * p2p_fiyat)
        st.metric("P2P Satış Geliri", f"{gelir:,.2f} TL")

    st.subheader("📈 Saatlik GES Üretim Grafiği")
    st.area_chart(df.set_index('Saat')['GES Üretimi (kW)'])

# C) TÜKETİCİ PANELİ (KAAN)
else:
    st.title("🏠 Tüketici Kontrol Paneli")
    st.subheader("🚗 Elektrikli Araç (EV) Akıllı Şarj")
    
    acil_durum = st.toggle("🚨 Uçak Yolculuğu / Acil Şarj Modu")
    
    if acil_durum:
        st.error("⚠️ ACİL MOD: Araç fiyata bakılmaksızın tam kapasite şarj ediliyor.")
        st.write(f"Enerji Kaynağı: **Şebeke Takviyeli** | Birim: **{sebeke_fiyat} TL**")
    else:
        st.success("✅ EKONOMİK MOD: P2P ucuz enerji saatleri bekleniyor.")
        st.write(f"Enerji Kaynağı: **Kooperatif İçi** | Birim: **{p2p_fiyat} TL**")

    st.subheader("📉 Bireysel Tüketim Analizi")
    st.bar_chart(df.set_index('Saat')['Hane Tüketimi (kW)'])
