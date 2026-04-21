import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import streamlit as st
import shap

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class AIEngine:
    def __init__(self, data, random_state=42):
        """
        AI Motorunu başlatır ve modelleri eğitir.
        :param data: pandas DataFrame (cars_database.csv içeriği)
        :param random_state: Sabit sonuçlar için seed değeri (None ise rastgele)
        """
        self.df = data.copy()
        self.random_state = random_state
        
        # 1. ÖNERİ SİSTEMİ (TF-IDF) HAZIRLIĞI
        self.df['features'] = self.df['features'].fillna('')
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf.fit_transform(self.df['features'])
        
        # 2. FİYAT TAHMİNİ (RANDOM FOREST) HAZIRLIĞI & ANALİZİ
        # Eğer random_state varsa sabit, yoksa her seferinde farklı model
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=self.random_state)
        self.regression_metrics = {}
        self.train_price_model()
        
    def train_price_model(self):
        """
        Fiyat tahmin modelini eğitir ve performansını ölçer.
        """
        feature_cols = ['year', 'engine_power', 'fuel_consumption', 'luggage_volume', 'km', 'brand', 'transmission']
        X = self.df[feature_cols].copy()
        y = self.df['price']
        
        # Sayısal değerlerdeki eksikleri 0 ile doldur
        for col in ['year', 'engine_power', 'fuel_consumption', 'luggage_volume', 'km']:
            X[col] = X[col].fillna(0)
            
        # Kategorik verileri doldur
        X['brand'] = X['brand'].fillna('Unknown')
        X['transmission'] = X['transmission'].fillna('Unknown')
            
        # One-Hot Encoding işlemi
        X = pd.get_dummies(X, columns=['brand', 'transmission'], drop_first=False)
        self.model_columns = X.columns # Bunu saklıyoruz ki tahminde aynı sütunları elde edelim
        
        # Veriyi Böl (%80 Eğitim, %20 Test Analizi İçin)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=self.random_state)
        
        # Modeli Eğit
        self.rf_model.fit(X_train, y_train)
        
        # SHAP Explainer oluştur
        self.explainer = shap.TreeExplainer(self.rf_model)
        
        # Test Seti Üzerinde Tahmin Yap
        y_pred = self.rf_model.predict(X_test)
        
        # Metrikleri Hesapla
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        
        # Sonuçları Sakla (Dashboard için)
        self.regression_metrics = {
            'r2': r2,
            'mae': mae,
            'mse': mse,
            'y_test': y_test.tolist(),
            'y_pred': y_pred.tolist()
        }


    def get_similar_cars(self, car_id, top_n=5):
        """
        Seçilen bir araca en benzer diğer araçları bulur (İçerik Bazlı).
        """
        try:
            # Seçilen aracın indeksini bul
            idx = self.df[self.df['car_id'] == car_id].index[0]
            
            # Benzerlik hesapla
            cosine_sim = cosine_similarity(self.tfidf_matrix[idx:idx+1], self.tfidf_matrix).flatten()
            
            # Skorları sırala
            similar_indices = cosine_sim.argsort()[::-1]
            
            # Kendisi hariç en yakınları al
            similar_indices = similar_indices[1:top_n+1]
            
            return self.df.iloc[similar_indices]
        except IndexError:
            return pd.DataFrame()
            
    def predict_fair_price(self, year, hp, consumption, luggage, km, brand, transmission):
        """
        Bir aracın özelliklerine göre 'Adil Piyasa Değeri'ni tahmin eder.
        """
        input_data = pd.DataFrame({
            'year': [year], 
            'engine_power': [hp], 
            'fuel_consumption': [consumption],
            'luggage_volume': [luggage],
            'km': [km],
            'brand': [brand],
            'transmission': [transmission]
        })
        
        input_encoded = pd.get_dummies(input_data, columns=['brand', 'transmission'])
        input_encoded = input_encoded.reindex(columns=self.model_columns, fill_value=0)
        
        predicted_price = self.rf_model.predict(input_encoded)[0]
        return int(predicted_price)

    def explain_price(self, year, hp, consumption, luggage, km, brand, transmission):
        """
        Modelin bir araç için verdiği fiyatın nedenlerini (XAI) döndürür.
        """
        input_data = pd.DataFrame({
            'year': [year], 
            'engine_power': [hp], 
            'fuel_consumption': [consumption],
            'luggage_volume': [luggage],
            'km': [km],
            'brand': [brand],
            'transmission': [transmission]
        })
        
        input_encoded = pd.get_dummies(input_data, columns=['brand', 'transmission'])
        input_encoded = input_encoded.reindex(columns=self.model_columns, fill_value=0)
        
        # SHAP değerlerini hesapla
        shap_values = self.explainer.shap_values(input_encoded)
        base_value = self.explainer.expected_value
        
        if isinstance(base_value, (list, np.ndarray)):
            base_value = base_value[0]
            
        if isinstance(shap_values, list):
             shap_values = shap_values[0]
        
        impacts = []
        for i, col in enumerate(self.model_columns):
            val = shap_values[0][i]
            if abs(val) > 5000:  # 5000 TL'den küçük etkileri yoksay kalabalık yapmasın
                impacts.append({'feature': col, 'impact': float(val)})
                
        # Etki büyüklüğüne göre sırala
        impacts = sorted(impacts, key=lambda x: abs(x['impact']), reverse=True)
        
        return {
            'base_price': float(base_value),
            'impacts': impacts[:3]
        }
