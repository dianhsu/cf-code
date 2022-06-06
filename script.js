// ==UserScript==
// @name        GYM code view - codeforces.com
// @namespace   Violentmonkey Scripts
// @match       https://codeforces.com/gym/*/status
// @grant       MIT
// @version     1.2
// @author      dianhsu
// @run-at      document-idle
// @license     MIT
// @downloadURL https://raw.githubusercontent.com/dianhsu/cf-code/main/script.js
// @homepageURL https://github.com/dianhsu/cf-code
// @supportURL  https://github.com/dianhsu/cf-code/issues
// @description 查看Codeforces GYM中的代码
// ==/UserScript==

$(function () {
    'use strict';
    let $tbody = $('table.status-frame-datatable>tbody');
    let tr = $tbody.find('tr');
    let reg = /\d+/g;
    let contestId = window.location.pathname.match(reg);
    for (let i = 1; i < tr.length; ++i) {
        let td = $(tr[i]).find('td');
        let submissionId = tr[i].dataset.submissionId;
        let cell = $(td[0]).find('span.hiddenSource');
        if (cell.length > 0) {
            let item = document.createElement("a");
            item.href = `https://cf.dianhsu.com/gym/${contestId}/submission/${submissionId}`;
            item.text = `${submissionId}`;
            item.target = '_blank';
            cell.after(item);
            cell.remove();
        }
    }
});
