import streamlit as st
import feedparser
from groq import Groq
import urllib.parse
import re
from datetime import datetime
import socket

# --- 1. SİSTEM AYARLARI (NOWAI v1.0 BETA) ---
st.set_page_config(layout="wide", page_title="NowAI v1.0 Beta", page_icon="🔴")
socket.setdefaulttimeout(15)

# --- API BAĞLANTISI ---
try:
    client = Groq(api_key="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")
except Exception as e:
    st.error(f"Sistem Hatası: {str(e)}")
    st.stop()

# --- 2. TASARIM KODLARI (HİZALAMA VE GÖRÜNÜM) ---
st.markdown("""
<style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"], header { display: none !important; }
    .stApp { background-color: #0e1117; color: #c9d1d9; font-family: 'Georgia', serif; }
    
    /* Sağ Üst Menü */
    .top-nav {
        position: absolute; top: 30px; right: 40px;
        display: flex; gap: 15px; z-index: 100;
    }
    .nav-item {
        border: 1px solid #30363d; color: #8b949e;
        padding: 6px 16px; border-radius: 6px;
        font-size: 0.75rem; background: rgba(22, 27, 34, 0.8);
        font-family: 'Arial', sans-serif; cursor: pointer;
    }
    
    /* Logo ve Canlı Işık */
    .brand-section {
        margin-top: 20px; padding-bottom: 25px;
        border-bottom: 1px solid #30363d; margin-bottom: 40px;
    }
    .logo-row { display: flex; align-items: center; gap: 20px; }
    .live-dot {
        width: 22px; height: 22px; background-color: #e63946;
        border-radius: 50%; box-shadow: 0 0 15px #e63946;
        animation: pulse 1.5s infinite; margin-top: 5px;
    }
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.3; transform: scale(1.1); }
        100% { opacity: 1; transform: scale(1); }
    }
    .main-title { font-size: 4.5rem; font-weight: 900; margin: 0; color: #f0f6fc; letter-spacing: -2px; font-family: 'Arial Black', sans-serif; }
    .slogan-box { font-size: 1.1rem; color: #8b949e; font-style: italic; margin-top: 5px; font-family: 'Georgia', serif; }
    
    /* Makale Alanı */
    .article-box {
        background: #161b22; border: 1px solid #30363d; 
        padding: 40px; border-radius: 8px; margin-bottom: 50px;
    }
    .article-header { color: #e63946; font-weight: bold; font-size: 1.1rem; margin-bottom: 20px; text-transform: uppercase; }
    .article-content { color: #e6edf3; line-height: 1.9; font-size: 1.15rem; white-space: pre-line; }

    /* HİZALAMA ÇÖZÜMÜ */
    .stButton button {
        height: 42px; 
        font-weight: bold;
        background-color: #e63946; 
        color: white; 
        border-radius: 6px; 
        border: none;
        width: 100%;
        margin-top: 2px;
    }
    div[data-testid="stForm"] { border: none; padding: 0; }
</style>

<div class="top-nav">
    <div class="nav-item">AYARLAR</div>
    <div class="nav-item">KAYIT OL</div>
</div>
""", unsafe_allow_html=True)

