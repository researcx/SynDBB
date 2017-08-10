$(".addalbum").click(function (e) {
    e.preventDefault();
    img = $(this).attr("id");
    $("a#albumlink").attr("href", function(i, href) {
      return href + img + ';';
    });
    var dialog = bootbox.dialog({
        message: "Image has been added to the temporary album.",
        size: 'small',
        closeButton: false,
        backdrop: false,
        onEscape: true
    });

    dialog.init(function(){
        setTimeout(function(){
            dialog.modal('hide');
        }, 500);
    });

});
