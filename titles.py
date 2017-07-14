#!/usr/bin/env python

import sys
import requests
import cPickle as pickle
from pyquery import PyQuery as pq

import util


def main():
    titles = {}
    for set_code in util.set_order:
        r = requests.get("http://magiccards.info/%s/en.html" % set_code.lower())
        d = pq(r.text)

        title = d("title")[0].text
        print set_code.upper().ljust(8) + title
        titles[set_code] = title

    with open("titles.pickle", "w") as f:
        pickle.dump(titles, f)


if __name__ == "__main__":
    main()
