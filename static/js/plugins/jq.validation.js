(function($) {

    var isSpecialKey = function(event) {
        if (event.ctrlKey) {
            switch (event.which) {
                case 45:
                case 65:
                case 67:
                case 86:
                case 88:
                case 90:
                case 97:
                case 99:
                case 114:
                case 118:
                case 120:
                case 122:
                    return true;
            }
        }
        if (event.which == 0) return true;
    };

    $.fn.integerField = function(options, value) {

        var PLUGIN_NAME = "integerField";

        var defaults = {
        };

        var settings = $.extend(defaults, options);

        var fieldKeyUp = function(event) {
            var key = event.which;

            if (isSpecialKey(event)) return true;

            if (key < 48 || event.which > 57) {
                switch(key) {
                    case 8:
                    case 9:
                    case 13:
                    case 35:
                    case 36:
                    case 37:
                    case 39:
                        return true;
                        break;
                    default:
                        return false;
                }
            }

            return true;
        }

        var create = function(element) {
            $(element).keypress(fieldKeyUp);
        };

        var fireEvent = function(element, options, value) {
            // Nothing
        };

        return this.each(function() {

            if (typeof options === "string") {
                fireEvent($(this), options, value);
            } else {
                create($(this));
            }
        });
    };

    $.fn.UUIDField = function(options, value) {

        var PLUGIN_NAME = "UUIDField";

        var defaults = {
        };

        var settings = $.extend(defaults, options);

        var fieldKeyPress = function(event) {
            var key = event.which;
            var value = $(this).val();

            if (isSpecialKey(event)) return true;

            if (key == 45 && (/^[\da-fA-F]{8}$/).test(value))
                return true;

            if ((/^[\da-fA-F]{8}\-[\da-fA-F]{4}$/).test(value)
                    || (/^[\da-fA-F]{8}\-[\da-fA-F]{4}-[\da-fA-F]{4}$/).test(value)
                    || (/^[\da-fA-F]{8}\-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{4}$/).test(value))
                return (key == 45);

            if (key < 48 || (key > 57 && key < 65) || (key > 70 && key < 97) || key > 102) {
                switch(key) {
                    case 8:
                    case 9:
                    case 13:
                    case 35:
                    case 36:
                    case 37:
                    case 39:
                        return true;
                        break;
                    default:
                        return false;
                }
            } else {
                if ((/^[\da-fA-F]{8}\-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{12}$/).test(value) ||
                    (/^[\da-fA-F]{32}$/).test(value))
                    return false;
            }

            return true;
        }

        var create = function(element) {
            $(element).keypress(fieldKeyPress);
        };

        var fireEvent = function(element, options, value) {
            // Nothing
        };

        return this.each(function() {

            if (typeof options === "string") {
                fireEvent($(this), options, value);
            } else {
                create($(this));
            }
        });
    };

    $.fn.regExpField = function(options, value) {

        var PLUGIN_NAME = "regExpField";

        var defaults = {
            "regexp":           null,
        };

        var settings = $.extend(defaults, options);

        var fieldKeyPress = function(event) {
            var key = event.which;
            var value = $(this).val();

            if (isSpecialKey(event)) return true;

            switch(key) {
                case 8:
                case 9:
                case 13:
                case 35:
                case 36:
                case 37:
                case 39:
                    return true;
                    break;
            }

            var newValue = value + String.fromCharCode(key);

            return settings['regexp'].test(newValue);
        }

        var create = function(element) {
            $(element).keypress(fieldKeyPress);
        };

        var fireEvent = function(element, options, value) {
            // Nothing
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
