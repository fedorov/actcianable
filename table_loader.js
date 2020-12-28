const collections = require("./output/collections.json");

$(function () {
    $('#table').bootstrapTable({
        data: collections
    });
});
