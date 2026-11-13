import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-3.8-flash"

# (bölüm adı, arama sorgusu, dil, ülke, ceid)
SORGULAR = [
    ("Türkiye", "Borsa İstanbul BIST 100", "tr", "TR", "TR:tr"),
    ("Türkiye", "dolar TL altın faiz piyasalar", "tr", "TR", "TR:tr"),
    ("Dünya", "Wall Street stocks markets", "en", "US", "US:en"),
    ("Dünya", "global markets Fed ECB oil", "en", "US", "US:en"),
]


def haberler(q, hl, gl, ceid, n=8):
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": q + " when:1d", "hl": hl, "gl": gl, "ceid": ceid}
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    sonuc = []
    for item in root.iter("item"):
        sonuc.append("- " + (item.findtext("title") or ""))
        if len(sonuc) >= n:
            break
    return sonuc


def gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": KEY},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.load(r)
    return d["candidates"][0]["content"]["parts"][0]["text"]


def main():
    bolumler = {}
    for bolum, q, hl, gl, ceid in SORGULAR:
        try:
            bolumler.setdefault(bolum, []).extend(haberler(q, hl, gl, ceid))
        except Exception as e:
            print("Haber çekilemedi:", q, e)

    ham = ""
    for bolum, liste in bolumler.items():
        ham += f"\n## {bolum} haber başlıkları\n" + "\n".join(liste) + "\n"

    bugun = datetime.now().strftime("%d.%m.%Y")
    prompt = f"""Sen bir finans haber özetleyicisisin. Tarih: {bugun}.
Aşağıda son 24 saate ait haber başlıkları var. Bunlara dayanarak Türkçe,
sade ve kısa bir günlük piyasa özeti yaz.

Format:
1. Türkiye Piyasaları (3-5 madde)
2. Dünya Piyasaları (3-5 madde)
3. Bugün Dikkat Edilecekler (2-3 madde)

Kurallar:
- Sadece verilen başlıklardaki bilgileri kullan.
- Başlıklarda olmayan rakam, endeks seviyesi veya oran UYDURMA.
- Emin olmadığın bir şeyi yazma.
- Yatırım tavsiyesi verme.
- En sonda şu cümleyi ekle: Bu özet otomatik üretilmiştir, yatırım tavsiyesi değildir.

{ham}"""

    ozet = gemini(prompt)
    with open("ozet.md", "w", encoding="utf-8") as f:
        f.write(ozet)
    print(ozet)


main()
