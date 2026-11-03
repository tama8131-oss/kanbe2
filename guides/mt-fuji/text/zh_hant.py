# Traditional Chinese (Taiwan wording), converted from text/zh_hans.py with OpenCC + place-name fixes (i18n.to_hant).
import i18n
from text.zh_hans import T as _T


def _fix(o):
    if isinstance(o, str):
        return o.replace("餺飥面", "餺飥麵").replace("蕎麥面", "蕎麥麵").replace("加面", "加麵")
    if isinstance(o, list):
        return [_fix(x) for x in o]
    if isinstance(o, tuple):
        return tuple(_fix(x) for x in o)
    if isinstance(o, dict):
        return {k: _fix(v) for k, v in o.items()}
    return o


T = _fix(i18n.to_hant(_T))
