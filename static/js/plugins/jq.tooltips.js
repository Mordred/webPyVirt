(function($) {

    var PLUGIN_NAME = "tooltip";

    var tooltipPrototype = function() {
        this.defaults = {
            xOffset:    10,
            yOffset:    20
        };
        this.lastMouseEvent = null;
        this.tooltip =
            $("<div />").addClass("tooltipCanvas")
                    .html("<table class=\"tooltipTable\"><tr><td><div class=\"tooltipContent\"></div></td>"
                        + "<th class=\"last\" style=\"background-position: 100% 0%;\"></th></tr><tr>"
                        + "<th style=\"background-position: 0% 100%;\" >&nbsp;</th>"
                        + "<th style=\"background-position: 100% 100%;\"></th></tr></table>")
                    .hide()
                    .css({
                        "position": "absolute"
                    })
                    .appendTo("body");
        this.getCanvas = function() {
            return this.tooltip.find(".tooltipContent");
        };
        this.show = function(event) {
            this.move(event);
            this.tooltip.show();
        };
        this.hide = function(event) {
            this.tooltip.hide();
        };
        this.move = function(event) {
            if (typeof(event) == "undefined")
                event = this.lastMouseEvent;

            this.lastMouseEvent = event;

            var x = event.pageX + this.defaults['xOffset'];
            var y = event.pageY + this.defaults['yOffset'];

            var rightEdge = $(window).width() - this.defaults['xOffset'] - this.tooltip.width();
            var bottomEdge = $(window).height() - this.defaults['yOffset'] - this.tooltip.height();

            // Right Border
            if (event.clientX > rightEdge)
                x = event.pageX - this.defaults['xOffset'] - this.tooltip.width();

            // Bottom Border
            if (event.clientY > bottomEdge)
                y = event.pageY - this.defaults['yOffset'] - this.tooltip.height();

            // Left Border
            if (x < $(window).scrollLeft())
                x = $(window).scrollLeft();

            // Top Border
            if (y < $(window).scrollTop())
                y = $(window).scrollTop();

            this.tooltip.css({
                "top":  y + "px",
                "left": x + "px"
            })

        };
        this.setText = function(text, event) {
            this.getCanvas().html(text);
            if (typeof(event) != "undefined") {
                this.lastMouseEvent = event;
                this.move();
            } else if (this.lastMouseEvent != null) {
                this.move();
            }
        }
    };

    $.fn.tooltip = function(options) {

        // Options
        var defaults = {
        }

        var settings = $.extend(defaults, options);

        return this.each(function() {

            if (typeof options === "string") {
                switch (options) {
                    case "disable":
                        $(this).data(PLUGIN_NAME + ".disabled", true);
                        break;
                    case "enable":
                        $(this).data(PLUGIN_NAME + ".disabled", false);
                }
                return;
            }

            if ($(this).hasClass("tooltip"))
                return;

            $(this).addClass("tooltip");

            if ($(this).hasClass("tooltipAlt")) {
                $(this).tooltipAlt();
            } else if ($(this).hasClass("tooltipBlock")) {
                $(this).tooltipBlock();
            } else {
                $(this).removeClass("tooltip");
            }

            $(this).data(PLUGIN_NAME + ".disabled", false);
        });

    };

    $.fn.tooltipAlt = function(options) {

        // Options
        var defaults = {
        }

        var settings = $.extend(defaults, options);

        var tooltip = new tooltipPrototype;
        tooltip.defaults = $.extend(tooltip.defaults, settings);

        var canvas = $("<span />")

        return this.each(function() {
            $(this).hover(
                function(e) {
                    if ($(this).data(PLUGIN_NAME + ".disabled")) return;

                    tooltip.setText(canvas.html($(this).attr("alt")), e);
                    tooltip.show(e);
                },
                function(e) { tooltip.hide(e); }
            ).mousemove(function(e) { tooltip.move(e); });
        });
    }

    $.fn.tooltipBlock = function(options) {

        // Options
        var defaults = {
        }

        var settings = $.extend(defaults, options);

        var tooltip = new tooltipPrototype;
        tooltip.defaults = $.extend(tooltip.defaults, settings);

        var canvas = $("<span />")

        return this.each(function() {
            var tooltipText = $(this).find(".tooltipText");

            if (tooltipText.size() != 1)
                return false;

            $(this).hover(
                function(e) {
                    if ($(this).data(PLUGIN_NAME + ".disabled")) return;
                    tooltip.setText(canvas.html(tooltipText.html()), e);
                    tooltip.show(e);
                },
                function(e) { tooltip.hide(e); }
            ).mousemove(function(e) { tooltip.move(e); });
        });
    }

})(jQuery);
