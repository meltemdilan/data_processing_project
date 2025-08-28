# Lifeway Motosiklet Kaskı - Sensör Veri Analizi Projesi

Bu proje, Türkiye'nin ilk akıllı motosiklet kaskı olan Lifeway'in prototipi için geliştirilmiş sensör verisi işleme ve anomali tespiti yazılımını içerir. Projenin temel amacı, kasktan gelen sensör verilerini (sıcaklık, titreşim, hareket vb.) gerçek zamanlı olarak analiz ederek potansiyel tehlikeleri ve anormal durumları otomatik olarak tespit etmektir.

## Proje Amacı ve Özellikleri

* **Zaman Serisi Veri İşleme:** Sensörlerden gelen ham zaman serisi verilerini işler ve analiz eder.
* **Anomali Tespiti:** Z-Skor metodunu kullanarak verideki beklenmedik ve anormal değerleri (örneğin, kaza veya ani bir darbe) tespit eder.
* **Veri Görselleştirme:** İşlenmiş veriyi ve tespit edilen anomalileri görselleştirmek için grafikler oluşturur.
* **Çoklu İş Parçacığı (Multi-threading):** Veri okuma ve veri işleme görevlerini paralel olarak yürüterek performansı artırır.

## Kurulum

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları takip edin.

### 1. Gereksinimler
Bu projenin çalışması için aşağıdaki Python kütüphanelerine ihtiyacınız vardır.
```bash
pip install -r requirements.txt
