window.token='';

function register() {
    // alert("开始注册");
    registerClean();
    $('#myModal').modal('show');
    // alert("出现模态框");
}

function showlessons(token){
    // alert(token);
    //console.log(window);
    //window.location.href="http://116.62.165.104/scratch?num=1&chapter=1";
    //top.location.load('http://www.baidu.com');
    //window.close();
    //$('#hiddenBtn').click();
   // alert('跳转')
}

function changepassword(token) {
    passwordclean();
    token="Token " + token;
    window.token=token;
    $('#changepassword').modal('show');

}

function passwordclean(){
    $("#oldpassword").val("");
    $("#newpassword").val("");
    $("#newrepassword").val("");
}

function passwordcheck(){
    var oldpsword=$.trim($("#oldpassword").val());
    var newpsword=$.trim($("#newpassword").val());
    var newrepsword=$.trim($("#newrepassword").val());
    if(newpsword!=newrepsword){
         $(".newpasswordMis").empty().append("两次输入密码不同");
        return;
    }
    ajax({
        url: "/changePassword/",              //请求地址
        type: "POST",                       //请求方式
        dataType: "json",
        data: {
            old_password: oldpsword,
            new_password: newpsword,
            new_password_confirm: newrepsword,
        },
        success: function (response) {
            alert("恭喜！修改成功！");
            var data = JSON.parse(response);
            if (data.code === "0") {
                //$('#registerModal').modal('hide');
                //document.getElementsByClassName("container")[0].style.left="-2000px";
                //document.getElementsByClassName("flowContainer2")[0].style.left="-2000px";
                //alert("恭喜！修改成功！");
            }
        },
        fail: function (status, response) {
            // 此处放失败后执行的代码
            var data = JSON.parse(response);
            // if (data.username.code === "2") {
            //     alert("用户名长度过短");
            // }
            // else if (data.username.code === '1') {
            //     registerClean();
            //     alert("该用户名已被占用，请重新设置用户名");
            // }
            alert('原密码不正确,修改失败');
        }
    });

    function ajax(options) {
        options = options || {};
        options.type = (options.type || "GET").toUpperCase();
        options.dataType = options.dataType || "json";
        var params = formatParams(options.data);

        //创建 - 非IE6 - 第一步
        if (window.XMLHttpRequest) {
            var xhr = new XMLHttpRequest();
        } else { //IE6及其以下版本浏览器
            var xhr = new ActiveXObject('Microsoft.XMLHTTP');
        }

        //接收 - 第三步
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4) {
                var status = xhr.status;
                if (status >= 200 && status < 300) {
                    options.success && options.success(xhr.responseText, xhr.responseXML);
                } else {
                    options.fail && options.fail(status, xhr.responseText);
                }
            }
        };

        //连接 和 发送 - 第二步
        if (options.type == "GET") {
            xhr.open("GET", options.url + "?" + params, true);
            xhr.setRequestHeader("Authorization", window.token);
            xhr.send(null);
        } else if (options.type == "POST") {
            xhr.open("POST", options.url, true);
            xhr.setRequestHeader("Authorization", window.token);
            //设置表单提交时的内容类型
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.send(params);
        }

    }

    //格式化参数
    function formatParams(data) {
        var arr = [];
        for (var name in data) {
            arr.push(encodeURIComponent(name) + "=" + encodeURIComponent(data[name]));
        }
        arr.push(("v=" + Math.random()).replace(".", ""));
        return arr.join("&");
    }
    $('#changepassword').modal('hide');
}

function registerClean() {
    //alert("yes>")
    $(".usernameError").html("");
    $(".passwordError").html("");
    $(".trueNameError").html("");
    $(".sexError").html("");
    $(".phone_numberError").html("");
    $("#cmbError").val("");
    $(".idError").html("");
    $("#username").val("");
    $("#password").val("");
    $("#rePassword").val("");
    $("#trueName").val("");
    $("#student_id").val("");
    $("#phonenumber").val("");
    $("#school").empty();
    document.getElementById("prov")[0].selected = true;
    document.getElementById("city").length = 1;
    document.getElementById("district").length = 1;
    document.getElementById("format_school").length = 1;
    document.getElementById("cmbProvince")[0].selected = true;
    document.getElementById("cmbCity").length = 1;
    document.getElementById("cmbArea").length = 1;
    $("#enroll_number_note").val("");
    var x = document.getElementsByName("sex");  //获取所有name=brand的元素
    for (var i = 0; i < x.length; i++) { //对所有结果进行遍历，如果状态是被选中的，则将其选择取消
        if (x[i].checked == true) {
            x[i].checked = false;
        }
    }
    // getSchool();
}

$(document).ready(function () {
        $("#school").change(function () {
            getClass($(this).val(), $("#student_class"));
        });
        $("#school_second").change(function () {
            getClass($(this).val(), $("#student_class_second"));
        });
})


