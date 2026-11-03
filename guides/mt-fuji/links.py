"""Links printed in the guide (booking sites and Google Maps navigation).

The booking-site addresses below are NOT yet verified (2026-11-03): this
session cannot open them. Tama checks each one by scanning the QR code in the
Japanese review copy; set verified=True only after that.
"""
from urllib.parse import quote

BOOKING = [
    # (key, English name, Japanese name, what for (en), what for (ja), url, verified)
    ("jre", "JR-EAST Train Reservation", "JR-EAST Train Reservation（英語の予約サイト）",
     "Book the Fuji Excursion in English", "富士回遊を英語で予約",
     "https://www.eki-net.com/en/jreast-train-reservation/", False),
    ("ekinet", "Eki-net (JR East)", "えきねっと（JR東日本）",
     "Book the Fuji Excursion (Japanese)", "富士回遊を予約（日本語）",
     "https://www.eki-net.com/", False),
    ("hwb", "Highway Bus.com", "ハイウェイバスドットコム",
     "Book the highway bus from Busta Shinjuku", "バスタ新宿からの高速バスを予約",
     "https://www.highwaybus.com/", False),
    ("fkrail", "Fujikyu Railway", "富士急行線",
     "Timetables, fares, Mt. FUJI Passport", "時刻表・運賃・富士山・富士五湖パスポート",
     "https://www.fujikyu-railway.jp/", False),
    ("fkbus", "Fujikyu Bus", "富士急バス",
     "Sightseeing buses, timetables, bus passes", "周遊バス・時刻表・乗り放題券",
     "https://www.fujikyubus.co.jp/", False),
    ("fujiq", "Fuji-Q Highland", "富士急ハイランド",
     "Ride passes and the opening calendar", "乗り放題パスと営業カレンダー",
     "https://www.fujiq.jp/", False),
    ("motosuko", "Fuji Motosuko Resort", "富士本栖湖リゾート",
     "Live camera and the Shibazakura Festival", "ライブカメラと富士芝桜まつり",
     "https://www.fujimotosuko-resort.jp/", False),
]

# Google Maps directions from the reader's current location (official Google Maps URL format).
PLACES = [
    # (mark, English name, Japanese name, search text)
    ("", "Kawaguchiko Station", "河口湖駅", "河口湖駅"),
    ("", "Busta Shinjuku (highway buses)", "バスタ新宿（高速バス）", "バスタ新宿"),
    ("①", "Chureito Pagoda", "五重塔（新倉山浅間公園）", "新倉山浅間公園 忠霊塔"),
    ("②", "Oishi Park", "大石公園", "大石公園 河口湖自然生活館"),
    ("③", "Oshino Hakkai", "忍野八海", "忍野八海"),
    ("④", "Mt. Fuji Panoramic Ropeway", "富士山パノラマロープウェイ", "富士山パノラマロープウェイ"),
    ("⑤", "Saiko Iyashi-no-Sato Nenba", "西湖いやしの里根場", "西湖いやしの里根場"),
    ("⑥", "Fuji Subaru Line 5th Station", "富士スバルライン五合目", "富士スバルライン五合目"),
    ("⑦", "Fuji-Q Highland", "富士急ハイランド", "富士急ハイランド"),
    ("⑧", "Lake Motosu viewpoint (Koansō)", "本栖湖（浩庵荘の近く）", "本栖湖 浩庵荘"),
    ("", "Royal Hotel Kawaguchiko (tattoos OK)", "ロイヤルホテル河口湖（タトゥーOK）", "ロイヤルホテル河口湖"),
    ("", "Fuji Choubou no Yu Yurari", "富士眺望の湯 ゆらり", "富士眺望の湯 ゆらり"),
]


def maps_url(query):
    return "https://www.google.com/maps/dir/?api=1&destination=" + quote(query) + "&travelmode=transit"
