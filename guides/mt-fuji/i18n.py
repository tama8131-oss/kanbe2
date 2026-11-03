"""Interface text for each language section of the guide.

Simplified Chinese is written by hand; Traditional Chinese is converted from it
with OpenCC (Taiwan wording) plus a few place-name fixes.
"""
import opencc

LANGS = [
    # code, native name, flags, font suffix, "start" label
    # Order follows the 2026 visitor ranking (Korea, Taiwan, China, USA, Hong Kong, Thailand,
    # Australia, Philippines, Vietnam, Malaysia).
    ("ko", "한국어", "🇰🇷", "KR", "읽기 시작 →"),
    ("zh-hant", "繁體中文", "🇹🇼 🇭🇰", "TC", "開始閱讀 →"),
    ("zh-hans", "简体中文", "🇨🇳", "SC", "开始阅读 →"),
    ("en", "English", "🇺🇸 🇦🇺 🇵🇭 🇬🇧", "", "Start reading →"),
    ("th", "ภาษาไทย", "🇹🇭", "", "เริ่มอ่าน →"),
    ("vi", "Tiếng Việt", "🇻🇳", "", "Bắt đầu đọc →"),
    ("ms", "Bahasa Melayu", "🇲🇾", "", "Mula membaca →"),
    ("ja", "日本語", "🇯🇵", "JP", "読みはじめる →"),  # added 2026-11-03 at Tama's request (last: not a visitor language)
]

TEXT = {
    "en": dict(
        kicker="First time? No worries!", big="Mt. Fuji",
        h1="The Complete Yamanashi / Mt. Fuji Area Guide Map", ed="Latest Edition: November 2026",
        stats=[("8", "places worth your time"), ("3", "ready-made courses"), ("2h", "from Shinjuku"), ("11.2026", "every fare &amp; time checked by phone &amp; official sites")],
        welcome="Welcome", before="Before you start",
        p1="Every fare, timetable and opening time in this guide was checked in <strong>November 2026</strong> against official websites or by phone with the operators themselves. Where we use another source, we say so.",
        alert="Prices and times in Japan do change, often in spring (when timetables are revised). <strong>Before you travel, check the official websites</strong> (QR codes in the Book &amp; Navigate section), especially for trains, buses and opening days.",
        author_h="From the author",
        author="I made this guide because the information on getting to Mt. Fuji is spread across dozens of Japanese websites, and quick online answers are often out of date or simply wrong. The text was written with the help of AI tools, but I checked every fare, timetable and opening time myself, on official websites and by phone with the railway and bus companies, museums, hot springs and tourist offices, in November 2026. I hope it saves you time and lets you enjoy the mountain. <strong>— Tama</strong>",
        contents="Contents",
        toc=["Know Before You Go", "Find Your Course", "Before You Go", "Getting There from Tokyo", "The 8 Best Places",
             "Ready-Made Itineraries", "Local Food", "Good to Know (with packing checklist)", "Book &amp; Navigate (QR codes)", "Route Diagram"],
        disclaimer="This guide is an independent travel guide. It is not affiliated with any of the companies or places it mentions.",
        change="🌐 Change language", essentials="ESSENTIALS", chapter="CHAPTER",
    ),
    "zh-hans": dict(
        kicker="第一次去也放心！", big="Mt. Fuji",
        h1="山梨／富士山周边导览地图完全版", ed="11月最新版（2026年）",
        stats=[("8", "值得去的地方"), ("3", "推荐行程"), ("2h", "从新宿出发"), ("11.2026", "所有票价和时间都经电话和官网确认")],
        welcome="Welcome", before="写在前面",
        p1="本指南中的所有票价、时刻表和营业时间，都在<strong>2026年11月</strong>通过官网或直接打电话向运营方确认过。使用其他信息来源的地方，都会注明。",
        alert="日本的票价和时间会变化，尤其是春季时刻表调整时。<strong>出发前请查看官网</strong>（可以用「预订与导航」部分的二维码打开），特别是电车、巴士和营业日。",
        author_h="作者的话",
        author="去富士山的交通信息分散在许多日文网站上，网上的简单答案也常常过时或说错，所以我做了这本指南。文字是借助AI工具写的，但所有票价、时刻表和营业时间，都是我本人在2026年11月通过官网核对，并打电话向铁路和巴士公司、美术馆、温泉和观光咨询处确认的。希望它能帮你节省时间，好好享受富士山。<strong>— Tama</strong>",
        contents="目录",
        toc=["出发前必看", "行程诊断", "出发之前", "从东京出发", "值得去的8个地方",
             "照着走的行程", "当地美食", "实用小知识（附携带物品清单）", "预订与导航（二维码）", "换乘示意图"],
        disclaimer="本指南为个人制作的旅游指南，与文中提到的公司和设施没有关系。",
        change="🌐 切换语言", essentials="ESSENTIALS", chapter="CHAPTER",
    ),
    "ko": dict(
        kicker="처음 가는 사람도 안심!", big="Mt. Fuji",
        h1="야마나시／후지산 주변 가이드맵 완전판", ed="11월 최신판 (2026년)",
        stats=[("8", "가 볼 만한 곳"), ("3", "추천 코스"), ("2h", "신주쿠에서"), ("11.2026", "요금·시간은 모두 전화와 공식 사이트로 확인")],
        welcome="Welcome", before="시작하기 전에",
        p1="이 가이드의 요금·시간표·영업시간은 모두 <strong>2026년 11월</strong>에 공식 사이트나 운영사에 전화로 직접 확인한 것입니다. 다른 정보를 쓴 곳은 그렇게 적어 두었습니다.",
        alert="일본의 요금과 시간은 바뀔 수 있습니다(특히 시간표가 바뀌는 봄). <strong>출발 전에 공식 사이트를 확인하세요</strong>('예약과 내비'의 QR 코드로 열 수 있습니다). 특히 전철·버스·영업일.",
        author_h="만든 사람의 말",
        author="후지산 가는 법에 관한 정보는 수많은 일본어 사이트에 흩어져 있고, 인터넷의 간단한 답변은 오래되었거나 틀린 경우가 많습니다. 그래서 이 가이드를 만들었습니다. 글은 AI 도구의 도움을 받아 썼지만, 요금·시간표·영업시간은 모두 2026년 11월에 제가 직접 공식 사이트에서 확인하고, 철도·버스 회사, 미술관, 온천, 관광안내소에 전화로 확인했습니다. 여러분의 시간을 아끼고 후지산을 즐기는 데 도움이 되면 좋겠습니다. <strong>— Tama</strong>",
        contents="목차",
        toc=["출발 전 꼭 알아둘 것", "나에게 맞는 코스 찾기", "출발하기 전에", "도쿄에서 가는 법", "가 볼 만한 8곳",
             "그대로 따라 하는 코스", "현지 음식", "알아두면 좋은 것(준비물 체크리스트 포함)", "예약과 내비(QR 코드)", "환승 안내도"],
        disclaimer="이 가이드는 개인이 만든 여행 가이드이며, 언급된 회사나 시설과는 관계가 없습니다.",
        change="🌐 언어 바꾸기", essentials="ESSENTIALS", chapter="CHAPTER",
    ),
}

