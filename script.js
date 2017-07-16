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


function save() {
    var data = [];

    var sets = document.querySelectorAll(".set");
    for (var i = 0; i < sets.length; i++) {
        var set_data = {};
        set_data["code"]  = sets[i].id;
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


function load_file(file) {
    var reader = new FileReader();
    reader.addEventListener("load", function(event) {
        var total = 0;
        var have = 0;

        var data = JSON.parse(event.target.result);
        for (var i in data) {
            for (var j in data[i]["cards"]) {
                var checkbox = document.getElementById(j);
                checkbox.checked = data[i]["cards"][j];

                if (checkbox.checked) {
                    have += 1;
                }
                total += 1;
            }
        }

        document.getElementById("checked").innerHTML = "" + have;
        document.getElementById("total").innerHTML   = "" + total;
    });
    reader.readAsText(file);
}


function checkbox_click(target) {
    var before = parseInt(document.getElementById("checked").innerHTML, 10);
    if (target.checked) {
        document.getElementById("checked").innerHTML = before + 1;
    }
    else {
        document.getElementById("checked").innerHTML = before - 1
    }
}


document.addEventListener("DOMContentLoaded", function(event) {
    document.getElementById("save").addEventListener("click", save);

    document.getElementById("load").addEventListener("change", function(event) {
        load_file(event.target.files[0]);
    });

    document.getElementById("reset").addEventListener("click", function(event) {
        document.getElementById("checked").innerHTML = "0";
    });

    var checks = document.getElementsByClassName("cardcheck");
    var total = 0;
    var have = 0;
    for (var i = 0; i < checks.length; i++) {
        checks[i].addEventListener("click", function(event) {
            checkbox_click(event.target);
        });

        if (checks[i].checked) {
            have += 1;
        }
        total += 1;
    }
    document.getElementById("total").innerHTML   = "" + total;
    document.getElementById("checked").innerHTML = "" + have;
});
