function MountTable(id, url, columns) {
    var oTable = $(id).dataTable({
        ajax:  {
            url: url,
            dataSrc: ''
        },
        columns: columns
    });
}