FINDER = {
    "en": dict(
        title="Find Your Course", lead="Answer the questions from the top. Each answer points you to one of the three ready-made courses in Chapter 4.",
        q=["Open a live camera the night before (Chapter 1). <strong>Is Mt. Fuji visible, and will it be dry?</strong>",
           "<strong>Is the famous red pagoda photo a must</strong>, and can you take the 7:30 Fuji Excursion from Shinjuku?",
           "<strong>First visit?</strong> Want an easy day using only one sightseeing bus line?"],
        yes="YES", no="NO",
        r=[("Course C · Rainy Day", "Museums, hoto noodles and a day-trip hot spring. Works even when Mt. Fuji is hidden."),
           ("Course B · Photo Lover's Day", "Chureito Pagoda before the crowds, Oishi Park and the thatched village of Nenba. Buy the 1-Day Pass."),
           ("Course A · Relaxed Day", "Ropeway, hoto lunch and Oishi Park on the Red Line. Pay single fares; no pass needed."),
           ("Build your own", "Pick from Chapter 3: add Oshino Hakkai (bus from Kawaguchiko) or Lake Motosu (needs about 3 hours).")],
        tips=[("Have a tattoo?", "For a hot spring, choose Royal Hotel Kawaguchiko (tattoos OK)."),
              ("June to August?", "Mt. Fuji is often hidden. Keep Course C ready as a backup."),
              ("Japan Rail Pass?", "It covers Shinjuku–Otsuki only. See Chapter 2."),
              ("Big suitcase?", "Leave it in a locker outside Kawaguchiko Station's ticket gates.")]),
    "zh-hans": dict(
        title="行程诊断", lead="从上往下回答问题。根据答案，就能知道第4章的三条推荐行程中哪一条适合你。",
        q=["前一晚看实时摄像头（第1章）。<strong>看得到富士山吗？不会下雨吗？</strong>",
           "<strong>一定要拍红色五重塔的经典照片吗？</strong>能坐新宿7:30发车的富士回游号吗？",
           "<strong>第一次去富士山？</strong>想要只坐一条周游巴士线路的轻松一天吗？"],
        yes="YES", no="NO",
        r=[("行程C・雨天", "美术馆、馎饦面和一日温泉。即使看不到富士山也能玩。"),
           ("行程B・摄影爱好者", "赶在人多之前去五重塔，再去大石公园和茅草屋村落根场。买周游巴士1日券。"),
           ("行程A・轻松的一天", "坐红线去缆车、吃馎饦面、逛大石公园。单程买票就好，不需要1日券。"),
           ("自己安排", "从第3章挑选：加上忍野八海（从河口湖站坐巴士）或本栖湖（约需3小时）。")],
        tips=[("有纹身？", "泡温泉请选河口湖皇家酒店（可纹身）。"),
              ("6～8月去？", "富士山常被云遮住，请把行程C作为备选。"),
              ("有JR Pass？", "只能坐新宿～大月。请看第2章。"),
              ("大行李箱？", "存在河口湖站检票口外的储物柜。")]),
    "ko": dict(
        title="나에게 맞는 코스 찾기", lead="위에서부터 질문에 답하세요. 답에 따라 제4장의 세 가지 추천 코스 중 어떤 것이 맞는지 알 수 있습니다.",
        q=["전날 밤 라이브 카메라를 확인(제1장). <strong>후지산이 보일 것 같나요? 비는 안 오나요?</strong>",
           "<strong>붉은 오층탑의 유명한 사진은 꼭 찍고 싶나요?</strong> 신주쿠 7:30 출발 후지 익스커션을 탈 수 있나요?",
           "<strong>후지산은 처음인가요?</strong> 주유버스 한 노선만 타는 느긋한 하루가 좋나요?"],
        yes="YES", no="NO",
        r=[("코스 C · 비 오는 날", "미술관, 호토, 당일치기 온천. 후지산이 가려져 있어도 즐길 수 있습니다."),
           ("코스 B · 사진 좋아하는 사람", "붐비기 전의 오층탑, 오이시 공원, 초가 마을 넨바. 주유버스 1일권을 사세요."),
           ("코스 A · 느긋한 하루", "레드 라인으로 로프웨이, 호토 점심, 오이시 공원. 1일권은 필요 없습니다."),
           ("직접 짜기", "제3장에서 고르세요. 오시노핫카이(가와구치코역에서 버스)나 모토스코(약 3시간 필요)를 추가.")],
        tips=[("문신이 있나요?", "온천은 로열 호텔 가와구치코(문신 가능)로."),
              ("6～8월에 가나요?", "후지산이 자주 가려집니다. 코스 C도 준비해 두세요."),
              ("JR 패스가 있나요?", "신주쿠～오쓰키만 됩니다. 제2장을 보세요."),
              ("큰 캐리어가 있나요?", "가와구치코역 개찰구 바로 밖의 로커에 맡기세요.")]),
}

