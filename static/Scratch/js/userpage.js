// todo :后续按钮和下拉菜单js函数
//实现标签页的跳转展示
// $(function () {
// 		$('#myTab li:eq(1) a').tab('show');
// 	});
$("#my_class_formatClass").change(function () {
    $.cookie("class_id", $("#my_class_formatClass").val(), {path: "/"});
    $.cookie("class_name", $("#my_class_formatClass").find("option:selected").text(), {path: "/"});
    $("#ketang").attr("href", "/my_format_class/" + $.cookie("class_id"));
});