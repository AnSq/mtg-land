#!/usr/bin/env python3
#coding: utf-8

class Consts:
    """a plain object to store some stuff"""
    pass


time_format = "%Y-%m-%d %H:%M:%S"

api_root = "https://api.scryfall.com"
search_endpoint = "/cards/search"
sets_endpoint = "/sets"

cards_fname = "cards.json"
sets_fname = "sets.json"
image_download_dir = "images_dl"
sheets_dir = "card_sheets"
cards_css_fname = "cards.css"
placeholders_html_fname = "placeholders.html"

scaled_width = 140
jpeg_quality = 85
sheet_background_color = (0, 0, 0)

card_query = "t:basic in:paper unique:prints lang:en -is:digital -s:CED -s:CEI -s:PTC -border:gold -s:RQS"
# RQS lands are indistinguishable from 4th edition

ignored_card_fields = (
    "cmc",
    "color_identity",
    "colors",
    "digital",
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
    "set_search_uri"
)
ignored_set_fields = (
    "object",
    "search_uri"
)
missing_release_dates = {
    "pgp17": "2017-10-00"
}
corrected_release_dates = {
    "j14":   "2014-08-04",
    "pgpx":  "2018-00-00",
}
set_symbol_translation = {
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
dda_order_fix = {
    "evg" : 1,
    "jvc" : 2,
    "dvd" : 3,
    "gvl" : 4
}
name_to_color = {
    "Plains"   : "W",
    "Island"   : "U",
    "Swamp"    : "B",
    "Mountain" : "R",
    "Forest"   : "G",
    "Wastes"   : "C"
}
color_to_name = {v:k for k,v in name_to_color.items()}
colors = "WUBRGC"
color_names = {
    "W" : "White",
    "U" : "Blue",
    "B" : "Black",
    "R" : "Red",
    "G" : "Green",
    "C" : "Colorless"
}
set_type_to_group = {
    "core"             : "standard",
    "expansion"        : "standard",
    "archenemy"        : "special_format",
    "planechase"       : "special_format",
    "draft_innovation" : "special_format",
    "commander"        : "special_format",
    "box"              : "other",
    "starter"          : "other",
    "premium_deck"     : "other",
    "funny"            : "un_set",
    "promo"            : "promo",
    "duel_deck"        : "duel_deck",
}
group_names_and_order = [
    ("standard"       , "Standard"),
    ("special_format" , "Special Formats"),
    ("duel_deck"      , "Duel Decks"),
    ("promo"          , "Promos"),
    ("un_set"         , "Un-Sets"),
    ("other"          , "Other"),
]

sheet_css = Consts()
sheet_css.sheet = ".card.color_{color} .img {{background-size: {width}px {height}px;}}\n"
sheet_css.card = "#{card_id} + label > .img {{background-position: -{x_offset}px -{y_offset}px;}}\n"

land_html = Consts()
land_html.header = """\
<!DOCTYPE html>
<html lang="en-US">
    <head>
        <meta charset="utf-8">
        <title>MTG Basic Land</title>
        <link href="/favicon.ico" rel="icon">
        <link href="styles.css" rel="stylesheet">
        <link href="cards.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/keyrune@latest/css/keyrune.css" rel="stylesheet" type="text/css">
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
land_html.toc_group_header = """\
                <div class="toc_group">
                    <h3>{group_name}</h3>
                    <ul>
"""
land_html.toc_group_footer = """\
                    </ul>
                </div>
"""
land_html.toc_entry = """\
                        <li id="toc_{set_code}">
                            <a href="#set_{set_code}" title="{set_title}">
                                <div><i class="ss ss-{set_symbol}"></i></div>
                                <div>{set_code}</div>
                                <div class="count"><span class="checked">?</span>/<span class="total">?</span></div>
                            </a>
                            <div class="meter"></div>
                        </li>
"""
land_html.set_group_header = """\
                <div class="group collapsible" id="group_{group_id}">
                    <div class="collapsible_header">
                        <h2>{group_name}</h2>
                        <span class="toggle">▼</span>
                        <a class="top_link" href="#">↑</a>
                    </div>
                    <div class="collapsible_content">
"""
land_html.set_group_footer = """\
                    </div>
                </div>
"""
land_html.set_title = """\
                        <div class="set collapsible" id="set_{set_code}" data-title="{set_title}">
                            <div class="collapsible_header">
                                <h3 class="set_title"><i class="ss ss-{set_symbol}"></i> {set_code} - {set_title}</h3>
                                <span class="toggle">▼</span>
                                <span class="count"><span class="checked">?</span> / <span class="total">?</span></span>
                                <a class="top_link" href="#">↑</a>
                            </div>
                            <div class="collapsible_content">
"""
land_html.card = """\
                                <div class="card color_{color}">
                                    <input type="checkbox" id="{card_id}" name="{card_id}">
                                    <label for="{card_id}"><span class="img"></span></label>
                                    <span>{alt}</span>
                                </div>
"""
land_html.set_end = """\
                            </div>
                        </div>
"""
land_html.footer = """\
            </div>
        </form>
    </body>
</html>
"""

placeholder_html = Consts()
placeholder_html.header = """\
<!DOCTYPE html>
<html lang="en-US">
    <head>
        <meta charset="utf-8">
        <title>MTG Land Placeholder Cards</title>
        <link href="/favicon.ico" rel="icon">
        <link href="placeholder_styles.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/keyrune@latest/css/keyrune.css" rel="stylesheet" type="text/css">
        <script src="https://code.jquery.com/jquery-3.3.1.min.js" integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
        <script src="placeholder_script.js"></script>
    </head>
    <body>
"""
placeholder_html.footer = """
    </body>
</html>
"""
placeholder_html.form_header = """\
        <form name="form" id="form">
            <table>
"""
placeholder_html.thead_start = """\
                <thead>
                    <tr>
                        <td></td>
"""
placeholder_html.header_cell = """\
                        <th scope="col"><button type="button" id="{group}" name="{group}">{group_name}</button></th>
"""
placeholder_html.thead_end = """\
                    </tr>
                </thead>
"""
placeholder_html.tbody_start = """\
                <tbody>
"""
placeholder_html.table_row_start = """\
                    <tr>
                        <th scope="row"><button type="button" id="{color}" name="{color}">{color_name}</button></th>
"""
placeholder_html.table_cell = """\
                        <td><label><input type="checkbox" id="{checkbox_id}" name="{checkbox_id}" class="{color} {group}" {checked_disabled}></label></td>
"""
placeholder_html.table_row_end = """\
                    </tr>
"""
placeholder_html.tbody_end = """\
                </tbody>
"""
placeholder_html.form_footer = """\
            </table>
        </form>
"""
placeholder_html.card = """\
        <div class="card {color}_{group_id}">
            <div class="card_1">
                <div class="card_body">
                    <p class="type">{card_name}</p>
                    <div class="card_center">
                        <p class="symbol"><i class="ss ss-{set_symbol}"></i></p>
                        <p class="set">{set_code}</p>
                        <p class="title">{set_name}</p>
                        <p class="group">{group_name}</p>
                        <p class="release_date">{release_date}</p>
                    </div>
                    <p class="range">{card_numbers}</p>
                </div>
            </div>
        </div>
"""
