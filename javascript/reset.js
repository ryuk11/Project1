function check_password() {
var password = document.getElementById("password").value ;
var cnf_password = document.getElementById("cnf_password").value ;
if (password === cnf_password) {
return true;
}
else{
alert("Password Doesn't match!!");
return false;
}
}