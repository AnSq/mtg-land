"use strict";


function checkbox_update(target) {
    if (target.checked) {
        $("." + target.id).show();
    }
    else {
        $("." + target.id).hide();
    }
}


function button_press(target) {
    var checkboxes = $("input[type='checkbox']." + target.id + ":not(:disabled)");
    var not_checked = $("input[type='checkbox']." + target.id + ":not(:disabled):not(:checked)");

    if (not_checked.length === 0) {
        checkboxes.click();
    }
    else {
        not_checked.click();
    }
}


$().ready(function() {
    $("input[type='checkbox']").each(function(i, el) {
        checkbox_update(el);
    });

    $("input[type='checkbox']").on("click", function(event) {
        checkbox_update(event.target);
    });

    $("button").on("click", function(event) {
        button_press(event.target);
    });
});
