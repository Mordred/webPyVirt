(function($) {

    $.fn.domainMigrateWizard = function(options, value) {

        var PLUGIN_NAME = "domainMigrateWizard";

        var defaults = {
            url:                "/domains/domain/migrate/wizard/",
            secret:             "#secret",
            loadImg:            MEDIA_URL + "/img/icons/load-roller.gif"
        };

        var settings = $.extend(defaults, options);

        // Variables
        var canvas = null;
        var nodeInfo = null;
        var loading = false;

        var sendNodeList = function() {
        }

        var addDescription = function(field, description) {
            field.append("<br />");
            field.append(
                $("<div />").addClass("description").append(description)
            );
        }

        var createInfo = function(label, data) {
            var field = $("<div />").addClass("field");
            var label = $("<label />").html(label + ":").addClass("bold");
            var text = $("<span />").html(data);

            field.append(label);
            field.append(text);
            return field;
        };

        var createInput = function(type, inpName, inpValue, label, validation) {
            var id = "id_" + inpName;
            var field = $("<div />").addClass("field").css("margin-top", "5px");
            var label = $("<label />").attr("for", id).html(label + ":");

            var input = null;
            if (type == "input") 
                input = $("<input />").attr("type", "text");
            else if (type == "textarea")
                input = $("<textarea />");

            input.attr("name", inpName).val((inpValue != null) ? inpValue : "").attr("id", id);

            input.keypress(function() { 
                var parent = $(this).parent().removeClass("error");
            });

            field.append(label);
            field.append(input);

            if (typeof validation != "undefined" && validation != null) {
                for (var i = 0; i < validation.length; i++) {
                    var validat = validation[i];
                    if (validat == "required") {
                        field.append($("<span />").addClass("required").html("*"));
                    } else if (validat == "uuid") {
                        input.UUIDField();
                    } else if (validat == "mac") {
                        input.MACAddressField();
                    }
                }
            }

            return field;
        }

        var createSelect = function(selName, items, label, selected) {
            var id = "id_" + selName;
            var field = $("<div />").addClass("field").css("margin-top", "5px");
            var label = $("<label />").attr("for", id).html(label + ":");

            var select = $("<select />").attr("name", selName).attr("id", id);

            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                var option = null;
                if (typeof item == "string") {
                    option = $("<option />").val(item).append(item);
                } else {
                    option = $("<option />").val(item['value']).append(item['label']);
                }

                if (typeof selected != "undefined" && option.val() == selected)
                    option.attr("selected", "selected");

                select.append(option);
            }

            field.append(label);
            field.append(select);

            return field;
        }

        var createSlider = function(sliderName, label, minValue, maxValue, currentValue, units, step) {
            var id = "id_" + sliderName;
            var field = $("<div />").addClass("field").css("margin-top", "15px");
            var label = $("<label />").attr("for", id).html(label + ": ");

            var slider = $("<div />").css({
                    "block":    "inline-block"
                }).attr("id", "id_slider_" + sliderName).slider({
                    value:      currentValue,
                    min:        minValue,
                    max:        maxValue,
                    step:       (typeof step != "undefined") ? step : 1,
                    slide:      function(event, ui) {
                        $("#"+id).val(ui.value);
                    }
            });

            var value = $("<input />").attr("name", sliderName).attr("type", "text")
                .css({
                    "text-align":       "right",
                    "margin-bottom":    "10px"
                })
                .attr("id", id).val(currentValue)
                .integerField().change(function() {
                    if ($(this).val() < minValue) {
                        $(this).val(minValue);
                    }
                    if ($(this).val() > maxValue) {
                        $(this).val(maxValue);
                    }
                    slider.slider("value", $(this).val());
                });

            field.append(label);
            field.append(value);
            if (typeof units != "undefined") field.append(" " + units);
            field.append(slider);

            return field;
        }

        var createForm = function(frmId) {
            var form = $("<form />").attr("action", "").attr("method", "post").attr("id", frmId);
            return form;
        }

        var showLoading = function(loadingMessage) {
            var buttons = getButtons(null, null);

            var content = $("<div />").addClass("align-justify");

            if (typeof loadingMessage != "undefined") {
                content.append($("<p />").css("text-indent", "25px").html(loadingMessage));
            }

            var loading = $("<div />").addClass("center").css("padding-top", "25px")
                .html($("<img />").attr("src", settings['loadImg']));

            content.append(loading);

            setContent(content, gettext("Loading, please wait..."), buttons);
        };

        var showError = function(data, previous) {
            if (data['status'] == 500 || data['status'] == 404) {
                var buttons = getButtons(null, previous);
                var error = $("<div />").addClass("align-justify").addClass("errornote")
                    .html(data['statusMessage']);

                setContent(error, gettext("Error"), buttons);
            }
        };

        var send = function(data, callback, loadingMessage) {
            showLoading(loadingMessage);

            data['secret'] = $(settings['secret']).val();

            $.ajax({
                type:       "POST",
                url:        settings['url'],
                data:       data,
                dataType:   "json",
                success:    callback
            });
        };

        var introduction = function() {
            var buttons = getButtons(sendNodeList, null);
            var content = $("<div />").addClass("align-justify").html(
                interpolate(
                    "This is domain migration wizard which will help you set necessary"
                    + " data so you will not have to fill everything alone."
                    + " If you are ready click on \"%s\" button.",
                    [ gettext("Next") ]
                )
            );

            setContent(content, gettext("Introduction"), buttons);
        }

        var setContent = function(content, title, buttons) {
            canvas.html("");
            canvas.append(content);
            var innerHtml = canvas.children(":first");
            var height = innerHtml.height() + 50 + (typeof buttons != "undefined" ? 150 : 0);

            canvas.dialog("option", "buttons", buttons);
            canvas.dialog("option", "height", height);
//            canvas.dialog("option", "position", [ "center" ]);
            canvas.dialog("option", "title", title);
        }


        var getButtons = function(next, previous, nextLabel, previousLabel) {
            var buttons = {};
            buttons[gettext("Close")] = function() {
                $(this).dialog("close");
            };

            if (next != null) 
                buttons[(typeof nextLabel == "undefined") ? gettext("Next") : nextLabel] = next;
            if (previous != null) 
                buttons[(typeof previousLabel == "undefined") ? gettext("Previous") : previousLabel] = previous;

            return buttons
        }

        var create = function(element) {
            canvas = $(element).addClass("dialog").addClass("smaller").dialog({
                    modal:          true,
                    width:          600,
                    position:       [ "center", 50 ],
                    autoopen:       false
                });

            introduction();

            canvas.dialog("open");
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
