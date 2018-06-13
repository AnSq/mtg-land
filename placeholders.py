#!/usr/bin/env python

import cPickle as pickle
import sys

import util


def main():
    print >>sys.stderr, "Generating placeholders"

    with open("images.pickle") as f:
        images = pickle.load(f)

    colors = "WUBRG"

    names = []
    for c, color in enumerate(images):
        n = []
        for card in color:
            s, num = card[32:].split(".")[0].split("/")
            s = s.upper()
            names.append((colors[c], s, num))

    with open("names.pickle", "w") as f:
        pickle.dump(names, f)

    org = {}
    for name in names:
        c, s, n = name
        if c not in org:
            org[c] = {}
        if s not in org[c]:
            org[c][s] = []
        org[c][s].append(n)

    placeholders = ""
    total = 0;

    for c in "WUBRG":
        for s in util.set_order:
            if s in org[c]:
                org[c][s] = sorted(org[c][s], key=util.natural_order)

                placeholder = "%s %s %s" % (c, s, ",".join([i for i in org[c][s]]))
                placeholders += placeholder + "\n"
                print placeholder

                total += len(org[c][s])

    with open("placeholders.txt", "w") as f:
        f.write(placeholders)

    print >>sys.stderr, total

    with open("org.pickle", "w") as f:
        pickle.dump(org, f)


if __name__ == "__main__":
    main()
