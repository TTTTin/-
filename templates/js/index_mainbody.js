function changePicture() {
		var c = $('#picture').children();
		var o = $('#carousel').children();
		var count = c.length;
		var where;
		for (var i = 0; i < c.length; i++) {
			if ($(c[i]).hasClass("active")) {
				where = i;
			}
		}
		$(c[where]).removeClass("active");
		$(o[where]).removeClass("active");
		where = (where + 1) % count;
		$(c[where]).addClass("active");
		$(o[where]).addClass("active");
	}
$(document).ready(function() {
	setInterval("changePicture()", 1000 * 5);
});