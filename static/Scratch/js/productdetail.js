//获取swf播放器加载内容的对应路径url
function getLoadUrl() {
    //获取当前页面地址的主机段
    var pagehost = window.location.host;
    // 获取当前页面下的swf内容资源地址
    //  var url = 'http://'+pagehost + window.sb2_url;
    var url =  window.sb2_url;
    // var url = 'http://116.62.165.104/files/zds1234567/zds1234567.sb2';
    // alert(url);

    var flashObject = document.getElementById("swfid");
    flashObject.downloadProject(url);
}


// This function is invoked by SWFObject once the <object> has been created
// 当SWFObject被创建时自动调用swfLoadEvent函数
// 对应说明文档：
// http://learnswfobject.com/advanced-topics/executing-javascript-when-the-swf-has-finished-loading/index.html
var callback = function (e) {
    function swfLoadEvent(fn) {

        //Ensure fn is a valid function
        if (typeof fn !== "function") {
            return false;
        }

        //This timeout ensures we don't try to access PercentLoaded too soon
        var initialTimeout = setTimeout(function () {
            //Ensure Flash Player's PercentLoaded method is available and returns a value
            if (typeof e.ref.PercentLoaded !== "undefined" && e.ref.PercentLoaded()) {
                //Set up a timer to periodically check value of PercentLoaded
                var loadCheckInterval = setInterval(function () {
                    // alert('cg2');
                    //Once value == 100 (fully loaded) we can do whatever we want
                    if (e.ref.PercentLoaded() === 100) {
                        //Execute function  以下为用户根据需要自行添加的加载内容（函数）
                         //自定义开始
                        getLoadUrl();
                        //自定义结束
                        //Clear timer
                        clearInterval(loadCheckInterval);
                    }

                }, 100);
            }
        }, 200);
    }

    //Only execute if SWFObject embed was successful
    if (!e.success || !e.ref) {
        return false;
    }

    swfLoadEvent(function () {
        //Put your code here
        getLoadUrl();

    });

}
//这部分需要放在js的相关函数后边
var flashvars = {};
var params = { scale: "exactFit" };
var attributes = {};

swfobject.embedSWF("/static/tsts.swf", "swfid", "500", "480", "9", false, flashvars, params, attributes, callback);