MAP_LABELS = {
    "en": dict(
        title="Route Diagram", note="Diagram only. Distances and positions are not to scale. All times are from Chapters 2 and 3.",
        station="Kawaguchiko<br>Station", rail="Fujikyu Railway", red="Red Line", green="Green Line", blue="Blue Line",
        route="Route bus", direct="Direct bus",
        p1="① Chureito Pagoda", p1b="Shimoyoshida Sta. + 25 min on foot", p2="② Oishi Park", p2b="about 27 min",
        p3="③ Oshino Hakkai", p3b="bus for Gotemba or Yamanakako Hirano", p4="④ Ropeway", p4b="about 11 min or 15 min on foot",
        p5="⑤ Iyashi-no-Sato Nenba", p5b="about 40 min", p6="⑥ 5th Station", p6b="about 1 hour",
        p7="⑦ Fuji-Q Highland", p7b="one stop", p8="⑧ Lake Motosu", p8b="about 1 hour + 1 hour on foot",
        tokyo="To Tokyo (Shinjuku): Fuji Excursion or highway bus (Chapter 2)"),
    "zh-hans": dict(
        title="换乘示意图", note="仅为示意图，位置和距离并不准确。时间均来自第2章和第3章已确认的信息。",
        station="河口湖站", rail="富士急行线", red="红线", green="绿线", blue="蓝线",
        route="路线巴士", direct="直达巴士",
        p1="① 五重塔", p1b="下吉田站＋步行25分钟", p2="② 大石公园", p2b="约27分钟",
        p3="③ 忍野八海", p3b="开往御殿场或山中湖平野", p4="④ 缆车", p4b="约11分钟（步行约15分钟）",
        p5="⑤ 治愈之乡根场", p5b="约40分钟", p6="⑥ 五合目", p6b="约1小时",
        p7="⑦ 富士急乐园", p7b="1站", p8="⑧ 本栖湖", p8b="约1小时＋步行约1小时",
        tokyo="回东京（新宿）：富士回游号或高速巴士（第2章）"),
    "ko": dict(
        title="환승 안내도", note="위치와 거리는 정확하지 않습니다. 시간은 제2장·제3장의 확인된 정보입니다.",
        station="가와구치코역", rail="후지큐코선", red="레드 라인", green="그린 라인", blue="블루 라인",
        route="노선버스", direct="직행버스",
        p1="① 오층탑", p1b="시모요시다역＋도보 25분", p2="② 오이시 공원", p2b="약 27분",
        p3="③ 오시노핫카이", p3b="고텐바행 또는 야마나카코 히라노행", p4="④ 로프웨이", p4b="약 11분(도보 약 15분)",
        p5="⑤ 이야시노사토 넨바", p5b="약 40분", p6="⑥ 5합목", p6b="약 1시간",
        p7="⑦ 후지큐 하이랜드", p7b="1정거장", p8="⑧ 모토스코", p8b="약 1시간＋도보 약 1시간",
        tokyo="도쿄(신주쿠)로: 후지 익스커션 또는 고속버스(제2장)"),
}

BN = {  # Book & Navigate page
    "en": dict(title="Book &amp; Navigate", h_book="Tickets &amp; official websites",
               h_nav="Navigation: directions from where you are",
               lead_book="Scan a QR code with your phone camera to open the page. In the PDF you can also tap the link.",
               lead_nav="Opens Google Maps with public-transport directions from where you are now.",
               open="Open in Google Maps",
               fc="Highway buses can also be booked on FUJIYAMA CONNECT, Fujikyu's own booking site (search \"FUJIYAMA CONNECT\")."),
    "zh-hans": dict(title="预订与导航", h_book="车票预订与官方网站", h_nav="导航：从你现在的位置出发",
                    lead_book="用手机相机扫描二维码即可打开网页。在PDF中也可以直接点击链接。",
                    lead_nav="会打开Google地图，显示从你现在的位置出发的电车・巴士路线。",
                    open="在Google地图中打开",
                    fc="高速巴士也可以在富士急自己的订票网站FUJIYAMA CONNECT预订（搜索「FUJIYAMA CONNECT」）。"),
    "ko": dict(title="예약과 내비", h_book="승차권 예약과 공식 사이트", h_nav="내비: 지금 있는 곳에서 가는 법",
               lead_book="휴대폰 카메라로 QR 코드를 읽으면 페이지가 열립니다. PDF에서는 링크를 눌러도 열립니다.",
               lead_nav="Google 지도가 열리고, 지금 있는 곳에서 전철·버스로 가는 법이 표시됩니다.",
               open="Google 지도에서 열기",
               fc="고속버스는 후지큐의 예약 사이트 FUJIYAMA CONNECT에서도 예약할 수 있습니다(\"FUJIYAMA CONNECT\"로 검색)."),
}

BOOK_NAMES = {  # key -> (name, what for)
    "zh-hans": {"jre": ("JR-EAST Train Reservation", "用英文预订富士回游号"), "ekinet": ("Eki-net（JR东日本）", "预订富士回游号（日文）"),
                "hwb": ("Highway Bus.com", "预订从Busta新宿出发的高速巴士"), "fkrail": ("富士急行线", "时刻表、票价、富士山・富士五湖护照"),
                "fkbus": ("富士急巴士", "周游巴士、时刻表、乘车券"), "fujiq": ("富士急乐园", "通票和营业日历"),
                "motosuko": ("富士本栖湖度假区", "实时摄像头和富士芝樱节")},
    "ko": {"jre": ("JR-EAST Train Reservation", "후지 익스커션을 영어로 예약"), "ekinet": ("에키넷(JR 동일본)", "후지 익스커션 예약(일본어)"),
           "hwb": ("하이웨이버스닷컴", "바스타 신주쿠 출발 고속버스 예약"), "fkrail": ("후지큐코선", "시간표·운임·후지산·후지고코 패스포트"),
           "fkbus": ("후지큐 버스", "주유버스·시간표·자유 승차권"), "fujiq": ("후지큐 하이랜드", "자유이용권과 영업 캘린더"),
           "motosuko": ("후지 모토스코 리조트", "라이브 카메라와 후지 시바자쿠라 축제")},
}

