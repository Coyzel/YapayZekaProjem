import streamlit as st
import pandas as pd
import os
import random


# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="AI Car Recommender",
    page_icon="🚗",
    layout="wide"
)

# --- CSS EKLENTİSİ (AESTHETICS) ---
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .car-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    .car-title {
        color: #2c3e50;
        font-size: 20px;
        font-weight: bold;
    }
    .car-price {
        color: #27ae60;
        font-size: 18px;
        font-weight: bold;
    }
    .metric-label {
        font-size: 12px;
        color: #7f8c8d;
    }
    .metric-value {
        font-size: 14px;
        font-weight: bold;
        color: #2c3e50;
    }
    
    /* KARŞILAŞTIRMA KART STİLLERİ (Görsel Bazlı) */
    .comp-card {
        background-color: #1a1c24;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 20px;
        color: white;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .comp-model {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 5px;
        color: #ffffff;
        min-height: 50px; /* Hizalama için */
    }
    .comp-price {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2ecc71; /* Yeşil Fiyat */
        margin-bottom: 0px;
    }
    .comp-year {
        font-size: 0.8rem;
        color: #888;
        margin-bottom: 15px;
    }
    .comp-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #333;
        font-size: 0.9rem;
    }
    .comp-row:last-child {
        border-bottom: none;
    }
    .comp-label {
        color: #ccc;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .comp-val {
        font-weight: bold;
        color: white;
    }
    /* EN İYİ ÖZELLİK VURGUSU (Yeşil Kutu + Tik) */
    .comp-best {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .bottom-info {
        font-size: 0.7rem;
        color: #666;
        margin-top: 15px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. VERİ YÜKLEME ---
@st.cache_data
def load_data():
    # Dosya yolunu scriptin olduğu klasöre göre belirle
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'cars_database.csv')
    
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error(f"Veritabanı dosyası bulunamadı: {file_path}")
        return pd.DataFrame()

from ai_engine import AIEngine # AI Motoru

# ... (Mevcut kodlar)

df = load_data()

# --- AI MOTORUNU BAŞLAT ---
# --- AI MOTORUNU BAŞLAT ---
# CACHE_RESOURCE: Modelin her reload'da tekrar tekrar eğitilmesini engeller.
@st.cache_resource
def load_ai_engine(data):
    if not data.empty:
        return AIEngine(data)
    return None

ai_engine = load_ai_engine(df)

# --- 2. YAN MENÜ (INPUTLAR) ---
with st.sidebar:
    st.subheader("📌 Navigasyon")
    sayfa = st.radio("Sayfa Seçimi", ["🏠 Ana Sayfa", "⚖️ Karşılaştırma", "🤖 Model Analizi (AI Metrics)"])
    st.markdown("---")

    if sayfa == "🏠 Ana Sayfa":
        st.header("🔍 Kriterlerinizi Belirleyin")
        
        # FORM BAŞLANGICI: Sayfanın her seçimde yenilenmesini engeller
        with st.form("arama_formu"):
            # Bütçe
            butce = st.slider("💰 Maksimum Bütçe (TL)", min_value=500000, max_value=5000000, value=2000000, step=50000)
            
            # Marka
            markalar = ["Fark etmez"] + sorted(df['brand'].unique().tolist())
            secilen_marka = st.selectbox("🚗 Tercih Edilen Marka", markalar)
            
            # Kasa Tipi
            kasalar = ["Fark etmez"] + sorted(df['body_type'].unique().tolist())
            secilen_kasa = st.selectbox("📐 Kasa Tipi", kasalar)
            
            # Aile Boyutu
            aile_boyu = st.number_input("👨‍👩‍👧‍👦 Aile Boyutu", min_value=1, max_value=7, value=1)
            
            # Vites Tipi (Manuel/Otomatik)
            vitesler = ["Fark etmez", "Automatic", "Manual"]
            secilen_vites = st.selectbox("🕹️ Vites Tipi", vitesler)
            
            # Araç Durumu (Sıfır / 2. El)
            durum = st.radio("Araç Durumu:", ["Fark etmez", "Sıfır (2024-2025)", "İkinci El (2018-2023)"])
            
            st.markdown("---")
            st.subheader("🎯 Sizin İçin Ne Önemli?")
            oncelik = st.radio(
                "Sıralama Kriteri:",
                ("Fiyat Odaklı (En Ucuz)", "Performans Odaklı (Güçlü Motor)", "Marka Tutkusu (Sadece Seçilen)", "Dengeli (Akıllı Öneri)"),
                index=3 # Varsayılan: Dengeli
            )
            
            # --- YENİ FİLTRELER (PHASE 3) ---
            st.markdown("---")
            st.subheader("🛠️ Donanım Özellikleri")
            
            all_features = set()
            if not df.empty and 'features' in df.columns:
                for f_str in df['features'].dropna():
                    for f in f_str.split(', '):
                        # Vites bilgisini özellik listesinden çıkar (Zaten filtresi var)
                        if f.strip() not in ["Manuel Vites", "Otomatik Vites"]:
                            all_features.add(f.strip())
            
            secilen_ozellikler = st.multiselect("Olmazsa Olmazlar:", sorted(list(all_features)))
            
            # FORM GÖNDERME BUTONU
            if st.form_submit_button("🔍 ARABA BUL", type="primary"):
                st.session_state.search_performed = True
                # Arama yapıldığında "re-run" için bir flag koyuyoruz ki aşağıda kodu çalıştırsın
                st.session_state.do_search = True
            
    # Karşılaştırma Sayfası Seçimi İçin Sidebar Güncellemesi
    if sayfa == "🏠 Ana Sayfa":
        pass # Zaten yukarıda hallettik
    


# --- 3. LOGLAMA FONKSİYONU ---
def log_feedback(car_model, liked):
    log_file = 'logs.csv'
    timestamp = pd.Timestamp.now()
    new_entry = {'timestamp': timestamp, 'car_model': car_model, 'liked': liked}
    
    if os.path.exists(log_file):
        log_df = pd.read_csv(log_file)
        log_df = pd.concat([log_df, pd.DataFrame([new_entry])], ignore_index=True)
    else:
        log_df = pd.DataFrame([new_entry])
    
    log_df.to_csv(log_file, index=False)
    st.toast(f"Geri bildiriminiz alındı: {'Beğendiniz' if liked else 'İlgilenmediniz'}")

# --- 4. AKILLI ALGORİTMA ---
def calculate_score(row, priority, max_price, user_brand, user_body, selected_features=[]):
    
    # KISIM 1: GENEL KALİTE PUANI (BASE SCORE) - Maksimum 50 Puan
    # Kullanıcı hiçbir şey seçmese bile arabanın "iyi" olup olmadığını belirler.
    
    # A. Fiyat Puanı (Max 20 Puan): Bütçeye göre ne kadar ucuz?
    # Bütçenin %50'si kadarsa tam puan, %100'ü ise 0 puan gibi lineer olmayan bir yaklaşım yerine:
    # Daha basit: (1 - fiyat/bütçe) * 40 diyelim ama bütçe sınırında 0 olur.
    # Kullanıcı genelde bütçesinin tamamını kullanmaya okeydir.
    # O yüzden: (1 - fiyat / (max_price * 1.2)) * 30
    price_ratio = row['price'] / max_price if max_price > 0 else 1
    base_price_score = max(0, (1 - price_ratio) * 30) # Max 30 puan (Çok ucuzsa)
    
    # B. Yıl Puanı (Max 15 Puan): Ne kadar yeni?
    # 2015 ve öncesi 0, 2025 -> 15
    y_score = max(0, min(15, (row['year'] - 2015) * 1.5))
    
    # C. Performans (Max 5 Puan)
    p_score = min(5, (row['engine_power'] / 200) * 5)
    
    base_total = base_price_score + y_score + p_score
    # Base puan genelde 25-45 arası çıkar.
    
    
    # KISIM 2: UYUMLULUK PUANI (MATCH SCORE) - Maksimum 50 Puan
    # Kullanıcının özel isteklerine ne kadar uyuyor?
    
    match_total = 0
    
    # Marka Tercihi (25 Puan)
    if user_brand != "Fark etmez":
        if row['brand'] == user_brand:
            match_total += 25
    # Kasa Tercihi (25 Puan)
    if user_body != "Fark etmez":
        if row['body_type'] == user_body:
            match_total += 25
            
    # Öncelik Modifikasyonu
    if priority == "Fiyat Odaklı (En Ucuz)":
        base_price_score *= 1.5 # Fiyat puanını artır
    elif priority == "Performans Odaklı (Güçlü Motor)":
        p_score *= 3 # Performans etkisini artır
        
    
    # KISIM 3: BONUSLAR
    bonus = 0
    # Özellik Bonusu
    if selected_features:
        feature_count = 0
        row_features = str(row.get('features', '')).lower()
        for f in selected_features:
            if f.lower() in row_features:
                feature_count += 1
        
        # Her eşleşen özellik için +8 puan (Bayağı etkili olsun)
        bonus += (feature_count * 8)


    # TOPLAM HESAPLAMA
    final_score = base_total + match_total + bonus
    
    # "Hiçbir şey seçilmedi" durumunda (Match=0), Base puan devrede (Max ~50).
    # Seçim yapıldıkça 90-100'e çıkar.
    
    # Random Jitter (Sıralama çok statik olmasın)
    # Eğer kullanıcı hiçbir özel seçim yapmadıysa ("Fark etmez" modu), varyasyonu artır ki puanlar hep aynı (35) gözükmesin.
    if match_total == 0 and bonus == 0:
        jitter = random.uniform(-5, 8) # %35 yerine %30-%43 arası gezinsin
    else:
        jitter = random.uniform(-1, 2) # Normal modda küçük oynamalar yeterli
        
    final_score += jitter
    
    return min(100, max(10, final_score)) # Min 10, Max 100

# --- 5. TCO HESAPLAMA (5 YILLIK) ---
def calculate_tco(price, fuel_consumption):
    # Varsayımlar
    km_per_year = 15000
    years = 5
    fuel_price = 42 # Ortalama yakıt fiyatı
    
    total_fuel_cost = (fuel_consumption / 100) * km_per_year * years * fuel_price
    tco = price + total_fuel_cost
    return tco

# --- 6. ANA EKRAN VE SONUÇLAR ---

if sayfa == "🏠 Ana Sayfa":
    st.header("🚗 Size En Uygun Araçlar")

    # Karşılaştırma Listesi (Session State)
    if 'compare_list' not in st.session_state:
        st.session_state.compare_list = []

    if 'search_results_df' not in st.session_state:
        st.session_state.search_results_df = None

    # Butona basıldıysa VEYA zaten hafızada bir sonuç varsa
    if st.session_state.get('search_performed', False):
        
        # YENİ ARAMA MI YAPILACAK?
        # (Butona basıldıysa 'do_search' True olur, sonuçları güncelleriz)
        if st.session_state.get('do_search', False):
             # 1. Filtreleme (Hard Filter)
            filtered_df = df.copy()
            
            # Bütçe Filtresi (+%10 esneme)
            filtered_df = filtered_df[filtered_df['price'] <= butce * 1.1]
            # ... diğer filtreler sidebar değişkenlerinden geliyor
            filtered_df = filtered_df[filtered_df['seats'] >= aile_boyu]
            if secilen_vites != "Fark etmez":
                filtered_df = filtered_df[filtered_df['transmission'] == secilen_vites]
            if durum == "Sıfır (2024-2025)":
                filtered_df = filtered_df[filtered_df['year'] >= 2024]
            elif durum == "İkinci El (2018-2023)":
                filtered_df = filtered_df[filtered_df['year'] < 2024]
            # Özellik Filtresi
            if secilen_ozellikler:
                for ozellik in secilen_ozellikler:
                    filtered_df = filtered_df[filtered_df['features'].astype(str).str.contains(ozellik, na=False)]
            
            # Puanlama
            if not filtered_df.empty:
                filtered_df['score'] = filtered_df.apply(
                    lambda x: calculate_score(x, oncelik, butce * 1.1, secilen_marka, secilen_kasa, secilen_ozellikler), 
                    axis=1
                )
                filtered_df = filtered_df.sort_values(by='score', ascending=False)
            
            st.session_state.search_results_df = filtered_df
            st.session_state.do_search = False # Aramayı tamamladık, flag'i indir.

        # GÖSTERİM: Hafızadaki 'search_results_df' kullanılır
        # Böylece sayfa yenilenince (buton tıklamalarında) sonuçlar değişmez/sıfırlanmaz.
        
        current_results = st.session_state.search_results_df
        
        if current_results is None or current_results.empty:
            st.warning(f"❌ Kriterlerinize uygun ({butce} TL altı) araç bulunamadı.")
        else:
            results = current_results # Artık sonuçları buradan alıyoruz
        
            # Sonuçları state'den alıyoruz, sıralama zaten yapılmıştı ama emin olmak için bir daha yapabiliriz.
            
            # Sonuç Gösterim Fonksiyonu
            def display_car_card(row):
                with st.container():
                    st.markdown(f'<div class="car-card">', unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns([1, 2, 1])
                    
                    with c1:

                        # GÖRSEL GÖSTERİMİ (Basitleştirilmiş - Performans İçin)
                        img_url = str(row.get('image_url', '')).strip()
                        
                        # PLACEHOLDER MODU (Kullanıcı İsteği: Resimler Yüklenmiyor)
                        # if img_url.lower().startswith('http'):
                        #     st.image(img_url, use_container_width=True)
                        # else:
                        safe_brand = str(row['brand']).replace(' ', '+')
                        safe_model = str(row['model']).replace(' ', '+')
                        fallback_url = f"https://placehold.co/600x400/EEE/31343C?font=montserrat&text={safe_brand}+{safe_model}"
                        st.image(fallback_url, use_container_width=True)
                            
                    with c2:
                        # Durum Rozeti (Yeni / İkinci El)
                        condition_badge = "🆕 SIFIR" if row['year'] >= 2024 else "İKİNCİ EL"
                        condition_color = "green" if row['year'] >= 2024 else "orange"
                        st.markdown(f'<span style="background-color:{condition_color}; color:white; padding:2px 6px; border-radius:4px; font-size:12px;">{condition_badge}</span>', unsafe_allow_html=True)
                        
                        # Model isminden parantez içlerini temizle
                        clean_model = str(row['model']).split('(')[0].strip()
                        st.markdown(f'<div class="car-title">{row["brand"]} {clean_model}</div>', unsafe_allow_html=True)
                        
                        # Detay Bilgisi (Yıl - KM? - Vites - Kasa)
                        km_info = ""
                        if row['year'] < 2024:
                            km_info = f" | 🛣️ {row['km']:,} KM"
                            
                        st.write(f"**Yıl:** {row['year']} {km_info} | **Kasa:** {row['body_type']} | **Vites:** {row['transmission']}")
                        
                        # Özellik Rozetleri
                        st.info(f"⛽ {row['fuel_consumption']}L/100km  |  🧳 {row['luggage_volume']}L Bagaj  |  🐎 {row['engine_power']} HP")
                        
                        # PHASE 3: Donanım Listesi (Hepsi)
                        if pd.notna(row.get('features')):
                             feats = str(row['features']).replace(',', ' •') # Daha şık ayraç
                             st.caption("✨ " + feats)
                        

                    
                    with c3:
                        st.markdown(f'<div class="car-price">{row["price"]:,.0f} TL</div>', unsafe_allow_html=True)
                        st.progress(int(row['score']), text=f"Uyumluluk: %{int(row['score'])}")
                        
                        # Compare Checkbox Logic (REVERTED TO CHECKBOX)
                        is_in_list = any(x['car_id'] == row['car_id'] for x in st.session_state.compare_list)
                        
                        # Checkbox state'i session'a bağlama
                        # 'value' parametresi session state'den gelir, değişim callback ile yönetilebilir veya basitçe if bloğu ile.
                        # Ancak checkbox state'i unique key ile yönetilmeli.
                        
                        is_compared = st.checkbox("Karşılaştır", key=f"cmp_{row['car_id']}", value=is_in_list)
                        
                        if is_compared:
                            if not is_in_list:
                                st.session_state.compare_list.append(row.to_dict())
                                st.toast(f"✅ {row['brand']} {row['model']} karşılaştırma listesine eklendi!", icon="⚖️")
                                # Checkbox değiştiğinde, eğer kullanıcı hemen başka sayfaya giderse state güncellenmeli.
                                # Rerun yapmaya gerek yok, checkbox state'i tutuyor ama listeyi güncelledik.
                        else:
                            if is_in_list:
                                st.session_state.compare_list = [x for x in st.session_state.compare_list if x['car_id'] != row['car_id']]
                                st.toast(f"❌ {row['brand']} {row['model']} karşılaştırma listesinden çıkarıldı.", icon="🗑️")

                        


                        
                        # PHASE 3: AI Fiyat Analizi
                        if ai_engine:
                            try:
                                km_val = row.get('km', 0) if pd.notna(row.get('km')) else 0
                                brand_val = row.get('brand', 'Unknown')
                                trans_val = row.get('transmission', 'Unknown')
                                
                                fair_price = ai_engine.predict_fair_price(row['year'], row['engine_power'], row['fuel_consumption'], row['luggage_volume'], km_val, brand_val, trans_val)
                                diff = row['price'] - fair_price
                                if diff < -50000:
                                    st.success(f"🔥 Fırsat! (Adil: {fair_price:,.0f})")
                                elif diff > 50000:
                                    st.warning(f"Pahalı (Adil: {fair_price:,.0f})")
                                else:
                                    st.info(f"Makul (Adil: {fair_price:,.0f})")
                                    
                                # SHAP XAI - Neden Bu Fiyat?
                                with st.expander("🤖 Neden Bu Fiyat? (Kısa Analiz)"):
                                    explanation = ai_engine.explain_price(row['year'], row['engine_power'], row['fuel_consumption'], row['luggage_volume'], km_val, brand_val, trans_val)
                                    st.caption("Fiyatı en çok etkileyen 3 neden:")
                                    for imp in explanation['impacts']:
                                        feat_name = imp['feature'].replace('engine_power', 'Motor Gücü')\
                                                                  .replace('year', 'Model Yılı')\
                                                                  .replace('fuel_consumption', 'Yakıt Tüketimi')\
                                                                  .replace('luggage_volume', 'Bagaj Hacmi')\
                                                                  .replace('km', 'Kilometre')\
                                                                  .replace('brand_', 'Marka (').replace('transmission_', 'Vites (')
                                        if 'Marka (' in feat_name or 'Vites (' in feat_name:
                                            feat_name += ')'
                                            
                                        if imp['impact'] > 0:
                                            text = f"🟢 <b>{feat_name}</b> faktörü piyasa değerini olumlu yönde etkiliyor."
                                            color = "#2ecc71"
                                        else:
                                            text = f"🔴 <b>{feat_name}</b> faktörü piyasa değerini olumsuz yönde etkileyip düşürüyor."
                                            color = "#e74c3c"
                                        
                                        st.markdown(f"<div style='color:{color}; font-size:0.85em; margin-bottom:4px;'>{text}</div>", unsafe_allow_html=True)
                            except Exception as e:
                                pass
                                
                        # PHASE 3: Fiyat Geçmişi Butonu
                        with st.expander("📈 Fiyat Geçmişi"):
                             if pd.notna(row.get('price_history')):
                                 try:
                                     hist_data = [float(x) for x in str(row['price_history']).split(';')]
                                     st.line_chart(hist_data)
                                 except:
                                     st.text("Veri yok")
                        
                        # Feedback
                        col_fb1, col_fb2 = st.columns(2)
                        with col_fb1:
                            if st.button("👍", key=f"like_{row['car_id']}"):
                                log_feedback(f"{row['brand']} {row['model']}", True)
                        with col_fb2:
                            if st.button("👎", key=f"dislike_{row['car_id']}"):
                                log_feedback(f"{row['brand']} {row['model']}", False)
                                
                    st.markdown('</div>', unsafe_allow_html=True)

            # GÖSTERİM MANTIĞI VE GRUPLAMA
            
            # 1. Durum: Kullanıcı hem Marka hem de Kasa seçmişse (En Katı Filtre)
            if secilen_marka != "Fark etmez" and secilen_kasa != "Fark etmez":
                 # Tam Eşleşenler: Marka + Kasa
                 main_recommendations = results[
                     (results['brand'] == secilen_marka) & 
                     (results['body_type'] == secilen_kasa)
                 ].head(5)
                 
                 # Alternatifler: Diğer her şey
                 # (Aynı marka farklı kasa OLABİLİR veya farklı marka aynı kasa OLABİLİR)
                 # Ana önerilerde olmayanları alalım
                 main_ids = main_recommendations['car_id'].tolist()
                 alternative_recommendations = results[~results['car_id'].isin(main_ids)].head(10)
                 
                 header_text = f"🎯 Tam Eşleşenler: {secilen_marka} {secilen_kasa}"
                 
            # 2. Durum: Sadece Marka seçilmişse
            elif secilen_marka != "Fark etmez":
                main_recommendations = results[results['brand'] == secilen_marka].head(5)
                alternative_recommendations = results[results['brand'] != secilen_marka].head(10)
                header_text = f"🎯 Marka Tercihiniz: {secilen_marka}"
                
            # 3. Durum: Sadece Kasa seçilmişse (Marka Fark etmez)
            elif secilen_kasa != "Fark etmez":
                 main_recommendations = results[results['body_type'] == secilen_kasa].head(5)
                 alternative_recommendations = results[results['body_type'] != secilen_kasa].head(10)
                 header_text = f"🎯 Kasa Tercihiniz: {secilen_kasa}"
                 
            # 4. Durum: Hiçbir şey seçilmemiş (Fark etmez - Fark etmez)
            else:
                # Eğer kullanıcı "Durum: Fark etmez" dediyse hem SIFIR hem İKİNCİ EL önerelim
                if durum == "Fark etmez":
                    new_cars = results[results['year'] >= 2024].head(5)
                    used_cars = results[results['year'] < 2024].head(5)
                    # Önce sıfırlar, sonra temiz ikinci eller
                    main_recommendations = pd.concat([new_cars, used_cars])
                else:
                    # Kullanıcı zaten "Sıfır" veya "İkinci El" seçmişse sıralamaya dokunma
                    main_recommendations = results.head(10)
                
                alternative_recommendations = pd.DataFrame() 
                header_text = "✨ En İyi Öneriler (Karma Liste)"

            # --- SONUÇLARI EKRAÑA BAS ---
            
            # Ana Bölüm
            if not main_recommendations.empty:
                st.subheader(header_text)
                for _, row in main_recommendations.iterrows():
                    display_car_card(row)
            else:
                 st.warning(f"⚠️ Kriterlerinize (Bütçe/Kişi Sayısı dahil) tam uyan araç bulunamadı: {header_text}")

            # Alternatif Bölüm
            if not alternative_recommendations.empty:
                st.subheader("✨ Güçlü Alternatifler / Benzer Seçenekler")
                for _, row in alternative_recommendations.iterrows():
                    display_car_card(row)

    else:
        st.info("👈 Yan menüden kriterlerinizi seçip 'ARABA BUL' butonuna basın.")


# --- YENİ KARŞILAŞTIRMA SAYFASI ---
elif sayfa == "⚖️ Karşılaştırma":
    st.header("⚖️ Araç Karşılaştırma")
    
    if 'compare_list' in st.session_state and st.session_state.compare_list:
        comp_df = pd.DataFrame(st.session_state.compare_list)
        st.info(f"Şu an {len(comp_df)} araç karşılaştırılıyor.")
        
        if not comp_df.empty:
            # --- KART VE IZGARA GÖRÜNÜMÜ ---
            
            # Karşılaştırılacak araç sayısı kadar sütun oluştur
            cols = st.columns(len(comp_df))
            
            # En iyi değerleri bul (Highlight için)
            best_values = {}
            if len(comp_df) > 1:
                try:
                    best_values['price'] = comp_df['price'].min()
                    best_values['fuel_consumption'] = comp_df['fuel_consumption'].min()
                    best_values['year'] = comp_df['year'].max()
                    best_values['engine_power'] = comp_df['engine_power'].max()
                    best_values['luggage_volume'] = comp_df['luggage_volume'].max()
                except:
                     pass

            # HER BİR ARAÇ İÇİN SÜTUN
            for idx, col in enumerate(cols):
                row = comp_df.iloc[idx]
                with col:
                    # 1. KART KUTUSU (Native Streamlit Container)
                    # height=None kullanarak native container'a bırakıyoruz, içerik hizalamasını spacer ile yapacağız.
                    with st.container(border=True):
                        
                        # 2. RESİM
                        safe_brand = str(row['brand']).replace(' ', '+')
                        safe_model = str(row['model']).replace(' ', '+')
                        
                        # PLACEHOLDER MODU
                        img_src = f"https://placehold.co/600x350/EEE/31343C?font=montserrat&text={safe_brand}+{safe_model}"
                        
                        # img_src = str(row.get('image_url', '')).strip()
                        # if not img_src.lower().startswith('http'):
                        #      img_src = f"https://placehold.co/600x350/EEE/31343C?font=montserrat&text={safe_brand}+{safe_model}"

                        # Resim için sabit yükseklik
                        st.markdown(f"""
                        <div style="height:200px; overflow:hidden; display:flex; align-items:center; justify-content:center; background:#eee; border-radius:8px; margin-bottom:10px;">
                            <img src="{img_src}" style="width:100%; height:auto;">
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 3. BAŞLIK VE DURUM
                        # Model isminden parantez içlerini temizle (Örn: "Egea (Manuel)" -> "Egea")
                        raw_model = str(row['model'])
                        clean_model = raw_model.split('(')[0].strip()
                        
                        condition_text = "🆕 SIFIR" if row['year'] >= 2024 else "İKİNCİ EL"
                        condition_style = "color: #2ecc71; font-weight:bold;" if row['year'] >= 2024 else "color: #f39c12; font-weight:bold;"

                        # Başlık Alanı
                        st.markdown(f"""
                        <div style='min-height: 80px;'>
                            <h3 style='margin-bottom:5px;'>{row['brand']} {clean_model}</h3>
                            <div style='font-size: 0.8rem; {condition_style}'>{condition_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        km_text = f"  |  🛣️ {row.get('km', '0'):,} KM" if row['year'] < 2024 else ""
                        
                        # FİYAT
                        st.markdown(f"<h2 style='color:#27ae60; margin:0; font-size:1.6rem;'>{row['price']:,.0f} TL</h2>", unsafe_allow_html=True)
                        
                        # YIL ve KM (Alt Alta, Açık Renk)
                        st.markdown(f"""
                        <div style='color:#eee; font-size:0.95rem; margin-top:4px; font-weight:500;'>
                            Yıl: {row['year']} <span style="opacity:0.8; font-size:0.9em;">{km_text}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        st.divider()

                        # 4. ÖZELLİK SATIRLARI
                        # Helper function for badges
                        def get_badge(val, metric):
                            is_best = False
                            if len(comp_df) > 1 and metric in best_values:
                                 if metric in ['price', 'fuel_consumption']:
                                     is_best = (val <= best_values[metric]) # Min is best
                                 else:
                                     is_best = (val >= best_values[metric]) # Max is best
                            
                            if is_best:
                                return f"<span style='background-color:#d4edda; color:#155724; padding:3px 8px; border-radius:4px; font-weight:bold;'>{val} ✅</span>"
                            else:
                                return f"<span style='color:#666;'>{val}</span>"

                        # Özellikleri Yazdır - Min-height ile hizalama
                        feature_html = f"""
                        <div style='min-height:180px;'>
                            <div style='display:flex; justify-content:space-between; margin-bottom:8px;'>
                                <strong>🐎 Motor:</strong> {get_badge(row['engine_power'], 'engine_power')} HP
                            </div>
                            <div style='display:flex; justify-content:space-between; margin-bottom:8px;'>
                                <strong>⛽ Yakıt:</strong> {get_badge(row['fuel_consumption'], 'fuel_consumption')} Lt
                            </div>
                            <div style='display:flex; justify-content:space-between; margin-bottom:8px;'>
                                <strong>🧳 Bagaj:</strong> {get_badge(row['luggage_volume'], 'luggage_volume')} Lt
                            </div>
                            <div style='display:flex; justify-content:space-between; margin-bottom:8px;'>
                                <strong>🕹️ Vites:</strong> {row['transmission']}
                            </div>
                            <div style='display:flex; justify-content:space-between; margin-bottom:8px;'>
                                <strong>📐 Kasa:</strong> {row['body_type']}
                            </div>
                            <div style='magin-top:10px; border-top:1px solid #444; padding-top:8px;'>
                                <div style='font-weight:bold; margin-bottom:4px; color:#ccc;'>🛠️ Donanım:</div>
                                <div style='font-size: 0.9em; color: #fff; line-height: 1.5; max-height: 200px; overflow-y: auto; padding-right: 5px; font-weight:500;'>
                                    {str(row.get('features', '')).replace(',', ' • ')}
                                </div>
                            </div>
                        </div>
                        """
                        
                        st.markdown(feature_html, unsafe_allow_html=True)
                        
                        # Boşluk Ekle
                        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                        
                        # Model Puanı
                        if 'score' in row:
                             st.progress(int(row['score']), text=f"Uyumluluk Oranı: %{int(row['score'])}")
                             st.caption("ℹ️ *Bu puan bütçe, yıl ve önceliğinize göre hesaplanır.*")
            
            st.divider()
            # Temizleme Butonu
            if st.button("🗑️ Karşılaştırma Listesini Temizle", type="primary"):
                st.session_state.compare_list = []
                st.rerun()
    else:
        st.info("Henüz karşılaştırma listesine araç eklemediniz.")



elif sayfa == "🤖 Model Analizi (AI Metrics)":
    st.header("🤖 Fiyat Tahmin Modeli Performansı")

    # Her seferinde YENİ model eğit (Cache kullanma)
    with st.spinner("Yapay Zeka Modeli verilerle yeniden eğitiliyor..."):
        # Cache'li 'ai_engine' yerine burada taze instance oluşturuyoruz (random_state=None -> Dinamik)
        dynamic_ai = AIEngine(df, random_state=None)
        metrics = dynamic_ai.regression_metrics
    
    # Metrikleri Göster
    col1, col2 = st.columns(2)
    with col1:
        st.metric("R² Skoru (Doğruluk)", f"%{metrics['r2']*100:.1f}")
    with col2:
        st.metric("Ortalama Sapma (MAE)", f"{metrics['mae']:,.0f} TL")

    # Detaylı Grafik (Çizgi Grafik - Gerçek vs Tahmin)
    st.subheader("📈 Gerçek Fiyat vs Tahmin Edilen Fiyat")
    
    # Veriyi Hazırla
    chart_df = pd.DataFrame({
        'Index': range(len(metrics['y_test'])),
        'Gerçek Fiyat': metrics['y_test'],
        'Tahmin Edilen': metrics['y_pred']
    })
    
    # Altair için 'Melt' (Uzun Format) yapıyoruz ki renkleri lejantta göstersin
    chart_melted = chart_df.melt('Index', var_name='Veri Tipi', value_name='Fiyat')
    
    import altair as alt
    
    # Çizgi Grafik
    # Gerçek Fiyat: Mavi, Tahmin: Kırmızı
    line_chart = alt.Chart(chart_melted).mark_line().encode(
        x=alt.X('Index', title='Test Edilen Araçlar (Rastgele Seçilen)'),
        y=alt.Y('Fiyat', title='Fiyat (TL)'),
        color=alt.Color('Veri Tipi', scale=alt.Scale(domain=['Gerçek Fiyat', 'Tahmin Edilen'], range=['#3498db', '#e74c3c'])),
        tooltip=['Index', 'Veri Tipi', 'Fiyat']
    ).interactive()
    
    st.altair_chart(line_chart, use_container_width=True)

    st.divider()

    # 2. Dağılım Grafiği (Scatter) - Correlation
    st.subheader("🎯 Tahmin Doğruluğu (Dağılım)")
    st.write("Her bir nokta bir aracı temsil eder. Çizgi üzerindeki noktalar tam isabetli tahminlerdir.")
    
    chart_scatter_df = pd.DataFrame({
        'Gerçek Fiyat': metrics['y_test'],
        'Tahmin Edilen': metrics['y_pred']
    })
    
    scatter = alt.Chart(chart_scatter_df).mark_circle(size=60, color='#e74c3c', opacity=0.7).encode(
        x=alt.X('Gerçek Fiyat', title='Gerçek Piyasa Fiyatı (TL)'),
        y=alt.Y('Tahmin Edilen', title='AI Tahmini (TL)'),
        tooltip=['Gerçek Fiyat', 'Tahmin Edilen']
    ).interactive()
    
    # İdeal Çizgisi (y=x)
    max_val = max(max(metrics['y_test']), max(metrics['y_pred']))
    line = alt.Chart(pd.DataFrame({'x': [0, max_val], 'y': [0, max_val]})).mark_line(color='#27ae60', strokeDash=[5,5]).encode(
        x='x',
        y='y'
    )
    
    st.altair_chart(scatter + line, use_container_width=True)
    
    st.markdown("""
    <div style="padding:15px; border:1px solid #ddd; border-radius:10px; border-left:5px solid #27ae60;">
        <h4 style="margin:0; color:#2c3e50;">💡 Metrikler Ne Anlama Geliyor?</h4>
        <ul style="margin-top:5px; color:#555;">
            <li><strong>R² Skoru:</strong> Modelin başarısıdır. %100 mükemmel eştir.</li>
            <li><strong>MAE (Sapma):</strong> Fiyat tahmininde ortalama ne kadar yanıldığıdır.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 Örneklem: Test Araçları Analiz Tablosu")
    st.write("Aşağıdaki tablo, yapay zekanın daha önce test amacıyla ayırdığı araç fiyatlarını ne kadar başarıyla tahmin ettiğini liste halinde gösterir.")
    
    # Veri Çerçevesi Oluştur
    table_df = pd.DataFrame({
        'Gerçek Fiyat': metrics['y_test'],
        'Tahmini Fiyat': metrics['y_pred']
    })
    
    # Hata Payını Hesapla
    table_df['Sapma Miktarı'] = table_df['Tahmini Fiyat'] - table_df['Gerçek Fiyat']
    
    sample_table = table_df.head(15).copy()
    
    # Rakamları noktalı formata çevirelim (Türkiye standardı)
    sample_table['Gerçek Fiyat'] = sample_table['Gerçek Fiyat'].apply(lambda x: f"{int(x):,} ₺".replace(",", "."))
    sample_table['Tahmini Fiyat'] = sample_table['Tahmini Fiyat'].apply(lambda x: f"{int(x):,} ₺".replace(",", "."))
    
    # Streamlit'in kendi modern DataFrame yapısı ile 
    # görselleştirmeyi (Progress Bar/İlerleme Çubuğu) kullanarak şekillendiriyoruz.
    st.dataframe(
        sample_table,
        column_config={
            "Gerçek Fiyat": st.column_config.TextColumn(
                "Gerçek Piyasa Fiyatı",
                help="Aracın gerçek ilan fiyatı"
            ),
            "Tahmini Fiyat": st.column_config.TextColumn(
                "Yapay Zeka (AI) Tahmini",
                help="Modelimizin tahmin ettiği fiyat"
            ),
            "Sapma Miktarı": st.column_config.ProgressColumn(
                "Hata Miktarı / Sapma",
                help="Tahmin ile gerçek arasındaki TL farkı",
                format="%d",
                min_value=int(sample_table['Sapma Miktarı'].min()) - 10000,
                max_value=int(sample_table['Sapma Miktarı'].max()) + 10000,
            ),
        },
        use_container_width=True,
        hide_index=False
    )
