$.getJSON("output/collections.json", function(json) {
    console.log(json); // this will show the info it in firebug console
});

/*
var $table = $('#collectionsTable');

const collections = require("./output/collections.json");

$(function () {
    $('#collectionsTable').bootstrapTable({
        data: collections
    });
});*/