PLACE_NAMES = {  # same order as links.PLACES
    "zh-hans": ["河口湖站", "Busta新宿（高速巴士）", "五重塔（新仓山浅间公园）", "大石公园", "忍野八海", "富士山全景缆车",
                "西湖治愈之乡根场", "富士斯巴鲁线五合目", "富士急乐园", "本栖湖（浩庵荘附近）", "河口湖皇家酒店（可纹身）", "富士眺望之汤 Yurari"],
    "ko": ["가와구치코역", "바스타 신주쿠(고속버스)", "오층탑(아라쿠라야마 센겐 공원)", "오이시 공원", "오시노핫카이", "후지산 파노라마 로프웨이",
           "사이코 이야시노사토 넨바", "후지 스바루 라인 5합목", "후지큐 하이랜드", "모토스코(고안소 근처)", "로열 호텔 가와구치코(문신 가능)", "후지초보노유 유라리"],
}

TEXT["th"] = dict(
    kicker="มาครั้งแรกก็มั่นใจได้!", big="Mt. Fuji",
    h1="แผนที่นำเที่ยวยามานาชิ／รอบภูเขาไฟฟูจิ ฉบับสมบูรณ์", ed="ฉบับล่าสุด เดือนพฤศจิกายน 2026",
    stats=[("8", "สถานที่ที่คุ้มค่า"), ("3", "แผนเที่ยวสำเร็จรูป"), ("2h", "จากชินจูกุ"), ("11.2026", "ค่าโดยสารและเวลาทั้งหมดตรวจสอบทางโทรศัพท์และเว็บไซต์ทางการ")],
    welcome="Welcome", before="ก่อนเริ่มต้น",
    p1="ค่าโดยสาร ตารางเวลา และเวลาเปิดทั้งหมดในคู่มือนี้ ได้ตรวจสอบเมื่อ<strong>พฤศจิกายน 2026</strong> จากเว็บไซต์ทางการหรือโทรถามผู้ให้บริการโดยตรง ส่วนที่ใช้แหล่งอื่นเราระบุไว้",
    alert="ราคาและเวลาในญี่ปุ่นเปลี่ยนได้ โดยเฉพาะฤดูใบไม้ผลิที่มีการปรับตารางเวลา <strong>ก่อนเดินทางโปรดตรวจสอบเว็บไซต์ทางการ</strong> (เปิดได้จาก QR โค้ดในหัวข้อ \"จองและนำทาง\") โดยเฉพาะรถไฟ รถบัส และวันเปิดทำการ",
    author_h="จากผู้จัดทำ",
    author="ข้อมูลการเดินทางไปภูเขาไฟฟูจิกระจัดกระจายอยู่ในเว็บไซต์ภาษาญี่ปุ่นมากมาย และคำตอบสั้น ๆ ทางอินเทอร์เน็ตมักล้าสมัยหรือผิด ฉันจึงทำคู่มือนี้ขึ้น เนื้อหาเขียนโดยใช้เครื่องมือ AI ช่วย แต่ค่าโดยสาร ตารางเวลา และเวลาเปิดทุกอย่าง ฉันตรวจสอบเองจากเว็บไซต์ทางการ และโทรถามบริษัทรถไฟ รถบัส พิพิธภัณฑ์ ออนเซ็น และศูนย์ข้อมูลท่องเที่ยว เมื่อพฤศจิกายน 2026 หวังว่าจะช่วยประหยัดเวลาและทำให้คุณสนุกกับภูเขาไฟฟูจิ <strong>— Tama</strong>",
    contents="สารบัญ",
    toc=["สิ่งที่ต้องรู้ก่อนออกเดินทาง", "ค้นหาแผนที่ใช่", "ก่อนออกเดินทาง", "การเดินทางจากโตเกียว", "8 สถานที่ที่คุ้มค่า",
         "แผนเที่ยวสำเร็จรูป", "อาหารท้องถิ่น", "เรื่องน่ารู้ (พร้อมรายการของที่ต้องเตรียม)", "จองและนำทาง (QR โค้ด)", "แผนผังการเดินทาง"],
    disclaimer="คู่มือนี้เป็นคู่มือท่องเที่ยวที่จัดทำโดยบุคคล ไม่มีความเกี่ยวข้องกับบริษัทหรือสถานที่ที่กล่าวถึง",
    change="🌐 เปลี่ยนภาษา", essentials="ESSENTIALS", chapter="CHAPTER",
)
TEXT["vi"] = dict(
    kicker="Lần đầu đến cũng yên tâm!", big="Mt. Fuji",
    h1="Bản đồ hướng dẫn Yamanashi / quanh núi Phú Sĩ – Bản đầy đủ", ed="Bản mới nhất tháng 11/2026",
    stats=[("8", "nơi đáng đến"), ("3", "lịch trình có sẵn"), ("2h", "từ Shinjuku"), ("11.2026", "mọi giá vé và giờ giấc đều kiểm tra qua điện thoại và trang chính thức")],
    welcome="Welcome", before="Trước khi bắt đầu",
    p1="Mọi giá vé, lịch chạy và giờ mở cửa trong cẩm nang này đều được kiểm tra vào <strong>tháng 11/2026</strong> trên trang chính thức hoặc gọi điện trực tiếp cho đơn vị vận hành. Chỗ nào dùng nguồn khác, chúng tôi đều ghi rõ.",
    alert="Giá và giờ ở Nhật có thể thay đổi, nhất là vào mùa xuân khi đổi lịch chạy. <strong>Trước khi đi, hãy xem trang chính thức</strong> (mở bằng mã QR ở phần Đặt vé &amp; Chỉ đường), nhất là tàu, xe buýt và ngày mở cửa.",
    author_h="Lời người biên soạn",
    author="Thông tin đi núi Phú Sĩ nằm rải rác trên hàng chục trang web tiếng Nhật, và câu trả lời nhanh trên mạng thường cũ hoặc sai. Vì vậy tôi làm cẩm nang này. Nội dung được viết với sự hỗ trợ của công cụ AI, nhưng mọi giá vé, lịch chạy và giờ mở cửa tôi đều tự kiểm tra trên trang chính thức và gọi điện cho công ty đường sắt, xe buýt, bảo tàng, suối nước nóng và trung tâm du lịch vào tháng 11/2026. Mong cẩm nang giúp bạn tiết kiệm thời gian và tận hưởng núi Phú Sĩ. <strong>— Tama</strong>",
    contents="Mục lục",
    toc=["Cần biết trước khi đi", "Tìm lịch trình phù hợp", "Trước khi đi", "Đi từ Tokyo", "8 nơi đáng đến",
         "Lịch trình có sẵn", "Ẩm thực địa phương", "Điều nên biết (kèm danh sách đồ cần mang)", "Đặt vé &amp; Chỉ đường (mã QR)", "Sơ đồ di chuyển"],
    disclaimer="Đây là cẩm nang du lịch do cá nhân biên soạn, không liên quan đến các công ty hay địa điểm được nhắc đến.",
    change="🌐 Đổi ngôn ngữ", essentials="ESSENTIALS", chapter="CHAPTER",
)
TEXT["ms"] = dict(
    kicker="Kali pertama? Jangan risau!", big="Mt. Fuji",
    h1="Peta Panduan Lengkap Yamanashi / Sekitar Gunung Fuji", ed="Edisi Terkini November 2026",
    stats=[("8", "tempat yang berbaloi"), ("3", "jadual perjalanan siap"), ("2h", "dari Shinjuku"), ("11.2026", "setiap tambang &amp; masa disemak melalui telefon &amp; laman rasmi")],
    welcome="Welcome", before="Sebelum bermula",
    p1="Setiap tambang, jadual dan waktu operasi dalam panduan ini telah disemak pada <strong>November 2026</strong> di laman rasmi atau melalui telefon terus dengan pengendali. Jika kami guna sumber lain, kami nyatakan.",
    alert="Harga dan masa di Jepun boleh berubah, terutamanya pada musim bunga apabila jadual disemak semula. <strong>Sebelum pergi, semak laman rasmi</strong> (kod QR dalam bahagian Tempah &amp; Navigasi), terutamanya untuk kereta api, bas dan hari operasi.",
    author_h="Daripada penulis",
    author="Maklumat untuk ke Gunung Fuji tersebar di puluhan laman web berbahasa Jepun, dan jawapan ringkas dalam talian selalunya lapuk atau salah. Sebab itu saya membuat panduan ini. Teksnya ditulis dengan bantuan alat AI, tetapi setiap tambang, jadual dan waktu operasi saya semak sendiri di laman rasmi dan melalui telefon dengan syarikat kereta api dan bas, muzium, mata air panas dan pejabat pelancongan pada November 2026. Semoga ia menjimatkan masa anda dan anda dapat menikmati Gunung Fuji. <strong>— Tama</strong>",
    contents="Kandungan",
    toc=["Perkara Penting Sebelum Pergi", "Cari Pelan Anda", "Sebelum Pergi", "Pergi dari Tokyo", "8 Tempat Terbaik",
         "Jadual Perjalanan Siap", "Makanan Tempatan", "Perlu Tahu (dengan senarai semak barang)", "Tempah &amp; Navigasi (kod QR)", "Rajah Laluan"],
    disclaimer="Panduan ini ialah panduan pelancongan bebas yang dibuat oleh individu. Ia tiada kaitan dengan mana-mana syarikat atau tempat yang disebut.",
    change="🌐 Tukar bahasa", essentials="ESSENTIALS", chapter="CHAPTER",
)

