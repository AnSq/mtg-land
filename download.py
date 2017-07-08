#!/usr/bin/env python

import cPickle as pickle
import urllib
import os
import multiprocessing

save_path = "images"

def main():
    pool = multiprocessing.Pool(32)

    try:
        colors = "WUBRG"

        with open("images.pickle") as f:
            images = pickle.load(f)

        if not os.path.exists(save_path):
            os.mkdir(save_path)

        for i, links in enumerate(images):
            color = colors[i]
            for link in links:
                sp = link.split("/")
                set_code = sp[5].upper()
                card_num = sp[6].replace(".jpg", "")
                fname = "%s_%s_%s.jpg" % (color, set_code, card_num)

                pool.apply_async(download, (link, fname))

        pool.close()

    except KeyboardInterrupt:
        pool.terminate()

    pool.join()


def download(url, fname):
    print "%s -> %s" % (url, fname)
    urllib.urlretrieve(url, save_path + "/" + fname)


if __name__ == "__main__":
    main()
