#!/usr/bin/env python
#coding: utf-8

import requests
import json
import time
import datetime
import urllib
import itertools
import re
import os
import sys
import math
from PIL import Image

from pprint import pprint as pp


class Consts (object):
    """a plain object to store some stuff"""
    pass


consts = Consts()

consts.time_format = "%Y-%m-%d %H:%M:%S"

consts.api_root = "https://api.scryfall.com"
consts.search_endpoint = "/cards/search"
consts.sets_endpoint = "/sets"

consts.cards_fname = "cards.json"
consts.sets_fname = "sets.json"
consts.image_download_dir = "images_dl"
consts.image_scaled_dir = "images_scaled"
consts.sheets_dir = "card_sheets"
consts.cards_css_fname = "cards.css"
consts.placeholders_html_fname = "placeholders.html"

consts.scaled_width = 140.0
consts.jpeg_quality = 85
consts.sheet_background_color = (0, 0, 0)

consts.card_query = "t:basic in:paper unique:prints lang:en -is:digital -s:CED -s:CEI -s:PTC -border:gold -s:RQS"
# RQS lands are indistinguishable from 4th edition

consts.ignored_card_fields = (
    "cmc",
    "color_identity",
    "colors",
    "colorshifted",
    "digital",
    "futureshifted",
    "lang",
    "layout",
    "legalities",
    "mana_cost",
    "multiverse_ids",
    "object",
    "oracle_id",
    "oracle_text",
    "oversized",
    "prints_search_uri",
    "purchase_uris",
    "related_uris",
    "reprint",
    "reserved",
    "rulings_uri",
    "set_search_uri",
    "timeshifted"
)
consts.ignored_set_fields = (
    "object",
    "search_uri"
)
consts.missing_release_dates = {
    "cst":   "2006-07-21",
    "j14":   "2014-08-00",
    "pal00": "2000-00-00",
    "pal01": "2001-00-00",
    "pal02": "2002-00-00",
    "pal03": "2003-00-00",
    "pal04": "2004-00-00",
    "pal05": "2005-00-00",
    "pal06": "2006-00-00",
    "pal99": "1999-00-00",
    "palp":  "1998-09-00",
    "parl":  "1996-00-00",
    "pdgm":  "2013-04-27",
    "pelp":  "2000-02-05",
    "pgp17": "2017-10-00",
    "pgpx":  "2018-00-00",
    "pgru":  "1999-07-12",
    "phuk":  "2006-00-00",
    "pss2":  "2017-09-29",
    "pss3":  "2018-07-13"
}
consts.set_symbol_translation = {
    "cst"   : "ice",
    "dd1"   : "evg",
    "dvd"   : "ddc",
    "gvl"   : "ddd",
    "itp"   : "x2ps",
    "j14"   : "pmei",
    "jvc"   : "dd2",
    "pal00" : "mmq",
    "pal01" : "parl2",
    "pal02" : "parl2",
    "pal03" : "parl",
    "pal04" : "parl",
    "pal05" : "parl",
    "pal06" : "parl",
    "pal99" : "usg",
    "palp"  : "papac",
    "parl"  : "pmtg1",
    "pdgm"  : "dgm",
    "pelp"  : "peuro",
    "pgp17" : "pmei",
    "pgpx"  : "pmei",
    "phuk"  : "psalvat05",
    "pss2"  : "pmei",
    "pss3"  : "pmei",
    "sum"   : "psum",
}
consts.name_to_color = {
    "Plains"   : "W",
    "Island"   : "U",
    "Swamp"    : "B",
    "Mountain" : "R",
    "Forest"   : "G",
    "Wastes"   : "C"
}
consts.color_to_name = {v:k for k,v in consts.name_to_color.items()}
consts.colors = "WUBRGC"
consts.set_type_to_group = {
    "core"             : "standard",
    "expansion"        : "standard",
    "archenemy"        : "special_format",
    "planechase"       : "special_format",
    "draft_innovation" : "special_format",
    "commander"        : "special_format",
    "box"              : "other",
    "starter"          : "other",
    "premium_deck"     : "other",
    "funny"            : "un_sets",
    "promo"            : "promo",
    "duel_deck"        : "duel_deck",
}
consts.group_names_and_order = [
    ("standard"       , "Standard"),
    ("special_format" , "Special Formats"),
    ("duel_deck"      , "Duel Decks"),
    ("promo"          , "Promos"),
    ("un_sets"        , "Un-Sets"),
    ("other"          , "Other"),
]

