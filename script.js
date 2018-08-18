"use strict";


function download(content, type, filename) {
    var body =  document.getElementsByTagName("body")[0];

    var old = document.getElementById("downloadlink");
    if (old) {
        body.removeChild(old);
    }

    var a = document.createElement("a");
    var blob = new File([content], filename, {"type":type});
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.id = "downloadlink";
    body.appendChild(a);

    a.click();
}


function save_button() {
    var data = [];

    var sets = document.querySelectorAll(".set");
    for (var i = 0; i < sets.length; i++) {
        var set_data = {};
        set_data["code"]  = sets[i].id.split("_")[1];
        set_data["title"] = sets[i].dataset.title;
        set_data["cards"] = {};

        var checks = sets[i].querySelectorAll(".card input");
        for (var j = 0; j < checks.length; j++) {
            set_data["cards"][checks[j].id] = checks[j].checked;
        }

        data.push(set_data);
    }

    var file_data = {
        "version" : "2",
        "sets" : data
    };

    var file_text = JSON.stringify(file_data, null, "\t");

    var have = document.querySelector("#totalcount .checked").innerHTML;
    download(file_text, "application/json", "mtg-land_" + have + ".json");
}


function update_complete(set_code, set_have, set_total) {
    if (set_have === set_total) {
        document.getElementById("set_" + set_code).classList.add("complete");
        document.getElementById("toc_" + set_code).classList.add("complete");
    }
    else {
        document.getElementById("set_" + set_code).classList.remove("complete");
        document.getElementById("toc_" + set_code).classList.remove("complete");
    }
}


function update_set_counter(set_code, set_have, set_total) {
    if (set_total === null) {
        set_total = parseInt(document.querySelector("#set_" + set_code + " .total").innerHTML, 10);
    }

    document.querySelector("#set_" + set_code + " .checked").innerHTML = set_have;
    document.querySelector("#set_" + set_code + " .total").innerHTML   = set_total;

    document.querySelector("#toc_" + set_code + " .checked").innerHTML = set_have;
    document.querySelector("#toc_" + set_code + " .total").innerHTML   = set_total;

    document.querySelector("#toc_" + set_code + " .meter").style.height = "" + (100 * set_have / set_total) + "%";

    update_complete(set_code, set_have, set_total);
}


function update_all_counter(have, total) {
    document.querySelector("#totalcount .checked").innerHTML = have;
    if (!(total === null)) {
        document.querySelector("#totalcount .total").innerHTML   = total;
    }
}


function load_file(file) {
    document.getElementById("reset").click();
    var reader = new FileReader();
    reader.addEventListener("load", function(event) {
        var data = JSON.parse(event.target.result);
        if (Array.isArray(data)) {
            load_v1_file(data);
        }
        else if (Object.prototype.toString.call(data) === "[object Object]" && data["version"] === "2") {
            load_v2_file(data);
        }
    });
    reader.readAsText(file);
}


function load_v1_file(data) {
    var have = 0;
    var itp_warning = false;

    for (var i in data) {
        var set_code = data[i]["code"];

        if (set_code in window.set_code_v1_to_v2) { // translaste changed set codes from v1 to v2
            var set_code_v2 = window.set_code_v1_to_v2[set_code]
            set_code = set_code_v2;
        }

        if (document.getElementById("set_" + set_code) !== null) {
            var set_total = 0;
            var set_have = 0;

            for (var card_code_v1 in data[i]["cards"]) {
                var card_code = card_code_v1;

                var card_split = card_code_v1.split("_");
                var card_color = card_split[0];
                var card_set = card_split[1];
                var card_num = card_split[2];

                if (card_set in window.set_code_v1_to_v2) { // translaste changed set codes from v1 to v2
                    card_set = window.set_code_v1_to_v2[card_set];
                    card_code = card_color + "_" + card_set + "_" + card_num;
                }

                if (card_code_v1 in window.card_code_v1_to_v2) { // translaste individual changed card codes from v1 to v2
                    card_code = window.card_code_v1_to_v2[card_code_v1];
                }

                if (set_code === "BFZ" && card_code_v1.endsWith("b")) { // translate BFZ cards (v2 doesn't use "b" codes)
                    card_code = card_code_v1.slice(0, -1);
                }
                else if (set_code === "ZEN" && parseInt(card_num, 10) >= 250) { // translate ZEN cards (v2 uses "a" codes for half-art)
                    card_code = card_color + "_" + set_code + "_" + (parseInt(card_num, 10) - 20) + "a";
                }
                else if (set_code === "CST") { // translate CST cards (v2 starts at a different number)
                    card_code = card_color + "_" + set_code + "_" + (parseInt(card_num, 10) + 321);
                }
                else if (set_code === "ITP" && card_code.endsWith("?")) { // ITP is missing some cards in v2
                    if (data[i]["cards"][card_code_v1]) {
                        console.log("Checked card missing: " + card_code_v1)
                        itp_warning = true;
                    }
                    continue;
                }

                var checkbox = document.getElementById(card_code);
                checkbox.checked = data[i]["cards"][card_code_v1];

                if (checkbox.checked) {
                    have += 1;
                    set_have += 1;
                }
                set_total += 1;
            }

            update_set_counter(set_code, set_have, null);
        }
    }

    update_all_counter(have, null);

    if (itp_warning) {
        alert("Notice: mtg-land v2 is currently missing some cards from the Introductory Two-Player Set (ITP) which were checked off in the loaded save file.");
    }
}


