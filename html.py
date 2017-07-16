#!/usr/bin/env python


import os
import cPickle as pickle

import util


html_header = """\
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>MTG Basic Land</title>
        <link href="styles.css" rel="stylesheet" />
        <link href="https://cdn.jsdelivr.net/npm/keyrune@latest/css/keyrune.css" rel="stylesheet" type="text/css" />
        <script src="script.js"></script>
    </head>
    <body>
        <h1>MTG Basic Land</h1>
        <form name="form" id="form">
            <table><tbody>
                <tr>
                    <input type="button" id="save" name="save" value="Save">
                    <input type="file" id="load" name="load" accept=".json">
                    <input type="reset" id="reset">
                    <span id="count"><span id="checked">?</span> / <span id="total">?</span></span>
                </tr>
"""

set_title_html = """\
                <tr class="set" id="{set_code}" data-title="{set_title}">
                    <td class="set_title"><i class="ss ss-{set_symbol}"></i> {set_code} - {set_title}</td>
"""

card_html = """\
                    <td><div class="card color_{color}">
                        <input type="checkbox" id="{card_code}" name="{card_code}" class="cardcheck">
                        <label for="{card_code}"><img src="{fname}" title="{alt}" /></label>
                        {alt}
                    </div></td>
"""

html_footer = """
            </tbody></table>
        </form>
    </body>
</html>
"""

set_order = list(reversed(util.set_order))


def main():
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

    body = ""

    total = 0

    for set_code in set_order:
        body += set_title_html.format(
            set_symbol=util.set_symbol(set_code),
            set_code=set_code,
            set_title=titles[set_code]
        )

        for color in "WUBRG":
            for card_num in sets[set_code][color]:
                card_code = "%s_%s_%s" % (color, set_code, card_num)
                fname = "images/%s.jpg" % card_code
                body += card_html.format(fname=fname, card_code=card_code, alt=card_code.replace("_"," "), color=color.lower())
                total += 1
        body += "\t\t\t\t</tr>\n"

    html = html_header + body + html_footer

    with open("land.html", "w") as f:
        f.write(html)

    print "Processed", total


if __name__ == "__main__":
    main()
