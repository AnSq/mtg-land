#!/usr/bin/env python3
#coding: utf-8

import json
import time
import datetime
import urllib.parse
import itertools
import re
import os
import sys
import math

import requests
from PIL import Image

import consts


session = requests.Session()



class Card:
    def __init__(self, raw):
        self.raw = raw


    def __getattr__(self, attr):
        return self.raw[attr]


    def color(self):
        return consts.name_to_color[self.name.split()[-1]]


    def id(self):
        return "{}_{}_{}".format(self.color(), caps_set_code(self.set), self.collector_number)


    def image_fname(self):
        return "{}.jpg".format(self.id())


    def download_image(self):
        url = self.image_uris["normal"]
        fname = os.path.join(consts.image_download_dir, self.image_fname())
        print("{} -> {}".format(url, fname.encode("utf-8")))

        with session.get(url, stream=True) as r:
            with open(fname, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)


class CardSet:
    def __init__(self, raw):
        self.raw = raw


    def __getattr__(self, attr):
        return self.raw[attr]


    def __str__(self):
        return "CardSet<{}>".format(self.code)


    def group(self):
        return consts.set_type_to_group[self.set_type]



class UpdateInfo:
    def __init__(self):
        self.old_size = 0
        self.new_size = 0
        self.updated = False


    def __str__(self):
        return "<old:{0.old_size}, new:{0.new_size}, updated:{0.updated}, diff:{1}>".format(self, self.diff())


    def diff(self):
        return self.new_size - self.old_size



def load_data(fname, update_function, ask_for_update, update_info=None, force_update=False):
    """Load a data file if it exists, and prompt for update. If it doesn't exist, fetch it."""

    data = None

    if os.path.isfile(fname):
        with open(fname) as f:

            data = json.load(f)

            if update_info:
                update_info.old_size = len(data["data"])

            updated = datetime.datetime.strptime(data["last_updated"], consts.time_format)
            now = time_now()
            days_since_update = (now - updated).total_seconds() / (60*60*24)

            if ask_for_update:
                if ask("{} last updated {:.1f} days ago. Refresh?".format(fname, days_since_update), False, True if force_update else None):
                    data = update_function()
                    save_data(data, fname)
                    if update_info:
                        update_info.updated = True
            else:
                print("{} last updated {:.1f} days ago.".format(fname, days_since_update))
    else:
        data = update_function()
        save_data(data, fname)
        if update_info:
            update_info.updated = True

    if update_info:
        update_info.new_size = len(data["data"])

    print("{}: {} items".format(fname, len(data["data"])))
    return data


def load_cards(ask_for_update=True, update_info=None, force_update=False):
    """Load card data"""
    cards = load_data(consts.cards_fname, get_cards, ask_for_update, update_info, force_update)
    for i,card in enumerate(cards["data"]):
        cards["data"][i] = Card(card)
    return cards


def load_sets(ask_for_update=True, update_info=None, force_update=False):
    """Load set data"""
    sets = load_data(consts.sets_fname, get_sets, ask_for_update, update_info, force_update)
    for set_code in sets["data"]:
        sets["data"][set_code] = CardSet(sets["data"][set_code])
    return sets


def save_data(data, fname):
    with open(fname, "w") as f:
        json.dump(data, f, sort_keys=True, indent=2, default=lambda x: x.raw)
    print("Saved data to {}".format(fname))


def get_cards():
    """Download card data"""
    params = "?" + urllib.parse.urlencode({"q": consts.card_query, "order": "released"})
    next_page = consts.api_root + consts.search_endpoint + params
    total_cards = None

    cards = {
        "last_updated": time_now().strftime(consts.time_format),
        "data": []
    }

    page = 1
    while True:
        print("Getting cards page {}".format(page))
        r = session.get(next_page)
        j = json.loads(r.text)

        # make sure the number of cards didn't change part way through
        assert j["total_cards"] == total_cards or total_cards is None
        total_cards = j["total_cards"]

        print_warnings(j, page)

        for card in j["data"]:
            for field in consts.ignored_card_fields:
                del card[field]

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
    print("Getting sets")
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


