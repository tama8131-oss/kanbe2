"""Course-finder flow chart (diagnosis chart) for the start of each language section.

Start -> Q1 (live camera) -> Q2 (what you want most) -> Q3 / Q4 -> one of 5 results.
Every result only points to content that is already checked in the book
(Chapter 4 courses, Chapter 3 places 6 and 8).
"""
import photos as ph

# results: key -> (label, title, short description, where in the book)
CHART = {
    "ja": dict(
        lead="上から質問に答えて、矢印をたどってください。あなたに合う1日がわかります。",
        q1="前の晩、ライブカメラ（第1章）を見ると…", q1a="富士山が見えそう", q1b="雲・雨っぽい",
        q2="いちばんしたいのは…", q2a="有名な写真を撮る", q2c="のんびり景色とごはん", q2b="特別な富士山を見る",
        q3="新宿7:30発の富士回遊に…", q3a="乗れる", q3b="朝は苦手",
        q4="バス停から片道約1時間歩くのは…", q4a="平気", q4b="歩きたくない",
        r=dict(B=("コースB", "写真好きの1日", "混む前の五重塔・大石公園・根場", "第4章"),
               A=("コースA", "のんびり1日", "ロープウェイ・ほうとう・大石公園", "第4章"),
               E=("本栖湖", "千円札の景色", "バスと歩きで約3時間", "第3章 ⑧"),
               D=("五合目", "富士山の中腹へ", "直行バス約1時間。道路が開いている日だけ", "第3章 ⑥"),
               C=("コースC", "雨の日", "美術館・ほうとう・日帰り温泉", "第4章"))),
    "en": dict(
        lead="Answer from the top and follow the arrows to find your perfect day.",
        q1="The night before, check a live camera (Chapter 1)…", q1a="Mt. Fuji looks clear", q1b="Cloudy or rainy",
        q2="What do you want most?", q2a="The famous photo", q2c="Easy views &amp; good food", q2b="A special Fuji view",
        q3="The 7:30 Fuji Excursion from Shinjuku?", q3a="I can make it", q3b="Too early for me",
        q4="Walk about 1 hour each way from the bus stop?", q4a="No problem", q4b="I'd rather not",
        r=dict(B=("COURSE B", "Photo Lover's Day", "Chureito Pagoda before the crowds, Oishi Park, Nenba", "Chapter 4"),
               A=("COURSE A", "Relaxed Day", "Ropeway, hoto lunch, Oishi Park", "Chapter 4"),
               E=("LAKE MOTOSU", "The ¥1,000 bill view", "About 3 hours by bus and on foot", "Chapter 3 · ⑧"),
               D=("5TH STATION", "Halfway up Mt. Fuji", "Direct bus, about 1 hour. Only when the road is open", "Chapter 3 · ⑥"),
               C=("COURSE C", "Rainy Day", "Museums, hoto, day-trip hot spring", "Chapter 4"))),
    "ko": dict(
        lead="위에서부터 질문에 답하고 화살표를 따라가세요. 나에게 맞는 하루를 찾을 수 있습니다.",
        q1="전날 밤 라이브 카메라(제1장)를 보면…", q1a="후지산이 보일 것 같다", q1b="구름·비가 올 것 같다",
        q2="가장 하고 싶은 것은…", q2a="유명한 사진 찍기", q2c="느긋하게 경치와 식사", q2b="특별한 후지산 보기",
        q3="신주쿠 7:30발 Fuji Excursion에…", q3a="탈 수 있다", q3b="아침은 힘들다",
        q4="버스 정류장에서 편도 약 1시간 걷기는…", q4a="괜찮다", q4b="걷고 싶지 않다",
        r=dict(B=("코스 B", "사진 좋아하는 사람의 하루", "붐비기 전의 오층탑·오이시 공원·넨바", "제4장"),
               A=("코스 A", "느긋한 하루", "로프웨이·호토·오이시 공원", "제4장"),
               E=("모토스코", "천 엔 지폐의 풍경", "버스와 도보로 약 3시간", "제3장 ⑧"),
               D=("5합목", "후지산 중턱으로", "직행버스 약 1시간. 도로가 열린 날만", "제3장 ⑥"),
               C=("코스 C", "비 오는 날", "미술관·호토·당일치기 온천", "제4장"))),
    "zh-hans": dict(
        lead="从上往下回答问题，顺着箭头走，就能找到适合你的一天。",
        q1="前一晚看直播摄像头（第1章）…", q1a="看得到富士山", q1b="多云或下雨",
        q2="你最想做的是…", q2a="拍有名的照片", q2c="悠闲看风景、吃美食", q2b="看特别的富士山",
        q3="新宿7:30发车的富士回游…", q3a="赶得上", q3b="早上起不来",
        q4="从巴士站单程步行约1小时…", q4a="没问题", q4b="不想走",
        r=dict(B=("行程B", "摄影爱好者", "人少时的五重塔、大石公园、根场", "第4章"),
               A=("行程A", "轻松的一天", "缆车、馎饦面、大石公园", "第4章"),
               E=("本栖湖", "千元纸币的风景", "坐巴士加步行约3小时", "第3章 ⑧"),
               D=("五合目", "前往富士山半山腰", "直达巴士约1小时。仅限道路开放时", "第3章 ⑥"),
               C=("行程C", "雨天", "美术馆、馎饦面、一日温泉", "第4章"))),
    "th": dict(
        lead="ตอบคำถามจากด้านบน แล้วเดินตามลูกศร จะได้วันเที่ยวที่เหมาะกับคุณ",
        q1="คืนก่อนไป ดูกล้องถ่ายทอดสด (บทที่ 1)…", q1a="น่าจะเห็นภูเขาไฟฟูจิ", q1b="มีเมฆหรือฝน",
        q2="สิ่งที่อยากทำที่สุดคือ…", q2a="ถ่ายรูปมุมดัง", q2c="ชมวิวและกินอาหารสบาย ๆ", q2b="ชมฟูจิมุมพิเศษ",
        q3="Fuji Excursion 7:30 จากชินจูกุ…", q3a="ขึ้นทัน", q3b="เช้าเกินไป",
        q4="เดินจากป้ายรถบัสราว 1 ชั่วโมงต่อเที่ยว…", q4a="ไม่มีปัญหา", q4b="ไม่อยากเดิน",
        r=dict(B=("แผน B", "คนรักการถ่ายภาพ", "เจดีย์ห้าชั้นก่อนคนเยอะ สวนโออิชิ เนมบะ", "บทที่ 4"),
               A=("แผน A", "วันสบาย ๆ", "กระเช้า โฮโตะ สวนโออิชิ", "บทที่ 4"),
               E=("ทะเลสาบโมโตสึ", "วิวธนบัตร 1,000 เยน", "รถบัสและเดินรวมราว 3 ชั่วโมง", "บทที่ 3 · ⑧"),
               D=("สถานีที่ 5", "ขึ้นไปกลางภูเขาไฟฟูจิ", "รถบัสตรงราว 1 ชั่วโมง เฉพาะวันที่ถนนเปิด", "บทที่ 3 · ⑥"),
               C=("แผน C", "วันฝนตก", "พิพิธภัณฑ์ โฮโตะ ออนเซ็น", "บทที่ 4"))),
    "vi": dict(
        lead="Trả lời từ trên xuống và đi theo mũi tên để tìm ngày đi phù hợp với bạn.",
        q1="Tối hôm trước, xem camera trực tiếp (Chương 1)…", q1a="Có vẻ thấy núi Phú Sĩ", q1b="Nhiều mây hoặc mưa",
        q2="Bạn muốn nhất là…", q2a="Chụp tấm ảnh nổi tiếng", q2c="Ngắm cảnh, ăn ngon thong thả", q2b="Ngắm Phú Sĩ thật đặc biệt",
        q3="Chuyến Fuji Excursion 7:30 từ Shinjuku…", q3a="Đi kịp", q3b="Quá sớm",
        q4="Đi bộ khoảng 1 giờ mỗi chiều từ trạm xe buýt…", q4a="Không sao", q4b="Không muốn",
        r=dict(B=("LỊCH TRÌNH B", "Mê chụp ảnh", "Chùa 5 tầng trước giờ đông, công viên Oishi, Nenba", "Chương 4"),
               A=("LỊCH TRÌNH A", "Ngày thong thả", "Cáp treo, mì hoto, công viên Oishi", "Chương 4"),
               E=("HỒ MOTOSU", "Cảnh tờ 1.000 yên", "Xe buýt và đi bộ khoảng 3 giờ", "Chương 3 · ⑧"),
               D=("TRẠM SỐ 5", "Lên lưng chừng núi Phú Sĩ", "Xe buýt thẳng khoảng 1 giờ. Chỉ khi đường mở", "Chương 3 · ⑥"),
               C=("LỊCH TRÌNH C", "Ngày mưa", "Bảo tàng, mì hoto, suối nước nóng", "Chương 4"))),
    "ms": dict(
        lead="Jawab dari atas dan ikut anak panah untuk mencari hari yang sesuai untuk anda.",
        q1="Malam sebelumnya, lihat kamera langsung (Bab 1)…", q1a="Gunung Fuji nampak jelas", q1b="Mendung atau hujan",
        q2="Apa yang paling anda mahu?", q2a="Foto yang terkenal", q2c="Pemandangan &amp; makanan, santai", q2b="Pemandangan Fuji istimewa",
        q3="Fuji Excursion 7:30 dari Shinjuku?", q3a="Sempat", q3b="Terlalu awal",
        q4="Berjalan kira-kira 1 jam sehala dari perhentian bas?", q4a="Tiada masalah", q4b="Tidak mahu",
        r=dict(B=("PELAN B", "Peminat Fotografi", "Pagoda Chureito sebelum sesak, Taman Oishi, Nenba", "Bab 4"),
               A=("PELAN A", "Hari Santai", "Kereta kabel, hoto, Taman Oishi", "Bab 4"),
               E=("TASIK MOTOSU", "Pemandangan wang ¥1,000", "Bas dan berjalan kira-kira 3 jam", "Bab 3 · ⑧"),
               D=("STESEN KE-5", "Ke pertengahan Gunung Fuji", "Bas terus kira-kira 1 jam. Hanya bila jalan dibuka", "Bab 3 · ⑥"),
               C=("PELAN C", "Hari Hujan", "Muzium, hoto, mata air panas", "Bab 4"))),
}

