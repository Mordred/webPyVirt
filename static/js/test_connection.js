$(function() {
    // Connection test button in add form
    $("#frmAddNode #btnTestConnection").testConnection();

    // Connection test button in edit form
    $("#frmEditNode #btnTestConnection").testConnection({
        formTag:    "#frmEditNode"
    });
});

