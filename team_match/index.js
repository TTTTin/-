const ArgumentType = require('../../extension-support/argument-type');
const BlockType = require('../../extension-support/block-type');
const formatMessage = require('format-message');



/**
 * The url of the server
 * @type {string}
 */

/**
 * Class for test
 * @constructor
 */

var gobang = function() {

    this.chessboard = null;

    this.CONNECTING = 0;
    this.OPEN = 1;
    this.CLOSING = 2;
    this.CLOSED = 3;
    this.gameStartSignal = false ;
    this.gameEndSignal = false ;

    this.opponentChessCount = 0;
    this.selfChessCount = 0;

    this.connectTimer = null;
    this.sendTimer = null;
    this.ACK = false;
    this.sendCycle = 180000; //ms
    this.connectCycle = 30000; //ms

    this.first = false ;

    this.recvOpponentMess = false ;
    this.opCode = null ;
    this.color = null ;

    this.opponentRow = 0;
    this.opponentCol = 0;
    this.gameSocket = null;
    this.wsUrl = null;

    this.sendMessFunction = null;
    this.connectFunction = null;

    this.sendReadySingalFunction = null;
    this.sendReadySingalTimer = null;
    this.sendReadySingalCycle = 30000;

    this.selfRow = null;
    this.selfCol = null;

    this.receiveAiResultSignal = false;
};




class Scratch3GobangBlocks {

    constructor () {

        window.obj = new gobang();

        window.obj.chessboard = new Array();
        for(var i  = 0; i < 15; i++){
            window.obj.chessboard[i] = new Array();
            for(var j = 0; j < 15; j++){
                window.obj.chessboard[i][j] = -1;
            }
        }

    }
    /**
     * The key to load & store a target's translate state.
     * @return {string} The key.
     */
    static get STATE_KEY () {
        return 'Scratch.Gobang';
    }

