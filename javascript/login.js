function encryption() {
          var username = document.getElementById('txt_name_uname').value
          var passwd = document.getElementById('txt_name_pwd').value
		  var key = CryptoJS.enc.Utf8.parse('7061737323313233');
          var iv = CryptoJS.enc.Utf8.parse('7061737323313233');
          var encrypted_username = CryptoJS.AES.encrypt(username, key, { iv: iv, mode: CryptoJS.mode.CBC });
          var encrypted_passwd = CryptoJS.AES.encrypt(passwd, key, { iv: iv, mode: CryptoJS.mode.CBC });

          document.getElementById('txt_name_uname').value = encrypted_username;
          document.getElementById("txt_name_pwd").value = encrypted_passwd;

		  return true;
}