FINDER["th"] = dict(
    title="ค้นหาแผนที่ใช่", lead="ตอบคำถามจากบนลงล่าง แต่ละคำตอบจะพาไปยังแผนเที่ยวสำเร็จรูป 1 ใน 3 แบบในบทที่ 4",
    q=["ดูกล้องถ่ายทอดสดคืนก่อน (บทที่ 1) <strong>เห็นภูเขาไฟฟูจิไหม และฝนจะไม่ตกใช่ไหม?</strong>",
       "<strong>ต้องได้ภาพเจดีย์ห้าชั้นสีแดงอันโด่งดังใช่ไหม</strong> และขึ้น Fuji Excursion 7:30 จากชินจูกุได้ไหม?",
       "<strong>มาครั้งแรก?</strong> อยากได้วันสบาย ๆ ที่นั่งรถบัสท่องเที่ยวสายเดียวใช่ไหม?"],
    yes="YES", no="NO",
    r=[("แผน C · วันฝนตก", "พิพิธภัณฑ์ โฮโตะ และออนเซ็น เที่ยวได้แม้มองไม่เห็นภูเขาไฟฟูจิ"),
       ("แผน B · คนรักการถ่ายภาพ", "เจดีย์ห้าชั้นก่อนคนเยอะ สวนโออิชิ และหมู่บ้านหลังคามุงจากเนมบะ ซื้อบัตร 1 วัน"),
       ("แผน A · วันสบาย ๆ", "กระเช้า มื้อกลางวันโฮโตะ และสวนโออิชิบนสายสีแดง จ่ายทีละเที่ยว ไม่ต้องซื้อบัตร"),
       ("วางแผนเอง", "เลือกจากบทที่ 3: เพิ่มโอชิโนะฮักไก (รถบัสจากคาวากุจิโกะ) หรือทะเลสาบโมโตสึ (ใช้เวลาประมาณ 3 ชั่วโมง)")],
    tips=[("มีรอยสัก?", "ออนเซ็นให้เลือกโรงแรมรอยัลคาวากุจิโกะ (รอยสักได้)"),
          ("ไปช่วงมิถุนายน–สิงหาคม?", "ภูเขาไฟฟูจิมักถูกเมฆบัง เตรียมแผน C ไว้สำรอง"),
          ("มี JR Pass?", "ใช้ได้เฉพาะชินจูกุ–โอสึกิ ดูบทที่ 2"),
          ("กระเป๋าใบใหญ่?", "ฝากที่ล็อกเกอร์หน้าประตูตรวจตั๋วสถานีคาวากุจิโกะ")])
