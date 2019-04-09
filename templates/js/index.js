$(document).ready(function() {
	var thisURL = window.location.href;
	var urls = thisURL.split('/');
	var thisLocation = urls[urls.length - 1];
	if (thisLocation.indexOf("index") == 0) {
		$($("#mynav").children()[0]).addClass("active");
	}
	if (thisLocation.indexOf("download") == 0) {
		$($("#mynav").children()[4]).addClass("active");
	}
});