    /**
     * @returns {object} metadata for this extension and its blocks.
     */
    getInfo () {

        return {
            id: 'Gobang',
            name: formatMessage({
                id: 'Gobang.categoryName',
                default: 'Gobang',
                description: 'Name of extension Gobang'
            }),
            blocks: [
                {
                    opcode: 'init',
                    text: formatMessage({
                        id: 'Gobang.init',
                        default: 'gobang game init',
                        description: 'gobang game init'
                    }),
                    blockType: BlockType.COMMAND
                },
                {
                    opcode: 'sendMessage',
                    text: formatMessage({
                        id: 'Gobang.sendMessageBlock',
                        default: 'drop chesspiece at row[ROW] col[COL]',
                        description: 'send message'
                    }),
                    blockType: BlockType.COMMAND,
                    arguments: {
                        ROW: {
                            type: ArgumentType.NUMBER,
                            defaultValue: formatMessage({
                                id: 'sendMessage.row',
                                default: 0,
                                description: 'row'
                            })
                        },
                        COL: {
                            type: ArgumentType.NUMBER,
                            defaultValue: formatMessage({
                                id: 'sendMessage.col',
                                default: 0,
                                description: 'col'
                            })
                        }
                    }
                },
                {
                    opcode: 'info_row',
                    text: formatMessage({
                        id: 'Gobang.row',
                        default: 'row',
                        description: 'row'
                    }),
                    blockType: BlockType.REPORTER
                },
                {
                    opcode: 'info_col',
                    text: formatMessage({
                        id: 'Gobang.col',
                        default: 'col',
                        description: 'col'
                    }),
                    blockType: BlockType.REPORTER
                },
                {
                    opcode: 'info_first',
                    text: formatMessage({
                        id: 'Gobang.first',
                        default: 'I action first',
                        description: 'I action first'
                    }),
                    blockType: BlockType.BOOLEAN
                },
                {
                    opcode: 'info_end',
                    text: formatMessage({
                        id: 'Gobang.end',
                        default: 'game end',
                        description: 'game end'
                    }),
                    blockType: BlockType.BOOLEAN
                },
                {
                    opcode: 'info_start',
                    text: formatMessage({
                        id: 'Gobang.start',
                        default: 'game start',
                        description: 'game start'
                    }),
                    blockType: BlockType.BOOLEAN
                },
                {
                    opcode: 'info_recvMess',
                    text: formatMessage({
                        id: 'Gobang.recvMess',
                        default: 'receive opponent\'s action message',
                        description: 'recvMess'
                    }),
                    blockType: BlockType.BOOLEAN
                },
                {
                    opcode: 'info_recvAiRequest',
                    text: formatMessage({
                        id: 'Gobang.recvAiRequest',
                        default: 'receive gobang ai request',
                        description: 'recvAiRequest'
                    }),
                    blockType: BlockType.BOOLEAN
                },
                {
                    opcode: 'get_info_chess_board',
                    text: formatMessage({
                        id: 'Gobang.getInfoChessBoard',
                        default: 'get chess board row[ROW] col[COL]',
                        description: 'get info chess board'
                    }),
                    blockType: BlockType.REPORTER,
                    arguments: {
                        ROW: {
                            type: ArgumentType.NUMBER,
                            defaultValue: formatMessage({
                                id: 'getInfoChessBoard.row',
                                default: 0,
                                description: 'row'
                            })
                        },
                        COL: {
                            type: ArgumentType.NUMBER,
                            defaultValue: formatMessage({
                                id: 'getInfoChessBoard.col',
                                default: 0,
                                description: 'col'
                            })
                        }
                    }
                },
                {
                    opcode: 'set_info_chess_board',
                    text: formatMessage({
                        id: 'Gobang.setInfoChessBoard',
                        default: 'set chess board row[ROW] col[COL] value[VAL]',
                        description: 'set info chess board'
                    }),
                    blockType: BlockType.COMMAND,
                    arguments: {
                        ROW: {
                            type: ArgumentType.NUMBER,
                            defaultValue: formatMessage({
                                id: 'setInfoChessBoard.row',
                                default: 0,
                                description: 'row'
                            })
                        },
                        COL: {
                            type: ArgumentType.NUMBER,
                            defaultValue: formatMessage({
                                id: 'setInfoChessBoard.col',
                                default: 0,
                                description: 'col'
                            })
                        },
                        VAL: {
                            type: ArgumentType.NUMBER,
                            defaultValue: formatMessage({
                                id: 'setInfoChessBoard.val',
                                default: 0,
                                description: 'val'
                            })
                        }
                    }
                },
                {
                    opcode: 'naive_gobang_ai_request',
                    text: formatMessage({
                        id: 'Gobang.naiveGobangAiRequest',
                        default: 'naive gobang ai request',
                        description: 'naive gobang ai request'
                    }),
                    blockType: BlockType.COMMAND
                },
                {
                    opcode: 'smart_gobang_ai_request',
                    text: formatMessage({
                        id: 'Gobang.smartGobangAiRequest',
                        default: 'smart gobang ai request',
                        description: 'smart gobang ai request'
                    }),
                    blockType: BlockType.COMMAND
                }
            ],
            menus: {

            }
        };
    }

    smart_gobang_ai_request(){
        let serializeBoard = "";
        for(var i = 0; i < 15; i++){
            let rowSerialized = window.obj.chessboard[i][0].toString();
            for(var j = 1; j < 15; j++){
                rowSerialized = rowSerialized + "," + window.obj.chessboard[i][j].toString();
            }
            if(serializeBoard === ""){
                serializeBoard = serializeBoard + rowSerialized;
            }else{
                serializeBoard = serializeBoard + ";" + rowSerialized;
            }
        }
        let color = 0;
        if(window.obj.color === 'white'){
            color = 1;
        }
        window.obj.receiveAiResultSignal = false;
        $.ajax({
            url : "http://" + window.location.host + "/team_match/smart_gobang_ai_request/",
            type : 'POST',
            data : {
                'chessboard' : serializeBoard,
                'color' : color
            },
            dataType : 'json',
            success : function (data) {
                window.obj.opponentRow = data.row;
                window.obj.opponentCol = data.col;
                window.obj.receiveAiResultSignal = true;
            },
            error : function () {
                alert("server error...");
            }
        });
    }

