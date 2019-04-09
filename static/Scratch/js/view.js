window.baseurl = "http://116.62.165.104/"

window.onbeforeunload = function () {
    return "";
}

function exitLoading() {
    var dom = document.getElementById('loader');
    dom.style.display = "none";
    var dom = document.getElementById('canvas');
    dom.style.display = "";
    var dom = document.getElementById('swfid');
    dom.style.display = "";
}


function getLoadUrl() {
    var url = decodeURIComponent(window.location.href);
    var index = url.lastIndexOf("?");
    if (index == -1) {
        return null;
    }
    url = url.substring(index + 5);
    // download(url);
    var flashObject = document.getElementById("swfid");
    flashObject.downloadProject(url);
}


//This function is invoked by SWFObject once the <object> has been created
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
                    //Once value == 100 (fully loaded) we can do whatever we want
                    if (e.ref.PercentLoaded() === 100) {
                        //Execute function
                        fn();
                        exitLoading();
                        //Clear timer
                        clearInterval(loadCheckInterval);
                    }
                    if (e.ref.PercentLoaded() > 90) {
                        exitLoading();
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

};
