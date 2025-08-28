import pandas as pd
import numpy as np
import threading
import queue
import time
import os

class DataProcessor:
    """
    Bu sınıf, sensör verilerini okuma, işleme ve anomali tespiti gibi 
    görevleri yerine getiren ana mantığı içerir.

    İşleyiş:
    - Bir thread sensörden veya dosyadan veriyi okur ve bir kuyruğa (queue) ekler.
    - Başka bir thread kuyruktaki veriyi alır, temizler ve işler.
    - İşlenen veriler, anomali tespiti yapıldıktan sonra bir sonuç kuyruğuna gönderilir.
    - Bu sayede veri okuma ve işleme işlemleri birbirini beklemeden paralel çalışır.
    """

    def __init__(self, config):
        self.config = config
        self.window_size = config.getint('ANOMALY_DETECTION', 'window_size')
        self.z_score_threshold = config.getfloat('ANOMALY_DETECTION', 'z_score_threshold')
        self.input_file = config.get('DATA_SOURCES', 'input_file')
        self.data_buffer = []

    def _read_data_from_source(self, data_queue):
        """
        Veri okuma thread'i. Sensörden veya örnek CSV dosyasından verileri okur
        ve işleme kuyruğuna ekler.
        """
        print(f"'{self.input_file}' dosyasından veri okunuyor...")
        if not os.path.exists(self.input_file):
            print(f"Hata: {self.input_file} dosyası bulunamadı.")
            data_queue.put(None)
            return

        try:
            df = pd.read_csv(self.input_file)
            for _, row in df.iterrows():
                data_queue.put(row.to_dict())
                time.sleep(0.01)
            print("Veri okuma tamamlandı.")
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")
        finally:
            data_queue.put(None)

    def _process_data(self, data_queue, processed_queue):
        """
        Veri işleme thread'i. Kuyruktan gelen veriyi işler, yumuşatma ve
        anomali tespiti yapar.
        """
        while True:
            data_point = data_queue.get()
            if data_point is None:
                # Veri okuma bittiyse bu thread de sonlansın
                break
            
            # Veri temizleme adımı: 'value' anahtarının varlığını kontrol et
            if 'value' not in data_point or pd.isna(data_point['value']):
                continue

            # Tampona ekle
            self.data_buffer.append(data_point)
            
            # Tampon dolduğunda en eski veriyi çıkar
            if len(self.data_buffer) > self.window_size:
                self.data_buffer.pop(0)

            # İşleme sadece yeterli veri varsa başla
            if len(self.data_buffer) >= 2:
                df_buffer = pd.DataFrame(self.data_buffer)
                
                df_buffer['smoothed_value'] = df_buffer['value'].rolling(window=self.window_size, min_periods=1).mean()
                
                last_point = df_buffer.iloc[-1].copy()
                
                # Z-skor hesaplaması için tüm pencereyi kullan
                mean = df_buffer['smoothed_value'].mean()
                std_dev = df_buffer['smoothed_value'].std()
                
                if std_dev > 0:
                    last_point['z_score'] = (last_point['smoothed_value'] - mean) / std_dev
                    last_point['is_anomaly'] = np.abs(last_point['z_score']) > self.z_score_threshold
                else:
                    last_point['z_score'] = 0.0
                    last_point['is_anomaly'] = False
                
                processed_queue.put(last_point.to_dict())

        processed_queue.put(None)

    def start_processing_pipeline(self):
        data_queue = queue.Queue()
        processed_queue = queue.Queue()
        
        reader_thread = threading.Thread(target=self._read_data_from_source, args=(data_queue,))
        processor_thread = threading.Thread(target=self._process_data, args=(data_queue, processed_queue))
        
        reader_thread.start()
        processor_thread.start()
        
        results = []
        while True:
            result_data = processed_queue.get()
            if result_data is None:
                break
            
            results.append(result_data)
            
            if result_data.get('is_anomaly'):
                print(f"Anomali Tespit Edildi: Değer={result_data['value']:.2f}, Z-Skor={result_data['z_score']:.2f}")

        reader_thread.join()
        processor_thread.join()
        
        return pd.DataFrame(results)