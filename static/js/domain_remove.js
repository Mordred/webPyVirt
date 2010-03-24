// On DOM Ready
$(function() {

    var settings = {
        url:                "/domains/domain/command/",
        secret:             "#secret",
        loadImg:            MEDIA_URL + "/img/icons/load-roller.gif"
    };

    var dialog = null;

    var getDialog = function() {
        if (dialog == null) {
            var buttons = {};
            buttons[gettext("Close")] = function() {
                $(this).dialog("close");
            };

            dialog = $("<div />").addClass("dialog").addClass("smaller").dialog({
                modal:          true,
                width:          500,
                autoopen:       false,
                buttons:        buttons
            });
        }
        return dialog;
    };

    var responseSuccess = function(data, textStatus) {
        if (data['status'] == 200) {
            getDialog().find(".dialog-loader").fadeOut(500, function() {
                getDialog().find(".dialog-status").addClass("success")
                    .html(gettext("OK"))
            });
            $("button.button-destroy").remove();
        } else {
            getDialog().find(".dialog-loader").fadeOut(500, function() {
                getDialog().find(".dialog-status").addClass("error")
                    .html(data['statusMessage'])
            });
        }
    };

    var buttonClick = function(event) {
        event.preventDefault();
        var title = gettext("Destroy domain");

        getDialog()
            .dialog("option", "title", title)
            .dialog("option", "position", ["center", 80 ])
            .dialog("open")
            .html("");

        $("<span />")
            .html(interpolate(gettext("Trying to %s domain..."), [title.toLowerCase()]))
            .appendTo(getDialog());

        var loadImage = $("<img />").attr("src", settings['loadImg']).addClass("dialog-loader");
        var status = $("<span />").addClass("dialog-status");

        $("<span />")
            .append("[&nbsp;")
            .append(loadImage)
            .append(status)
            .append("&nbsp;]")
            .addClass("status")
            .appendTo(getDialog());

        $("<br />").appendTo(getDialog());

        $.ajax({
            type:       "POST",
            url:        settings['url'],
            data:       { "command": "destroy", "secret": $(settings['secret']).val() },
            dataType:   "json",
            success:    responseSuccess
        });
    };

    $("button.button-destroy").click(buttonClick);

});