consts.sheet_css = Consts()
consts.sheet_css.sheet = ".card.color_{color} .img {{background-size: {width}px {height}px;}}\n"
consts.sheet_css.card = "#{card_code} + label > .img {{background-position: -{x_offset}px -{y_offset}px;}}\n"

consts.land_html = Consts()
consts.land_html.header = """\
<!DOCTYPE html>
<html lang="en-US">
    <head>
        <meta charset="utf-8">
        <title>MTG Basic Land</title>
        <link href="styles.css" rel="stylesheet" />
        <link href="cards.css" rel="stylesheet" />
        <link href="https://cdn.jsdelivr.net/npm/keyrune@latest/css/keyrune.css" rel="stylesheet" type="text/css" />
        <script src="https://code.jquery.com/jquery-3.3.1.min.js" integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
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
                {toc}
            </div>
            <div id="sets">
"""
consts.land_html.toc_group_header = """\
                <div class="toc_group">
                    <h3>{group_name}</h3>
                    <ul>
"""
consts.land_html.toc_group_footer = """\
                    </ul>
                </div>
"""
consts.land_html.toc_entry = """\
                        <li id="toc_{set_code}">
                            <a href="#set_{set_code}" title="{set_title}">
                                <div><i class="ss ss-{set_symbol}"></i></div>
                                <div>{set_code}</div>
                                <div class="count"><span class="checked">?</span>/<span class="total">?</span></div>
                            </a>
                            <div class="meter"></div>
                        </li>
"""
consts.land_html.set_group_header = """\
                <div class="group" id="group_{group_id}">
                    <div class="collapsible_header">
                        <h2>{group_name}</h2>
                        <span class="toggle">▼</span>
                        <a class="top_link" href="#">↑</a>
                    </div>
                    <div class="collapsible_content">
"""
consts.land_html.set_group_footer = """\
                    </div>
                </div>
"""
consts.land_html.set_title = """\
                        <div class="set" id="set_{set_code}" data-title="{set_title}">
                            <div class="collapsible_header">
                                <h3 class="set_title"><i class="ss ss-{set_symbol}"></i> {set_code} - {set_title}</h3>
                                <span class="toggle">▼</span>
                                <span class="count"><span class="checked">?</span> / <span class="total">?</span></span>
                                <a class="top_link" href="#">↑</a>
                            </div>
                            <div class="collapsible_content">
"""
consts.land_html.card = """\
                                <div class="card color_{color}">
                                    <input type="checkbox" id="{card_code}" name="{card_code}">
                                    <label for="{card_code}"><span class="img"></span></label>
                                    <span>{alt}</span>
                                </div>
"""
consts.land_html.set_end = """\
                            </div>
                        </div>
"""
consts.land_html.footer = """\
            </div>
        </form>
    </body>
</html>
"""

consts.placeholder_html = Consts()
consts.placeholder_html.header = """\
<!DOCTYPE html>
<html lang="en-US">
    <head>
        <meta charset="utf-8">
        <title>MTG Land Placeholder Cards</title>
        <link href="placeholder_styles.css" rel="stylesheet" />
        <link href="https://cdn.jsdelivr.net/npm/keyrune@latest/css/keyrune.css" rel="stylesheet" type="text/css" />
    </head>
    <body>"""
consts.placeholder_html.footer = """
    </body>
</html>
"""
consts.placeholder_html.card = """\
            <div class="card">
                <div class="card_1">
                    <div class="card_body">
                        <p class="type">{card_name}</p>
                        <div class="card_center">
                            <p class="symbol"><i class="ss ss-{set_symbol}"></i></p>
                            <p class="title">{set_name}</p>
                            <p class="set">({set_code})</p>
                        </div>
                        <p class="range">{card_numbers}</p>
                    </div>
                </div>
            </div>"""
