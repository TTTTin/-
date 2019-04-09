var timer = null;

function game_start(game_id){
    $.ajax({
        url : '/team_match/push_game_into_list/',
        type : "GET",
        data : {
            "game_id":game_id
        },
        dataType : 'json',
        success:function (data) {
            console.log(data);
            if(data.game_will_start){
                console.log('game will start');
                timer = window.setInterval(function () {
                    showAction(data.code);
                },1500);
            }else{
                console.log(data.mess);
            }
        },
        error:function () {
            console.log('game_start error');
        }
    })
}

var chessboard = new Map();

function showAction(code) {
    $.ajax({
        url : '/team_match/game_detail_to_page/',
        type : "GET",
        data : {
            "code":code
        },
        dataType : 'json',
        success:function (data) {
            console.log(data);
            if(data.player_action){
                oneStep(data.row, data.col, data.color, chessboard);
                if(data.game_end){
                    window.clearInterval(timer);
                    chessboard.clear();
                    if(data.action_error){
                        alert("action error, "+data.color+" lose !!!");
                    }else{
                        alert(data.color+" win !!!");
                    }
                }
            }else{
                console.log('no player action');
            }
        },
        error:function () {
            console.log('show player action error');
        }
    })
}