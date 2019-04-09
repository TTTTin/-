/**
 * AI
 * @author Airing
 */


var canvas = document.getElementById("chess");
var context = canvas.getContext("2d");

function startGame() {
    // 清除棋盘
    cleanChessBoard();
    // 绘制棋盘
    drawChessBoard();
}

/**
 * 清除棋盘
 */
function cleanChessBoard() {
    context.fillStyle = "#ff9900";
    context.fillRect(0, 0, canvas.width, canvas.height);
}

/**
 * 绘制棋盘
 */
function drawChessBoard() {
    for (var i = 0; i < 15; i++) {
        context.fillStyle = "#0099ff";
        context.strokeStyle = "#BFBFBF";
        context.beginPath();
        context.moveTo(15 + i *30, 15);
        context.lineTo(15 + i *30, canvas.height - 15);
        context.closePath();
        context.stroke();
        context.beginPath();
        context.moveTo(15, 15 + i *30);
        context.lineTo(canvas.width - 15, 15 + i * 30);
        context.closePath();
        context.stroke();
    }
}

/**
 * 绘制棋子
 * @param i     棋子x轴位置
 * @param j     棋子y轴位置
 * @param color    棋子颜色
 */
function oneStep(i, j , color, chessboard) {
    if(i < 1 || i > 15 || j < 1 || j > 15 || chessboard.hasOwnProperty(i * 16 + j)){
        return ;
    }
    chessboard.set((i * 16 + j),true)
    context.beginPath();
    context.arc(j * 30 - 15, i * 30 - 15, 13, 0, 2 * Math.PI);
    context.closePath();
    var gradient = context.createRadialGradient(15 + j * 30 + 2, 15 + i * 30 - 2, 13, 15 + j * 30 + 2, 15 + i * 30 - 2, 0);
    if (color == 'white') {
        gradient.addColorStop(0, "#D1D1D1");
        gradient.addColorStop(1, "#E0E0E0");
    } else {
        gradient.addColorStop(0, "#0A0A0A");
        gradient.addColorStop(1, "#636766");
    }
    context.fillStyle = gradient;
    context.fill();
}
var numSteps = 0;
var curStep = 0;
var timer ;
var steps ;
function play(gameDetail) {
    steps = gameDetail ;
    numSteps = steps.length;
    chessboard = new Map();
    timer = setInterval(function () {
        go(chessboard)
    },1000);
}
function go(chessboard) {
    if(curStep == numSteps){
        window.clearInterval(timer);
        curStep = 0;
        chessboard.clear();
        return ;
    }
    var color = 'black';
    if(curStep % 2 == 1){
        color = 'white';
    }
    oneStep(steps[curStep].detail.x, steps[curStep].detail.y, color, chessboard);
    curStep += 1;
}

