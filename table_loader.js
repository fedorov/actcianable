$.getJSON("output/collections.json", function(json) {
    //console.log(json); // this will show the info it in firebug console
    var $table = $('#collectionsTable');
    const collections = JSON.parse(json);
    $(function () {
        $('#collectionsTable').bootstrapTable({
            data: collections
        });
    });
});

/*


const collections = require("./output/collections.json");

*/
