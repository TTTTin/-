$(document).ready(function () {
    var link = "/scratch2/scratch.html";
    // var link = "http://scratch.tuopinpin.com/scratch.html";
    $("#my_class_formatClass").val($.cookie("class_id"));
    getTOC();
    $('#my_class_formatClass').comboSelect();
    $("#my_class_formatClass").change(function () {
        $.cookie("class_id", $("#my_class_formatClass").val(), {path: "/"});
        $.cookie("class_name", $("#my_class_formatClass").find("option:selected").text(), {path: "/"});
        $("#ketang").attr("href", "/my_format_class/" + $.cookie("class_id"));
        $('#my_class_formatClass').comboSelect();
        getTOC();
    });
    function getTOC() {
        var token = $.cookie("token");
        if (token == null || token == undefined) {
            token = "";
        } else {
            token = "Token " + token;
        }
        $.ajax({
            url:"/course_info/TOC/",
            data:{
                "format_class": $("#my_class_formatClass").val()
            },
            method: "GET",
            // data: {"Authorization": token},
            beforeSend: function(request) {
                request.setRequestHeader("Authorization", token);
            },
            success:function(result) {
                var allLessons = eval(result);
                var count = 0;
                $("#list").empty();
                for (var i = 0; i < allLessons.length; i++) {
                    if (count == 0) {
                        $("#list").append('<div class="row course-list"></div>');
                        var child = $("#list").children()[$("#list").children().length - 1];
                        $(child).append('<div class="col-lg-2 col-lg-offset-2">\n' +
                            '               <a href="1" class="thumbnail" style="text-decoration: none">\n' +
                            '                   <img src="1" style="border: 1px solid #eaeaea; padding: 5px">\n' +
                            '                   <div class="caption">\n' +
                            '                       <h3>' + allLessons[i].name + '</h3>' +
                            '                       <p><strong>发布者</strong>：' + allLessons[i].author +'</p>' +
                            '                       <small>' + allLessons[i].short_introduction + '</small>\n' +
                            '                   </div>\n' +
                            '               </a>\n' +
                            '            </div>');
                        $(child).find("img").last().attr("src", allLessons[i].image);
                        //$(child).find("h3").last().text(allLessons[i].name);
                        if($.cookie("class_id") != undefined){
                            $(child).find("a").last().attr("href", link + "?num=" + allLessons[i].lesson_id + "&chapter=1" + "&format_class_id=" + $.cookie("class_id"));
                        }else{
                            $(child).find("a").last().attr("href", link + "?num=" + allLessons[i].lesson_id + "&chapter=1" );
                        }

                        //$(child).find("a").attr("href", "http://www.baidu.com");
                        count = 1;
                    } else if (count == 1) {
                        var child = $("#list").children()[$("#list").children().length - 1];
                        $(child).append('<div class="col-lg-2 col-lg-offset-1">\n' +
                            '               <a href="#" class="thumbnail" style="text-decoration: none">\n' +
                            '                   <img src="1" style="border: 1px solid #eaeaea; padding: 5px">\n' +
                            '                   <div class="caption">\n' +
                            '                       <h3>' + allLessons[i].name + '</h3>' +
                            '                       <p><strong>发布者</strong>：' + allLessons[i].author +'</p>' +
                            '                       <small>' + allLessons[i].short_introduction + '</small>\n' +
                            '                   </div>\n' +
                            '               </a>\n' +
                            '            </div>');
                        $(child).find("img").last().attr("src", allLessons[i].image);
                        //$(child).find("h3").last().text(allLessons[i].name);
                        if($.cookie("class_id") != undefined){
                            $(child).find("a").last().attr("href", link + "?num=" + allLessons[i].lesson_id + "&chapter=1" + "&format_class_id=" + $.cookie("class_id"));
                        }else{
                            $(child).find("a").last().attr("href", link + "?num=" + allLessons[i].lesson_id + "&chapter=1" );
                        };
                        //$(child).find("a").attr("href", "http://www.baidu.com");
                        count = 2;
                    } else if (count == 2) {
                        var child = $("#list").children()[$("#list").children().length - 1];
                        $(child).append('<div class="col-lg-2 col-lg-offset-1">\n' +
                            '               <a href="#" class="thumbnail"  style="text-decoration: none">\n' +
                            '                   <img src="1" style="border: 1px solid #eaeaea; padding: 5px">\n' +
                            '                   <div class="caption">\n' +
                            '                       <h3>' + allLessons[i].name + '</h3>' +
                            '                       <p><strong>发布者</strong>：' + allLessons[i].author +'</p>' +
                            '                       <small>' + allLessons[i].short_introduction + '</small>\n' +
                            '                   </div>\n' +
                            '               </a>\n' +
                            '            </div>');
                        $(child).find("img").last().attr("src", allLessons[i].image);
                        //$(child).find("h3").last().text(allLessons[i].name);
                        if($.cookie("class_id") != undefined){
                            $(child).find("a").last().attr("href", link + "?num=" + allLessons[i].lesson_id + "&chapter=1" + "&format_class_id=" + $.cookie("class_id"));
                        }else{
                            $(child).find("a").last().attr("href", link + "?num=" + allLessons[i].lesson_id + "&chapter=1" );
                        }
                        count = 0;
                    }
                }
            }
        });
    }

});