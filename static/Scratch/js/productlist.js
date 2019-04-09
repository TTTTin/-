// todo :后续按钮和下拉菜单js函数
$(document).ready(function () {
    $('.list-boder').hover(function (event) {
        //console.log($(this));
        $(this).animate({bottom:"8px"},700);
        $(this).addClass("shadow");
    },function (event) {
         $(this).animate({bottom:"-8px"});
         $(this).removeClass("shadow");
    });
});