def show_new_sets(sets):
    old_used_sets = set()
    if os.path.isfile(consts.used_sets_fname):
        with open(consts.used_sets_fname) as f:
            old_used_sets = set([tuple(x) for x in json.load(f)])

    used_sets = set([(s,sets["data"][s].released_at) for s in sets["data"]])
    new_used_sets = used_sets - old_used_sets
    new_set_codes = [caps_set_code(x[0]) for x in sorted(list(new_used_sets), key=lambda x: x[1], reverse=True)]

    if new_set_codes:
        print("New sets found: {}".format(", ".join(new_set_codes)))
    else:
        print("No new sets found.")

    save_data(list(used_sets), consts.used_sets_fname)
    with open(consts.new_sets_fname, "w") as f:
        for s in new_set_codes:
            f.write(s + "\n")



def download_card_images(cards, update_info=None):
    mkdir_if_not_exists(consts.image_download_dir)

    existing_images = []
    missing_images = []

    for i,card in enumerate(cards["data"]):
        if os.path.exists(os.path.join(consts.image_download_dir, card.image_fname())):
            existing_images.append(i)
        else:
            missing_images.append(i)

    download_images = missing_images

    print("{} missing card images will be downloaded.".format(len(missing_images)))
    if existing_images:
        if ask("Would you also like to redownload {} existing card images?".format(len(existing_images)), False):
            download_images += existing_images
            download_images.sort()

    if update_info:
        update_info.old_size = len(existing_images)
        update_info.new_size = len(cards["data"])
        if len(download_images):
            update_info.updated = True

    for i in download_images:
        cards["data"][i].download_image()


def build_card_sheets(cards, force_update=False):
    if not ask("(Re)build card sheets?", False, True if force_update else None):
        return

    mkdir_if_not_exists(consts.sheets_dir)

    with Image.open(os.path.join(consts.image_download_dir, (cards["data"][0]).image_fname())) as card_im:
        card_width = int(consts.scaled_width)
        card_height = int(consts.scaled_width * card_im.height / card_im.width)

    card_colors = {c:[] for c in consts.colors}
    for card in reversed(cards["data"]):
        color = card.color()
        card_colors[color].append(card)

    coords = []

    with open(consts.cards_css_fname, "w", encoding="utf-8") as f:
        for color in consts.colors:
            print("{}...".format(color))

            sheet_fname = os.path.join(consts.sheets_dir, color + ".jpg")

            num_cards = len(card_colors[color])
            sheet_width = int(math.ceil(math.sqrt(num_cards+1)))
            sheet_height = sheet_width
            while sheet_width * (sheet_height - 1) >= num_cards + 1:
                sheet_height -= 1

            sheet_width_px = sheet_width * card_width
            sheet_height_px = sheet_height * card_height

            print("\t{} total cards".format(num_cards))
            print("\t{}x{} cards".format(sheet_width, sheet_height))
            print("\t{}x{} pixels".format(sheet_width_px, sheet_height_px))

            f.write(consts.sheet_css.sheet.format(color=color.lower(), width=sheet_width_px, height=sheet_height_px))

            im = Image.new("RGB", (sheet_width_px, sheet_height_px), consts.sheet_background_color)

            for j,card in enumerate(card_colors[color]):
                i = j + 1
                card_fname = os.path.join(consts.image_download_dir, card.image_fname())

                x_card_offset = i %  sheet_width
                y_card_offset = i // sheet_width

                x_pixel_offset = x_card_offset * card_width
                y_pixel_offset = y_card_offset * card_height

                coords.append((card.id(), x_pixel_offset, y_pixel_offset))

                with Image.open(card_fname) as card_im:
                    scaled_height = consts.scaled_width * card_im.height / card_im.width
                    card_resized_im = card_im.resize((int(consts.scaled_width), int(scaled_height)), Image.BICUBIC)
                    im.paste(card_resized_im, (x_pixel_offset, y_pixel_offset))

            im.save(sheet_fname, quality=consts.jpeg_quality, optimize=True)

        for c in coords:
            f.write(consts.sheet_css.card.format(card_id=c[0], x_offset=c[1], y_offset=c[2]))


