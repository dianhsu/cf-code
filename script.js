// ==UserScript==
// @name        GYM code view - codeforces.com
// @namespace   Violentmonkey Scripts
// @match       https://codeforces.com/gym/*/status
// @grant       MIT
// @version     1.0
// @author      dianhsu
// @run-at      document-idle
// @description 2022/6/4 15:41:09
// ==/UserScript==

function init(){
  let items = document.querySelector('.status-frame-datatable').querySelectorAll('tr')
  let reg = /\d+/g;
  let contestId = window.location.pathname.match(reg);
  items.forEach(function(item){
    if(item.className === 'first-row'){
      let th = document.createElement('th');
      th.class = 'top right';
      th.append("View");
      item.append(th);
    }else{
      let submissionId = item.dataset.submissionId;
      let td = document.createElement('td');
      let a = document.createElement('a');
      a.append('code');
      a.title = 'code';
      a.target = '_blank';
      a.href = `https://cf.dianhsu.com/gym/${contestId}/submission/${submissionId}`;
      td.append(a);
      item.append(td);
    }
  });
};

init();