consts.placeholder_html.page_start = '\n        <div class="page">'
consts.placeholder_html.page_end = '\n        </div>'
consts.placeholder_html.cards_per_page = 9


session = requests.Session()


def load_data(fname, update_function, ask_for_update):
    """Load a data file if it exists, and prompt for update. If it doesn't exist, fetch it."""

    data = None

    if os.path.isfile(fname):
        with open(fname) as f:

            data = json.load(f)

            updated = datetime.datetime.strptime(data["last_updated"], consts.time_format)
            now = time_now()
            days_since_update = (now - updated).total_seconds() / (60*60*24)

            if ask_for_update:
                do_update = raw_input("{} last updated {:.1f} days ago. Refresh? (y/N): ".format(fname, days_since_update))
                if len(do_update) and do_update[0] == "y":
                    data = update_function()
                    save_data(data, fname)
            else:
                print "{} last updated {:.1f} days ago.".format(fname, days_since_update)
    else:
        data = update_function()
        save_data(data, fname)

    print "{}: {} items".format(fname, len(data["data"]))
    return data


def load_cards(ask_for_update=True):
    """Load card data"""
    cards = load_data(consts.cards_fname, get_cards, ask_for_update)
    for card in cards["data"]:
        card["collector_number"] = card["collector_number"].encode("utf-8")
    return cards


def load_sets(ask_for_update=True):
    """Load set data"""
    return load_data(consts.sets_fname, get_sets, ask_for_update)


def save_data(data, fname):
    with open(fname, "w") as f:
        json.dump(data, f, sort_keys=True, indent=2)
    print "Saved data to {}".format(fname)


def get_cards():
    """Download card data"""
    params = "?" + urllib.urlencode({"q": consts.card_query, "order": "released"})
    next_page = consts.api_root + consts.search_endpoint + params
    total_cards = None

    cards = {
        "last_updated": time_now().strftime(consts.time_format),
        "data": []
    }

    page = 1
    while True:
        print "Getting cards page {}".format(page)
        r = session.get(next_page)
        j = json.loads(r.text)

        # make sure the number of cards didn't change part way through
        assert j["total_cards"] == total_cards or total_cards is None
        total_cards = j["total_cards"]

        print_warnings(j, page)

        for card in j["data"]:
            for field in consts.ignored_card_fields:
                del card[field]

            #card["collector_number"] = card["collector_number"].encode("utf-8")

            cards["data"].append(card)

        if j["has_more"]:
            next_page = j["next_page"]
            page += 1
            time.sleep(0.1)
        else:
            break

    return cards


def get_sets():
    """Download set data"""
    print "Getting sets"
    next_page = consts.api_root + consts.sets_endpoint

    sets = {
        "last_updated": time_now().strftime(consts.time_format),
        "data" : {}
    }

    page = 1
    while True:
        r = session.get(next_page)
        j = json.loads(r.text)

        print_warnings(j, page)

        for s in j["data"]:
            for field in consts.ignored_set_fields:
                del s[field]
            sets["data"][s["code"]] = s

        if j["has_more"]:
            next_page = j["next_page"]
            page += 1
            time.sleep(0.1)
        else:
            break

    return sets


def download_card_images(cards):
    mkdir_if_not_exists(consts.image_download_dir)

    existing_images = []
    missing_images = []

    for i,card in enumerate(cards["data"]):
        if os.path.exists(os.path.join(consts.image_download_dir, card_image_fname(card))):
            existing_images.append(i)
        else:
            missing_images.append(i)

    download_images = missing_images

    print "{} missing card images will be downloaded.".format(len(missing_images))
    if existing_images:
        do_update = raw_input("Would you also like to update {} existing card images? [y/N]: ".format(len(existing_images)))
        if len(do_update) and do_update[0] == "y":
            download_images += existing_images
            download_images.sort()

    for i in download_images:
        download_card_image(cards["data"][i])


