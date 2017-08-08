function replyTo(id){
  $("#reply").val(id);
  $("html, body").animate({
      scrollTop: 0
  }, 9000);
}

function replyToNested(id, user){
  $("#reply").val(id);
  $("#postform").val("**"+user+":** ");
    $("html, body").animate({
        scrollTop: 0
    }, 1);
}

function replyToThread(id){
	$("#postform").val($("#postform").val() + "[reply]"+id+"[/reply]\n\n");
	$("#replyToPost").val(id);
	$("html, body").animate({
		scrollTop: $(document).height()-$(window).height()
	}, 1);
	setTimeout(function(){
		$('#postform').focus();
	},100);
}

function redirect(data){
   window.location.assign(data);
};

function refresh() {
  window.location.reload();
}

function update_checks() {
    var title = $("#thread_title").val();
    var content = $("#postform").val();

    var allowed = true;

    if(content == "" || (title == "" && document.getElementById("thread_title"))) {
        allowed = false;
    }

    return allowed;
}

$("#activityform").submit(function(event) {
    if(update_checks()) {
        $.ajax({
            type: "POST",
            url: "/functions/create_reply/",
            data: $("#activityform").serialize(),
            success: function(data)
            {
                if(data[0] == "/"){
				  if(document.getElementById("postEdit")) {
                    var dialog = bootbox.dialog({
                        title: 'Post Editing',
                        message: '<i class="fa fa-spin fa-cog fa-fw" style="margin-right: 5px;"></i> Redirecting you to the edited post. ',
                        closeButton: false
                    });
                    setTimeout(redirect(data), 500);
			      } else if(document.getElementById("thread_title")) {
                    var dialog = bootbox.dialog({
                        title: 'Thread Submission',
                        message: '<i class="fa fa-spin fa-cog fa-fw" style="margin-right: 5px;"></i> Redirecting you to the created thread. ',
                        closeButton: false
                    });
                    setTimeout(redirect(data), 500);
                  } else {
                    var dialog = bootbox.dialog({
                        title: 'Post Submission',
                        message: '<i class="fa fa-spin fa-cog fa-fw" style="margin-right: 5px;"></i> Redirecting you to the created post.',
                        closeButton: false
                    });
                    $("#postform").val("");
                    setTimeout(refresh, 500);
                  }

                } else {
                  var title = "";

                  if(document.getElementById("thread_title")) {
                    title = "Thread Submission";
                  } else {
                    title = "Post Submission";
                  }

                  var dialog = bootbox.dialog({
                      title: title,
                      message: '<p class="text-center">' + data + '</p>',
                      closeButton: true,
					  backdrop: true,
					  onEscape: true
                  });
                }
            }
        });
    }

    event.preventDefault();
});
