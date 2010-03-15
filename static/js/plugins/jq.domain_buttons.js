(function($) {

    $.fn.domainButton = function(options, value) {

        var PLUGIN_NAME = "domainButton";

        var defaults = {
            url:                "/domains/domain/command/",
            secret:             "#secret",
            loadImg:            MEDIA_URL + "/img/icons/load-roller.gif"
        };

        var settings = $.extend(defaults, options);

        // Variables
        var dialog = null;
        var elements = [];

        var disable = function(element) {
            $(element).data(PLUGIN_NAME + ".disabled", true);

            // Efect
            $(element).fadeTo(1, 0.1);
            $(element).tooltip("disable");
        };

        var enable = function(element) {
            $(element).data(PLUGIN_NAME + ".disabled", false);

            // Efect
            $(element).fadeTo(1, 0.5);
            $(element).tooltip("enable");
        };

        var disableAll = function() {
            for (var i = 0; i < elements.length; i++) {
                disable(elements[i]);
                $(elements[i]).data(PLUGIN_NAME + ".status", -1);
            }
        };

        var changeStatus = function(element, value) {
            var command = $(element).data(PLUGIN_NAME + ".command");
            switch (value) {
                case 0:             // No state
                case 1:             // Running
                case 2:             // Blocked
                    if (command === "run") {
                        disable(element);
                    } else {
                        enable(element);
                    }
                    break;
                case 3:             // Paused
                    if (command === "run") {
                        enable(element);
                    } else {
                        disable(element);
                    }
                    break;
                case 4:             // Shutdown (but not shutoff!!!)
                    disable(element);
                    break;
                case 5:             // Shutdown (but not shutoff!!!)
                    if (command === "run") {
                        enable(element);
                    } else {
                        disable(element);
                    }
                    break;
                case 6:             // Shutdown (but not shutoff!!!)
                    if (command === "reboot" || command === "shutdown") {
                        enable(element);
                    } else {
                        disable(element);
                    }
                    break;
                default:
                    disable(element);
            }
            $(element).data(PLUGIN_NAME + ".status", value);
        }

        var fireEvent = function(element, event, value) {
            switch (event) {
                case "status":
                    status = value;
                    changeStatus(element, value);
                    break;
            }
        };

        var getDialog = function() {
            if (dialog == null) {
                var buttons = {};
                buttons[gettext("Close")] = function() {
                    $(this).dialog("close");
                    disableAll();
                    $(".domain-status").checkDomainStatus("restart");
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

        var getTitle = function(element) {
            var command = $(element).data(PLUGIN_NAME + ".command");
            var status = $(element).data(PLUGIN_NAME + ".status");

            switch (command) {
                case "pause":
                    return gettext("Pause");
                case "reboot":
                    return gettext("Reboot");
                case "run":
                    if (status == 3) {
                        return gettext("Resume");
                    } else {
                        return gettext("Start");
                    }
                case "shutdown":
                    return gettext("Shutdown");
                case "suspend":
                    return gettext("Suspend");
            }
        };

        var responseSuccess = function(data, textStatus) {
            if (data['status'] == 200) {
                getDialog().find(".dialog-loader").fadeOut(500, function() {
                    getDialog().find(".dialog-status").addClass("success")
                        .html(gettext("OK"))
                });
            } else {
                getDialog().find(".dialog-loader").fadeOut(500, function() {
                    getDialog().find(".dialog-status").addClass("error")
                        .html(data['statusMessage'])
                });
            }

            disableAll();
            $(".domain-status").checkDomainStatus("restart");
        }

        var buttonClick = function(event) {
            event.preventDefault();
            if ($(this).data(PLUGIN_NAME + ".disabled")) return; // Disabled button

            var command = $(this).data(PLUGIN_NAME + ".command");

            var title = getTitle(this);

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
                data:       { "command": command, secret: $(settings['secret']).val() },
                dataType:   "json",
                success:    responseSuccess
            });

        };

        var create = function(element) {
            if ($(element).hasClass("button-run")) {
                $(element).data(PLUGIN_NAME + ".command", "run");
            } else if ($(element).hasClass("button-pause")) {
                $(element).data(PLUGIN_NAME + ".command", "pause");
            } else if ($(element).hasClass("button-reboot")) {
                $(element).data(PLUGIN_NAME + ".command", "reboot");
            } else if ($(element).hasClass("button-suspend")) {
                $(element).data(PLUGIN_NAME + ".command", "suspend");
            } else if ($(element).hasClass("button-shutdown")) {
                $(element).data(PLUGIN_NAME + ".command", "shutdown");
            }

            disable(element);

            // Efect
            $(element).hover(
                function() { if (!$(this).data(PLUGIN_NAME + ".disabled")) $(this).fadeTo(300, 1); },
                function() { if (!$(this).data(PLUGIN_NAME + ".disabled")) $(this).fadeTo(300, 0.5); }
            );

            $(element).click(buttonClick);
            elements.push(element);
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