# --- 3. LOGO ALANI ---
st.markdown("""
    <div class="brand-section">
        <div class="logo-row">
            <div class="live-dot"></div>
            <h1 class="main-title">NowAI</h1>
        </div>
        <div class="slogan-box">"Bilgi herkesindir, ama kişisel deneyim bir tercihtir."</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. KONTROL MASASI ---
with st.form("control_panel", border=False):
    c1, c2, c3 = st.columns([1.5, 2.5, 1], gap="medium")
    with c1:
        kanal = st.selectbox("Gündem Tercihi", ["Gündem", "Ekonomi", "Dünya", "Teknoloji", "Spor"])
    with c2:
        arama = st.text_input("Özel Odak Noktası", placeholder="Konuyu yazın ve Enter'a basın...")
    with c3:
        st.markdown('<p style="margin-bottom:8px; height:24px;"></p>', unsafe_allow_html=True)
        calistir = st.form_submit_button("GÜNDEMİ DEĞERLENDİR")

# --- 5. VERİ VE ANALİZ MOTORU ---
@st.cache_data(ttl=300, show_spinner=False)
def verileri_topla(kategori, sorgu):
    hedef = sorgu if sorgu else kategori
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(hedef)}&hl=tr&gl=TR&ceid=TR:tr"
    veriler = []
    try:
        f = feedparser.parse(url)
        for e in f.entries[:10]:
            tarih = datetime.now().strftime("%H:%M")
            if hasattr(e, 'published_parsed') and e.published_parsed:
                tarih = datetime(*e.published_parsed[:6]).strftime("%H:%M")
            veriler.append({
                "baslik": e.title.split(" - ")[0],
                "ozet": re.sub(r'<[^>]+>', '', e.get('summary', ''))[:180] + "...",
                "link": e.link, "tarih": tarih,
                "kaynak": e.get('source', {}).get('title', 'AJANS').upper()
            })
    except: pass
    return veriler

# --- 6. YAYIN EKRANI (DÜZELTİLMİŞ ANALİZ) ---
if calistir:
    with st.spinner('Veri akışı sağlanıyor...'):
        haberler = verileri_topla(kanal, arama)
    
    if haberler:
        st.success("✓ Güncel Haber Akışı Başarıyla Tamamlandı")
        
        try:
            # GÜVENLİ VE TEMİZ TÜRKÇE PROMPT
            prompt = f"""
            GÖREV: Sen tarafsız ve profesyonel bir haber analistisin. 
            Aşağıdaki haber başlıklarını sentezleyerek objektif, bilgi odaklı bir durum raporu yaz.
            
            KURALLAR:
            1. KESİNLİKLE siyasi yorum yapma, taraf tutma veya spekülasyona girme. Sadece gerçekleri analiz et.
            2. DİL: Sadece kusursuz, resmi ve akıcı bir Türkçe kullan. Asla yabancı kelime veya bozuk karakter (Çince vb.) kullanma.
            3. FORMAT: Liste yapma. Birbirini takip eden akıcı paragraflar (en az 4 paragraf) şeklinde yaz.
            4. İÇERİK: Olayların ne olduğunu ve toplumsal/ekonomik yansımalarını nesnel bir dille anlat.
            
            KONU: {arama if arama else kanal}
            HABERLER: {[h['baslik'] for h in haberler]}
            """
            
            # Temperature'ı düşürdük (0.3) -> Daha tutarlı ve hatasız çıktı için
            makale = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile", 
                temperature=0.3 
            ).choices[0].message.content
        except: makale = "Analiz şu an gerçekleştirilemedi."
        
        st.markdown(f"""
            <div class="article-box">
                <div class="article-header">📊 STRATEJİK DURUM RAPORU</div>
                <div class="article-content">{makale}</div>
            </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, h in enumerate(haberler):
            with cols[i % 3]:
                st.markdown(f"""
                    <div class="news-card" style="background-color: #161b22; border: 1px solid #30363d; padding: 25px; border-radius: 8px; margin-bottom: 20px; height: 350px; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <div style="color:#e63946; font-size:0.75rem; font-weight:bold; margin-bottom:10px;">{h['kaynak']} • {h['tarih']}</div>
                            <div style="font-weight:bold; font-size:1.1rem; line-height:1.4; color:white; margin-bottom:12px;">{h['baslik']}</div>
                            <div style="color:#8b949e; font-size:0.9rem; line-height:1.5;">{h['ozet']}</div>
                        </div>
                        <a href="{h['link']}" target="_blank" style="color:#e63946; text-decoration:none; font-weight:bold; margin-top:15px; display:inline-block;">KAYNAĞA GİT &rarr;</a>
                    </div>
                """, unsafe_allow_html=True)
