$("#file-upload").change(function(){
         //submit the form here
		 var file = $('#file-upload')[0].files[0].name;
		document.getElementById('lblid').innerHTML = file;
 });
 
 // On Load Form
function OnLoadDisableFirstObject()
{
	if("{{window_open}}" === "YES" || "{{admin_access}}" === "YES")
	{


	}
	else if ("{{window_open}}"==="NO")
	{
		document.getElementById('file-upload').disabled=true;
		document.getElementById('lblid').disabled=true;
		document.getElementById('btn_upload').disabled=true;
		alert("The Window has been closed, Please contact administrator");
	}
}