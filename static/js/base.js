$(function() {

    $("#frmSelectUser #id_username").autocomplete({
        source:     "/accounts/user/select/autocomplete/" + $("#frmSelectUser #autocomplete_permission").val() + "/",
        minLength:  2
    });

    $("#frmSelectGroup #id_name").autocomplete({
        source:     "/accounts/group/select/autocomplete/" + $("#frmSelectGroup #autocomplete_permission").val() + "/",
        minLength:  2
    });

    $("#frmSelectNode #id_name").autocomplete({
        source:     "/nodes/node/select/autocomplete/" + $("#frmSelectNode #autocomplete_permission").val() + "/",
        minLength:  2
    });

    $("#frmSelectDomain #id_name").autocomplete({
        source:     "/domains/domain/select/autocomplete/" + $("#frmSelectDomain #autocomplete_permission").val() + "/",
        minLength:  2,
        select: function(event, ui) {
            console.log($("#frmSelectDomain #id_id"));
            $("#frmSelectDomain #id_id").attr("value", ui.item['id']);
        },
        open:   function(event, ui) {
            $("#frmSelectDomain #id_id").removeAttr("value");
        }
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
