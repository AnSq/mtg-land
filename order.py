#!/usr/bin/env python

import re

natural_order = lambda text: [(int(group) if group.isdigit() else group) for group in re.split("(\d+)", text)]


set_order = [
    'AL',
    'BE',
    'UN',
    'AN',
    'CED',
    'CEDI',
    'RV',
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
]
