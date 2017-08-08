$("#profileAvatar").click(function (e) {
   e.preventDefault();
   avatarFunc($(this).attr("href"));
});

$("#profileAvatar").dblclick(function (e) {
   e.preventDefault();
   avatarFunc($(this).attr("href"));

});

function avatarFunc(link) {
  var dialog = bootbox.dialog({
     message: '<br/><img class="center-block" src="' + link + '"/>',
     size: "small",
	 closeButton: true,
	 backdrop: true,
	 onEscape: true
 });
}