def download_card_image(card):
    url = card["image_uris"]["normal"]
    fname = os.path.join(consts.image_download_dir, card_image_fname(card))
    print "{} -> {}".format(url, fname)

    with session.get(url, stream=True) as r:
        with open(fname, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)


def build_card_sheets(cards):
    mkdir_if_not_exists(consts.sheets_dir)

    with Image.open(os.path.join(consts.image_download_dir, card_image_fname(cards["data"][0]))) as card_im:
        card_width = int(consts.scaled_width)
        card_height = int(consts.scaled_width * card_im.height / card_im.width)

    card_colors = {c:[] for c in consts.colors}
    for card in reversed(cards["data"]):
        color = card_color(card)
        card_colors[color].append(card)

    coords = []

    with open(consts.cards_css_fname, "w") as f:
        for color in consts.colors:
            print "{}...".format(color)

            sheet_fname = os.path.join(consts.sheets_dir, color + ".jpg")

            num_cards = len(card_colors[color])
            sheet_width = int(math.ceil(math.sqrt(num_cards+1)))
            sheet_height = sheet_width
            while sheet_width * (sheet_height - 1) >= num_cards + 1:
                sheet_height -= 1

            sheet_width_px = sheet_width * card_width
            sheet_height_px = sheet_height * card_height

            print "\t{} total cards".format(num_cards)
            print "\t{}x{} cards".format(sheet_width, sheet_height)
            print "\t{}x{} pixels".format(sheet_width_px, sheet_height_px)

            f.write(consts.sheet_css.sheet.format(color=color.lower(), width=sheet_width_px, height=sheet_height_px))

            im = Image.new("RGB", (sheet_width_px, sheet_height_px), consts.sheet_background_color)

            for j,card in enumerate(card_colors[color]):
                i = j + 1
                card_fname = os.path.join(consts.image_download_dir, card_image_fname(card))

                x_card_offset = i %  sheet_width
                y_card_offset = i // sheet_width

                x_pixel_offset = x_card_offset * card_width
                y_pixel_offset = y_card_offset * card_height

                coords.append((card_code(card), x_pixel_offset, y_pixel_offset))

                with Image.open(card_fname) as card_im:
                    scaled_height = consts.scaled_width * card_im.height / card_im.width
                    card_resized_im = card_im.resize((int(consts.scaled_width), int(scaled_height)), Image.BICUBIC)
                    im.paste(card_resized_im, (x_pixel_offset, y_pixel_offset))

            im.save(sheet_fname, quality=consts.jpeg_quality, optimize=True)

        for c in coords:
            f.write(consts.sheet_css.card.format(card_code=c[0], x_offset=c[1], y_offset=c[2]))


def generate_land_html(cards, sets):
    print "Assembling land.html"

    organized_cards = cards_by_set_and_color(cards)

    toc = ""
    body = ""

    total = 0

    for group in consts.group_names_and_order:
        toc += consts.land_html.toc_group_header.format(group_name=group[1])
        body += consts.land_html.set_group_header.format(group_name=group[1], group_id=group[0])
        for set_code in set_order(sets, group[0]):
            set_info = {
                "set_symbol" : set_symbol(set_code),
                "set_code"   : caps_set_code(set_code),
                "set_title"  : sets["data"][set_code]["name"]
            }

            toc  += consts.land_html.toc_entry.format(**set_info)
            body += consts.land_html.set_title.format(**set_info)

            for color in consts.colors:
                for card in organized_cards[set_code][color]:
                    body += consts.land_html.card.format(card_code=card_code(card), alt=card_code(card).replace("_"," "), color=color.lower())
                    total += 1
            body += consts.land_html.set_end

        toc += consts.land_html.toc_group_footer
        body += consts.land_html.set_group_footer

    html = consts.land_html.header.format(toc=toc.strip()) + body + consts.land_html.footer

    with open("land.html", "w") as f:
        f.write(html)

    print "Processed", total


def generate_placeholders(cards, sets):
    placeholders = []

    organized_cards = cards_by_set_and_color(cards)

    for set_code in set_order(sets):
        for color in consts.colors:
            if organized_cards[set_code][color] == []:
                continue

            ph = {
                "color" : color,
                "set_code" : set_code,
                "set_name" : sets["data"][set_code]["name"],
                "numbers" : [c["collector_number"] for c in organized_cards[set_code][color]]
            }
            placeholders.append(ph)

    return placeholders


