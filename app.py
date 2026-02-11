import streamlit as st
import feedparser
from groq import Groq
import urllib.parse
import time
import socket
import re
from datetime import datetime

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(layout="wide", page_title="NowAI Terminal", page_icon="🔴")
socket.setdefaulttimeout(15)

# --- API BAĞLANTISI ---
try:
    client = Groq(api_key="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")
except Exception as e:
    st.error(f"API Hatası: {str(e)}")
    st.stop()

# --- 2. TASARIM (SABİTLENMİŞ ÜST MENÜ & HİZALI LOGO) ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    header[data-testid="stHeader"] { display: none; }
    .stAppDeployButton { display: none; }
    
    /* SAĞ ÜST MENÜ - SAYFANIN BAŞINA SABİTLENDİ (AŞAĞI GELMEZ) */
    .top-nav {
        position: absolute; /* Absolute sayesinde sayfa kayınca yukarıda kalır */
        top: 25px;
        right: 30px;
        display: flex;
        gap: 12px;
        z-index: 10;
    }
    
    .nav-item {
        border: 1px solid #30363d;
        color: #8b949e;
        padding: 5px 12px;
        border-radius: 4px;
        font-size: 0.72rem;
        background: rgba(22, 27, 34, 0.6);
        font-family: 'Segoe UI', sans-serif;
        cursor: not-allowed;
    }
    
    .brand-container {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        border-bottom: 1px solid #30363d;
        padding-bottom: 25px;
        margin-bottom: 30px;
        margin-top: 10px;
    }
    
    .logo-row {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .live-dot {
        width: 16px;
        height: 16px;
        background-color: #e63946;
        border-radius: 50%;
        box-shadow: 0 0 12px #e63946;
        animation: pulse 2s infinite;
        flex-shrink: 0;
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.1;
        color: white;
    }
    
    .slogan-box {
        margin-left: 31px;
        font-size: 0.95rem;
        color: #8b949e;
        font-style: italic;
        margin-top: 5px;
    }
    
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.1); }
        100% { opacity: 1; transform: scale(1); }
    }

    .news-card { 
        background-color: #161b22; border: 1px solid #30363d; 
        padding: 15px; border-radius: 6px; margin-bottom: 15px; 
        height: 100%; transition: 0.2s;
    }
    .news-card:hover { border-color: #e63946; background: #1c2128; }
    
    .stSpinner > div > div + div { display: none !important; }
</style>

<div class="top-nav">
    <div class="nav-item">AYARLAR (Yakında)</div>
    <div class="nav-item">KAYIT OL (Yakında)</div>
</div>
""", unsafe_allow_html=True)

# --- 3. KAYNAKLAR ---
KAYNAKLAR = {
    "Gündem": "https://www.trthaber.com/gundem_articles.rss",
    "Ekonomi": "https://www.bloomberght.com/rss",
    "Dünya": "https://www.aa.com.tr/tr/rss/default?cat=dunya",
    "Teknoloji": "https://www.donanimhaber.com/rss/tum/",
    "Spor": "https://www.ntvspor.net/rss"
}

# --- 4. VERİ MOTORU ---
@st.cache_data(ttl=300, show_spinner=False)
def verileri_cek(kategori, arama):
    veriler = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    sorgu = arama if arama else kategori
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(sorgu)}&hl=tr&gl=TR&ceid=TR:tr"
    
    try:
        f = feedparser.parse(url, request_headers=headers)
        for e in f.entries[:15]:
            if any(x in e.title.lower() for x in [" the ", " of "]): continue
            tarih = datetime.now().strftime("%H:%M")
            if hasattr(e, 'published_parsed') and e.published_parsed:
                tarih = datetime(*e.published_parsed[:6]).strftime("%H:%M")
            veriler.append({
                "baslik": e.title, "link": e.link, "zaman": tarih,
                "kaynak": e.get('source', {}).get('title', 'HABER AKIŞI').upper(),
                "ozet": re.sub(r'<[^>]+>', '', e.get('summary', e.title))[:120] + "..."
            })
    except: pass
    return veriler

# --- 5. AI ANALİZ ---
def ai_raporla(haber_listesi, konu):
    prompt = f"GÖREV: Aşağıdaki haberleri kapsamlı bir 'STRATEJİK DURUM RAPORU' olarak %100 Türkçe analiz et: {haber_listesi}"
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        return completion.choices[0].message.content
    except: return "Analiz oluşturulamadı."

# --- 6. ARAYÜZ ---
with st.sidebar:
    st.markdown("<h4 style='color:#e63946; border-bottom:1px solid #30363d; padding-bottom:10px;'>YAYIN AKIŞI</h4>", unsafe_allow_html=True)
    kanal = st.selectbox("Kategori", list(KAYNAKLAR.keys()))
    arama = st.text_input("Konu Ara (Opsiyonel)")
    st.markdown("<br>", unsafe_allow_html=True)
    calistir = st.button("ANALİZİ BAŞLAT", type="primary", use_container_width=True)
    st.markdown("<div style='text-align:center; color:#586069; margin-top:20px; font-size:0.75rem;'>NowAI v1.0 Beta</div>", unsafe_allow_html=True)

# --- 7. ANA EKRAN ---
st.markdown("""
    <div class="brand-container">
        <div class="logo-row">
            <div class="live-dot"></div>
            <h1 class="main-title">NowAI</h1>
        </div>
        <div class="slogan-box">"Bilgi herkesindir, ama kişisel deneyim bir tercihtir."</div>
    </div>
""", unsafe_allow_html=True)

if calistir:
    hedef = arama if arama else kanal
    with st.spinner(''):
        data = verileri_cek(kanal, arama)
    
    if data:
        st.success("Yayın Akışı Başarıyla Güncellendi ✅")
        
        ozet_input = "\n".join([f"- {h['baslik']}" for h in data])
        analiz = ai_raporla(ozet_input, hedef)
        
        st.markdown(f"""
            <div style="background:#0d1117; border: 1px solid #30363d; border-left:4px solid #2ea043; padding:25px; border-radius:6px; margin-bottom:30px;">
                <h3 style="color:#2ea043; margin-top:0; font-size:1.1rem;">STRATEJİK DURUM RAPORU</h3>
                <div style="color:#c9d1d9; margin-top:15px; line-height:1.7; font-size:1rem; white-space: pre-line;">
                    {analiz}
                </div>
            </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        for i, h in enumerate(data):
            with cols[i % 3]:
                st.markdown(f"""
                    <div class="news-card">
                        <div style="font-size:0.7rem; color:#8b949e; margin-bottom:8px; display:flex; justify-content:space-between;">
                            <span style="color:#e63946; font-weight:bold;">{h['kaynak']}</span>
                            <span>{h['zaman']}</span>
                        </div>
                        <div style="font-weight:700; font-size:0.95rem; line-height:1.35; margin-bottom:8px; color:#f0f6fc;">
                            {h['baslik']}
                        </div>
                        <a href="{h['link']}" target="_blank" style="color:#58a6ff; text-decoration:none; font-weight:bold; font-size:0.75rem; float:right;">İNCELE ➔</a>
                        <div style="clear:both;"></div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.error("Veri alınamadı. Lütfen tekrar deneyin.")

elif not calistir:
    st.info("Terminal hazır. Analizi başlatın.")