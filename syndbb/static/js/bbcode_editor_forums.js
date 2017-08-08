function insert_bbcode(id){
  var bbcode = id;
  var before = "["+bbcode+"]"
  var after = "[/"+bbcode+"]"

  if(bbcode == "url"){
    var before = "["+bbcode+"=]"
    var after = "[/"+bbcode+"]"
  }

  if(bbcode == "size"){
    var before = "["+bbcode+"=4]"
    var after = "[/"+bbcode+"]"
  }

  if(bbcode == "color"){
    var before = "["+bbcode+"=red]"
    var after = "[/"+bbcode+"]"
  }

  if(bbcode == "bulletlist"){
    var before = "[ul]\n[li]"
    var after = "[/li]\n[/ul]"
  }

  if(bbcode == "orderedlist"){
    var before = "[ol]\n[li]"
    var after = "[/li]\n[/ol]"
  }

  $(".bbcode-textarea").surroundSelectedText(before, after)
  //$txt.val(textAreaTxt.substring(0, caretPos) + before + after + textAreaTxt.substring(caretPos));

  //textarea.val(textarea.val() + before + after);
}

function show_emoticons(){
	window.open('/emoticons/','_blank');
}

$("#submitContent").click(function (e) {
    e.preventDefault();
    $( "#activityform" ).submit();
});

$("#submitContent").dblclick(function (e) {
    e.preventDefault();
    $( "#activityform" ).submit();
});


$("#previewContent").click(function (e) {
    e.preventDefault();
    inlinePreview($(this).attr("href"));
});

$("#previewContent").dblclick(function (e) {
    e.preventDefault();
    inlinePreview($(this).attr("href"));
});

function inlinePreview(){
  $.ajax({
      type: "POST",
      url: "/functions/preview_bbcode/",
      data: $("#activityform").serialize(),
      success: function(data)
      {
			  bootbox.dialog({
				  message: data,
				  backdrop: true,
				  onEscape: true,
          size: 'large',
				  className: "replies-dialog"
			  });
      }
   });
}


$("#uploadContent").click(function (e) {
    e.preventDefault();
    uploadContent($(this).attr("href"));
});

$("#uploadContent").dblclick(function (e) {
    e.preventDefault();
    uploadContent($(this).attr("href"));
});

function uploadContent(){
  $.ajax({
      type: "GET",
      url: "/upload/simple/",
      data: $("#uploadContent").serialize(),
      success: function(data)
      {
			  bootbox.dialog({
				  message: data,
				  backdrop: true,
				  onEscape: true,
          size: 'large',
				  className: "replies-dialog"
			  });
      }
   });
}


function initUpload(){
  $('#uploadform').css('display', 'none');
  $('#uploadLoader').css('display', 'block');
  var form = new FormData($("#uploadform")[0]);
  $.ajax({
      url: "/functions/upload",
      method: "POST",
      data: form,
      processData: false,
      contentType: false,
      success: function(data)
      {
        bootbox.hideAll()
        $.ajax({
            type: "GET",
            url: data,
            data: $("#uploadContent").serialize(),
            success: function(data)
            {
      			  bootbox.dialog({
      				  message: data,
      				  backdrop: true,
      				  onEscape: true,
                size: 'large',
      				  className: "replies-dialog"
      			  });
            }
         });
      }
   });
}