    naive_gobang_ai_request(){
        let serializeBoard = "";
        for(var i = 0; i < 15; i++){
            let rowSerialized = window.obj.chessboard[i][0].toString();
            for(var j = 1; j < 15; j++){
                rowSerialized = rowSerialized + "," + window.obj.chessboard[i][j].toString();
            }
            if(serializeBoard === ""){
                serializeBoard = serializeBoard + rowSerialized;
            }else{
                serializeBoard = serializeBoard + ";" + rowSerialized;
            }
        }
        let color = 0;
        if(window.obj.color === 'white'){
            color = 1;
        }
        window.obj.receiveAiResultSignal = false;
        $.ajax({
            url : "http://" + window.location.host + "/team_match/naive_gobang_ai_request/",
            type : 'POST',
            data : {
                'chessboard' : serializeBoard,
                'color' : color
            },
            dataType : 'json',
            success : function (data) {
                window.obj.opponentRow = data.row;
                window.obj.opponentCol = data.col;
                window.obj.receiveAiResultSignal = true;
            },
            error : function () {
                alert("server error...");
            }
        });
    }

    set_info_chess_board(args){
        window.obj.chessboard[args.ROW - 1][args.COL - 1] = args.VAL;
    }

    get_info_chess_board(args){
        return window.obj.chessboard[args.ROW - 1][args.COL - 1];
    }

    info_recvAiRequest(){
        return window.obj.receiveAiResultSignal;
    }

