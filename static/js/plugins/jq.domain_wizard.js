(function($) {

    $.fn.domainWizard = function(options, value) {

        var PLUGIN_NAME = "domainWizard";

        var defaults = {
            url:                "/domains/domain/add/wizard/",
            secret:             "#secret",
            loadImg:            MEDIA_URL + "/img/icons/load-roller.gif"
        };

        var settings = $.extend(defaults, options);

        // Variables
        var canvas = null;
        var nodeInfo = null;
        var loading = false;

        var memory = function(data) {
            if (data['status'] == 200) {
                var buttons = getButtons(
                    null,
                    function() { if (saveMemory()) loadMetadata(); }
                );

                var content = $("<div />");
                var text = $("<div />").addClass("align-justify").html(
                    interpolate(
                        "Choose memory and CPU settings: "
                    )
                );
                content.append(text);

                var form = createForm("id_frmMemory");
                form.append(createSlider("memory", gettext("Memory (RAM)"),
                    50, nodeInfo['memory'],
                    (data['memory'] != null) ? data['memory'] : Math.ceil(nodeInfo['memory'] / 2), "MB"));
                form.append(createSlider("vcpu", gettext("CPUs"),
                    1, nodeInfo['cpus'],
                    (data['vcpu'] != null) ? data['vcpu'] : Math.ceil(nodeInfo['cpus'] / 2)));

                content.append(form);

                setContent(content, gettext("Memory"), buttons);

            } else {
                showError(data, loadMetadata);
            }
        }

        var metadata = function(data) {
            if (data['status'] == 200) {
                var buttons = getButtons(
                    function() { if (saveMetadata()) loadMemory(); },
                    function() { if (saveMetadata()) introduction(); }
                );
                var content = $("<div />");
                var text = $("<div />").addClass("align-justify").html(
                    interpolate(
                        "First we need some basic data: "
                    )
                );

                content.append(text);

                var form = createForm("id_frmMetadata");
                form.append(createInput("input", "name", data['name'], gettext("Domain Name"), [ "required" ]));
                form.append(createInput("input", "uuid", data['uuid'], gettext("UUID"), [ "uuid" ]));
                form.append(createInput("textarea", "description", data['description'], gettext("Description")));

                content.append(form);

                setContent(content, gettext("Metadata"), buttons);
            } else {
                showError(data, introduction);
            }
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

            if (typeof validation != "undefined") {
                for (var i = 0; i < validation.length; i++) {
                    var validat = validation[i];
                    if (validat == "required") {
                        field.append($("<span />").addClass("required").html("*"));
                    } else if (validat == "uuid") {
                        input.UUIDField();
                    }
                }
            }

            return field;
        }

        var createSlider = function(sliderName, label, minValue, maxValue, currentValue, units) {
            var id = "id_" + sliderName;
            var field = $("<div />").addClass("field").css("margin-top", "15px");
            var label = $("<label />").attr("for", id).html(label + ": ");

            var slider = $("<div />").css({
                    "block":    "inline-block"
                }).slider({
                    value:      currentValue,
                    min:        minValue,
                    max:        maxValue,
                    step:       1,
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

        var showLoading = function() {
            var buttons = getButtons(null, null);
            var loading = $("<div />").addClass("center").css("padding-top", "25px")
                .html($("<img />").attr("src", settings['loadImg']));

            setContent(loading, gettext("Loading..."), buttons);
        };

        var showError = function(data, previous) {
            if (data['status'] == 500) {
                var buttons = getButtons(null, previous);
                var error = $("<div />").addClass("align-justify").addClass("errornote")
                    .html(data['statusMessage']);

                setContent(error, gettext("Error"), buttons);
            }
        };

        var nodeCheck = function(data) {
            if (data['status'] == 200) {
                if (data['nodeStatus']) {
                    nodeInfo = data['info'];
                    loadMetadata();
                } else {
                    var buttons = getButtons(metadata, introduction);
                    var text = $("<div />").addClass("align-justify").addClass("errornote").html(
                        interpolate(
                            "Node \"%s\" with URI: \"%s\" is currently"
                            + " unavailable. You can continue, but"
                            + " all data will be saved only to database"
                            + " and the domain will not be created."
                            + " You can create it later from record"
                            + " in database if you decide to continue.",
                            [ data['name'], data['uri'] ]
                        )
                    );

                    setContent(text, gettext("Node Status"), buttons);
                }
            } else {
                showError(data, introduction);
            }
        };

        var saveMemory = function() {
            var data = {
                "action":       "saveMemory",
                "memory":       $("#id_memory").val(),
                "vcpu":         $("#id_vcpu").val()
            }
            send(data, null);

            return true;
        };

        var loadMemory = function() {
            var data = {
                "action":       "loadMemory",
            }
            send(data, memory);
        };

        var saveMetadata = function() {
            var inpName = $("#id_name");
            var domName = inpName.val();
            if (domName.length == 0 || domName == "") {
                alert(gettext("Name is required!"));
                inpName.parent().addClass("error");
                return false;
            }

            var inpUuid = $("#id_uuid");
            var domUuid = inpUuid.val();
            if (!((/^[\da-fA-F]{8}\-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{12}$/).test(domUuid) ||
                (/^[\da-fA-F]{32}$/).test(domUuid)) && domUuid.length != 0) {
                alert(gettext("UUID is invalid!"));
                inpUuid.parent().addClass("error");
                return false;
            }

            var data = {
                "action":       "saveMetadata",
                "name":         domName,
                "uuid":         $("#id_uuid").val(),
                "description":  $("#id_description").val()
            }
            send(data, null);

            return true;
        };

        var loadMetadata = function() {
            var data = {
                "action":       "loadMetadata"
            }
            send(data, metadata);
        };

        var sendNodeCheck = function() {
            var data = {
                "action":       "nodeCheck"
            }
            send(data, nodeCheck);
        };

        var send = function(data, callback) {
            showLoading();

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
            var buttons = getButtons(sendNodeCheck, null);
            var content = $("<div />").addClass("align-justify").html(
                interpolate(
                    "This is domain creation wizard which will help you set necessary"
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
            canvas.dialog("option", "position", "center");
            canvas.dialog("option", "title", title);
        }


        var getButtons = function(next, previous) {
            var buttons = {};
            buttons[gettext("Close")] = function() {
                $(this).dialog("close");
            };

            if (next != null) buttons[gettext("Next")] = next;
            if (previous != null) buttons[gettext("Previous")] = previous;

            return buttons
        }

        var create = function(element) {
            canvas = $(element).addClass("dialog").addClass("smaller").dialog({
                    modal:          true,
                    width:          600,
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