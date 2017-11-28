#!/usr/bin/env python

import os
import re
import subprocess

natural_order = lambda text: [(int(group) if group.isdigit() else group) for group in re.split("(\d+)", text)]


def init_docs():
    if not os.path.exists("docs"):
        os.mkdir("docs")

    for f in ("script.js", "styles.css", "placeholder_styles.css", "blanks.html", "index.html"):
        if not os.path.exists("docs/" + f) or os.path.getmtime(f) > os.path.getmtime("docs/" + f):
            subprocess.call(["cp", f, "docs/"])


set_symbol_translation = {
    "DDAGVL": "ddd",
    "DDADVD": "ddc",
    "DDAJVC": "dd2",
    "DDAEVG": "evg",
    "JR"    : "pmei",
    "PTC"   : "dgm",
    "PVC"   : "dde",
    "PDS"   : "h09",
    "GVL"   : "ddd",
    "PCH"   : "hop",
    "DVD"   : "ddc",
    "JVC"   : "dd2",
    "LW"    : "lrw",
    "TS"    : "tsp",
    "CSTD"  : "ice",
    "9E"    : "9ed",
    "UH"    : "unh",
    "MI"    : "mrd",
    "8E"    : "8ed",
    "ON"    : "ons",
    "DM"    : "dkm",
    "OD"    : "ody",
    "7E"    : "7ed",
    "BD"    : "btd",
    "IN"    : "inv",
    "EURO"  : "peuro",
    "BR"    : "brb",
    "MM"    : "mmq",
    "ST"    : "s99",
    "P3K"   : "ptk",
    "6E"    : "6ed",
    "GURU"  : "pgru",
    "AT"    : "ath",
    "US"    : "usg",
    "UG"    : "ugl",
    "APAC"  : "papac",
    "TP"    : "tmp",
    "PO"    : "por",
    "5E"    : "5ed",
    "MR"    : "mir",
    "ARENA" : "parl2",
    "ITP"   : "x2ps",
    "IA"    : "ice",
    "4E"    : "4ed",
    "SUMMER": "psum",
    "RV"    : "3ed",
    "CEDI"  : "xice",
    "CED"   : "xcle",
    "AN"    : "arn",
    "UN"    : "2ed",
    "BE"    : "leb",
    "AL"    : "lea"
}

set_symbol = lambda set_code: set_symbol_translation[set_code] if set_code in set_symbol_translation else set_code.lower()


set_order = [
    'AL',
    'BE',
    'UN',
    'AN',
    'CED',
    'CEDI',
    'RV',
    'SUMMER',
    '4E',
    'IA',
    'ITP',
    'ARENA',
    'MR',
    '5E',
    'PO',
    'TP',
    'APAC',
    'PO2',
    'UG',
    'US',
    'AT',
    'GURU',
    '6E',
    'P3K',
    'ST',
    'MM',
    'BR',
    'EURO',
    'IN',
    'BD',
    '7E',
    'OD',
    'DM',
    'ON',
    '8E',
    'MI',
    'CHK',
    'UH',
    '9E',
    'RAV',
    'CSTD',
    'TS',
    '10E',
    'LW',
    'EVG',
    'SHM',
    'ALA',
    'JVC',
    'DVD',
    'M10',
    'PCH',
    'ZEN',
    'GVL',
    'PDS',
    'PVC',
    'ROE',
    'DPA',
    'ARC',
    'M11',
    'DDF',
    'SOM',
    'PD2',
    'MBS',
    'DDG',
    'NPH',
    'CMD',
    'M12',
    'DDH',
    'ISD',
    'PD3',
    'DDI',
    'AVR',
    'PC2',
    'M13',
    'DDJ',
    'RTR',
    'DDK',
    'PTC',
    'M14',
    'DDL',
    'THS',
    'C13',
    'DDM',
    'MD1',
    'M15',
    'JR',
    'DDN',
    'KTK',
    'C14',
    'DDAEVG',
    'DDAJVC',
    'DDADVD',
    'DDAGVL',
    'FRF',
    'DDO',
    'DTK',
    'ORI',
    'DDP',
    'BFZ',
    'C15',
    'DDQ',
    'SOI',
    'DDR',
    'KLD',
    'C16',
    'PCA',
    'DDS',
    'AKH',
    'CMA',
    'E01',
    'HOU',
    'C17',
    'XLN'
]


if __name__ == "__main__":
    init_docs()
