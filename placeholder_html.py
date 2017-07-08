#!/usr/bin/env python

import sys


html_header = """\
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>MTG Land Placeholder Cards</title>
        <link href="placeholder_styles.css" rel="stylesheet" />
    </head>
    <body>"""

html_footer = """
    </body>
</html>
"""

card_html = '            <div class="card">\n$body$\n            </div>'

card_body = """\
                <div class="card_1">
                    <div class="card_body">
                        <p class="type">{type}</p>
                        <p class="title">{title}</p>
                        <p class="set">({set})</p>
                        <p class="range">{range}</p>
                    </div>
                </div>"""

page_start = '\n        <div class="page">'
page_end = '\n        </div>'
cards_per_page = 9


def main():
    placeholders = []
    with open("placeholders.txt") as f:
        for line in f:
            if line:
                placeholders.append(line.strip())

    titles = {}
    with open("titles.txt") as f:
        for line in f:
            if line:
                code, title = line.strip().split(" ", 1)
                code = code.strip()
                title = title.strip()
                titles[code] = title

    types = {
        "W": "Plains",
        "U": "Island",
        "B": "Swamp",
        "R": "Mountain",
        "G": "Forest",
    }

    body = page_start
    n = 0

    for p in placeholders:
        body += "\n" + card_html.replace("$body$", card(p, titles, types))
        n += 1
        if n % cards_per_page == 0:
            body += page_end + page_start

    body += page_end

    html = html_header + body + html_footer

    with open("placeholders.html", "w") as f:
        f.write(html)


def card(p, titles, types):
    color_code, set_code, num_range = p.split()
    set_title = titles[set_code]
    color_type = types[color_code]
    num_range = num_range.replace(",", ", ")
    return card_body.format(type=color_type, title=set_title, set=set_code, range=num_range)



if __name__ == "__main__":
    main()