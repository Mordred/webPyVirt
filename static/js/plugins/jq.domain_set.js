(function($) {

    $.fn.domainSet = function(options, value) {

        var PLUGIN_NAME = "domainSet";

        var defaults = {
            url:                "/domains/domain/ajax/edit/",
            secret:             "#secret",
            loadImg:            MEDIA_URL + "/img/icons/load-roller.gif"
        };

        var settings = $.extend(defaults, options);

        // Variables
        var dialog = null;
        var success = false;
        var toClear = null;

        var getDialog = function() {
            if (dialog == null) {
                var buttons = {};
                buttons[gettext("Close")] = function() {
                    $(this).dialog("close");
                    if (success) location.reload();
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
                success = true;
                toClear.val("");
            } else {
                getDialog().find(".dialog-loader").fadeOut(500, function() {
                    getDialog().find(".dialog-status").addClass("error")
                        .html(data['statusMessage'])
                });
            }
        }

        var buttonClick = function(event) {
            event.preventDefault();

            var tableRow = $(this).parent().parent();
            var input = tableRow.find("input");
            // Value of the input will be cleared if success
            toClear = input;
            if (input.val() == "") return;

            var parameterName = {
                "vcpu":         gettext("Virtual CPUs"),
                "max_memory":   gettext("Maximum Memory"),
                "cur_memory":   gettext("Current Memory")
            }[input.attr("name")]

            var title = gettext("Set parameter");

            getDialog()
                .dialog("option", "title", title)
                .dialog("option", "position", ["center", 80 ])
                .dialog("open")
                .html("");

            $("<span />")
                .html(interpolate(gettext("Trying to set parameter \"%s\" to value \"%s\"..."), 
                    [parameterName, input.val()]))
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

            var data = { "secret": $(settings['secret']).val() };
            data[input.attr("name")] = input.val();

            $.ajax({
                type:       "POST",
                url:        settings['url'],
                data:       data,
                dataType:   "json",
                success:    responseSuccess
            });

        };

        var create = function(element) {
            $(element).click(buttonClick);
        };

        var fireEvent = function(element, event, value) {
            // pass
        };

        return this.each(function() {

            if (typeof options === "string") {
                fireEvent($(this), options, value);
            } else {
                create($(this));
            }
        });
    };

})(jQuery);
