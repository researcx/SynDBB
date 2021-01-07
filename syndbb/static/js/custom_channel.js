function redirect(data){
   window.location.assign(data);
};

function update_checks() {
    var title = $("#channel-name").val();
    var content = $("#channel-description").val();

    var allowed = true;

    if(content == "" || (title == "" && document.getElementById("channel-name"))) {
        allowed = false;
    }

    return allowed;
}

$("#custom-channel").submit(function(event) {
    if(update_checks()) {
        $.ajax({
            type: "POST",
            url: "/functions/custom_channel/",
            data: $("#custom-channel").serialize(),
            success: function(data)
            {
                if(data[0] == "/"){
                    var dialog = bootbox.dialog({
                        title: 'Channel Creation',
                        message: '<i class="fa fa-spin fa-cog fa-fw" style="margin-right: 5px;"></i> Redirecting you to the created channel.',
                        closeButton: false
                    });
                    setTimeout(redirect(data), 500);
                } else {
                  var dialog = bootbox.dialog({
                      title: 'Channel Creation',
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
