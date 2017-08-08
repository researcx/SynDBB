$(".DoRatingUp").click(function (e) {
    e.preventDefault();
    DoPostRateUp($(this).attr("href"));
});

$(".DoRatingUp").dblclick(function (e) {
    e.preventDefault();
    DoPostRateUp($(this).attr("href"));
});

function DoPostRateUp(content){
  $.ajax({
      type: "GET",
      url: content,
      data: "",
      success: function(data)
      {
        if(Math.floor(data) == data && $.isNumeric(data)){
          var num = parseInt($('.PostRating-'+data).text());
          $('.PostRating-'+data).text(num+1);
        }else{
  			  bootbox.dialog({
  				  message: data,
  				  backdrop: true,
  				  onEscape: true,
            size: 'small',
  				  className: "replies-dialog"
  			  });
        }
      }
   });
}

$(".DoRatingDown").click(function (e) {
    e.preventDefault();
    DoPostRateDown($(this).attr("href"));
});

$(".DoRatingDown").dblclick(function (e) {
    e.preventDefault();
    DoPostRateDown($(this).attr("href"));
});

function DoPostRateDown(content){
  $.ajax({
      type: "GET",
      url: content,
      data: "",
      success: function(data)
      {
        if(Math.floor(data) == data && $.isNumeric(data)){
          var num = parseInt($('.PostRating-'+data).text());
          $('.PostRating-'+data).text(num-1);
        }else{
  			  bootbox.dialog({
  				  message: data,
  				  backdrop: true,
  				  onEscape: true,
            size: 'small',
  				  className: "replies-dialog"
  			  });
        }
      }
   });
}