function registerCheck() {
    var username = $("#username").val();
    var password = $.trim($("#password").val());
    var rePassword = $.trim($("#rePassword").val());
    var sex = '';
    var radio = document.getElementsByName("sex");
    for (var i = 0; i < radio.length; i++) {
        if (radio[i].checked == true) {
            sex = radio[i].value;
            break;
        }
    }
    var birthday = $("#birthday_y").val() + '-' + $("#birthday_m").val() + '-' + $("#birthday_d").val();
    var name = $.trim($("#trueName").val());
    var phone_number = $("#phonenumber").val();
    var local_province = $("#cmbProvince").find("option:selected").text();
    var local_city = $("#cmbCity").find("option:selected").text();
    var local_district = $("#cmbArea").find("option:selected").text();
    var format_school = $("#format_school").val();
    var enrollment_number_note = $("#enroll_number_note").val();

    if (username.length == 0) {
        $(".usernameError").empty().append("请输入用户名");
        return;
    }
    else
        $(".usernameError").empty();
    if (password.length == 0) {
        $(".passwordError").empty().append("密码不能为空");
        return;
    }
    else
        $(".passwordError").empty();
    if (password.length < 6) {
        $(".passwordError").empty().append("密码长度过短");
        return;
    }
    else
        $(".passwordError").empty();
    if (rePassword.length == 0) {
        $(".passwordMis").empty().append("密码不能为空");
        return;
    }else
        $(".passwordMis").empty();
    if (password != rePassword) {
        $(".passwordMis").empty().append("两次输入密码不同");
        return;
    }
    else
        $(".passwordMis").empty();
    if (name.length == 0) {
        $(".trueNameError").empty().append("真实姓名不能为空");
        return;
    }
    else
        $(".trueNameError").empty();
    if (sex.length == 0) {
        $(".sexError").empty().append("未选择性别");
        return;
    }
    else
        $(".sexError").empty();

    if (local_province == "=请选择省份="){
        $("#cmbError").empty().append("请选择省份");
        return;
    }else if (local_city == "=请选择城市="){
        $("#cmbError").empty().append("请选择城市");
        return;
    }else if(local_district == "=请选择县区="){
        $("#cmbError").empty().append("请选择县区");
        return;
    }
    else{
        $("#cmbError").empty();
    }


    if (phone_number.length != 11) {
        $(".phone_numberError").empty().append("手机号码不正确");
        return;
    }
    else
        $(".phone_numberError").empty();
    var note = "";
    if (enrollment_number_note != ""){
        note = {
            "enrollment_number": enrollment_number_note
        }
    }

    ajax({
        url: "/register",              //请求地址
        type: "POST",                       //请求方式
        dataType: "json",
        data: {
            username: username,
            password: password,
            name: name,
            sex: sex,
            local_province: local_province,
            local_city: local_city,
            local_district: local_district,
            birthday: birthday,
            phone_number: phone_number,
            format_school: format_school,
            note: JSON.stringify(note)
        },
        success: function (response) {
            var data = JSON.parse(response);
            if (data.code === "0") {
                //$('#registerModal').modal('hide');
                //document.getElementsByClassName("container")[0].style.left="-2000px";
                //document.getElementsByClassName("flowContainer2")[0].style.left="-2000px";
                alert("恭喜！注册成功！");
                $('#studentModal').modal('toggle');
            }
        },
        fail: function (status, response) {
            // 此处放失败后执行的代码
            var data = JSON.parse(response);
            if (data.username.code === "2") {
                alert("用户名长度过短");
            }
            else if (data.username.code === '1') {
                registerClean();
                alert("该用户名已被占用，请重新设置用户名");
            } else if (data.username.code === '3') {
                registerClean();
                alert("用户名只能包含字母或数字");
            }


        }
    });

    function ajax(options) {
        options = options || {};
        options.type = (options.type || "GET").toUpperCase();
        options.dataType = options.dataType || "json";
        var params = formatParams(options.data);

        //创建 - 非IE6 - 第一步
        if (window.XMLHttpRequest) {
            var xhr = new XMLHttpRequest();
        } else { //IE6及其以下版本浏览器
            var xhr = new ActiveXObject('Microsoft.XMLHTTP');
        }

        //接收 - 第三步
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4) {
                var status = xhr.status;
                if (status >= 200 && status < 300) {
                    options.success && options.success(xhr.responseText, xhr.responseXML);
                } else {
                    options.fail && options.fail(status, xhr.responseText);
                }
            }
        };

        //连接 和 发送 - 第二步
        if (options.type == "GET") {
            xhr.open("GET", options.url + "?" + params, true);
            xhr.send(null);
        } else if (options.type == "POST") {
            xhr.open("POST", options.url, true);
            //设置表单提交时的内容类型
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.send(params);
        }

    }

    //格式化参数
    function formatParams(data) {
        var arr = [];
        for (var name in data) {
            arr.push(encodeURIComponent(name) + "=" + encodeURIComponent(data[name]));
        }
        arr.push(("v=" + Math.random()).replace(".", ""));
        return arr.join("&");
    }
    $('#myModal').modal('hide');
}
function getFormatSchool(prov, city, country, format_school){
    $.ajax({
        url: '/format_school/',
        type: 'get',
        dataType: 'json',
        data:{
            province:prov,
            city: city,
            district: country
        },
        success:function (response) {
            // console.log("response: " + response);
            for(var i=0; i<response.length; i++){
                var data = response[i];
                // console.log(data);
                var schoolOpt = document.createElement('option');
                schoolOpt.innerText = data.name;
                schoolOpt.value = data.id;
                format_school.append(schoolOpt);
            }
        }
    })
}

