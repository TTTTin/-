//in order to get csrf token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function () {
    var is_signin_submit = false;
    $("#truenameloginError").hide();
    var thisURL = window.location.href;
    var urls = thisURL.split('/');
    var thisLocation = urls[urls.length - 2];
    var classid = [];

    if (thisLocation.indexOf("download") == 0 && thisURL.indexOf("next=") == -1) {
        $('#download').addClass("active");
    } else if (thisLocation.indexOf("lesson") == 0) {
        $($("#mynav").children()[1]).addClass("active");
    } else if (thisLocation.indexOf("productlist") == 0 || thisURL.indexOf('productdetail') >= 0) {
        $("#production").addClass("active");
    } else if (thisURL.indexOf('qa') >= 0) {
        $("#qa").addClass("active");
    } else {
        $("#index").addClass("active");
    }

    changeSignIn();

    $("#student").click(function () {
        $('#firstModal').modal('toggle');
        //alert("fasdaf")
        showCmbProv($("#cmbProvince"));
        showProv($("#prov"));
        registerClean();
    });

    $("#teacher").click(function () {
        $('#firstModal').modal('toggle');
        window.location.href = '/t/signup/';
    });

    $("#loginError").css("color", "red");
    $("#loginError").hide();

    $("#signin_submit").click(function () {
        if(!is_signin_submit){
            is_signin_submit = true;
        }else{
            return;
        }
            var userName = $("#signin_username").val().toString();
            var password = $("#signin_password").val().toString();
            $.ajax({
                type: "post",
                url: "/login/",
                data: {"username": userName, "password": password},
                success: function (result) {
                    is_signin_submit =false;
                    var result = eval(result);
                    if (result.token == null || result.token == undefined) {
                        $("#loginError").show();
                    } else {
                        $('#signInModal').modal('toggle');
                        var id = result.token;
                        // $.cookie('token', id, {path: '/', domain:'.tuopinpin.com'});
                        // $.cookie('username', userName, {path: '/', domain:'.tuopinpin.com'});

                        $.cookie('token', id, {path: '/'});
                        $.cookie('username', userName, {path: '/'});
                        //按照老师的说法是关闭浏览器后去掉登录状态，因此这里我去掉了expires
                        $.cookie("class_id", $("#classes_list").val(), {path: '/'});
                        $.cookie("class_name", $("#classes_list").find("option:selected").text(), {path: '/'});
                    }

                    var csrftoken = getCookie('csrftoken');
                    $.ajax({
                        type: "post",
                        url: "/website/login/",
                        data: {"username": userName, "password": password, "csrfmiddlewaretoken": csrftoken},
                        success: function (result) {
                            var result = eval(result);
                            if (result.role == 'teacher') {
                                // $.cookie('role', result.role, {path: '/', domain:'.tuopinpin.com'});

                                $.cookie('role', result.role, {path: '/'});
                            }
                            changeSignIn();
                            var str = location.href;
                            var num = str.indexOf("next=");
                            if (num != -1){
                                str = str.substr(num+5);
                                document.location.href = str;
                            }else{
                                window.location.reload();
                            }
                        }
                    });
                },
                error: function () {
                    $("#loginError").show();
                    is_signin_submit = false;
                }
            });
        }
    );

    $("#signin_truenamesubmit").click(function () {

        if($("#signin_truenamepwd").val() == ""){
            $("#signin_truenamepwd_error").text("密码不能为空");
            $("#signin_truenamepwd_error").show();
            return;
        }else {
            $("#signin_truenamepwd_error").text("");
        }

        if($("#classes_truenamelist").val() == 0){
            $("#classTrueNameError").text("请选择班级");
            return;
        }
        $.ajax({
            type: "post",
            url: "/loginTrueName/",
            data: {
                "name": $("#signin_truename").val(),
                "password": $("#signin_truenamepwd").val(),
                "format_class": $("#classes_truenamelist").val()
            },
            success: function (result) {
                var result = eval(result);
                var usrname = result.username;
                console.log(usrname);
                if (result.token == null || result.token == undefined) {
                    $("#loginError").show();
                } else {
                    $('#signInModal').modal('toggle');
                    var id = result.token;
                    $.cookie('token', id, {path: '/'});
                    $.cookie('username', usrname, {path: '/'});
                    //按照老师的说法是关闭浏览器后去掉登录状态，因此这里我去掉了expires
                    $.cookie("class_id", $("#classes_truenamelist").val(), {path: '/'});
                    $.cookie("class_name", $("#classes_truenamelist").find("option:selected").text(), {path: '/'});
                }

                var csrftoken = getCookie('csrftoken');
                $.ajax({
                    url: "/website/login/",
                    type: "POST",
                    data: {"username": usrname, "password": $("#signin_truenamepwd").val(), "csrfmiddlewaretoken": csrftoken},
                    success: function (result) {
                        var result = eval(result);
                        if (result.role == 'teacher') {
                            // $.cookie('role', result.role, {path: '/', domain:'.tuopinpin.com'});
                            $.cookie('role', result.role, {path: '/'});
                        }
                        changeSignIn();
                        var str = location.href;
                        var num = str.indexOf("next=");
                        if (num != -1){
                            str = str.substr(num+5);
                            document.location.href = str;
                        }else{
                            window.location.reload();
                        }
                    }
                });
            },
            error: function (response) {
                var response = response.responseJSON;
                if (response.username.code != undefined && response.username.code == 5){
                    $("#moreNameTitle").text(response.username.message);
                    var result = response.username.result;
                    result = eval("(" + result + ")");
                    var model = $("#moreName_div").clone();
                    $("#moreName_content").empty();
                    $("#moreName_content").append(model);
                    for (var i=0; i<result.length; i++){
                        var item = $("#moreName_div").clone();
                        item.attr("id", result[i]["username"]);
                        item.children(":eq(1)").text(result[i]["username"]);
                        item.children(":eq(4)").text(result[i]["birthday"]);
                        item.css("display", "");
                        $("#moreName_content").append(item);
                    }
                    $("#moreNameModal").modal("show");
                    $(".moreName_div").click(function () {
                        $(".moreName_div").removeClass("active");
                        $(this).addClass("active");
                    });
                    $(".moreName_div").dblclick(function () {
                        $(".moreName_div").removeClass("active");
                        $(this).addClass("active");
                        $("#moreNameSubmit").click();
                    })
                }else{
                    $("#truenameloginError").show();
                }

            }
        });
    });
    $("#moreNameSubmit").click(function () {
        var username = $("#moreName_content .active #moreName_username").text();
        if (username == undefined || username == ""){
            $("#moreNameError").text("请选择用户");
            return;
        }else{
            $("#moreNameError").text("");
            $("#moreNameModal").modal("toggle");
        }
        $.ajax({
            url: "/login/",
            type: "POST",
            data:{
                username: username,
                password: $("#signin_truenamepwd").val()
            },
            success:function (response) {
                var response = eval(response);
                if (response.token == null || response.token == undefined) {
                    $("#truenameloginError").show();
                    return;
                } else {
                    $('#trueNameModal').modal('toggle');
                    var id = response.token;
                    $.cookie('token', id, {path: '/'});
                    $.cookie('username', username, {path: '/'});
                    //按照老师的说法是关闭浏览器后去掉登录状态，因此这里我去掉了expires
                    $.cookie("class_id", $("#classes_truenamelist").val(), {path: '/'});
                    $.cookie("class_name", $("#classes_truenamelist").find("option:selected").text(), {path: '/'});
                }
                console.log(username);
                var csrftoken = getCookie('csrftoken');
                $.ajax({
                    type: "post",
                    url: "/website/login/",
                    data: {
                        "username": username,
                        "password": $("#signin_truenamepwd").val(),
                        "csrfmiddlewaretoken": csrftoken},
                    success: function (result) {
                        var result = eval(result);
                        if (result.role == 'teacher') {
                            // $.cookie('role', result.role, {path: '/', domain:'.tuopinpin.com'});
                            $.cookie('role', result.role, {path: '/'});
                        }
                        changeSignIn();
                        var str = location.href;
                        var num = str.indexOf("next=");
                        if (num != -1){
                            str = str.substr(num+5);
                            document.location.href = str;
                        }else{
                            window.location.reload();
                        }
                    }
                });
            },
            error:function (response) {
                $("#truenameloginError").show();
            }
        });
    });
    $("#signin_truename").change(function () {
        $("#truenameloginError").hide();
        //通过真实姓名取得学生的学校
        $("#schools_list").empty();
        var opt = document.createElement("option");
        opt.innerText = "=请选择学校=";
        opt.value = 0;
        $("#schools_list").append(opt);
        $("#classes_truenamelist").empty();
        var optClass = document.createElement("option");
        optClass.innerText = "=请选择班级=";
        optClass.value = 0;
        $("#classes_truenamelist").append(optClass);
        $.ajax({
            url: "/get_format_scname/",
            type: "GET",
            data:{
                name: $("#signin_truename").val()
            },
            success:function (response) {
                var response = eval(response);
                for(var i=0; i<response.length; i++){
                    var opt = document.createElement("option");
                    opt.innerText = response[i].school;
                    opt.value = response[i].pk;
                    $("#schools_list").append(opt);
                }
            }
        });
    });
    $("#classes_truenamelist").change(function () {
       $("#truenameloginError").hide();
       $("#classTrueNameError").text("");
    });
    $("#signin_password").change(function () {
        $("#truenameloginError").hide();
    });
    $("#schools_list").change(function () {
        $("#truenameloginError").hide();
        $("#classes_truenamelist").empty();
        var opt = document.createElement("option");
        opt.innerText = "=请选择班级=";
        opt.value = 0;
        $("#classes_truenamelist").append(opt);
        $.ajax({
            url: "/get_format_classname/",
            type: "GET",
            data:{
                truename: $("#signin_truename").val(),
                school_id: $("#schools_list").val()
            },
            success: function (response) {
                response = eval(response);
                for (var i=0; i<response.length; i++){
                    var opt = document.createElement("option");
                    opt.innerText = response[i]['class'];
                    opt.value = response[i]['pk'];
                    $("#classes_truenamelist").append(opt);
                }

            }
        })
    });


    $("#sign-in-button").click(function () {
        $("#classes_list").html("");
    });

    $("#signin_username").change(function () {
        if($("#signin_username").val() == ""){
            return;
        }
        $("#classes_list").empty();
        var opt = document.createElement("option");
        opt.innerText = "=请选择班级=";
        opt.value = 0;
        $("#classes_list").append(opt);
        //取得学生的班级
        $.ajax({
            url: "/get_format_classes/",
            type: "GET",
            data: {
                username: $("#signin_username").val()
            },
            success:function (response) {
                var response = eval(response)
                for(var i=0; i<response.length; i++){
                    var opt = document.createElement("option");
                    opt.innerText = response[i]["class"];
                    opt.value = response[i]['pk'];
                    $("#classes_list").append(opt);
                }
            },
            error:function () {
                // alert("获取班级失败");
            }
        })
    });


    $("#sign_out").click(function () {
        //alert("qqq")
        // $.cookie('token', null, {expires: -100, path:'/', domain:'.tuopinpin.com'});
        // $.cookie('username', null, {expires: -100, path:'/', domain:'.tuopinpin.com'});
        // $.cookie('role', null, {expires: -100, path:'/', domain:'.tuopinpin.com'});
        // $.cookie('class_id', null, {expires: -100, path:'/', domain:'.tuopinpin.com'});
        // $.cookie('class_name', null, {expires: -100, path:'/', domain:'.tuopinpin.com'});
        $.cookie('token', null, {expires: -100, path: '/'});
        $.cookie('username', null, {expires: -100, path: '/'});
        $.cookie('role', null, {expires: -100, path: '/'});
        $.cookie('class_id', null, {expires: -100, path: '/'});
        $.cookie('class_name', null, {expires: -100, path: '/'});
        $.ajax({
            type: "get",
            url: "/website/logout/",
            success: function () {
                changeSignIn();
                //location.reload();
                window.location.href = "/";
            }
        });
        //alert("asdfaf")
        //changeSignIn();
        //alert("this?")
        //window.location.href= window.location;
    });

    function changeSignIn() {
        var token = $.cookie('token');
        var sessionid = $.cookie('sessionid');
        if ((token != null && token != undefined) && (sessionid != null && sessionid != undefined)) {
            //alert(token)
            $("#sign-up-in").html('<div class="btn-group">\n' +
                '  <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">\n' +
                '    ' + $.cookie('username') + ' <span class="caret"></span>\n' +
                '  </button>\n' +
                '  <ul class="dropdown-menu">\n' +
                '    <li><a href="/userpage/' + $.cookie("username") + '/" >个人中心</a></li><li role="separator" class="divider"></li>\n' +
                '    <li><a href="/OJ/personal/' + $.cookie("username") + '/" >我的OJ</a></li><li role="separator" class="divider"></li>\n' +
                '    <li><a id="ketang" href="/my_format_class/' + $.cookie("class_id") + '">我的课堂</a></li><li role="separator" class="divider"></li>\n' +
                '    <li><a href="/change_password/">修改密码</a></li><li role="separator" class="divider"></li>\n' +
                '    <li><a id="sign_out">注销</a></li>\n' +
                '  </ul>\n' +
                '</div>');
            // if ($.cookie("class_id") == undefined || $.cookie("class_id") == "" || $.cookie("class_id") == null) {
            //     $("#ketang").attr("href", "/my_class/" + $.cookie("username"));
            // }
        } else {
            if (sessionid) {
                $.ajax({
                    url: "/website/logout/",
                    success: function () {
                        location.reload();
                    }
                });
            } else {
                $("#sign-up-in").html('<ul class="nav nav-pills" id="login">\n' +
                    '                <li role="presentation">\n' +
                    '                    <button type="button" class="btn" data-toggle="modal" data-target="#modename">\n' +
                    '                        登录\n' +
                    '                    </button>\n' +
                    '                </li>\n' +
                    '                <li role="presentation">\n' +
                    '                    <button type="button" class="btn" data-toggle="modal" data-target="#firstModal">\n' +
                    '                        注册\n' +
                    '                    </button>\n' +
                    '                </li>\n' +
                    '            </ul>');
                // location.reload();
            }
        }
        var role = $.cookie('role');
        if (role === 'teacher' && (token != null || token != undefined) && (sessionid != null || sessionid != undefined)) {
            $('#teacher_li').css({"display": ""});
            $('#exam_li').css({"display": ""});
            $("#sign-up-in").html('<div class="btn-group">\n' +
                '  <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">\n' +
                '    ' + $.cookie('username') + ' <span class="caret"></span>\n' +
                '  </button>\n' +
                '  <ul class="dropdown-menu">\n' +
                '    <li><a href="/OJ/personal/' + $.cookie("username") + '/" >我的OJ</a></li><li role="separator" class="divider"></li>\n' +
                '    <li><a href="/change_password/">修改密码</a></li><li role="separator" class="divider"></li>\n' +
                '    <li><a href="/#" id="sign_out">注销</a></li>\n' +
                '  </ul>\n' +
                '</div>');
        }
    }

    $("#signInModal").keydown(function (event) {
        if (event.keyCode == 13) {
            document.getElementById("signin_submit").click();
        }
    });

    function myBrowser() {
        var userAgent = navigator.userAgent; //取得浏览器的userAgent字符串
        // alert(userAgent);
        var isOpera = userAgent.indexOf("Opera") > -1; //判断是否Opera浏览器
        var isIE = !isOpera &&  (userAgent.indexOf("MSIE") > -1||userAgent.indexOf("Trident") > -1); //判断是否IE浏览器
        var isFF = userAgent.indexOf("Firefox") > -1; //判断是否Firefox浏览器
        var isSafari = userAgent.indexOf("Safari") > -1; //判断是否Safari浏览器
        var isChrome = userAgent.indexOf("Chrome") > -1; //判断是否是chrome浏览器
        var is360 = userAgent.indexOf("360") > -1; //判断是否是360浏览器
        var isQQ = userAgent.indexOf("QQBrowser") > -1; //判断是否是QQ浏览器
        if (isIE) {
            return "IE";
            var IE5 = IE55 = IE6 = IE7 = IE8 = false;
            var reIE = new RegExp("MSIE (\\d+\\.\\d+);");
            reIE.test(userAgent);
            var fIEVersion = parseFloat(RegExp["$1"]);
            IE55 = fIEVersion == 5.5;
            IE6 = fIEVersion == 6.0;
            IE7 = fIEVersion == 7.0;
            IE8 = fIEVersion == 8.0;
            if (IE55) {
                return "IE55";
            }
            if (IE6) {
                return "IE6";
            }
            if (IE7) {
                return "IE7";
            }
            if (IE8) {
                return "IE8";
            }
        }//isIE end
        if (isFF) {
            return "FF";
        }
        if (isOpera) {
            return "Opera";
        }
        if (isChrome) {
            return "Chrome";
        }
        if (isSafari) {
            return "Safari";
        }
        if (is360) {
            return "360";
        }
        if (isQQ) {
            return "QQ";
        }
    }

    var browser = myBrowser();
    //alert(browser);
    if (browser == 'IE') {
        alert("检测到您的浏览器版本古老，与我们的网站不兼容，可以尝试用其他浏览器或者桌面版使用");
    }
    // alert(browser);
    // if (browser == 'IE55' || browser == 'IE6' || browser == 'IE7' || browser == 'IE8') {
    //     alert("检测到您的浏览器版本古老，与我们的网站不兼容，可以尝试用其他浏览器或者桌面版使用");
    // }
    if (browser == 'Chrome' || browser == 'FF') {
        //alert("检测到您的浏览器为谷歌浏览器或火狐浏览器，如果页面不能正常显示请用360浏览器或QQ浏览器");
    }
});