def generate_land_html(cards, sets):
    print("Assembling land.html")

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
                "set_title"  : sets["data"][set_code].name
            }

            toc  += consts.land_html.toc_entry.format(**set_info)
            body += consts.land_html.set_title.format(**set_info)

            for color in consts.colors:
                for card in organized_cards[set_code][color]:
                    body += consts.land_html.card.format(card_id=card.id(), alt=card.id().replace("_"," "), color=color.lower())
                    total += 1
            body += consts.land_html.set_end

        toc += consts.land_html.toc_group_footer
        body += consts.land_html.set_group_footer

    html = consts.land_html.header.format(toc=toc.strip()) + body + consts.land_html.footer

    with open("land.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Processed", total)


def generate_placeholders(cards, sets):
    placeholders = {color : {group[0] : [] for group in consts.group_names_and_order} for color in consts.colors}

    organized_cards = cards_by_set_and_color(cards)

    for set_code in set_order(sets):
        for color in consts.colors:
            if organized_cards[set_code][color] == []:
                continue

            ph = {
                "color"        : color,
                "group"        : sets["data"][set_code].group(),
                "set_code"     : set_code,
                "set_name"     : sets["data"][set_code].name,
                "release_date" : sets["data"][set_code].released_at,
                "numbers"      : [c.collector_number for c in organized_cards[set_code][color]]
            }
            group = sets["data"][set_code].group()
            placeholders[color][group].append(ph)

    return placeholders


def generate_placeholders_html(placeholders):
    form = consts.placeholder_html.form_header

    form += consts.placeholder_html.thead_start
    for group in consts.group_names_and_order:
        form += consts.placeholder_html.header_cell.format(group_name=group[1].replace(" ","<br>"), group=group[0])
    form += consts.placeholder_html.thead_end

    form += consts.placeholder_html.tbody_start
    for color in consts.colors:
        form += consts.placeholder_html.table_row_start.format(color_name=consts.color_names[color], color=color)
        for group in consts.group_names_and_order:
            checkbox_id = "{}_{}".format(color, group[0])
            checked_disabled = "checked" if len(placeholders[color][group[0]]) else "disabled"
            form += consts.placeholder_html.table_cell.format(checkbox_id=checkbox_id, color=color, group=group[0], checked_disabled=checked_disabled)
        form += consts.placeholder_html.table_row_end
    form += consts.placeholder_html.tbody_end

    form += consts.placeholder_html.form_footer

    body = ""
    for ph in itertools.chain.from_iterable([placeholders[color][group[0]] for color in consts.colors for group in consts.group_names_and_order]):
        body += consts.placeholder_html.card.format(
            color        = ph["color"],
            group_id     = ph["group"],
            card_name    = consts.color_to_name[ph["color"]],
            group_name   = group_name(ph["group"]),
            set_symbol   = set_symbol(ph["set_code"]),
            set_name     = ph["set_name"],
            set_code     = caps_set_code(ph["set_code"]),
            release_date = ph["release_date"],
            card_numbers = ", ".join(ph["numbers"])
        )

    html = consts.placeholder_html.header + form + body + consts.placeholder_html.footer

    with open(consts.placeholders_html_fname, "w", encoding="utf-8") as f:
        f.write(html)


def find_invalid_sets(sets):
    """Return set() of mtg sets that are online-only or non-tournament-legal"""
    result = []
    for set_code in sorted(sets["data"].keys()):
        s = sets["data"][set_code]
        if s.digital or s.set_type == "memorabilia":
            result.append(s.code)
    return set(result)


def prune_invalid_cards(cards, sets):
    """Modify cards, removing, in-place, invalid cards.
    This should never do anything because the card_query should filter them out before we ever see them"""
    inv = find_invalid_sets(sets)

    for card in cards["data"]:
        if card.set in inv:
            print("{} {} #{}".format(card.set, card.name, card.collector_number))

    count_before = len(cards["data"])
    cards["data"][:] = filter(lambda c: c.set not in inv, cards["data"])
    if len(cards["data"]) != count_before:
        print("WARNING: {} invalid cards were detected and removed from the card list".format(count_before - len(cards["data"])))

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

    print("Pruned {} unused sets".format(count_before - len(sets["data"])))

    return sets


