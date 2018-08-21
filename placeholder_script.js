"use strict";


function checkbox_update(target) {
    if (target.checked) {
        $("." + target.id).show();
    }
    else {
        $("." + target.id).hide();
    }
}


$().ready(function() {
    $("input[type='checkbox']").each(function(i, el) {
        checkbox_update(el);
    });

    $("input[type='checkbox']").on("click", function(event) {
        checkbox_update(event.target);
    });
});
