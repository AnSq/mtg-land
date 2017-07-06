#!/usr/bin/env python

import sys
import requests
from pyquery import PyQuery as pq

import order


def main():
    titles = ""
    for s in order.set_order:
        r = requests.get("http://magiccards.info/%s/en.html" % s.lower())
        d = pq(r.text)

        title = s.upper().ljust(8) + d("title")[0].text
        titles += title + "\n"
        print title

    with open("titles.txt", "w") as f:
        f.write(titles)


if __name__ == "__main__":
    main()
