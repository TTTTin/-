/**
 * Created by zyczyc on 2017/7/12.
 */

window.onload=function () {
    function removeFileList() {
        document.getElementsByClassName("container")[0].style.left="-2000px";
        document.getElementsByClassName("flowContainer")[0].style.left="-2000px";
    }

    getFileList("dd3bfa060d3cc60a2e023849e8a3fb668ddf383b");
    function getFileList(token) {
        document.getElementsByClassName("container")[0].style.left="0px";
        document.getElementsByClassName("flowContainer")[0].style.left="50%";
        token = "Token " + token;
        // $.ajax({
        //     type: "GET",
        //     url:  "http://10.103.246.93/getList/?ordering=update_time",
        //     dataType: "json",
        //     beforeSend: function(request) {
        //         request.setRequestHeader("Authorization", token);
        //     },
        //     success: function (data) {
        //         render(data);
        //     }
        // });
        ajax({
            url: "http://10.103.246.93/getList/?ordering=update_time",              //请求地址
            type: "GET",                       //请求方式
            dataType: "json",
            success: function (response, xml) {
               var data = JSON.parse(response);
                console.log(data);
                for (var index in data){
                    console.log(response[index]);
                }
                render(data);
            },
            fail: function (status) {
                // 此处放失败后执行的代码
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
                        options.fail && options.fail(status);
                    }
                }
            }

            //连接 和 发送 - 第二步
            if (options.type == "GET") {
                xhr.open("GET", options.url + "?" + params, true);
                xhr.setRequestHeader("Authorization", token);
                xhr.send(null);
            } else if (options.type == "POST") {
                xhr.open("POST", options.url, true);
                xhr.setRequestHeader("Authorization", token);
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
            arr.push(("v=" + Math.random()).replace(".",""));
            return arr.join("&");
        }
    }

    function render(data) {
        var html = '<ul>';
        for (var index in data){
            var item = data[index];
            html += '<li><div class="itemContainer"><div class="img"><img  src="';
            html += item['image'] +'"></div><div class="filename">';
            html += item['name'] +'<a href="';
            html += item['file'] + '" class="download">下载</a> </div> </div> </li>';
        }
        html += '</ul>';
        console.log(html);
        document.getElementsByClassName("flow")[0].innerHTML=html;
    }




}
