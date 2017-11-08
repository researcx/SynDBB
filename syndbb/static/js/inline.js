$(".profile-inline").click(function (e) {
    e.preventDefault();
    inlineReply($(this).attr("href"));
});

$(".profile-inline").dblclick(function (e) {
    e.preventDefault();
    inlineReply($(this).attr("href"));
});

function inlineProfile(link) {
        $.ajax({
            type: "GET",
            url: link+"?inlinecontent=1",
            data: $(".profile-inline").serialize(),
            success: function(data)
            {
			  bootbox.dialog({
				  message: data,
				  backdrop: true,
				  onEscape: true
			  });
		}
   });
}

$(".reply-inline").click(function (e) {
    e.preventDefault();
    inlineReply($(this).attr("href"));
});

$(".reply-inline").dblclick(function (e) {
    e.preventDefault();
    inlineReply($(this).attr("href"));
});

function inlineReply(link) {
      $.ajax({
          type: "GET",
          url: link+"?inlinecontent=1",
          data: $(".reply-inline").serialize(),
          success: function(data)
          {
    			  bootbox.dialog({
    				  message: data,
    				  backdrop: true,
    				  onEscape: true,
    				  className: "replies-dialog"
    			  });
	        }
   });
}

$('.majorpoints').click(function(){
    $(this).find('.hider').toggle();
    
    // Find the iframes within our newly-visible element
    $(this).find("iframe").prop("src", function(){
        // Set their src attribute to the value of data-src
        return $(this).data("src");
    });
});