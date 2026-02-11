import sqlite3
from datetime import datetime

def baglan():
    # Anayasa Madde 11: Modüler ve sağlam yapı
    return sqlite3.connect('saf_haber_merkezi.db')

def anayasal_kurulum():
    conn = baglan()
    cursor = conn.cursor()
    
    # Haber Havuzu - Meta verilerle birlikte
    # Anayasa Madde 5: Çoklu kaynak takibi için
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS haber_havuzu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kaynak_adi TEXT,
            baslik TEXT,
            icerik TEXT,
            kategori TEXT,
            yayin_zamani TEXT,
            islenme_durumu INTEGER DEFAULT 0 -- 0:Ham, 1:İşlendi, 2:Çelişkili/Reddedildi
        )
    ''')
    
    # Anonim Kullanım Kayıtları
    # Anayasa Madde 8: Sadece sistemi geliştirecek anonim veri
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anonim_istatistik (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kategori_tercihi TEXT,
            zaman_damgasi DATETIME,
            dil_tercihi TEXT DEFAULT 'TR'
        )
    ''')

    conn.commit()
    conn.close()

# Sistemi anayasal standartta başlat
anayasal_kurulum()