//$.getJSON("output/collections.json", function(json) {
/*$.getJSON("https://raw.githubusercontent.com/fedorov/actcianable/master/output/collections.json", function(json) {
    var $table = $('#collectionsTable');
    //const collections = JSON.parse(json);
    $(function () {
        $('#collectionsTable').bootstrapTable({
            data: json
        });
    });
});
*/




function LinkFormatter(value, row, index) {
  return "<a href='"+value+"'>DOI</a>";
}

/*


const collections = require("./output/collections.json");

*/
