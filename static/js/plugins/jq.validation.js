(function($) {

    $.fn.integerField = function(options, value) {

        var PLUGIN_NAME = "integerField";

        var defaults = {
        };

        var settings = $.extend(defaults, options);

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

})(jQuery);
