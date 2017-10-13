/*!
 * IE10 viewport hack for Surface/desktop Windows 8 bug
 * Copyright 2014-2015 Twitter, Inc.
 * Licensed under MIT (https://github.com/twbs/bootstrap/blob/master/LICENSE)
 */

// See the Getting Started docs for more information:
// http://getbootstrap.com/getting-started/#support-ie10-width

(function () {
  'use strict';

  if (navigator.userAgent.match(/IEMobile\/10\.0/)) {
    var msViewportStyle = document.createElement('style')
    msViewportStyle.appendChild(
      document.createTextNode(
        '@-ms-viewport{width:auto!important}'
      )
    )
    document.querySelector('head').appendChild(msViewportStyle)
  }

})();


function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function set_theme(theme) {
  setCookie("theme", theme, 356);
  themepath = "#";
  if (theme == "invert"){
  themepath = "/static/css/invert.css";
  }
  if (theme == "oify"){
  themepath = "/static/css/oify.css";
  }
  document.getElementById('themeselector').href=themepath;
}

  $(document).ready(function() {
    $('#uploads').DataTable( {
        "dom": '<"top"p<"clear">>rt<"bottom"p<"clear">>',
        "ordering": false,
        "info":     false,
        "stateSave": true,
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]]
    } );
  } );