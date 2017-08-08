function redirect(){
   window.location.assign("/");
};

function update_checks() {
  var plain_pw = $("#inputPassword").val();
  var confirm_pw = $("#confirmPassword").val();
  var score = scorePassword(plain_pw);
  var username = $("#inputUsername").val();
  var pattern = /^[a-z][a-z0-9-_]{2,32}$/i;

  var submit = true;

  if(!pattern.test(username)){
    $("#username").addClass("has-error");
    submit = false;
  }else{
    $("#username").removeClass("has-error");
  }

  if(plain_pw != confirm_pw || confirm_pw == "") {
    $("#confPassword").addClass("has-error");
    submit = false;
  } else {
    $("#confPassword").removeClass("has-error");
  }

  if(score < 30) {
    $("#password").addClass("has-error");
    submit = false;
  } else {
    $("#password").removeClass("has-error");
  }

  if(submit) {
    $("#submission").removeClass("disabled");
  } else {
    $("#submission").addClass("disabled");
  }

  return submit;
}

$(function() {
  update_checks();
});

$("#regform").submit(function(event) {
  var crypt = new Crypt();
  var plain_pw = $("#inputPassword").val();
  var password = CryptoJS.SHA256(plain_pw);
  var score = scorePassword(plain_pw);
  var confirm_pw = $("#confirmPassword").val();

  $("#pword").val(password);

  if(update_checks()) {
    $.ajax({
           type: "POST",
           url: "/functions/register/",
           data: $("#regform").serialize(),
           success: function(data)
           {
             if(data == "Registration successful."){
               var dialog = bootbox.dialog({
                   title: 'Registration Attempt',
                   message: '<i class="fa fa-spin fa-cog fa-fw" style="margin-right: 5px;"></i> Registration successful. Redirecting you to the main page...',
                   closeButton: false
               });
               setTimeout(redirect, 500);
             } else {
               var dialog = bootbox.dialog({
                   title: 'Registration Attempt',
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

$("#inputUsername").on("change keyup paste click", function() {
  update_checks();
});

$("#inputPassword").on("change keyup paste click", function() {
  var plain_pw = $("#inputPassword").val();
  var score = scorePassword(plain_pw);
  var txtscore = checkPassStrength(score);
  var confirm_pw = $("#confirmPassword").val();

  if(score > 100) {
    $("#stronk").css('width', 100+'%').attr("aria-valuenow", score);
  }
  else {
    $("#stronk").css('width', score+'%').attr("aria-valuenow", score);
  }

  if(txtscore == "") {
    $("#stronk").addClass("progress-bar-danger").removeClass("progress-bar-info").removeClass("progress-bar-warning").removeClass("progress-bar-success");
  }
  else if(txtscore == "Weak") {
    $("#stronk").removeClass("progress-bar-danger").addClass("progress-bar-warning").removeClass("progress-bar-info").removeClass("progress-bar-success");
  }
  else if(txtscore == "Good") {
    $("#stronk").removeClass("progress-bar-danger").removeClass("progress-bar-warning").removeClass("progress-bar-info").addClass("progress-bar-success");
  }
  else if(txtscore == "Strong") {
    $("#stronk").removeClass("progress-bar-danger").removeClass("progress-bar-warning").removeClass("progress-bar-success").addClass("progress-bar-info");
  }

  if(txtscore != "") {
    $("#score").text(score + " - " + txtscore);
  }
  else {
    $("#score").text(score + " - None");
  }

  update_checks();
});

$("#confirmPassword").on("change keyup paste click", function() {
  update_checks();
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
