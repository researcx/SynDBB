$(function() {
  $('.image-editor').cropit({ maxZoom: 4, });

  $('form').submit(function() {
    // Move cropped image data to hidden input
    var imageData = $('.image-editor').cropit('export');
    $('.hidden-image-data').val(imageData);
  });
});

$("#avatar_crop").change(function(){
     $("#avatarform").removeClass("hidden");
 });
