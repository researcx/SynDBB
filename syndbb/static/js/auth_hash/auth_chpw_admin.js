function redirect(){
   window.location.assign("/account/admin/users");
};

$("#pwform").submit(function(event) {
  var crypt = new Crypt();
  var user_id = $("#user_id").val();
  var plain_pw2 = $("#inputPassword").val();
  var confirm_pw2 = $("#confirmPassword").val();
  var newpassword = CryptoJS.SHA256(plain_pw2);

  if(plain_pw2 != confirm_pw2){
    $("#submission").addClass("disabled");
    $("#password").addClass("has-error");
  }else{
    $("#submission").removeClass("disabled");
    $("#password").removeClass("has-error");
  }

  $("#user_id").val(user_id);
  $("#newpword").val(newpassword);

  if(plain_pw2 == confirm_pw2) {

  $.ajax({
         type: "POST",
         url: "/functions/admin_change_password/",
         data: $("#pwform").serialize(),
         success: function(data)
         {
           if(data == "Password change successful."){
             var dialog = bootbox.dialog({
                 title: 'Password Change',
                 message: '<i class="fa fa-spin fa-cog fa-fw" style="margin-right: 5px;"></i> Password change successful. Redirecting you back to the users page... ',
                 closeButton: false
             });
             setTimeout(redirect, 500);
           } else {
             var dialog = bootbox.dialog({
                 title: 'Password Change',
                 message: data,
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

$("#inputPassword").on("change keyup paste click", function() {
  var plain_pw = $("#inputPassword").val();
  var score = scorePassword(plain_pw);
  var txtscore = checkPassStrength(score);

  if(score > 100) {
    $("#stronk").css('width', 100+'%').attr("aria-valuenow", score);
  }
  else {
    $("#stronk").css('width', score+'%').attr("aria-valuenow", score);
  }

  if(txtscore == "") {
    $("#stronk").addClass("progress-bar-danger").removeClass("progress-bar-info").removeClass("progress-bar-warning").removeClass("progress-bar-success");
    $("#submission").addClass("disabled");
    $("#password").addClass("has-error");
  }
  else if(txtscore == "Weak") {
    $("#stronk").removeClass("progress-bar-danger").addClass("progress-bar-warning").removeClass("progress-bar-info").removeClass("progress-bar-success");
    $("#submission").removeClass("disabled");
    $("#password").removeClass("has-error");
  }
  else if(txtscore == "Good") {
    $("#stronk").removeClass("progress-bar-danger").removeClass("progress-bar-warning").removeClass("progress-bar-info").addClass("progress-bar-success");
    $("#submission").removeClass("disabled");
    $("#password").removeClass("has-error");
  }
  else if(txtscore == "Strong") {
    $("#stronk").removeClass("progress-bar-danger").removeClass("progress-bar-warning").removeClass("progress-bar-success").addClass("progress-bar-info");
    $("#submission").removeClass("disabled");
    $("#password").removeClass("has-error");
  }

  if(txtscore != "") {
    $("#score").text(score + " - " + txtscore);
  }
  else {
    $("#score").text(score + " - None");
  }
});

$("#confirmPassword").on("change keyup paste click", function() {
  var confirm_pw2 = $("#confirmPassword").val();
  var plain_pw2 = $("#inputPassword").val();

  if(plain_pw2 != confirm_pw2) {
    $("#submission").addClass("disabled");
    $("#confPassword").addClass("has-error");
  } else {
    $("#submission").removeClass("disabled");
    $("#confPassword").removeClass("has-error");
  }
});

function scorePassword(pass) {
    var score = 0;
    if (!pass)
        return score;

    // award every unique letter until 5 repetitions
    var letters = new Object();
    for (var i=0; i<pass.length; i++) {
        letters[pass[i]] = (letters[pass[i]] || 0) + 1;
        score += 5.0 / letters[pass[i]];
    }

    // bonus points for mixing it up
    var variations = {
        digits: /\d/.test(pass),
        lower: /[a-z]/.test(pass),
        upper: /[A-Z]/.test(pass),
        nonWords: /\W/.test(pass),
    }

    variationCount = 0;
    for (var check in variations) {
        variationCount += (variations[check] == true) ? 1 : 0;
    }
    score += (variationCount - 1) * 10;

    return parseInt(score);
}

function checkPassStrength(score) {
    if (score > 80)
        return "Strong";
    if (score > 60)
        return "Good";
    if (score >= 30)
        return "Weak";

    return "";
}
