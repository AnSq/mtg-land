#!/bin/bash

python get.py
read -p "Press any key to continue... " -n 1 -s; echo
python download.py
python titles.py
./shrink.sh images
python sheet.py images
python html.py
python placeholders.py
python placeholder_html.py