def generate_placeholders_html(placeholders):
    body = consts.placeholder_html.page_start
    n = 0

    for ph in placeholders:
        body += "\n" + consts.placeholder_html.card.format(
            card_name=consts.color_to_name[ph["color"]],
            set_symbol=set_symbol(ph["set_code"]),
            set_name=ph["set_name"],
            set_code=caps_set_code(ph["set_code"]),
            card_numbers=", ".join(ph["numbers"])
        )
        n += 1
        if n % consts.placeholder_html.cards_per_page == 0:
            body += consts.placeholder_html.page_end + consts.placeholder_html.page_start

    body += consts.placeholder_html.page_end

    html = consts.placeholder_html.header + body + consts.placeholder_html.footer

    with open(consts.placeholders_html_fname, "w") as f:
        f.write(html)


def find_invalid_sets(sets):
    """Return set() of mtg sets that are online-only or non-tournament-legal"""
    result = []
    for set_code in sorted(sets["data"].keys()):
        s = sets["data"][set_code]
        if s["digital"] or s["set_type"] == "memorabilia":
            #print (s["code"], s["name"], s["digital"], s["set_type"])
            result.append(s["code"])
    return set(result)


def prune_invalid_cards(cards, sets):
    """Modify cards, removing, in-place, invalid cards.
    This should never do anything because the card_query should filter them out before we ever see them"""
    inv = find_invalid_sets(sets)

    for card in cards["data"]:
        if card["set"] in inv:
            print "{} {} #{}".format(card["set"], card["name"], card["collector_number"])

    count_before = len(cards["data"])
    cards["data"][:] = itertools.ifilter(lambda c: c["set"] not in inv, cards["data"])
    if len(cards["data"]) != count_before:
        print "WARNING: {} invalid cards were detected and removed from the card list".format(count_before - len(cards["data"]))

    return cards


def prune_unused_sets(cards, sets):
    """Modify sets, removing, in-place, sets we have no cards of.
    Unlike prune_invalid_cards(), this actually does something"""
    used_sets = find_card_sets(cards)

    to_delete = []
    for set_code in sets["data"]:
        if set_code not in used_sets:
            to_delete.append(set_code)

    count_before = len(sets["data"])
    for set_code in to_delete:
        del sets["data"][set_code]

    print "Pruned {} unused sets".format(count_before - len(sets["data"]))

    return sets


def fix_missing_release_dates(sets):
    """Modifies the input param to add release dates to sets that are missing them"""
    for set_code in sets["data"]:
        if "released_at" not in sets["data"][set_code]:
            if set_code in consts.missing_release_dates:
                sets["data"][set_code]["released_at"] = consts.missing_release_dates[set_code]
            else:
                print "WARNING: Set '{}' has no release date and is not in missing_release_dates".format(set_code)
        elif set_code in consts.missing_release_dates:
            print "WARNING: Set '{}' has a release date ({}) and is in missing_release_dates ({})".format(set_code, sets["data"][set_code]["released_at"], consts.missing_release_dates[set_code])

    return sets


def find_card_sets(cards):
    """Return a set() of mtg sets that we have cards of"""
    result = set()
    for card in cards["data"]:
        result.add(card["set"])
    return result


def cards_by_set_and_color(cards):
    """arranges cards into a structure of the form {set_code : {color : [card] } }, where [card] is a list of cards sorted by the natural order of their collector numbers"""
    result = {}

    for card in cards["data"]:
        color = card_color(card)
        set_code = card["set"]
        if set_code not in result:
            result[set_code] = {c:[] for c in consts.colors}
        result[set_code][color].append(card)

    for set_code in result:
        for color in result[set_code]:
            result[set_code][color].sort(key=lambda card: [(int(group) if group.isdigit() else group) for group in re.split("(\d+)", card["collector_number"])])

    return result


