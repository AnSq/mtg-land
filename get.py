#!/usr/bin/env python

import requests
from pyquery import PyQuery as pq
import cPickle as pickle
import multiprocessing
import sys


def get_base():
    basics = ["plains", "island", "swamp", "mountain", "forest"]
    base = []
    for basic in basics:
        print basic
        r = requests.get("http://magiccards.info/query?q=!%s" % basic)
        d = pq(r.text)
        d.make_links_absolute("http://magiccards.info")
        l = d("body > table > tr:nth-child(1) > td:nth-child(2) > span:nth-child(1) > a:nth-child(1)")
        base.append(l[0].attrib["href"])
    return base


def process_set_link(link):
    global queue

    set_code = link.split("/")[3]

    print link
    r = requests.get(link)

    d = pq(r.text)
    comment = d("body table:nth-child(7) td:nth-child(3) p:nth-child(2) span b")
    if comment and comment[0].text == "ONLY AVAILABLE ONLINE":
        print "\tSkip %s" % set_code.upper()
        return

    d = pq(r.text)
    d.make_links_absolute("http://magiccards.info")
    l = d("table:nth-child(7) td:nth-child(3) a[href$='.html'][href*='/en/'][href*='/%s/']" % set_code)

    queue.put(link)
    for l in [i.attrib['href'] for i in l]:
        queue.put(l)


def pool_init(q):
    global queue
    queue = q


def main():
    base = get_base()
    images = []
    total = 0

    for b in base:
        set_code = b.split("/")[3]

        print b
        r = requests.get(b)

        d = pq(r.text)
        d.make_links_absolute("http://magiccards.info")
        l = d("table:nth-child(7) td:nth-child(3) a[href$='.html'][href*='/en/']").not_("[href*='/%s/']" % set_code)

        set_links = [b] + [i.attrib['href'] for i in l]

        all_links = []

        queue = multiprocessing.Queue()
        pool = multiprocessing.Pool(32, pool_init, [queue])

        try:
            for link in set_links:
                pool.apply_async(process_set_link, [link])
            pool.close()
        except KeyboardInterrupt:
            pool.terminate()
        pool.join()

        while not queue.empty():
            all_links.append(queue.get())

        color_images = []
        for link in all_links:
            sp = link.split("/")
            set_code = sp[3]
            card_num = sp[5].replace(".html", "")
            color_images.append("http://magiccards.info/scans/en/%s/%s.jpg" % (set_code, card_num))

        images.append(color_images)
        print len(color_images)
        total += len(color_images)

    print "Total: %d" % total

    with open("images.pickle", "w") as f:
        pickle.dump(images, f)

if __name__ == "__main__":
    main()
