$(document).ready(() => {

    $.fn.dataTable.ext.order['dom-text'] = function (settings, col) {
        return this.api()
            .column(col, { order: 'index' })
            .nodes()
            .map(function (td, i) {
                return $('input', td).val();
            });
    };

    $('#backlogTable').DataTable({
        "columnDefs": [
            { "targets": 15 , "orderDataType": "dom-text", 'type': 'string' }
        ]
    });

});