PHOTO = dict(B="chureito", A="ropeway", E="motosu", D="fifth", C="itchiku")

# Layout in millimetres (chart area is 124 mm wide).
W, H = 124, 146
PILL, CHIP = 10, 9


def _q(x, y, w, text, chips):
    """A question: rounded box with a check mark, answer chips (A./B./C.) underneath."""
    out = (f'<div class="cq" style="left:{x}mm;top:{y}mm;width:{w}mm;height:{PILL}mm">'
           f'<span class="ck">✔</span><span>{text}</span></div>')
    for letter, cx, cw, t in chips:
        out += (f'<div class="cc" style="left:{cx}mm;top:{y + PILL + 2}mm;width:{cw}mm;height:{CHIP}mm">'
                f'<i>{letter}.</i><span>{t}</span></div>')
    return out


def _r(key, x, y, w, h, R, ph_h):
    lab, title, desc, ref = R[key]
    return (f'<div class="cr" style="left:{x}mm;top:{y}mm;width:{w}mm;height:{h}mm">'
            f'<img src="{ph.src(PHOTO[key])}" style="height:{ph_h}mm">'
            f'<div class="cb"><b>{lab}</b><strong>{title}</strong><span>{desc}</span><em>→ {ref}</em></div></div>')


def chart(lang, title, tips, to_hant=None):
    C = CHART.get(lang) or to_hant(CHART["zh-hans"])
    R = C["r"]
    y1, y2, y3, yr = 2, 34, 70, 104
    c1 = y1 + PILL + 2 + CHIP   # bottom of Q1 chips
    c2 = y2 + PILL + 2 + CHIP
    c3 = y3 + PILL + 2 + CHIP
    boxes = (
        _q(24, y1, 80, C["q1"], [("A", 24, 39, C["q1a"]), ("B", 65, 39, C["q1b"])]) +
        _q(0, y2, 86, C["q2"], [("A", 0, 27.3, C["q2a"]), ("B", 29.3, 27.3, C["q2c"]), ("C", 58.7, 27.3, C["q2b"])]) +
        _q(0, y3, 58, C["q3"], [("A", 0, 28, C["q3a"]), ("B", 30, 28, C["q3b"])]) +
        _q(66, y3, 58, C["q4"], [("A", 66, 28, C["q4a"]), ("B", 96, 28, C["q4b"])]) +
        _r("C", 92, y2 - 2, 32, 36, R, 14) +
        _r("B", 0, yr, 28, H - yr, R, 22) + _r("A", 30, yr, 28, H - yr, R, 22) +
        _r("E", 66, yr, 28, H - yr, R, 22) + _r("D", 96, yr, 28, H - yr, R, 22))
    lines = [
        f"M43.5 {c1} V{y2}",                                   # Q1-A -> Q2
        f"M84.5 {c1} V{y2 - 5} H108 V{y2 - 2}",                # Q1-B -> Course C
        f"M13.65 {c2} V{y3}",                                  # Q2-A -> Q3
        f"M72.35 {c2} V{y3}",                                  # Q2-C (special view) -> Q4
        f"M42.95 {c2} V{c2 + 4} H62 V{yr - 4} H44 V{yr}",      # Q2-B (relaxed) -> Course A
        f"M14 {c3} V{yr}", f"M44 {c3} V{yr}",                   # Q3 -> B / A
        f"M80 {c3} V{yr}", f"M110 {c3} V{yr}",                  # Q4 -> Motosu / 5th Station
    ]
    paths = "".join(f'<path d="{d}" marker-end="url(#ah)"/>' for d in lines)
    svg = (f'<svg class="cl" viewBox="0 0 {W} {H}" style="width:{W}mm;height:{H}mm">'
           '<defs><marker id="ah" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="5" markerHeight="5" orient="auto">'
           '<path d="M0 0 L6 3 L0 6 z" fill="#2c3e5c" stroke="none"/></marker></defs>'
           f'<g fill="none" stroke="#2c3e5c" stroke-width=".35" stroke-dasharray="1.2 .9">{paths}</g></svg>')
    tip_html = "".join(f'<div><strong>{a}</strong> {b}</div>' for a, b in tips)
    return (f'<section class="chart"><div class="chead"><span class="start">Start!</span>'
            f'<div><p class="eb">Course Finder</p><h2>{title}</h2><p class="lead">{C["lead"]}</p></div></div>'
            f'<div class="cwrap" style="height:{H}mm">{svg}{boxes}</div><div class="ctips">{tip_html}</div></section>')


