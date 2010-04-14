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

        var storagePools = function(data) {
            if (data['status'] == 200) {
                var content = $("<div />");
                var text = $("<div />").addClass("align-justify").html(
                    interpolate(
                        "Select storage pool where disk for this virtual machine will be saved: "
                    )
                );

                var form = createForm("id_frmStoragePool");
                // TODO: Allow creating pools
                var createStoragePool = $("<input />").attr("type", "radio").attr("name", "poolAction")
                    .val(0).attr("selected", "selected");

                form.append(createStoragePool);
                form.append(gettext("Create a new storage pool.<br />"));

                var subData = $("<div />").css("padding-left", "25px");
                var inpName = createInput("input", "name", "", gettext("Storage Pool Name"));
                var selType = createSelect("type", [
                        { "value": "dir", "label": "Filesystem Directory" }
                    ], gettext("Storage Pool Type"));

                createStoragePool.change(function() {
                    $("#id_name").removeAttr("disabled");
                    $("#id_type").removeAttr("disabled");
                    $("#id_pool").attr("disabled", "disabled");
                });

                subData.append(inpName);
                subData.append(selType);

                form.append(subData);

                var selectStoragePool = $("<input />").attr("type", "radio").attr("name", "poolAction")
                   .val(1);

                selectStoragePool.change(function() {
                    $("#id_name").attr("disabled", "disabled");
                    $("#id_type").attr("disabled", "disabled");
                    $("#id_pool").removeAttr("disabled");
                });

                form.append(selectStoragePool);
                form.append(gettext("Select existing storage pool.<br />"));

                var subData = $("<div />").css("padding-left", "25px");
                var selPool = createSelect("pool", data['storagePools'], gettext("Existing pools"), data['pool']);
                subData.append(selPool);

                form.append(subData);

                content.append(text);
                content.append(form);

                var buttons = getButtons(
                    null,
                    function() { if (saveStoragePools()) loadMemory(); }
                );
                setContent(content, gettext("Storage Pool"), buttons);

                // Select second option at start
                selectStoragePool.attr("checked", "checked").change();
            } else {
                showError(data, loadMemory);
            }
        }

        var disk = function(data) {
            if (data['status'] == 200) {
                var buttons = getButtons(
                    null,
                    function() { if (saveDisk()) loadMemory(); }
                );

                var content = $("<div />");
                var text = $("<div />").addClass("align-justify").html(
                    interpolate(
                        "Select storage for this virtual machine: "
                    )
                );

                var form = createForm("id_frmDisk");
                var createStorage = $("<input />").attr("type", "radio").attr("name", "diskAction")
                    .val(0).attr("selected", "selected");

                form.append(createStorage);
                form.append(gettext("Create a disk image on the computer's hard drive.<br />"));

                var selectStorage = $("<input />").attr("type", "radio").attr("name", "diskAction")
                    .val(1);
                form.append(selectStorage);
                form.append(gettext("Select managed or other existing storage.<br />"));

                content.append(text);
                content.append(form);

                setContent(content, gettext("Disk"), buttons);

            } else {
                showError(data, loadMemory);
            }
        }

        var memory = function(data) {
            if (data['status'] == 200) {
                var buttons = getButtons(
                    function() { if (saveMemory()) loadStoragePools(); },
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

        var saveDisk = function() {
            var data = {
                "action":       "saveDisk"
            }
            send(data, null);
            return true;
        }

        var loadDisk = function() {
            var data = {
                "action":       "loadDisk"
            }
            send(data, disk);
        };

        var saveStoragePools = function() {
            var formData = $("#id_frmStoragePool").serializeArray();
            var poolAction = null;

            for (var i = 0; i < formData.length; i++) {
                var item = formData[i];
                if (item['name'] == "poolAction") {
                    poolAction = item['value'];
                }
            }

            var data = {
                "action":       "saveStoragePools",
                "poolAction":   poolAction
            }

            if (poolAction == 0) {
                data['pool'] = $("#id_name").val();
                data['type'] = $("#id_type").val();
            } else if (poolAction == 1) {
                data['pool'] = $("#id_pool").val();
            }

            send(data, null);
            return true;
        }

        var loadStoragePools = function() {
            var data = {
                "action":       "loadStoragePools"
            }
            send(data, storagePools);
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
