$(document).ready(function () {
    $('.demo-default').score();

    var divs = $(".divs > div");
    for (var i = 0; i < haveScore.length; i++) {
        //alert("yes")
        $(divs[i]).score('score', haveScore[i]);
    }

    $('select').comboSelect();
    $("#class_lesson_list").change(function () {
       $("#class_form") .submit();
    });
    $("#homework_lesson_list").change(function () {
        $("#homework_form").submit();
    });
    $("#my_class_formatClass").change(function () {
        $.cookie("class_id", $("#my_class_formatClass").val(), {path: "/"});
        $.cookie("class_name", $("#my_class_formatClass").find("option:selected").text(), {path: "/"});
        document.location.href = "/my_format_class/" + $.cookie("class_id");
    });
});