def fix_release_dates(sets):
    """Modifies the input param to add release dates to sets that are missing them and correct release dates that are wrong"""
    for set_code in sets["data"]:
        if "released_at" not in sets["data"][set_code].raw:
            if set_code in consts.missing_release_dates:
                sets["data"][set_code].raw["released_at"] = consts.missing_release_dates[set_code]
            else:
                print("WARNING: Set '{}' has no release date and is not in missing_release_dates".format(set_code))
        else:
            if set_code in consts.missing_release_dates:
                print("WARNING: Set '{}' has a release date ({}) and is in missing_release_dates ({}). missing_release_dates will be ignored.".format(set_code, sets["data"][set_code].released_at, consts.missing_release_dates[set_code]))
            elif set_code in consts.corrected_release_dates:
                if sets["data"][set_code].released_at == consts.corrected_release_dates[set_code]:
                    print("INFO: Release date for set '{}' matches its corrected_release_dates ({})".format(set_code, sets["data"][set_code].released_at))
                else:
                    print("Using release date {} instead of {} for set '{}'".format(consts.corrected_release_dates[set_code], sets["data"][set_code].released_at, set_code))
                    sets["data"][set_code].released_at = consts.corrected_release_dates[set_code]

    return sets


def find_card_sets(cards):
    """Return a set() of mtg sets that we have cards of"""
    result = set()
    for card in cards["data"]:
        result.add(card.set)
    return result


def cards_by_set_and_color(cards):
    """arranges cards into a structure of the form {set_code : {color : [card] } }, where [card] is a list of cards sorted by the natural order of their collector numbers"""
    result = {}

    for card in cards["data"]:
        color = card.color()
        set_code = card.set
        if set_code not in result:
            result[set_code] = {c:[] for c in consts.colors}
        result[set_code][color].append(card)

    for set_code in result:
        for color in result[set_code]:
            result[set_code][color].sort(key=lambda card: [(int(group) if group.isdigit() else group) for group in re.split("(\d+)", card.collector_number)])

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


def group_name(group):
    return dict(consts.group_names_and_order)[group]


def set_order(sets, group=None):
    return [
        s.code
        for s
        in sorted(
            list(sets["data"].values()),
            key=lambda x: (
                x.released_at,
                consts.dda_order_fix[x.code] if x.code in consts.dda_order_fix else 0,
                x.code
            ),
            reverse=True
        )
        if (consts.set_type_to_group[s.set_type] == group or group is None)
    ]


def print_warnings(data, page):
    """Print any warnings that may exist in a Scryfall list response"""
    if "warnings" in data:
        for w in data["warnings"]:
            print("WARNING (page {}): {}".format(page, w))


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


def ask(question, default, override=None):
    y = "Y" if default else "y"
    n = "n" if default else "N"
    if override is None:
        response = input(question + " ({}/{}): ".format(y, n))
        return len(response) and response[0].lower() == "y"
    else:
        print("{} ({}/{}): {} [override]".format(question, y, n, "yes" if override else "no"))
        return override


def main():
    sets_update = UpdateInfo()
    sets = load_sets(update_info=sets_update)

    cards = load_cards(force_update=bool(sets_update.diff()))

    cards = prune_invalid_cards(cards, sets)
    sets = prune_unused_sets(cards, sets)
    sets = fix_release_dates(sets)
    save_data(sets, "sets2.json")

    show_new_sets(sets)

    images_update = UpdateInfo()
    download_card_images(cards, images_update)

    build_card_sheets(cards, force_update=images_update.diff() or images_update.updated)
    generate_land_html(cards, sets)

    placeholders = generate_placeholders(cards, sets)
    generate_placeholders_html(placeholders)


if __name__ == "__main__":
    main()
