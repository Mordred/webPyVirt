$(function() {

    $("#frmSelectUser #id_username").autocomplete({
        source:     "/accounts/selectUser/autocomplete/",
        minLength:  2
    });

    $("div.accordion").each(function() {
        var sections = $(this).children("div");
        var index = sections.index(sections.has("div.field-error"));
        $(this).accordion({
            autoHeight:     false,
            navigation:     true,
            active:         (index == -1) ? 0 : index
        });
    });
});