function getSchool() {
    $("#school_second").empty();
    ajax({
        url: "/school",              //请求地址
        type: "GET",                       //请求方式
        dataType: "json",
        success: function (response) {
            var data = JSON.parse(response);
            for (var i = 0; i < data.length; i++) {
                $("#school").append("<option>" + data[i].school_name + "</option>");
                $("#school_second").append("<option>" + data[i].school_name + "</option>");
            }
            $("#school").append("<option>无</option>");
            $("#school_second").append("<option>无</option>");
            if (data.length > 0) {
                getClass(data[0].school_name, $("#student_class"));
                getClass(data[0].school_name, $("#student_class_second"));
            }

        },
        fail: function (status, response) {
            // 此处放失败后执行的代码
            alert("失败");
        }
    });

    function ajax(options) {
        options = options || {};
        options.type = (options.type || "GET").toUpperCase();
        options.dataType = options.dataType || "json";
        var params = formatParams(options.data);

        //创建 - 非IE6 - 第一步
        if (window.XMLHttpRequest) {
            var xhr = new XMLHttpRequest();
        } else { //IE6及其以下版本浏览器
            var xhr = new ActiveXObject('Microsoft.XMLHTTP');
        }

        //接收 - 第三步
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4) {
                var status = xhr.status;
                if (status >= 200 && status < 300) {
                    options.success && options.success(xhr.responseText, xhr.responseXML);
                } else {
                    options.fail && options.fail(status, xhr.responseText);
                }
            }
        };

        //连接 和 发送 - 第二步
        if (options.type == "GET") {
            xhr.open("GET", options.url + "?" + params, true);
            xhr.send(null);
        } else if (options.type == "POST") {
            xhr.open("POST", options.url, true);
            //设置表单提交时的内容类型
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.send(params);
        }

    }

    //格式化参数
    function formatParams(data) {
        var arr = [];
        for (var name in data) {
            arr.push(encodeURIComponent(name) + "=" + encodeURIComponent(data[name]));
        }
        arr.push(("v=" + Math.random()).replace(".", ""));
        return arr.join("&");
    }
}


function getClass(school_name, studnetClass) {
    $(studnetClass).empty();
    ajax({
        url: "/getClassList/",              //请求地址
        type: "POST",                       //请求方式
        dataType: "json",
        data: {
            school_name: school_name
        },
        success: function (response) {
            var data = JSON.parse(response);
            for (var i = 0; i < data.length; i++) {
                $(studnetClass).append("<option>" + data[i].class_name + "</option>");
            }
            $(studnetClass).append("<option>无</option>");
        },
        fail: function (status, response) {
            // 此处放失败后执行的代码
            alert("获取班级失败");
        }
    });

    function ajax(options) {
        options = options || {};
        options.type = (options.type || "GET").toUpperCase();
        options.dataType = options.dataType || "json";
        var params = formatParams(options.data);

        //创建 - 非IE6 - 第一步
        if (window.XMLHttpRequest) {
            var xhr = new XMLHttpRequest();
        } else { //IE6及其以下版本浏览器
            var xhr = new ActiveXObject('Microsoft.XMLHTTP');
        }

        //接收 - 第三步
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4) {
                var status = xhr.status;
                if (status >= 200 && status < 300) {
                    options.success && options.success(xhr.responseText, xhr.responseXML);
                } else {
                    options.fail && options.fail(status, xhr.responseText);
                }
            }
        };

        //连接 和 发送 - 第二步
        if (options.type == "GET") {
            xhr.open("GET", options.url + "?" + params, true);
            xhr.send(null);
        } else if (options.type == "POST") {
            xhr.open("POST", options.url, true);
            //设置表单提交时的内容类型
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.send(params);
        }

    }

    //格式化参数
    function formatParams(data) {
        var arr = [];
        for (var name in data) {
            arr.push(encodeURIComponent(name) + "=" + encodeURIComponent(data[name]));
        }
        arr.push(("v=" + Math.random()).replace(".", ""));
        return arr.join("&");
    }
}