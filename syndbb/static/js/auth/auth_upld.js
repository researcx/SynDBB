$("#uploadlogin").submit(function() {
  var crypt = new Crypt();
  var plain_pw = $("#inputPassword").val();
  var password = CryptoJS.SHA256(plain_pw);

  $("#pword").val(password);
})
