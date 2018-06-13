#!/usr/bin/env python
#coding=utf8

import os
import cPickle as pickle

import util


header_html = """\
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>MTG Basic Land</title>
        <link href="styles.css" rel="stylesheet" />
        <link href="cards.css" rel="stylesheet" />
        <link href="https://cdn.jsdelivr.net/npm/keyrune@latest/css/keyrune.css" rel="stylesheet" type="text/css" />
        <script src="script.js"></script>
    </head>
    <body>
        <h1>MTG Basic Land</h1>
        <form name="form" id="form">
            <div id="buttons">
                <input type="button" id="save" name="save" value="Save">
                <input type="file" id="load" name="load" accept=".json">
                <input type="reset" id="reset">
                <span id="totalcount" class="count"><span class="checked">?</span> / <span class="total">?</span></span>
            </div>
            <div id="toc">
                <h2>Table of Contents</h2>
                <ul>
                    {toc}
                </ul>
            </div>
"""

toc_entry_html = """\
                    <li><a href="#set_{set_code}" title="{set_title}"><i class="ss ss-{set_symbol}"></i><br>{set_code}</a></li>
"""

set_title_html = """\
            <div class="set" id="set_{set_code}" data-title="{set_title}">
                <h2 class="set_title"><i class="ss ss-{set_symbol}"></i> {set_code} - {set_title}</h2>
                <span class="count"><span class="checked">?</span> / <span class="total">?</span></span>
                <a class="top_link" href="#">↑</a>
                <br>
"""

card_html = """\
                <div class="card color_{color}">
                    <input type="checkbox" id="{card_code}" name="{card_code}">
                    <label for="{card_code}"><div class="img"></div></label>
                    {alt}
                </div>
"""

set_end_html = """\
            </div>
"""

footer_html = """\
        </form>
    </body>
</html>
"""

set_order = list(reversed(util.set_order))


def main():
    print "Assembling land.html"

    util.init_docs()

    sets = {}

    for i in os.listdir("images"):
        color, set_code, card_num = i.replace(".jpg","").split("_")
        if set_code not in sets:
            sets[set_code] = {c:[] for c in "WUBRG"}
        sets[set_code][color].append(card_num)

    for s in sets:
        for c in sets[s]:
            sets[s][c].sort(key=util.natural_order)

    with open("titles.pickle") as f:
        titles = pickle.load(f)

    toc = ""
    body = ""

    total = 0

    for set_code in set_order:
        set_info = {
            "set_symbol" : util.set_symbol(set_code),
            "set_code"   : set_code,
            "set_title"  : titles[set_code]
        }

        toc  += toc_entry_html.format(**set_info)
        body += set_title_html.format(**set_info)

        for color in "WUBRG":
            for card_num in sets[set_code][color]:
                card_code = "%s_%s_%s" % (color, set_code, card_num)
                fname = "images/%s.jpg" % card_code
                body += card_html.format(fname=fname, card_code=card_code, alt=card_code.replace("_"," "), color=color.lower())
                total += 1
        body += set_end_html

    html = header_html.format(toc=toc.strip()) + body + footer_html

    with open("docs/land.html", "w") as f:
        f.write(html)

    print "Processed", total


if __name__ == "__main__":
    main()