CSS = """
.chart { page-break-before: always; page-break-after: always; }
.chead { display: flex; gap: 10px; align-items: flex-end; margin-bottom: 3mm; }
.chead .start { font-family: "Cormorant Garamond", serif; font-style: italic; font-weight: 600; color: var(--red); font-size: 26pt; transform: rotate(-8deg); }
.chead h2 { margin: 0; font-family: var(--serif); font-weight: 800; font-size: 15pt; line-height: 1.3; letter-spacing: .04em; }
.chead .lead { margin: 1px 0 0; font-size: 6.6pt; color: var(--muted); line-height: 1.35; }
.cwrap { position: relative; width: 124mm; }
.cwrap .cl { position: absolute; left: 0; top: 0; }
.cq { position: absolute; display: flex; align-items: center; gap: 4px; background: #fff; border: 1px solid #b7bfd0; border-radius: 6mm;
  padding: 0 8px; font-size: 7.4pt; line-height: 1.2; box-shadow: 0 1px 2px rgba(44,62,92,.18); }
.cq .ck { color: var(--red); font-size: 9pt; font-weight: 700; flex: none; }
.cc { position: absolute; background: var(--navy); color: #fff; display: flex; align-items: center; justify-content: center; text-align: center;
  font-size: 7pt; line-height: 1.15; font-weight: 700; padding: 0 3px 0 9px; }
.cc i { position: absolute; left: -2px; top: -2.5mm; background: #fff; color: var(--navy); border: 1px solid var(--navy);
  font-style: italic; font-family: "Noto Serif", serif; font-size: 6.5pt; padding: 0 3px; line-height: 1.3; }
.cr { position: absolute; background: #fff; border: 1px solid #b7bfd0; box-shadow: 0 1.5px 3px rgba(44,62,92,.2); overflow: hidden; }
.cr img { display: block; width: 100%; object-fit: cover; }
.cr .cb { padding: 3px 5px; line-height: 1.22; }
.cr b { display: block; font-size: 5.8pt; letter-spacing: .1em; color: var(--red); }
.cr strong { display: block; font-family: "Noto Serif CJK JP", serif; font-size: 8.2pt; color: var(--navy); }
.cr span { display: block; font-size: 6.4pt; color: var(--ink); margin-top: 1px; }
.cr em { display: block; font-style: normal; font-weight: 700; font-size: 6.2pt; color: var(--red); margin-top: 2px; }
.ctips { display: grid; grid-template-columns: 1fr 1fr; gap: 3px 8px; margin-top: 3mm; font-size: 6.6pt; line-height: 1.3; color: var(--ink); }
.ctips div { border-left: 2px solid var(--red); padding-left: 5px; }
"""