FINDER["vi"] = dict(
    title="Tìm lịch trình phù hợp", lead="Trả lời các câu hỏi từ trên xuống. Mỗi câu trả lời dẫn bạn đến một trong ba lịch trình có sẵn ở Chương 4.",
    q=["Xem camera trực tiếp tối hôm trước (Chương 1). <strong>Có thấy núi Phú Sĩ và trời có khô ráo không?</strong>",
       "<strong>Nhất định phải chụp bức ảnh chùa 5 tầng đỏ nổi tiếng</strong>, và bạn đi được chuyến Fuji Excursion 7:30 từ Shinjuku chứ?",
       "<strong>Lần đầu đến?</strong> Muốn một ngày thong thả chỉ đi một tuyến xe buýt tham quan?"],
    yes="YES", no="NO",
    r=[("Lịch trình C · Ngày mưa", "Bảo tàng, mì hoto và suối nước nóng trong ngày. Vẫn vui dù núi Phú Sĩ bị che."),
       ("Lịch trình B · Mê chụp ảnh", "Chùa 5 tầng trước giờ đông, công viên Oishi và làng mái tranh Nenba. Hãy mua vé 1 ngày."),
       ("Lịch trình A · Ngày thong thả", "Cáp treo, ăn trưa mì hoto và công viên Oishi trên tuyến Đỏ. Mua vé lẻ, không cần vé ngày."),
       ("Tự lên kế hoạch", "Chọn từ Chương 3: thêm Oshino Hakkai (xe buýt từ Kawaguchiko) hoặc hồ Motosu (mất khoảng 3 giờ).")],
    tips=[("Có hình xăm?", "Muốn tắm suối nước nóng, hãy chọn Royal Hotel Kawaguchiko (có hình xăm vẫn được)."),
          ("Đi tháng 6–8?", "Núi Phú Sĩ hay bị mây che. Chuẩn bị sẵn Lịch trình C."),
          ("Có JR Pass?", "Chỉ dùng được đoạn Shinjuku–Otsuki. Xem Chương 2."),
          ("Vali lớn?", "Gửi ở tủ khóa ngay ngoài cửa soát vé ga Kawaguchiko.")])
FINDER["ms"] = dict(
    title="Cari Pelan Anda", lead="Jawab soalan dari atas. Setiap jawapan membawa anda ke salah satu daripada tiga jadual perjalanan siap dalam Bab 4.",
    q=["Lihat kamera langsung pada malam sebelumnya (Bab 1). <strong>Adakah Gunung Fuji kelihatan, dan adakah cuaca kering?</strong>",
       "<strong>Gambar pagoda merah yang terkenal itu wajib</strong>, dan bolehkah anda naik Fuji Excursion 7:30 dari Shinjuku?",
       "<strong>Kali pertama?</strong> Mahu hari santai dengan satu laluan bas pelancongan sahaja?"],
    yes="YES", no="NO",
    r=[("Pelan C · Hari Hujan", "Muzium, mi hoto dan mata air panas sehari. Sesuai walaupun Gunung Fuji tersembunyi."),
       ("Pelan B · Peminat Fotografi", "Pagoda Chureito sebelum sesak, Taman Oishi dan kampung beratap jerami Nenba. Beli Pas 1 Hari."),
       ("Pelan A · Hari Santai", "Kereta kabel, makan tengah hari hoto dan Taman Oishi di Laluan Merah. Bayar sehala; tiada pas diperlukan."),
       ("Rancang sendiri", "Pilih dari Bab 3: tambah Oshino Hakkai (bas dari Kawaguchiko) atau Tasik Motosu (perlukan kira-kira 3 jam).")],
    tips=[("Bertatu?", "Untuk mata air panas, pilih Royal Hotel Kawaguchiko (tatu dibenarkan)."),
          ("Jun hingga Ogos?", "Gunung Fuji kerap tersembunyi. Sediakan Pelan C sebagai sandaran."),
          ("Ada Japan Rail Pass?", "Hanya meliputi Shinjuku–Otsuki. Lihat Bab 2."),
          ("Beg pakaian besar?", "Simpan di loker di luar pintu tiket Stesen Kawaguchiko.")])

MAP_LABELS["th"] = dict(
    title="แผนผังการเดินทาง", note="เป็นแผนผังเท่านั้น ตำแหน่งและระยะทางไม่ตรงตามจริง เวลาทั้งหมดมาจากบทที่ 2 และ 3",
    station="สถานี<br>คาวากุจิโกะ", rail="Fujikyu Railway", red="สายสีแดง", green="สายสีเขียว", blue="สายสีน้ำเงิน",
    route="รถบัสประจำทาง", direct="รถบัสตรง",
    p1="① เจดีย์ห้าชั้น", p1b="สถานีชิโมโยชิดะ＋เดิน 25 นาที", p2="② สวนโออิชิ", p2b="ประมาณ 27 นาที",
    p3="③ โอชิโนะฮักไก", p3b="รถไปโกเท็มบะหรือยามานากะโกะฮิราโนะ", p4="④ กระเช้า", p4b="ประมาณ 11 นาที (เดิน 15 นาที)",
    p5="⑤ อิยาชิโนะซาโตะเนมบะ", p5b="ประมาณ 40 นาที", p6="⑥ สถานีที่ 5", p6b="ประมาณ 1 ชั่วโมง",
    p7="⑦ ฟูจิคิวไฮแลนด์", p7b="1 สถานี", p8="⑧ ทะเลสาบโมโตสึ", p8b="ประมาณ 1 ชม.＋เดิน 1 ชม.",
    tokyo="กลับโตเกียว (ชินจูกุ): Fuji Excursion หรือรถบัสทางด่วน (บทที่ 2)")
