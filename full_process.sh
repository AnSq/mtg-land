#!/bin/bash

python get.py
python download.py
python titles.py
./shrink.sh images
python sheet.py images
python html.py
python placeholders.py
python placeholder_html.py
