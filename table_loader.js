//$.getJSON("output/collections.json", function(json) {
$.getJSON("https://raw.githubusercontent.com/fedorov/actcianable/master/output/collections.json", function(json) {
    var $table = $('#collectionsTable');
    //const collections = JSON.parse(json);
    $(function () {
        $('#collectionsTable').bootstrapTable({
            data: json
        });
    });
});

$.getJSON("https://raw.githubusercontent.com/fedorov/actcianable/master/output/analysis_collections.json", function(json) {
    var $table = $('#analysisCollectionsTable');
    //const collections = JSON.parse(json);
    $(function () {
        $('#analysisCollectionsTable').bootstrapTable({
            data: json
        });
    });
});

/*

function LinkFormatter(value, row, index) {
  return "<a href='"+row.url+"'>"+value+"</a>";
}*/

/*


const collections = require("./output/collections.json");

*/
