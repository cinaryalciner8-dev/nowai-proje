import feedparser
import subprocess

# 1. ADIM: Haberleri İnternetten Çekme
def haberleri_bul():
    # Test için Türkiye'den bir kaynak (AA)
    url = "https://www.aa.com.tr/tr/rss/default?cat=guncel"
    besleme = feedparser.parse(url)
    # En son 1 haberi alalım (Test için)
    son_haber = besleme.entries[0]
    return f"Başlık: {son_haber.title}\nDetay: {son_haber.summary}"

# 2. ADIM: Bilgisayarındaki Yapay Zekaya (Ollama) Sorma
def yapay_zekaya_ozetlet(ham_haber):
    komut = f'ollama run llama3 "Aşağıdaki haberi tarafsız, kısa ve net bir şekilde özetle: {ham_haber}"'
    
    # Bilgisayarındaki Ollama ile konuşuyoruz
    sonuc = subprocess.check_output(komut, shell=True, encoding='utf-8')
    return sonuc

# 3. ADIM: Sistemi Çalıştır
print("Haberler taranıyor...")
ham_veri = haberleri_bul()
print("Yapay zeka analiz ediyor (Bu biraz sürebilir, bilgisayarın çalışıyor)...")
temiz_haber = yapay_zekaya_ozetlet(ham_veri)

print("\n--- İŞTE SON DAKİKA ---")
print(temiz_haber)