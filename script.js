"use strict";


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

    var file_text = JSON.stringify(data, null, 4);

    // https://stackoverflow.com/questions/2897619/using-html5-javascript-to-generate-and-save-a-file
    var a = document.createElement("a");
    var blob = new Blob([file_text], {"type":"application/json"});
    a.href = window.URL.createObjectURL(blob);
    a.download = "mtg-land.json";

    var event = document.createEvent('MouseEvents');
    event.initEvent('click', true, true);
    a.dispatchEvent(event);
}


function load_file(file) {
    var reader = new FileReader();
    reader.addEventListener("load", function(event) {
        var data = JSON.parse(event.target.result);
        for (var i in data) {
            for (var j in data[i]["cards"]) {
                document.getElementById(j).checked = data[i]["cards"][j];
            }
        }
    });
    reader.readAsText(file);
}


document.addEventListener("DOMContentLoaded", function(event) {
    document.getElementById("save").addEventListener("click", save)

    document.getElementById("load").addEventListener("change", function(event) {
        load_file(event.target.files[0]);
    });
});
