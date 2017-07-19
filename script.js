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

    var file_text = JSON.stringify(data, null, "\t");

    download(file_text, "application/json", "mtg-land.json");
}


function update_complete(set_code, set_have, set_total) {
    if (set_have === set_total) {
        document.getElementById("set_" + set_code).classList.add("complete");
    }
    else {
        document.getElementById("set_" + set_code).classList.remove("complete");
    }
}


function update_set_counter(set_code, set_have, set_total) {
    document.querySelector("#set_" + set_code + " .checked").innerHTML = set_have;
    document.querySelector("#set_" + set_code + " .total").innerHTML   = set_total;
    update_complete(set_code, set_have, set_total);
}


function update_all_counter(have, total) {
    document.querySelector("#totalcount .checked").innerHTML = have;
    document.querySelector("#totalcount .total").innerHTML   = total;
}


function load_file(file) {
    var reader = new FileReader();
    reader.addEventListener("load", function(event) {
        var total = 0;
        var have = 0;

        var data = JSON.parse(event.target.result);
        for (var i in data) {
            var set_total = 0;
            var set_have = 0;

            for (var j in data[i]["cards"]) {
                var checkbox = document.getElementById(j);
                checkbox.checked = data[i]["cards"][j];

                if (checkbox.checked) {
                    have += 1;
                    set_have += 1;
                }
                total += 1;
                set_total += 1;
            }

            update_set_counter(data[i]["code"], set_have, set_total);
        }

        update_all_counter(have, total);
    });
    reader.readAsText(file);
}


function checkbox_click(target) {
    var before = parseInt(document.querySelector("#totalcount .checked").innerHTML, 10);

    var set_code = target.id.split("_")[1];
    var set_query = "#set_" + set_code + " .checked";
    var set_before = parseInt(document.querySelector(set_query).innerHTML, 10);
    var set_total  = parseInt(document.querySelector("#set_" + set_code + " .total").innerHTML, 10);
    var set_have;

    if (target.checked) {
        document.querySelector("#totalcount .checked").innerHTML = before + 1;
        set_have = set_before + 1;
        document.querySelector(set_query).innerHTML              = set_have;
    }
    else {
        document.querySelector("#totalcount .checked").innerHTML = before - 1;
        set_have = set_before - 1;
        document.querySelector(set_query).innerHTML              = set_have;
    }

    update_complete(set_code, set_have, set_total);
}


function reset_button() {
    var counters = document.getElementsByClassName("checked");
    for (var i = 0; i < counters.length; i++) {
        counters[i].innerHTML = 0;
    }

    var sets = document.getElementsByClassName("set");
    for (var i = 0; i < sets.length; i++) {
        sets[i].classList.remove("complete");
    }
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


document.addEventListener("DOMContentLoaded", function(event) {
    document.getElementById("save").addEventListener("click", save_button);

    document.getElementById("load").addEventListener("change", function(event) {
        load_file(event.target.files[0]);
    });

    document.getElementById("reset").addEventListener("click", reset_button);

    setup_counters();
});