    info_recvMess(){
        return  window.obj.recvOpponentMess;
    }
    info_start(){
        return window.obj.gameStartSignal;
    }
    info_end(){
        return window.obj.gameEndSignal;
    }
    info_first(){
        return window.obj.first;
    }
    init(){
        if(window.opCodeAndMess === null) return ;

        if(window.opCodeAndMess.substr(16, 1) === '1'){
            window.obj.first = true;
            window.obj.color = 'black';
        }else if(window.opCodeAndMess.substr(16, 1) === '2'){
            window.obj.first = false;
            window.obj.color = 'white';
        }else{
            return false;
        }

        function getCookie(cname)
        {
            var name = cname + "=";
            var ca = document.cookie.split(';');
            for(var i=0; i<ca.length; i++)
            {
                var c = ca[i].trim();
                if (c.indexOf(name)===0) return c.substring(name.length,c.length);
            }
            return "";
        }

        window.obj.opCode = window.opCodeAndMess.substr(0, 16);
        var type = getCookie(window.obj.opCode);
        if(type === 'notAI'){
            window.obj.wsUrl = 'ws://' + window.location.host + '/ws/battleroom/' + window.obj.opCode + '/';
        }else if(type === 'AI'){
            window.obj.wsUrl = 'ws://' + window.location.host + window.obj.opCode + '/';
        }else{
            return false;
        }

        window.obj.sendReadySingalFunction = function () {
            if(window.obj.gameStartSignal === true || window.obj.gameEndSignal === true){
                window.clearInterval(window.obj.sendReadySingalTimer); return ;
            }
            console.log("send ready signal...");
            let message = {'type': 'readySignal', 'opCode': window.obj.opCode, 'role': window.obj.color};
            window.obj.gameSocket.send(JSON.stringify({
                'message': message
            }));
        };

        window.obj.connectFunction = function () {
            //已经处于连接状态
            if(window.obj.gameSocket !== null && window.obj.gameSocket.readyState === window.obj.OPEN) return ;
            //比赛已经结束
            if(window.obj.gameEndSignal === true){window.clearInterval(window.obj.connectTimer); window.clearInterval(window.obj.sendTimer); return ;}
            window.obj.gameSocket = new WebSocket(window.obj.wsUrl);
            window.obj.gameSocket.onopen = function () {
                // 连接之后，如果比赛还没开始，则发送ready信号
                if(window.obj.gameStartSignal === null || window.obj.gameStartSignal === false){
                    window.obj.sendReadySingalFunction();
                    window.obj.sendReadySingalTimer = setInterval("window.obj.sendReadySingalFunction();", window.obj.sendReadySingalCycle);
                }
            };
            window.obj.gameSocket.onclose = function(e) {
                console.log('Chat socket closed ');
            };
            window.obj.gameSocket.onmessage = function(e) {
                let data = JSON.parse(e.data);
                let message = data['message'];
                if(message['type'] === 'gameStart'){
                    window.obj.gameStartSignal = true;
                    window.clearInterval(window.obj.sendReadySingalTimer);
                }else if(message['type'] === 'action'){
                    if(data['message']['color'] !== window.obj.color) {
                        if(data['message']['count'] === window.obj.opponentChessCount + 1){
                            window.obj.opponentChessCount = window.obj.opponentChessCount + 1;

                            let chess = window.obj.opponentChessCount * 2 - 2;
                            if (window.obj.color === 'black') {
                                chess = window.obj.selfChessCount * 2 - 1;
                            }
                            window.obj.chessboard[Number(data['message']['row']) - 1][Number(data['message']['col']) - 1] = chess;

                            window.obj.opponentRow = data['message']['row'];
                            window.obj.opponentCol = data['message']['col'];
                            window.obj.recvOpponentMess = true;
                            window.obj.ACK = true;
                        }

                    }
                    if(data['message']['gameEnd']) {
                        window.obj.gameEndSignal = true;
                        window.clearInterval(window.obj.connectTimer);
                        window.clearInterval(window.obj.sendTimer);
                        window.obj.gameSocket.close();
                    }
                }else if(message['type'] === 'gameEnd'){
                    window.obj.gameEndSignal = true;
                    window.clearInterval(window.obj.connectTimer);
                    window.clearInterval(window.obj.sendTimer);
                    window.obj.gameSocket.close();
                }
            };
        };
        window.obj.connectFunction();
        window.obj.connectTimer = setInterval("window.obj.connectFunction();", window.obj.connectCycle);
    }
    info_col() {
        return window.obj.opponentCol;
    }
    info_row() {
        return window.obj.opponentRow;
    }

    /**
     *  send drop chesspiece message row and col
     */
    sendMessage (args) {

        window.obj.selfChessCount = window.obj.selfChessCount + 1;
        window.obj.ACK = false;
        window.obj.recvOpponentMess = false;
        window.obj.sendMessFunction = function (row, col, count) {
            if(window.obj.ACK === true){window.clearInterval(window.obj.sendTimer); return false;}
            let message = {'type': 'action', 'row': row, 'col': col, 'color': window.obj.color, 'count': count};
            window.obj.gameSocket.send(JSON.stringify({
                'message': message
            }));
        };

        let chess = window.obj.selfChessCount * 2 - 2;
        if (window.obj.color === 'white') {
            chess = window.obj.selfChessCount * 2 - 1;
        }
        window.obj.chessboard[Number(args.ROW) - 1][Number(args.COL) - 1] = chess;

        window.obj.selfRow = args.ROW;
        window.obj.selfCol = args.COL;
        window.obj.sendMessFunction(window.obj.selfRow, window.obj.selfCol, window.obj.selfChessCount);
        window.clearInterval(window.obj.sendTimer);
        window.obj.sendTimer = setInterval("window.obj.sendMessFunction(window.obj.selfRow, window.obj.selfCol, window.obj.selfChessCount);", window.obj.sendCycle);
    }


}
module.exports = Scratch3GobangBlocks;