MAP_LABELS["vi"] = dict(
    title="Sơ đồ di chuyển", note="Chỉ là sơ đồ, vị trí và khoảng cách không đúng tỉ lệ. Mọi thời gian lấy từ Chương 2 và 3.",
    station="Ga<br>Kawaguchiko", rail="Fujikyu Railway", red="Tuyến Đỏ", green="Tuyến Xanh lá", blue="Tuyến Xanh dương",
    route="Xe buýt thường", direct="Xe buýt thẳng",
    p1="① Chùa 5 tầng", p1b="Ga Shimoyoshida + đi bộ 25 phút", p2="② Công viên Oishi", p2b="khoảng 27 phút",
    p3="③ Oshino Hakkai", p3b="xe đi Gotemba hoặc Yamanakako Hirano", p4="④ Cáp treo", p4b="khoảng 11 phút (đi bộ 15 phút)",
    p5="⑤ Iyashi-no-Sato Nenba", p5b="khoảng 40 phút", p6="⑥ Trạm 5", p6b="khoảng 1 giờ",
    p7="⑦ Fuji-Q Highland", p7b="1 ga", p8="⑧ Hồ Motosu", p8b="khoảng 1 giờ + đi bộ 1 giờ",
    tokyo="Về Tokyo (Shinjuku): Fuji Excursion hoặc xe buýt cao tốc (Chương 2)")
MAP_LABELS["ms"] = dict(
    title="Rajah Laluan", note="Rajah sahaja. Kedudukan dan jarak tidak mengikut skala. Semua masa daripada Bab 2 dan 3.",
    station="Stesen<br>Kawaguchiko", rail="Fujikyu Railway", red="Laluan Merah", green="Laluan Hijau", blue="Laluan Biru",
    route="Bas laluan", direct="Bas terus",
    p1="① Pagoda Chureito", p1b="Stesen Shimoyoshida + 25 minit berjalan", p2="② Taman Oishi", p2b="kira-kira 27 minit",
    p3="③ Oshino Hakkai", p3b="bas ke Gotemba atau Yamanakako Hirano", p4="④ Kereta kabel", p4b="kira-kira 11 minit (15 minit berjalan)",
    p5="⑤ Iyashi-no-Sato Nenba", p5b="kira-kira 40 minit", p6="⑥ Stesen ke-5", p6b="kira-kira 1 jam",
    p7="⑦ Fuji-Q Highland", p7b="1 hentian", p8="⑧ Tasik Motosu", p8b="kira-kira 1 jam + 1 jam berjalan",
    tokyo="Ke Tokyo (Shinjuku): Fuji Excursion atau bas lebuh raya (Bab 2)")

BN["th"] = dict(title="จองและนำทาง", h_book="ตั๋วและเว็บไซต์ทางการ", h_nav="นำทาง: เส้นทางจากตำแหน่งปัจจุบันของคุณ",
                lead_book="สแกน QR โค้ดด้วยกล้องโทรศัพท์เพื่อเปิดหน้าเว็บ ใน PDF แตะลิงก์ได้เลย",
                lead_nav="เปิด Google Maps แสดงเส้นทางรถไฟและรถบัสจากตำแหน่งที่คุณอยู่ตอนนี้",
                open="เปิดใน Google Maps",
                fc="รถบัสทางด่วนจองได้ที่ FUJIYAMA CONNECT เว็บไซต์จองของ Fujikyu ด้วย (ค้นหา \"FUJIYAMA CONNECT\")")
BN["vi"] = dict(title="Đặt vé &amp; Chỉ đường", h_book="Vé &amp; trang chính thức", h_nav="Chỉ đường: lộ trình từ chỗ bạn đang đứng",
                lead_book="Quét mã QR bằng camera điện thoại để mở trang. Trong PDF bạn cũng có thể chạm vào liên kết.",
                lead_nav="Mở Google Maps với lộ trình tàu và xe buýt từ chỗ bạn đang đứng.",
                open="Mở trong Google Maps",
                fc="Xe buýt cao tốc cũng đặt được trên FUJIYAMA CONNECT, trang đặt vé của Fujikyu (tìm \"FUJIYAMA CONNECT\").")
BN["ms"] = dict(title="Tempah &amp; Navigasi", h_book="Tiket &amp; laman rasmi", h_nav="Navigasi: arah dari tempat anda berada",
                lead_book="Imbas kod QR dengan kamera telefon untuk membuka halaman. Dalam PDF anda juga boleh ketik pautan.",
                lead_nav="Membuka Google Maps dengan arah pengangkutan awam dari tempat anda sekarang.",
                open="Buka dalam Google Maps",
                fc="Bas lebuh raya juga boleh ditempah di FUJIYAMA CONNECT, laman tempahan Fujikyu sendiri (cari \"FUJIYAMA CONNECT\").")

BOOK_NAMES["th"] = {"jre": ("JR-EAST Train Reservation", "จอง Fuji Excursion เป็นภาษาอังกฤษ"), "ekinet": ("Eki-net (JR East)", "จอง Fuji Excursion (ภาษาญี่ปุ่น)"),
                    "hwb": ("Highway Bus.com", "จองรถบัสทางด่วนจากบัสตะชินจูกุ"), "fkrail": ("Fujikyu Railway", "ตารางเวลา ค่าโดยสาร Mt. FUJI Passport"),
                    "fkbus": ("Fujikyu Bus", "รถบัสท่องเที่ยว ตารางเวลา บัตรโดยสาร"), "fujiq": ("Fuji-Q Highland", "บัตรเล่นและปฏิทินวันเปิด"),
                    "motosuko": ("Fuji Motosuko Resort", "กล้องถ่ายทอดสดและเทศกาลชิบะซากุระ")}
