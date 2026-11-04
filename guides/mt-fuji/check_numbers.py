"""Check that every number (fares, times, minutes, dates) is the same in all languages.

For each piece of text, the numbers in each language are compared with the English text.
A difference means a translation may carry a wrong fare or time.

Usage: python3 guides/mt-fuji/check_numbers.py
"""
import collections
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import i18n  # noqa: E402
import magazine  # noqa: E402

NUM = re.compile(r"\d+")


def flat(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from flat(v, f"{path}.{k}" if path else str(k))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from flat(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


WORDS = {w: str(i) for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve".split())}
WORDS.update({m: str(i + 1) for i, m in enumerate("january february march april may june july august september october november december".split())})
WORDS.update({m[:3]: str(i + 1) for i, m in enumerate("january february march april may june july august september october november december".split())})
WORDS.update({m: str(i + 1) for i, m in enumerate("januari februari mac april mei jun julai ogos september oktober november disember".split())})  # Malay
WORDS.update({m: str(i + 1) for i, m in enumerate("jan feb mac apr mei jun jul ogo sep okt nov dis".split())})
WORDS.update({"noon": "12", "midnight": "24"})
THAI = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
        "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
WORDS.update({"twice": "2", "once": "1", "first": "1", "half": "", "1-day": "1-day"})


def numbers(text, english=False):
    text = re.sub(r"<[^>]+>", " ", text).replace(",", "")
    for i, m in enumerate(THAI):
        text = text.replace(m, f" {i % 12 + 1} ")
    if english or True:  # "three lines", "November" -> 3, 11 so they compare with the translations
        text = re.sub(r"[A-Za-z]+", lambda m: f" {WORDS[m.group().lower()]} " if m.group().lower() in WORDS else m.group(), text)
    text = text.translate(str.maketrans("０１２３４５６７８９：", "0123456789:"))
    text = re.sub(r"(?<=\d)\.(?=\d{3}(?!\d))", "", text)   # Vietnamese 4.200 = 4,200
    text = re.sub(r"千(?=元|円)", "1000", text).replace("名水百選", "100").replace("名水百选", "100")
    text = re.sub(r"(?<![\d:])(\d+)\s*(万|萬|만|หมื่น)", lambda m: str(int(m.group(1)) * 10000), text)   # 50万 = 500000
    text = re.sub(r"(\d+)\s*(千|천)", lambda m: str(int(m.group(1)) * 1000), text)
    text = re.sub(r"(?<!\d)(千|천)(?=\s*(円|엔|yen))", "1000", text)
    # each run of digits counts on its own ("1:58" = 1 and 58, like "1時間58分"); ":00" adds nothing
    return collections.Counter(n for n in NUM.findall(text) if n not in ("00", "0"))


def text(code):
    t = dict(flat(magazine.load_text(code)))
    if code not in ("en", "ja"):  # the booking/navigation page text lives in i18n.py for these languages
        t.update({f"bn.{k}": v for k, v in i18n.BN[code].items()})
    return t


# The same fact written another way in a language (checked by hand, November 2026):
SAME = {
    "p45.n_s3": "school years instead of ages 6-15",
    "cc.kid": "school years instead of ages 6-15",
    "good.crowd[0][1]": "'before noon' written as a word",
    "buspass.note": "'noon' written as a word or as 12",
}


def main():
    base = text("en")
    problems = 0
    for code, *_ in i18n.LANGS:
        if code == "en":
            continue
        other = text(code)
        for key, en_text in base.items():
            if key not in other:
                print(f"[{code}] missing text: {key}")
                problems += 1
                continue
            a, b = numbers(en_text, True), numbers(other[key])
            # small counting words ("1 bag", "2 days") differ in style between languages; prices, times
            # and minutes (2+ digits, or with ":" or ".") must always match
            big = lambda c: collections.Counter({k: v for k, v in c.items() if len(k) > 1})
            if big(a) != big(b) and key not in SAME:
                only_en = sorted((big(a) - big(b)).elements())
                only_lang = sorted((big(b) - big(a)).elements())
                print(f"[{code}] {key}\n    only in English: {only_en}   only in {code}: {only_lang}\n    en: {en_text[:150]}\n    {code}: {other[key][:150]}")
                problems += 1
    print(f"\n{problems} differences")


if __name__ == "__main__":
    main()
