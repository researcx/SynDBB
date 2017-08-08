function redirect(data){
   window.location.assign(data);
};

$(".deletebutton").click(function (e) {
    e.preventDefault();
    redirFunc($(this).attr("href"));
});

$(".deletebutton").dblclick(function (e) {
    e.preventDefault();
    redirFunc($(this).attr("href"));
});

function redirFunc(link) {
  bootbox.confirm({
      title: "Confirmation",
      message: "Are you sure you want to do this?",
	  backdrop: true,
      buttons: {
          confirm: {
              label: '<i class="fa fa-check"></i> Yes',
              className: 'btn-success'
          },
          cancel: {
              label: '<i class="fa fa-times"></i> No',
              className: 'btn-danger'
          }
      },
      callback: function (result) {
          if(result) {
            setTimeout(redirect(link), 500);
          }
      }
  });
}