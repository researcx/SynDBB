function redirect(){
   window.location.assign("/");
};

$("#loginform").submit(function(event) {
  var crypt = new Crypt();
  var plain_pw = $("#inputPassword").val();
  var password = CryptoJS.SHA256(plain_pw);

  $("#pword").val(password);

  $.ajax({
         type: "POST",
         url: "/functions/login",
         data: $("#loginform").serialize(),
         success: function(data)
         {
           if(data == "Login successful."){
             var dialog = bootbox.dialog({
                 title: 'Login Attempt',
                 message: '<i class="fa fa-spin fa-cog fa-fw" style="margin-right: 5px;"></i> Login successful. Redirecting you to the main page...',
                 closeButton: false
             });
             setTimeout(redirect, 500);
           } else {
             var dialog = bootbox.dialog({
                 title: 'Login Attempt',
                 message: data,
                 closeButton: true,
                 backdrop: true,
                 onEscape: true
             });
           }
         }
       });

  event.preventDefault();
});
