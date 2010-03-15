(function($) {

    $.fn.domainButton = function(options, value) {

        var PLUGIN_NAME = "domainButton";

        var defaults = {
            url:                "/domains/domain/command/"
        };

        var settings = $.extend(defaults, options);

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
                    if (command === "pause") {
                        disable(element);
                    } else {
                        enable(element);
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
        }

        var fireEvent = function(element, event, value) {
            switch (event) {
                case "status":
                    changeStatus(element, value);
                    break;
            }
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