function load_v2_file(data) {
    var sets = data["sets"];

    var have = 0;

    for (var i in sets) {
        var set_code = sets[i]["code"];

        if (document.getElementById("set_" + set_code) !== null) {
            var set_have = 0;

            for (var card_code in sets[i]["cards"]) {
                var checkbox = document.getElementById(card_code);
                checkbox.checked = sets[i]["cards"][card_code];

                if (checkbox.checked) {
                    have += 1;
                    set_have += 1;
                }
            }

            update_set_counter(set_code, set_have, null);
        }
    }

    update_all_counter(have, null);
}


function checkbox_click(target) {
    var total_before = parseInt(document.querySelector("#totalcount .checked").innerHTML, 10);
    var total_have;

    var set_code = target.id.split("_")[1];
    var set_query = "#set_" + set_code + " .checked";
    var set_before = parseInt(document.querySelector(set_query).innerHTML, 10);
    var set_total  = parseInt(document.querySelector("#set_" + set_code + " .total").innerHTML, 10);
    var set_have;

    if (target.checked) {
        total_have = total_before + 1;
        set_have = set_before + 1;
    }
    else {
        total_have = total_before - 1;
        set_have = set_before - 1;
    }

    update_all_counter(total_have, null);
    update_set_counter(set_code, set_have, set_total);
    update_complete(set_code, set_have, set_total);
}


function toggle_set_collapse(target) {
    var start = performance.now();

    var container = $(target).closest(".collapsible");
    var collapse = $(container).find(".collapsible_content").first();
    if (container.hasClass("group")) {
        collapse.toggle();
    }
    else {
        collapse.slideToggle(200);
    }
    container.toggleClass("collapsed");

    console.log(performance.now() - start);
}


function toc_entry_click(target) {
    var set_id = $(target.closest("li")).find("a")[0].href.split("#")[1];
    var set_element = $("#" + set_id);
    var group_element = set_element.closest(".group");

    group_element.find(".collapsible_content").first().show();
    set_element.find(".collapsible_content").show();
    group_element.removeClass("collapsed");
    set_element.removeClass("collapsed");
}


function reset_button() {
    $(".checked").html("0");
    $(".complete").removeClass("complete");
    $(".meter").css("height", 0);
}


function setup_counters() {
    var sets = document.getElementsByClassName("set");
    var total = 0;
    var have = 0;

    for (var i = 0; i < sets.length; i++) {
        var checks = sets[i].querySelectorAll(".card > input");
        var set_total = 0;
        var set_have = 0;

        for (var j = 0; j < checks.length; j++) {
            checks[j].addEventListener("click", function(event) {
                checkbox_click(event.target);
            });

            if (checks[j].checked) {
                have += 1;
                set_have += 1;
            }
            total += 1;
            set_total += 1;
        }

        update_set_counter(sets[i].id.split("_")[1], set_have, set_total);
    }
    update_all_counter(have, total);
}


var xhr = new XMLHttpRequest();
xhr.onreadystatechange = function() {
    if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);
            window.set_code_v1_to_v2 = data["set_code_v1_to_v2"];
            window.card_code_v1_to_v2 = data["card_code_v1_to_v2"];
        }
        else {
            alert("Error loading data: " + xhr.status);
        }
    }
}
xhr.open("GET", "v1_to_v2_translations.json");
xhr.send();


document.addEventListener("DOMContentLoaded", function(event) {
    document.getElementById("save").addEventListener("click", save_button);

    document.getElementById("load").addEventListener("change", function(event) {
        load_file(event.target.files[0]);
    });

    document.getElementById("reset").addEventListener("click", reset_button);

    setup_counters();

    var toggles = document.getElementsByClassName("toggle");
    for (var i = 0; i < toggles.length; i++) {
        toggles[i].addEventListener("click", function(event) {
            toggle_set_collapse(event.target);
        });
    }

    var toc_entries = document.querySelectorAll("#toc li");
    for (var i = 0; i < toc_entries.length; i++) {
        toc_entries[i].addEventListener("click", function(event) {
            toc_entry_click(event.target);
        });
    }
});
