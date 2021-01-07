$(document).ready(function() {
    if(!getCookie("nsfwAllow")){
      bootbox.confirm({
          title: "NSFW Warning",
          message: "This page may contain content which has been deemed <strong>Not Safe For Work</strong>!",
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
                window.location.reload();
                setCookie("nsfwAllow", "1", 356);
              }else{
                window.location.assign("/");
              }
          }
      });
    }
});
