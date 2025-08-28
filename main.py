import pandas as pd
import configparser
import matplotlib.pyplot as plt
from data_processor import DataProcessor
import os
import numpy as np

def load_config(filename='config.ini'):
    """
    Yapılandırma dosyasını yükler ve döndürür.
    """
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def save_results_to_csv(df, filename):
    """
    İşlenmiş verileri bir CSV dosyasına kaydeder.
    """
    if not df.empty:
        df.to_csv(filename, index=False)
        print(f"\nİşlenmiş veriler '{filename}' dosyasına kaydedildi.")
    else:
        print("\nUyarı: İşlenecek veri bulunamadığından CSV dosyası oluşturulamadı.")

def plot_data(df, filename):
    """
    İşlenmiş verileri ve anomalileri grafik üzerinde görselleştirir.
    """
    # Hata kontrolü: DataFrame boşsa veya 'value' sütunu yoksa fonksiyonu durdur.
    if df.empty or 'value' not in df.columns or 'smoothed_value' not in df.columns:
        print("\nUyarı: Grafik çizmek için yeterli veri bulunamadı veya veri formatı hatalı.")
        return

    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(15, 7))

    # Orijinal veriyi çiz
    plt.plot(df.index, df['value'], label='Orijinal Veri', color='skyblue', alpha=0.7)
    
    # Hareketli ortalama çizgisini çiz
    plt.plot(df.index, df['smoothed_value'], label='Hareketli Ortalama', color='coral', linewidth=2)
    
    # Anomalileri işaretle
    anomalies = df[df['is_anomaly']]
    if not anomalies.empty:
        plt.scatter(anomalies.index, anomalies['value'], color='red', s=100, zorder=5, label='Anomali', edgecolors='black')
    
    plt.title('Zaman Serisi Veri Analizi ve Anomali Tespiti', fontsize=16)
    plt.xlabel('Veri Noktası', fontsize=12)
    plt.ylabel('Değer', fontsize=12)
    plt.legend()
    
    # Grafiği dosyaya kaydet
    plt.savefig(filename, dpi=300)
    print(f"Grafik '{filename}' olarak kaydedildi.")
    # Ekranda göster
    plt.show()

if __name__ == "__main__":
    # 1. Config dosyasını yükle
    config = load_config()

    # 2. Örnek veri dosyası oluştur (Gerçek sensör gelene kadar)
    input_file_path = config['DATA_SOURCES']['input_file']
    if not os.path.exists(input_file_path):
        print("Örnek veri dosyası oluşturuluyor...")
        sample_data = pd.DataFrame({
            'timestamp': pd.date_range(start='2025-01-01', periods=200, freq='s'),
            'value': pd.Series(np.random.randn(200)).rolling(window=5).mean() * 10 + 50
        })
        # Rastgele anomaliler ekle
        sample_data.loc[50, 'value'] = 250
        sample_data.loc[120, 'value'] = 10
        
        sample_data.to_csv(input_file_path, index=False)
        print("Örnek veri dosyası başarıyla oluşturuldu.")
        
    # 3. Veri işleme hattını başlat
    processor = DataProcessor(config)
    processed_df = processor.start_processing_pipeline()

    # 4. Sonuçları CSV'ye kaydet
    save_results_to_csv(processed_df, config['DATA_SOURCES']['output_file'])
    
    # 5. Grafiği çiz ve kaydet
    plot_data(processed_df, config['PLOTTING']['plot_file'])