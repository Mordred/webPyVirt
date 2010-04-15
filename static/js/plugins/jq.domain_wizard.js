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

        var createNewPool = false;
        var poolType = null;
        var createNewVolume = false;

        var network = function(data) {
            if (data['status'] == 200) {
                var content = $("<div />");
                var text = $("<div />").addClass("align-justify").html(
                    gettext("Please specify network settings (Currently only DHCP is supported): ")
                );

                var form = createForm("id_frmNetwork");
                var inpTargetDev = createInput("input", "targetDev", data['targetDev'], gettext("Target Device Name"));
                addDescription(inpTargetDev, gettext("(e.g. \"vnet2\")"));

                var selNetwork = createSelect("network", data['networks'], gettext("Defined Networks"), data['name']);
                var inpMAC = createInput("input", "mac", data['mac'], gettext("MAC Address"), [ "mac" ]);

                form.append(selNetwork);
                form.append(inpTargetDev);
                form.append(inpMAC);

                content.append(text);
                content.append(form);

                var buttons = getButtons(
                    null,
                    function() { saveNetwork(loadVolumes); }
                );

                setContent(content, gettext("Network"), buttons);

            } else {
                showError(data, loadVolumes);
            }
        }

        var newStorageVolumeResult = function(data) {
            if (data['status'] == 200) {
                var content = $("<div />");
                var text = $("<div />").addClass("align-justify").html(
                    gettext("Result: ")
                );

                var para = $("<p />").css("text-indent", "25px");

                if (data['created']) {
                    para.html(
                        gettext(
                            "Storage volume created."
                        )
                    );
                } else {
                    para.addClass("error").html(
                        interpolate(
                            "During process there was an error, so the volume is not created."
                            + " (error = %s)", [ data['error'] ]
                        )
                    );
                }

                content.append(text);
                content.append(para);

                var buttons = getButtons(
                    (data['created']) ? loadNetwork : null,
                    loadVolumes
                );

                setContent(content, gettext("New Storage Volume"), buttons);

            } else {
                showError(data, loadVolumes);
            }
        };

        var newStoragePoolResult = function(data) {
            if (data['status'] == 200) {
                var content = $("<div />");
                var text = $("<div />").addClass("align-justify").html(
                    gettext("Result: ")
                );

                var para = $("<p />").css("text-indent", "25px");

                if (data['poolCreated']) {
                    var freeSpace = data['poolInfo']['available'] / (1024 * 1024 * 1024);
                    var size = data['poolInfo']['capacity'] / ( 1024 * 1024 * 1024);
                    var allocation = data['poolInfo']['allocation'] / ( 1024 * 1024 * 1024);
                    // To format of %0.2f
                    freeSpace = Math.round(freeSpace * 100) / 100;
                    size = Math.round(size * 100) / 100;
                    allocation = Math.round(allocation * 100) / 100;

                    para.html(
                        interpolate(
                            "Storage pool created and has %s GB of free space."
                            + " (logical size = %s GB, current allocation = %s GB)",
                            [ freeSpace, size, allocation ]
                        )
                    );
                } else {
                    para.addClass("error").html(
                        interpolate(
                            "During process there was an error, so the pool is not created."
                            + " (error = %s)", [ data['error'] ]
                        )
                    );
                }

                content.append(text);
                content.append(para);

                var buttons = getButtons(
                    (data['poolCreated']) ? loadVolumes : null,
                    loadStoragePools
                );

                setContent(content, gettext("New Storage Pool"), buttons);

            } else {
                showError(data, windowCreateNewPool);
            }
        }

        var windowCreateNewPool = function() {
            var content = $("<div />");
            var text = $("<div />").addClass("align-justify").html(
                interpolate(
                    "Specify a storage location to be later split into virtual machine storage: "
                )
            );

            var form = createForm("id_frmNewStoragePool");
            var inpTargetPath = createInput("input", "targetPath", "", gettext("Target Path"), [ "required" ]);
            form.append(inpTargetPath);

            var formats = null;
            if (poolType == "dir" || poolType == "iscsi" || poolType == "logical" || poolType == "scsi")
                formats = [ "" ];
            else if (poolType == "disk")
                formats = [ "auto", "bsd", "dos", "dvh", "gpt", "mac", "pc98", "sun" ];
            else if (poolType == "netfs")
                formats = [ "auto", "nfs", "glusterfs" ];
            else 
                formats = [ "auto", "ext2", "ext3", "ext4", "ufs", "iso9660", "udf", "gfs", "gfs2",
                    "vfat", "hfs+", "xfs" ];

            var selFormat = createSelect("format", formats, gettext("Format"));
            var inpHostName = createInput("input", "hostname", "", gettext("Host Name"));
            var inpSourcePath = createInput("input", "sourcePath", "", gettext("Source Path"));

            form.append(selFormat);
            form.append(inpHostName);
            form.append(inpSourcePath);

            content.append(text);
            content.append(form);

            // Append help descriptions
            if (poolType == "dir") {
                addDescription(inpTargetPath, gettext("Directory to use for the storage pool."));
            } else if (poolType == "disk") {
                addDescription(inpTargetPath, gettext("Root location for identifying new storage volumes."));
                addDescription(selFormat, gettext("Format of the source device's partition table."));
                addDescription(inpSourcePath, gettext("Path to the existing disk device."));
            } else if (poolType == "fs") {
                addDescription(inpTargetPath, gettext("Location to mount the source device."));
                addDescription(selFormat, gettext("Filesystem type of the source device."));
                addDescription(inpSourcePath, gettext("The existing device to mount for the pool."));
            } else if (poolType == "iscsi") {
                addDescription(inpTargetPath, gettext("Root location for identifying new storage volumes."));
                addDescription(inpHostName, gettext("Name of the host sharing the storage."));
                addDescription(inpSourcePath, gettext("Path on the host that is being shared."));
            } else if (poolType == "logical") {
                addDescription(inpTargetPath, gettext("Location of the existing LVM volume group."));
                addDescription(inpSourcePath, gettext("Optional device to build new LVM volume on."));
            } else if (poolType == "netfs") {
                addDescription(inpTargetPath, gettext("Location to mount the source device."));
                addDescription(selFormat, gettext("Type of the network filesystem."));
                addDescription(inpHostName, gettext("Name of the host sharing the storage."));
                addDescription(inpSourcePath, gettext("Path on the host that is being shared."));
            } else if (poolType == "scsi") {
                addDescription(inpTargetPath, gettext("Root location for identifying new storage volumes."));
                addDescription(inpSourcePath, gettext("Name of the SCSI adapter (ex. host2)."));
            }

            var buttons = getButtons(
                saveNewStoragePool,
                loadStoragePools
            );
            setContent(content, gettext("New Storage Pool"), buttons);

            // Set disabled inputs for poolType
            if (poolType == "dir") {
                $("#id_format").attr("disabled", "disabled");
                $("#id_hostname").attr("disabled", "disabled");
                $("#id_sourcePath").attr("disabled", "disabled");
            } else if (poolType == "disk") {
                $("#id_hostname").attr("disabled", "disabled");
//                $("#id_sourcePath").attr("disabled", "disabled");
            } else if (poolType == "fs") {
                $("#id_hostname").attr("disabled", "disabled");
            } else if (poolType == "iscsi") {
                $("#id_format").attr("disabled", "disabled");
            } else if (poolType == "logical" || poolType == "scsi") {
                $("#id_format").attr("disabled", "disabled");
                $("#id_hostname").attr("disabled", "disabled");
            }
        }

        var storagePools = function(data) {
            if (data['status'] == 200) {
                var content = $("<div />");
                var text = $("<div />").addClass("align-justify").html(
                    interpolate(
                        "Select storage pool where disk for this virtual machine will be saved: "
                    )
                );

                var form = createForm("id_frmStoragePool");
                var createStoragePool = $("<input />").attr("type", "radio").attr("name", "poolAction")
                    .val(0).attr("selected", "selected");

                form.append(createStoragePool);
                form.append(gettext("Create a new storage pool.<br />"));

                var subData = $("<div />").css("padding-left", "25px");
                var inpName = createInput("input", "name", "", gettext("Storage Pool Name"), [ "required" ]);
                var selType = createSelect("type", [
                        { "value": "dir", "label": gettext("Filesystem Directory") },
                        { "value": "disk", "label": gettext("Physical Disk Device") },
                        { "value": "fs", "label": gettext("Pre-Formatted Block Device") },
                        { "value": "iscsi", "label": gettext("iSCSI Target") },
                        { "value": "logical", "label": gettext("LVM Volume Group") },
                        { "value": "netfs", "label": gettext("Network Exported Directory") },
                        { "value": "scsi", "label": gettext("SCSI Host Adapter") },
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
                    function() { saveStoragePools(createNewPool ? windowCreateNewPool : loadVolumes) },
                    function() { saveStoragePools(loadMemory) }
                );
                setContent(content, gettext("Storage Pool"), buttons);

                // Select second option at start
                selectStoragePool.attr("checked", "checked").change();
            } else {
                showError(data, loadMemory);
            }
        }

        var volumes = function(data) {
            if (data['status'] == 200) {
                var buttons = getButtons(
                    function() { saveVolumes(createNewVolume ? null : loadNetwork); },
                    function() { saveVolumes(loadStoragePools); }
                );

                var content = $("<div />");
                var text = $("<div />").addClass("align-justify").html(
                    interpolate(
                        "Select storage for this virtual machine: "
                    )
                );

                if (typeof data['error'] != "undefined") {
                    var para = $("<p />").addClass("error").css("text-indent", "25px")
                        .html(data['error']);
                    content.append(para);
                    setContent(content, gettext("Volumes"), buttons);
                    return;
                }

                var form = createForm("id_frmVolumes");
                var createStorage = $("<input />").attr("type", "radio").attr("name", "volumeAction")
                    .val(0);

                form.append(createStorage);
                form.append(gettext("Create a disk image on the computer's hard drive.<br />"));

                var subData = $("<div />").css("padding-left", "25px");

                subData.append(
                    createInput("input", "name", "", gettext("Volume Name"), [ "required" ])
                );
                subData.append(
                    createSelect("format", [ 
                        "raw", "bochs", "cloop", "cow", "dmg", "iso", "qcow",
                        "qcow2", "vmdk", "vpc"
                        ], gettext("Format"))
                );

                // To format of %0.1f
                var freeSpace = data['poolInfo']['available'] / (1024 * 1024 * 1024);
                freeSpace = Math.round(freeSpace * 100) / 100;
                subData.append(
                    createSlider("volumeSize", gettext("Size of the volume"), 1,
                        freeSpace, (freeSpace > 8) ? 8 : freeSpace, "GB", 0.01)
                );

                createStorage.change(function() {
                    $("#id_slider_volumeSize").slider("enable");
                    $("#id_name").removeAttr("disabled");
                    $("#id_format").removeAttr("disabled");
                    $("#id_volumeSize").removeAttr("disabled");
                    $("#id_volume").attr("disabled", "disabled");
                });

                form.append(subData);

                var selectStorage = $("<input />").attr("type", "radio").attr("name", "volumeAction")
                    .val(1);
                form.append(selectStorage);
                form.append(gettext("Select managed or other existing storage.<br />"));

                var subData = $("<div />").css("padding-left", "25px");
                var selVolume = createSelect("volume", data['volumes'], gettext("Existing volumes"), data['volume']);
                subData.append(selVolume);

                form.append(subData);

                selectStorage.change(function() {
                    $("#id_slider_volumeSize").slider("disable");
                    $("#id_volumeSize").attr("disabled", "disabled");
                    $("#id_name").attr("disabled", "disabled");
                    $("#id_format").attr("disabled", "disabled");
                    $("#id_volume").removeAttr("disabled");
                });

                content.append(text);
                content.append(form);

                setContent(content, gettext("Volumes"), buttons);

                // Select second option on start
                selectStorage.attr("checked", "checked").change();
            } else {
                showError(data, loadStoragePools);
            }
        }

        var memory = function(data) {
            if (data['status'] == 200) {
                var buttons = getButtons(
                    function() { saveMemory(loadStoragePools); },
                    function() { saveMemory(loadMetadata); }
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
                    function() { saveMetadata(loadMemory); },
                    function() { saveMetadata(introduction); }
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

        var addDescription = function(field, description) {
            field.append("<br />");
            field.append(
                $("<div />").addClass("description").append(description)
            );
        }

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

        var saveVolumes = function(callback) {
            var formData = $("#id_frmVolumes").serializeArray();
            var volumeAction = null;

            for (var i = 0; i < formData.length; i++) {
                var item = formData[i];
                if (item['name'] == "volumeAction") {
                    volumeAction = item['value'];
                }
            }

            createNewVolume = (volumeAction == 0);

            var data = {
                "action":       "saveVolumes",
                "volumeAction": volumeAction
            };

            if (volumeAction == 0) {
                var inpName = $("#id_name");
                var volName = inpName.val();

                if (volName.length == 0 || volName == "") {
                    alert(gettext("Name is required!"));
                    inpName.parent().addClass("error");
                    return false;
                }

                data['format'] = $("#id_format").val();
                data['volume'] = volName + "." + data['format'];
                data['size'] = $("#id_volumeSize").val();

            } else if (volumeAction == 1) {
                data['volume'] = $("#id_volume").val();
            }

            if (volumeAction == 0) {
                send(data, newStorageVolumeResult, 
                    gettext(
                        "This operation can take more time depending on the volume size."
                        + " Please be patent and do not close this window."
                    )
                );
            } else {
                send(data, callback);
            }
            return true;
        }

        var loadVolumes = function() {
            var data = {
                "action":       "loadVolumes"
            }
            send(data, volumes);
        };

        var saveNetwork = function(callback) {
            var inpMac = $("#id_mac");
            var mac = inpMac.val();
            if (!((/^([\da-fA-F]{2}:){5}[\da-fA-F]{2}$/).test(mac)) && mac.length != 0) {
                alert(gettext("MAC Address is invalid!"));
                inpMac.parent().addClass("error");
                return false;
            }

            var data = {
                "action":       "saveNetwork",
                "mac":          $("#id_mac").val(),
                "network":      $("#id_network").val(),
                "targetDev":    $("#id_targetDev").val()
            }
            send(data, callback);
            return true;
        }

        var loadNetwork = function() {
            var data = {
                "action":       "loadNetwork"
            }
            send(data, network);
        };

        var saveNewStoragePool = function() {
            var inpTargetPath = $("#id_targetPath");
            var targetPath = inpTargetPath.val();

            if (targetPath.length == 0 || targetPath == "") {
                alert(gettext("Target Path is required!"));
                inpTargetPath.parent().addClass("error");
                return false;
            }

            var data = {
                "action":       "saveNewStoragePool",
                "targetPath":   targetPath,
                "format":       $("#id_format").val(),
                "hostname":     $("#id_hostname").val(),
                "sourcePath":   $("#id_sourcePath").val()
            }
            send(data, newStoragePoolResult);
            return true;
        }

        var saveStoragePools = function(callback) {
            var formData = $("#id_frmStoragePool").serializeArray();
            var poolAction = null;

            for (var i = 0; i < formData.length; i++) {
                var item = formData[i];
                if (item['name'] == "poolAction") {
                    poolAction = item['value'];
                }
            }

            createNewPool = (poolAction == 0);

            var data = {
                "action":       "saveStoragePools",
                "poolAction":   poolAction
            }

            if (poolAction == 0) {
                var inpPoolName = $("#id_name");
                var poolName = inpPoolName.val();

                if (poolName.length == 0 || poolName == "") {
                    alert(gettext("Name is required!"));
                    inpPoolName.parent().addClass("error");
                    return false;
                }

                data['pool'] = $("#id_name").val();
                data['type'] = $("#id_type").val();

                poolType = data['type'];

            } else if (poolAction == 1) {
                data['pool'] = $("#id_pool").val();
            }

            send(data, callback);
            return true;
        }

        var loadStoragePools = function() {
            var data = {
                "action":       "loadStoragePools"
            }
            send(data, storagePools);
        };

        var saveMemory = function(callback) {
            var data = {
                "action":       "saveMemory",
                "memory":       $("#id_memory").val(),
                "vcpu":         $("#id_vcpu").val()
            }
            send(data, callback);

            return true;
        };

        var loadMemory = function() {
            var data = {
                "action":       "loadMemory",
            }
            send(data, memory);
        };

        var saveMetadata = function(callback) {
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
            send(data, callback);

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
//            canvas.dialog("option", "position", [ "center" ]);
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