def caps_set_code(code):
    if len(code) >= 4 and code[0] == "p":
        return code[0] + code[1:].upper()
    else:
        return code.upper()


def set_symbol(set_code):
    if set_code in consts.set_symbol_translation:
        return consts.set_symbol_translation[set_code]
    else:
        return set_code


def card_code(card):
    return "{}_{}_{}".format(card_color(card), caps_set_code(card["set"]), card["collector_number"])


def card_image_fname(card):
    return "{}.jpg".format(card_code(card))


def card_color(card):
    return consts.name_to_color[card["name"].split()[-1]]


def set_order(sets, group=None):
    return [
        s["code"]
        for s
        in sorted(
            sets["data"].values(),
            key=lambda x: x["released_at"],
            reverse=True
        )
        if (consts.set_type_to_group[s["set_type"]] == group or group is None)
    ]


def print_warnings(data, page):
    """Print any warnings that may exist in a Scryfall list response"""
    if "warnings" in data:
        for w in data["warnings"]:
            print "WARNING (page {}): {}".format(page, w)


def parse_time(time_string):
    return datetime.datetime.strptime(time_string, consts.time_format)


def time_now():
    return datetime.datetime.now()


def mkdir_if_not_exists(dirname):
    if not os.path.exists(dirname):
        os.mkdir(dirname)


def cr():
    """carriage return and clear line"""
    sys.stdout.write("\r\x1b[K")


def write_percentage(i, total, prefix=""):
    """print a progress tracker"""
    cr()
    if prefix:
        sys.stdout.write(prefix + " ")
    sys.stdout.write("%d/%d - %.2f%%" % (i+1, total, float(i+1)*100/total))
    sys.stdout.flush()


def _set_symbol_test(sets):
    with open("symbol-test.html", "w") as f:
        f.write("""<!DOCTYPE html>
            <html>
                <head>
                    <meta charset="utf-8">
                    <title>Symbol Test</title>
                    <link href="https://cdn.jsdelivr.net/npm/keyrune@latest/css/keyrune.css" rel="stylesheet" type="text/css" />
                </head>
                <body>
                    <ul>""")
        for s in sorted(sets["data"].keys()):
            f.write('<li><i class="ss ss-{}"></i> {} {}</li>'.format(set_symbol(s), caps_set_code(s), sets["data"][s]["name"]))
        f.write("""</ul>
                </body>
            </html>""")


def _set_code_translation_table(sets):
    import cPickle as pickle
    with open("../titles.pickle") as f:
        titles = pickle.load(f)

    diff = {}
    for code in titles:
        diff[titles[code]] = {"old":code}
    for s in sets["data"].values():
        if s["name"] in diff:
            diff[s["name"]]["new"] = caps_set_code(s["code"])
        else:
            diff[s["name"]] = {"new": caps_set_code(s["code"])}
    to_del = []
    for name in diff:
        if "new" in diff[name] and "old" in diff[name] and diff[name]["new"] == diff[name]["old"]:
            to_del.append(name)
    for name in to_del:
        del diff[name]

    print "{:6}  ->  {:6}  {}".format("old", "new", "name")
    for name in sorted(diff.keys()):
        print "{:6}  ->  {:6}  {}".format(diff[name]["old"] if "old" in diff[name] else "", diff[name]["new"] if "new" in diff[name] else "", name)


def _set_types(sets):
    pp(set([x["set_type"] for x in sets["data"].values()]))

    t = {}
    for s in sets["data"].values():
        if s["set_type"] not in t:
            t[s["set_type"]] = []
        t[s["set_type"]].append(caps_set_code(s["code"]))
    pp(t)


def main():
    cards = load_cards()
    sets = load_sets()

    cards = prune_invalid_cards(cards, sets)
    sets = prune_unused_sets(cards, sets)
    sets = fix_missing_release_dates(sets)
    save_data(sets, "sets2.json")

    download_card_images(cards)

    build_card_sheets(cards)
    generate_land_html(cards, sets)

    placeholders = generate_placeholders(cards, sets)
    generate_placeholders_html(placeholders)


if __name__ == "__main__":
    main()
