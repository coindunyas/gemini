import requests
import time

# --- AYARLAR ---
TELEGRAM_TOKEN = "8681298464:AAF_UNr68LU2mvq4pjzBS5xbL0f7edzgC4M"
CHAT_ID = "1520850915"
BASE_URL = "https://www.trbinance.com/api/v3"

def mesaj_at(metin):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": metin, "parse_mode": "Markdown"})

def analiz_motoru():
    print(f"📊 Verimli Analiz Başladı... {time.strftime('%H:%M:%S')}")
    
    try:
        # Tüm market verisini çek
        market_data = requests.get(f"{BASE_URL}/ticker/24hr").json()
        try_pairs = [d for d in market_data if d['symbol'].endswith('TRY')]
    except: return

    firsatlar = []

    for coin in try_pairs:
        sembol = coin['symbol']
        fiyat = float(coin['lastPrice'])
        degisim = float(coin['priceChangePercent'])
        hacim = float(coin['quoteVolume'])
        yuksek = float(coin['highPrice'])
        dusuk = float(coin['lowPrice'])

        # --- GÜVENLİK FİLTRELERİ ---
        if hacim < 3000000: continue # 3 Milyon TL altı hacmi olanı "güvensiz" kabul et, ele.
        if fiyat == 0: continue

        # --- PUANLAMA SİSTEMİ (En Verimli Tercih İçin) ---
        puan = 0
        
        # Kriter 1: Aşırı Satış (Dip Yakalama)
        if degisim <= -7: puan += 3
        elif degisim <= -4: puan += 1
        
        # Kriter 2: Hacim Gücü (Para Girişi)
        if hacim > 50000000: puan += 3 # 50M+ Hacim çok güçlüdür
        elif hacim > 15000000: puan += 1
        
        # Kriter 3: Günlük Aralık (Volatility)
        # Fiyat günün en düşüğüne ne kadar yakın? (Dibe yakınlık puanı)
        dibe_yakinlik = (fiyat - dusuk) / (yuksek - dusuk + 0.000001)
        if dibe_yakinlik < 0.2: puan += 2 # Günlük dibe %20 yakınsa alım için güvenli bölge

        if puan >= 5: # Sadece 5 ve üzeri puan alan "Kaliteli" fırsatları listele
            firsatlar.append({
                "sembol": sembol,
                "puan": puan,
                "fiyat": fiyat,
                "degisim": degisim,
                "hedef": fiyat * 1.15 # %15-20 arası kar hedefi
            })

    # Fırsatları puana göre diz (En yüksek puanlı başa)
    firsatlar = sorted(firsatlar, key=lambda x: x['puan'], reverse=True)[:3]

    if firsatlar:
        rapor = "🎯 EN VERİMLİ 3 FIRSAT (AI ANALİZ)\n\n"
        for i, f in enumerate(firsatlar, 1):
            rapor += (
                f"{i}. #{f['sembol']} (Skor: {f['puan']}/8)\n"
                f"💰 Fiyat: {f['fiyat']} TL\n"
                f"📈 Değişim: %{f['degisim']}\n"
                f"🚀 Hedef Satış: {f['hedef']:.2f} TL\n"
                f"--------------------------\n"
            )
        rapor += "💡 Strateji: Bakiyeni bu 3 coin arasında paylaştırarak riski dağıtabilirsin."
        mesaj_at(rapor)

if _name_ == "_main_":
    analiz_motoru()
