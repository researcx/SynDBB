function setCookie(key, value) {
    var expires = new Date();
    expires.setTime(expires.getTime() + (1 * 24 * 60 * 60 * 1000));
    document.cookie = key + '=' + value + ';expires=' + expires.toUTCString();
}

function getCookie(key) {
    var keyValue = document.cookie.match('(^|;) ?' + key + '=([^;]*)(;|$)');
    return keyValue ? keyValue[2] : null;
}

$(document).ready(function() {
    if(!getCookie("nsfwAllow")){
      bootbox.confirm({
          title: "NSFW Warning",
          message: "This forum may contain content which has been deemed <strong>Not Safe For Work</strong>!",
          backdrop: false,
          closeButton: false,
          onEscape: false,
          animate: false,
          className: "nsfwModal",
          buttons: {
              confirm: {
                  label: 'Enter',
                  className: 'btn-success'
              },
              cancel: {
                  label: 'Leave',
                  className: 'btn-danger'
              }
          },
          callback: function (result) {
              if(result == true) {
                this.modal('hide')
                setCookie("nsfwAllow", "1");
              }else{
                window.location.assign("/");
              }
          }
      });
    }
});
