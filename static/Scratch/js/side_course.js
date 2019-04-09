$(document).ready(function () {
    var url = location.search;
    var theRequest = new Object();
    var str = url.substr(1);
    var strs = str.split("&");
    for(var i = 0; i < strs.length; i ++) {
        theRequest[strs[i].split("=")[0]]=unescape(strs[i].split("=")[1]);
    }
    //用户行为
    var behavior = {
        user : "",
        lesson_id : 0,
        chapter_id : 0,
        start_time : 0,
        end_time : 0,
        click_audio : false,
    };
    behavior.user = $.cookie("username");
    //alert($.cookie("username"));
    behavior.start_time = getNowFormatDate();
    behavior.lesson_id = Number(theRequest["num"]);
    behavior.chapter_id = Number(theRequest["chapter"]);

    window.onbeforeunload = function () {
        behavior.end_time = getNowFormatDate();
        $.ajax({
            url: "/behavior/",
            data: {"user":behavior.user, "lesson_id": behavior.lesson_id, "chapter_id": behavior.chapter_id,
                "start_time": behavior.start_time, "end_time": behavior.end_time, "click_audio": behavior.click_audio},
            success: function (result) {
                //alert("yes");
            }
        });
    }

    var eventTester = function(e){
        document.getElementById("audio").addEventListener(e,function(){
            //alert("dianle")
            behavior.click_audio = true;
        });
    };
    eventTester("play");


    //end 用户行为

    $("#allCourseButton").click(function() {
        if ($("#allCourse").is(":hidden")) {
            $("#allCourse").show();
        } else {
            $("#allCourse").hide();
        }
    });
});

function getNowFormatDate() {
    var date = new Date();
    var seperator1 = "-";
    var seperator2 = ":";
    var month = date.getMonth() + 1;
    var strDate = date.getDate();
    if (month >= 1 && month <= 9) {
        month = "0" + month;
    }
    if (strDate >= 0 && strDate <= 9) {
        strDate = "0" + strDate;
    }
    var currentdate = date.getFullYear() + seperator1 + month + seperator1 + strDate
            + " " + date.getHours() + seperator2 + date.getMinutes()
            + seperator2 + date.getSeconds();
    return currentdate;
}