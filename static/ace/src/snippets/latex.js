define("ace/snippets/latex",["require","exports","module"], function(require, exports, module) {
"use strict";

exports.snippetText =undefined;
exports.scope = "latex";

});
                (function() {
                    window.require(["ace/snippets/latex"], function(m) {
                        if (typeof module == "object") {
                            module.exports = m;
                        }
                    });
                })();
            