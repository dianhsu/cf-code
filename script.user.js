// ==UserScript==
// @name        GYM code view - codeforces.com
// @namespace   Violentmonkey Scripts
// @match       https://codeforces.com/gym/*/status
// @match       https://codeforces.com/submissions/*
// @match       https://codeforces.ml/gym/*/status
// @match       https://codeforces.ml/submissions/*
// @match       https://codeforc.es/gym/*/status
// @match       https://codeforc.es/submissions/*
// @grant       MIT
// @version     1.5
// @author      dianhsu
// @run-at      document-idle
// @downloadURL https://raw.githubusercontent.com/dianhsu/cf-code/main/script.user.js
// @homepageURL https://greasyfork.org/zh-CN/scripts/446066-gym-code-view-codeforces-com
// @supportURL  https://github.com/dianhsu/cf-code/issues
// @description 在没有登录或者没有开启Coach模式的时候查看Codeforces GYM的代码
// ==/UserScript==

$(function () {
  'use strict';
  let $tbody = $('table.status-frame-datatable>tbody');
  let tr = $tbody.find('tr');
  let reg = /\d+/g;
  for (let i = 1; i < tr.length; ++i) {
    let td = $(tr[i]).find('td');
    let submissionId = tr[i].dataset.submissionId;
    let cell = $(td[0]).find('span.hiddenSource');
    let problem = $(td[3]).children("a").get(0).getAttribute('href');
    let contestId = problem.match(reg);
    if (cell.length > 0) {
      let item = document.createElement("a");
      item.href = `https://cf.dianhsu.com/gym/${contestId}/submission/${submissionId}?version=${GM_info.script.version}`;
      item.text = `${submissionId}`;
      item.target = '_blank';
      cell.after(item);
      cell.remove();
    }
  }
});
