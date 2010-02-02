$(function() {

    $("#frmSelectUser #id_username").autocomplete({
        source:     "/accounts/selectUser/autocomplete/",
        minLength:  2
    });

    $("#frmSelectGroup #id_name").autocomplete({
        source:     "/accounts/selectGroup/autocomplete/",
        minLength:  2
    });

    $("div.accordion").each(function() {
        var sections = $(this).children("div");
        var index = sections.index(sections.has("div.field-error"));

        if (index == -1) {
            index = sections.index(sections.filter("div.selected"));
        }

        $(this).accordion({
            autoHeight:     false,
            navigation:     true,
            active:         (index == -1) ? 0 : index
        });
    });

});
