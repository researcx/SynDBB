function redirect(data){
   window.location.assign(data);
};

function update_checks() {
    var title = $("#forum-name").val();
    var content = $("#forum-description").val();

    var allowed = true;

    if(content == "" || (title == "" && document.getElementById("forum-name"))) {
        allowed = false;
    }

    return allowed;
}

$("#custom-forum").submit(function(event) {
    if(update_checks()) {
        $.ajax({
            type: "POST",
            url: "/functions/custom_forum/",
            data: $("#custom-forum").serialize(),
            success: function(data)
            {
                if(data[0] == "/"){
                    var dialog = bootbox.dialog({
                        title: 'Forum Creation',
                        message: '<i class="fa fa-spin fa-cog fa-fw" style="margin-right: 5px;"></i> Redirecting you to the created forum.',
                        closeButton: false
                    });
                    setTimeout(redirect(data), 500);
                } else {
                  var dialog = bootbox.dialog({
                      title: 'Forum Creation',
                      message: '<p class="text-center">' + data + '</p>',
                      closeButton: true,
                      backdrop: true
                  });
                }
            }
        });
    }

    event.preventDefault();
});
