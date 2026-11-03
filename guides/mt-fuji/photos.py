"""Photos used in the guide (from Wikimedia Commons, same as the photo prototype guide_v1).

Tama confirmed on 2026-11-03 that all of these photos may be used. Keep the credits page:
CC BY needs the credit line, CC BY-SA asks that changed versions keep the same licence.
The highway bus photo is shown with its destination sign (Kofu Station) and number plate blurred.
"""
import pathlib

DIR = pathlib.Path(__file__).parent / "photos"

# key: (file, author, licence, used for, has recognisable people?)
PHOTOS = {
    "cover":   ("cover-pagoda.jpg", "Dang Son", "CC0", "Cover", False),
    "chureito": ("chureito.jpg", "Supanut Arunoprayote", "CC BY 4.0", "Place 1 · Course B", False),
    "lake":    ("lake-dusk.jpg", "lumoplank", "CC0", "Chapter 1 · Place 2", False),
    "spring":  ("lake-spring.jpg", "Midori", "CC BY 3.0", "Chapter 3 · Quick map", False),
    "oshino":  ("oshino.jpg", "lumoplank", "CC0", "Place 3", False),
    "ropeway": ("ropeway.jpg", "sergejf", "CC BY 2.0", "Course finder · Place 4 · Course A", False),
    "nenba":   ("nenba.jpg", "sergejf", "CC BY 2.0", "Place 5", False),
    "fifth":   ("fifth-station.jpg", "Fabio Achilli", "CC BY 2.0", "Place 6", True),
    "fujiq":   ("fujiq.jpg", "663highland", "CC BY-SA 4.0", "Place 7 · Book & navigate", False),
    "motosu":  ("motosu.jpg", "Supanut Arunoprayote", "CC BY 4.0", "Know before you go · Place 8", False),
    "train":   ("fuji-excursion.jpg", "MaedaAkihiko", "CC0", "Chapter 2", False),
    "bus":     ("highway-bus.jpg", "Cassiopeia sweet", "Public domain", "Chapter 2 · Highway bus", False),
    "station": ("kawaguchiko-station.jpg", "Seloloving", "CC BY 4.0", "Chapter 6", False),
    "hoto":    ("hoto.jpg", "GiveMeMollusks", "CC0", "Chapter 5", True),
    "udon":    ("yoshida-udon.jpg", "Ocdp", "CC0", "Chapter 5", False),
    "itchiku": ("museum-itchiku.jpg", "江戸村のとくぞう", "CC BY-SA 4.0", "Chapter 4 · Course C", True),
    "music":   ("museum-music-forest.jpg", "江戸村のとくぞう", "CC BY-SA 4.0", "Course C", True),
}

OPENER = {"ESSENTIALS": "motosu", "FINDER": "ropeway", 1: "lake", 2: "train", 3: "spring", 4: "itchiku",
          5: ["hoto", "udon"], 6: "station", "BOOK": "fujiq", "MAP": "spring"}
PLACES = ["chureito", "lake", "oshino", "ropeway", "nenba", "fifth", "fujiq", "motosu"]
COURSES = [["ropeway"], ["chureito"], ["itchiku", "music"]]
FOOD = [None, None]
CH2 = [None, "bus"]


def src(key):
    return (DIR / PHOTOS[key][0]).as_uri()
