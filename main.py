import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# 1. VERİ YÜKLEME (GÜNCELLENDİ)
# ==========================================
print("📂 Veri tabanı yükleniyor...")

# Yüklediğin dosyanın adı 'cars_database.csv' olduğu için burayı güncelledik.
try:
    df_cars = pd.read_csv('cars_database.csv')
    print(f"✅ Başarıyla yüklendi. Toplam Araç Sayısı: {len(df_cars)}")
    
    # Veri setindeki sütunları kontrol edelim (Gerekirse sayısal olmayanları temizlemek için)
    # Price, engine_power, fuel_consumption ve seats sütunlarının sayısal olduğundan emin oluyoruz.
    numeric_cols = ['price', 'engine_power', 'fuel_consumption', 'seats']
    for col in numeric_cols:
        df_cars[col] = pd.to_numeric(df_cars[col], errors='coerce')
        
    # Eksik veri varsa satırı silelim (AI hatasını önlemek için)
    df_cars.dropna(subset=numeric_cols, inplace=True)
    
except FileNotFoundError:
    print("❌ HATA: 'cars_database.csv' dosyası bulunamadı!")
    # Hata durumunda programın çökmemesi için örnek boş bir yapı oluşturabiliriz veya çıkış yapabiliriz.
    exit()

# ==========================================
# 2. YAPAY ZEKA MOTORU (VERİ SETİNE GÖRE UYARLANDI)
# ==========================================
def ai_oneri_yap(user_input, dataset):
    """
    Kullanıcının girdiği özellikleri, yüklenen CSV dosyasındaki araçlarla
    Cosine Similarity kullanarak karşılaştırır.
    """
    # VERİ SETİNDEKİ SÜTUNLARLA EŞLEŞTİRME:
    # engine_cc -> engine_power (HP)
    # fuel_cons -> fuel_consumption
    features = ['price', 'engine_power', 'fuel_consumption', 'seats']
    
    # 1. Veri Hazırlığı
    temp_df = dataset.copy()
    
    # Kullanıcı girdisini bir satır olarak ekle
    # Kullanıcıdan gelen sözlük anahtarlarının yukarıdaki 'features' ile aynı sırada olması önemli
    user_row = pd.DataFrame([[
        user_input['price'],
        user_input['engine_power'],
        user_input['fuel_consumption'],
        user_input['seats']
    ]], columns=features)
    
    temp_df = pd.concat([temp_df, user_row], ignore_index=True)
    
    # 2. Normalizasyon (MinMaxScaler)
    # Verileri 0-1 aralığına çeker (Fiyatın milyonlar olması ile koltuğun 5 olması dengeyi bozmaz)
    scaler = MinMaxScaler()
    normalized_matrix = scaler.fit_transform(temp_df[features])
    
    # 3. Kosinüs Benzerliği Hesaplama
    user_vector = normalized_matrix[-1].reshape(1, -1) # Son satır (Kullanıcı)
    car_vectors = normalized_matrix[:-1]               # Diğer tüm satırlar (Arabalar)
    
    similarity_scores = cosine_similarity(user_vector, car_vectors)
    
    # Skorları ana tabloya ekle
    dataset['similarity_score'] = similarity_scores[0]
    
    # 4. Sıralama (En yüksek puandan en düşüğe)
    recommendations = dataset.sort_values(by='similarity_score', ascending=False)
    
    return recommendations

# ==========================================
# 3. KULLANICI ARAYÜZÜ
# ==========================================
print("\n" + "="*50)
print("🤖 AI DESTEKLİ ARAÇ TAVSİYE SİSTEMİ 🤖")
print("="*50)

try:
    print("Lütfen tercihlerinizi giriniz:")
    
    # Girdileri veri setindeki mantığa göre istiyoruz
    target_price = float(input("Hedef Bütçeniz (TL): "))
    
    # Veri setinde 'engine_power' (Beygir Gücü) olduğu için soruyu buna göre güncelledik
    target_hp = float(input("İstenen Motor Gücü (HP) (örn: 130): ")) 
    
    target_fuel = float(input("İstenen Yakıt Tüketimi (Lt/100km) (örn: 5.5): "))
    target_seats = int(input("Koltuk Sayısı (örn: 5): "))
    
    # AI Fonksiyonuna gidecek sözlük
    user_preferences = {
        'price': target_price, 
        'engine_power': target_hp,  # Veri setindeki sütun adı ile uyumlu
        'fuel_consumption': target_fuel,
        'seats': target_seats
    }
    
    print("\n🔄 Yapay Zeka (Cosine Similarity) veritabanını tarıyor...")
    
    # AI Fonksiyonunu Çağır
    results = ai_oneri_yap(user_preferences, df_cars)
    
    # SONUÇLARI GÖSTER
    print("\n✨ SİZE EN UYGUN ARAÇLAR (Benzerlik Puanına Göre):")
    print("-" * 75)
    
    # Sonuç tablosunda gösterilecek sütunlar (Dosyadaki sütun isimlerine göre)
    display_cols = ['brand', 'model', 'price', 'engine_power', 'fuel_consumption', 'match_percent']
    
    # Benzerlik skorunu yüzdeye çevir
    results['match_percent'] = (results['similarity_score'] * 100).round(2).astype(str) + '%'
    
    # İlk 5 sonucu ekrana bas
    print(results[display_cols].head(5).to_string(index=False))
    
    print("-" * 75)
    best_car = results.iloc[0]
    print(f"🏆 En İyi Eşleşme: {best_car['brand']} {best_car['model']}")
    print(f"   Fiyat: {best_car['price']:,.0f} TL | Uyumluluk: {best_car['match_percent']}")
    # Eğer resim url sütunu varsa onu da yazdıralım (Dosyada 'image_url' var görünüyor)
    if 'image_url' in best_car:
        print(f"   Resim: {best_car['image_url']}")

except Exception as e:
    print(f"\n❌ Bir hata oluştu: {e}")
    print("Lütfen girdiğiniz değerlerin sayı olduğundan emin olun.")