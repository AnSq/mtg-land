#!/usr/bin/env python


import os
import cPickle as pickle

import order


html_header = """\
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>MTG Basic Land</title>
        <link href="styles.css" rel="stylesheet" />
        <!--<script src="script.js"></script>-->
    </head>
    <body>
        <table>
            <tbody>
"""


html_footer = """
            </tbody>
        </table>
    </body>
</html>
"""

set_order = list(reversed(order.set_order))


def main():
    sets = {}

    for i in os.listdir("images"):
        color, set_code, card_num = i.replace(".jpg","").split("_")
        if set_code not in sets:
            sets[set_code] = {c:[] for c in "WUBRG"}
        sets[set_code][color].append(card_num)

    for s in sets:
        for c in sets[s]:
            sets[s][c].sort(key=order.natural_order)

    with open("titles.pickle") as f:
        titles = pickle.load(f)

    body = ""

    total = 0

    for set_code in set_order:
        body += "<tr><td>{set_code} - {set_title}</td>".format(set_code=set_code, set_title=titles[set_code])
        for color in "WUBRG":
            for card_num in sets[set_code][color]:
                card_code = "%s_%s_%s" % (color, set_code, card_num)
                fname = "images/%s.jpg" % card_code
                body += '<td><div><img src="{fname}" title="{alt}" />{alt}</div></td>'.format(fname=fname, card_code=card_code, alt=card_code.replace("_"," "))
                total += 1
        body += "</tr>\n"

    html = html_header + body + html_footer

    with open("land.html", "w") as f:
        f.write(html)

    print "Processed", total


if __name__ == "__main__":
    main()