BOOK_NAMES["vi"] = {"jre": ("JR-EAST Train Reservation", "Đặt Fuji Excursion bằng tiếng Anh"), "ekinet": ("Eki-net (JR East)", "Đặt Fuji Excursion (tiếng Nhật)"),
                    "hwb": ("Highway Bus.com", "Đặt xe buýt cao tốc từ Busta Shinjuku"), "fkrail": ("Fujikyu Railway", "Lịch tàu, giá vé, Mt. FUJI Passport"),
                    "fkbus": ("Fujikyu Bus", "Xe buýt tham quan, lịch chạy, vé xe buýt"), "fujiq": ("Fuji-Q Highland", "Vé trò chơi và lịch mở cửa"),
                    "motosuko": ("Fuji Motosuko Resort", "Camera trực tiếp và lễ hội Shibazakura")}
BOOK_NAMES["ms"] = {"jre": ("JR-EAST Train Reservation", "Tempah Fuji Excursion dalam bahasa Inggeris"), "ekinet": ("Eki-net (JR East)", "Tempah Fuji Excursion (bahasa Jepun)"),
                    "hwb": ("Highway Bus.com", "Tempah bas lebuh raya dari Busta Shinjuku"), "fkrail": ("Fujikyu Railway", "Jadual, tambang, Mt. FUJI Passport"),
                    "fkbus": ("Fujikyu Bus", "Bas pelancongan, jadual, pas bas"), "fujiq": ("Fuji-Q Highland", "Pas permainan dan kalendar operasi"),
                    "motosuko": ("Fuji Motosuko Resort", "Kamera langsung dan Festival Shibazakura")}

PLACE_NAMES["th"] = ["สถานีคาวากุจิโกะ", "บัสตะชินจูกุ (รถบัสทางด่วน)", "เจดีย์ห้าชั้น (สวนอาราคุระยามะเซ็นเง็น)", "สวนโออิชิ", "โอชิโนะฮักไก",
                     "กระเช้าพาโนรามาภูเขาไฟฟูจิ", "ไซโกะอิยาชิโนะซาโตะเนมบะ", "สถานีที่ 5 ฟูจิซูบารุไลน์", "ฟูจิคิวไฮแลนด์",
                     "ทะเลสาบโมโตสึ (ใกล้โคอันโซ)", "โรงแรมรอยัลคาวากุจิโกะ (รอยสักได้)", "ฟูจิโจโบโนะยุ ยูราริ"]
PLACE_NAMES["vi"] = ["Ga Kawaguchiko", "Busta Shinjuku (xe buýt cao tốc)", "Chùa 5 tầng (công viên Arakurayama Sengen)", "Công viên Oishi", "Oshino Hakkai",
                     "Cáp treo toàn cảnh núi Phú Sĩ", "Saiko Iyashi-no-Sato Nenba", "Trạm 5 Fuji Subaru Line", "Fuji-Q Highland",
                     "Hồ Motosu (gần Koansō)", "Royal Hotel Kawaguchiko (có hình xăm vẫn được)", "Fuji Choubou no Yu Yurari"]
PLACE_NAMES["ms"] = ["Stesen Kawaguchiko", "Busta Shinjuku (bas lebuh raya)", "Pagoda Chureito (Taman Arakurayama Sengen)", "Taman Oishi", "Oshino Hakkai",
                     "Kereta Kabel Panorama Gunung Fuji", "Saiko Iyashi-no-Sato Nenba", "Stesen ke-5 Fuji Subaru Line", "Fuji-Q Highland",
                     "Tasik Motosu (dekat Koansō)", "Royal Hotel Kawaguchiko (tatu dibenarkan)", "Fuji Choubou no Yu Yurari"]

SRC_KEYWORDS = {  # words that mark a "where this was checked" note
    "zh-hans": ["官网", "官方", "电话", "Google"],
    "zh-hant": ["官網", "官方", "電話", "Google"],
    "ko": ["공식", "전화로 확인", "Google"],
    "th": ["ทางการ", "ยืนยันทางโทรศัพท์", "Google"],
    "vi": ["chính thức", "Xác nhận qua điện thoại", "xác nhận qua điện thoại", "Google"],
    "ms": ["rasmi", "Disahkan melalui telefon", "disahkan melalui telefon", "Google"],
}

NEWPAGE_H3 = {
    "zh-hans": ["什么时候真的能看到富士山？", "实用日语"],
    "zh-hant": ["什麼時候真的能看到富士山？", "實用日語"],
    "ko": ["후지산은 언제 보일까?", "쓸모 있는 일본어 한마디"],
    "th": ["เห็นภูเขาไฟฟูจิได้เมื่อไหร่?", "ประโยคภาษาญี่ปุ่นที่ใช้ได้"],
    "vi": ["Khi nào thật sự nhìn thấy núi Phú Sĩ?", "Câu tiếng Nhật hữu ích"],
    "ms": ["Bilakah Gunung Fuji benar-benar kelihatan?", "Frasa Jepun berguna"],
}

_TW_FIXES = [("富士迴游", "富士回遊"), ("富士回游", "富士回遊"), ("本棲湖", "本栖湖"), ("捲心菜", "高麗菜"), ("網上", "網路上"),
             ("檢票口", "剪票口"), ("烏冬", "烏龍")]


def to_hant(obj):
    conv = opencc.OpenCC("s2twp")

    def c(s):
        s = conv.convert(s)
        for a, b in _TW_FIXES:
            s = s.replace(a, b)
        return s

    def walk(o):
        if isinstance(o, str):
            return c(o)
        if isinstance(o, list):
            return [walk(x) for x in o]
        if isinstance(o, tuple):
            return tuple(walk(x) for x in o)
        if isinstance(o, dict):
            return {k: walk(v) for k, v in o.items()}
        return o
    return walk(obj)


for _table in (TEXT, FINDER, MAP_LABELS, BN, BOOK_NAMES, PLACE_NAMES):
    _table["zh-hant"] = to_hant(_table["zh-hans"])
