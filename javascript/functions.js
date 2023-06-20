//Functions.js
var selectedKpiArray = [];
var str_kpi_data_type = [];
$(document).ready(function() {
  $(".custom-file-input").on("change", function() {
    var fileName = $(this)
      .val()
      .split("\\")
      .pop();
    $(this)
      .siblings(".custom-file-label")
      .addClass("selected")
      .html(fileName);
  });
  let tailSelect = tail.select("#select_multi_kpi_name", {
    multiShowCount: true,
    multiSelectAll: true,
    search: true,
    width: "30%",
    placeholder: 'Select a KPI'
  });
  //Once remove button is clicked
  $(".container").on("click", ".remove_button", function(e) {
    e.preventDefault();
    let parentDiv = $(this).parent("div");
    let id = parentDiv.attr("id");
    parentDiv.remove(); //Remove field html
  });
  tailSelect.on("change", function(item, state) {
    const ytdSelectedValue = document.getElementById("ytdSelect").value;
    let wrapper = $("#kpiValues");
    //My Variables
      var int_click_count = document.getElementById("clickcal").value;
      var int_cal_click = parseInt(int_click_count) + 1;
      var txt_box_name = 'txt_box_no_' + String(int_cal_click);
      var txt_lbl_name = 'txt_lbl_no_' + String(int_cal_click);
      var txt_hiden_field_name = 'txt_hiddn_no_' + String(int_cal_click);
      var txt_box_target_name='txt_box_target_no_' + String(int_cal_click);
      document.getElementById("clickcal").value = int_cal_click;
      var str_kpi = item.key;
      var remove_spl_char = str_kpi.replace(/[^A-Z0-9]+/ig, "_") ;
    //End My Variables
    if (state === "select") {
       if (!selectedKpiArray.includes(remove_spl_char))
       {
        var str_all_textbox_name = [];
        var val_category = document.getElementById("drp_select_category").value ;
        var val_plant = document.getElementById("drp_select_plant").value ;
        var val_year = document.getElementById("drp_select_year").value ;
        var all_values = val_category.concat(';' + val_plant);
        all_values = all_values.concat(';' + val_year);
        all_values = all_values.concat(';' + item.value.replace(/[\/]/g,'~'));
        input_type="";
        if (str_kpi_data_type.length >0)
        {
        	for (i = 0; i < str_kpi_data_type.length; i++)
        	{
        		if (item.value == str_kpi_data_type[i])
        		{
				// New Code 11 March
					fetch('/multi_drp_kpi_click/' + all_values).then(function(response)
					{
						response.json().then(function(data)
						{
							if(data.kpi_exist === 'NO' || "{{admin_access}}" === "YES")
							{
							selectedKpiArray.push(remove_spl_char);
							// New Code 11 March
								$(wrapper).append(
									"<div id='kpi" +
									remove_spl_char +
									"' class='form-group row' ><label class='col-sm-4 col-form-label' name='" +
									txt_lbl_name + "'>" +
									item.value +
									" :</label><input type='hidden' name='" +
									txt_hiden_field_name +
									"' value='" +
									item.value +
									"'/><div class='col-sm-4'><input type='text' class='form-control form-control-sm' onkeypress='return onlyAlphabets(event,this);' required='required' name='" +
									txt_box_name +
									"' ></div><a href='javascript: void (0);' class='remove_button' id='" +
									item.value +
									"' onclick='OnDeleteClick(this.id);'><i class='fas fa-trash'></i></a></div>"
									);
									// New Code 11 March
							}
							else
							{
								alert("Target value already inserted for KPI ".concat(item.value.toString()));
								tailSelect.options.unselect(item.value.toString(), "#");
							}
						})
					}); // New Code 11 March
        		}
        		else
        		{
					// New Code 11 March
					fetch('/multi_drp_kpi_click/' + all_values).then(function(response)
					{
						response.json().then(function(data)
						{
							if(data.kpi_exist === 'NO' || "{{admin_access}}"==="YES")
							{ // New Code 11 March
							selectedKpiArray.push(remove_spl_char);
								$(wrapper).append(
								"<div id='kpi" +
								remove_spl_char +
								"' class='form-group row' ><label class='col-sm-4 col-form-label' name='" +
								txt_lbl_name + "'>" +
								item.value +
								" :</label><input type='hidden' name='" +
								txt_hiden_field_name +
								"' value='" +
								item.value +
								"'/><div class='col-sm-4'><input type='text' class='form-control form-control-sm' onkeyup='checkDec(this);' required='required' name='" +
								txt_box_name +
								"' ></div><a href='javascript: void (0);' class='remove_button' id='" +
								item.value +
								"' onclick='OnDeleteClick(this.id);'><i class='fas fa-trash'></i></a></div>"
								);
							// New Code 11 March
							}
							else
							{
								alert("Target value already inserted for KPI ".concat(item.value.toString()));
								tailSelect.options.unselect(item.value.toString(), "#");
							}
						})
					}); // New Code 11 Marc
        		}
        	}
        }
        else
        {
			// New Code 11 March
			fetch('/multi_drp_kpi_click/' + all_values).then(function(response)
			{
				response.json().then(function(data)
				{
					if(data.kpi_exist === 'NO' || "{{admin_access}}"==="YES")
					{
					selectedKpiArray.push(remove_spl_char);
					// New Code 11 March
						$(wrapper).append(
						"<div id='kpi" +
						remove_spl_char +
						"' class='form-group row' ><label class='col-sm-4 col-form-label' name='" +
						txt_lbl_name + "'>" +
						item.value +
						" :</label><input type='hidden' name='" +
						txt_hiden_field_name +
						"' value='" +
						item.value +
						"'/><div class='col-sm-4'><input type='text' class='form-control form-control-sm' onkeyup='checkDec(this);' required='required' name='" +
						txt_box_name +
						"' ></div><a href='javascript: void (0);' class='remove_button' id='" +
						item.value +
						"' onclick='OnDeleteClick(this.id);'><i class='fas fa-trash'></i></a></div>"
						);
					// New Code 11 March
					}
					else
					{
						alert("Target value already inserted for KPI ".concat(item.value.toString()));
						tailSelect.options.unselect(item.value.toString(), "#");
					}
				})
			}); // New Code 11 Marc
        }
       }
    }
    else if (state === "unselect")
    {
    echo "hi";
        selectedKpiArray = selectedKpiArray.filter(e => e !== remove_spl_char);
        $("#kpi" + remove_spl_char).remove();
    }
  });
});
$(document).ready(function(){
 $('#drp_select_function').change(function(){
    if (this.selectedIndex !== 0) {
        function_name = $(this).val();
		var select_period = document.getElementById("drp_select_period");
        var selected_type = document.getElementById("typeSelect").value;
        var selected_plant = document.getElementById("drp_select_plant").value;
        function_name = function_name.concat(";" + selected_type);
        function_name = function_name.concat(";" + selected_plant);
        $("#kpiValues").empty();
        let tailSelect = tail.select("#select_multi_kpi_name", {
            multiShowCount: true,
            multiSelectAll: true,
            search: true,
            width: "30%",
            placeholder: 'Select a KPI'
            });
        tailSelect.reload();
        fetch('/select_multi_kpi_name/' + function_name).then(function(response) {
                response.json().then(function(data) {
                    var instance = tail.select("#select_multi_kpi_name", {
                            multiShowCount: true,
	                		multiSelectAll: true,
	                		search: true,
	                		width: "100%",
	                		placeholder: 'Select a KPI'
                    });
			        instance.options.add(data.str_plant_data);
			        str_kpi_data_type= data.str_kpi_data_type_array;
					if (data.str_period_array != 'NO')
					{
						var optionHTML = '';
						for (var period of data.str_period_array) {
							optionHTML += '<option value="' + period.key + '">' + period.value + '</option>';
						}
						select_period.innerHTML = optionHTML;
						select_period.options[0].disabled = true;
					}
                })
        });
    }
 })
});
//End Functions.js
//Fill Sub Category Drop Down
        var category_select = document.getElementById("drp_select_category");
        var sub_category_select = document.getElementById("drp_select_sub_category");
        category_select.onchange = function()
        {
               $("#succcessmsg").hide();
            category = category_select.value;
            fetch('/drp_select_sub_category/' + category).then(function(response) {
                response.json().then(function(data) {
                    var optionHTML = '';
                    for (var data of data.str_category_data) {
                        optionHTML += '<option value="' + data.id + '">' + data.name + '</option>';
                    }
                    sub_category_select.innerHTML = optionHTML;
                    sub_category_select.options[0].disabled = true;
                })
            });
                $("#drp_select_sub_category")[0].selectedIndex = 0;
                $("#drp_select_plant")[0].selectedIndex = 0;
                $("#ytdSelect")[0].selectedIndex = 0;
                $("#typeSelect")[0].selectedIndex = 0;
                $("#drp_select_year")[0].selectedIndex = 0;
                $("#drp_select_period")[0].selectedIndex = 0;
                $("#drp_select_function")[0].selectedIndex = 0;
ClearKpiDdl();
        }
//End Fill Sub Category Drop Down
//Fill Plant Drop Down
        var sub_category_select = document.getElementById("drp_select_sub_category");
        var plant_select = document.getElementById("drp_select_plant");
        sub_category_select.onchange = function()
        {
            $("#drp_select_plant")[0].selectedIndex = 0;
            sub_category = sub_category_select.value;
            fetch('/drp_select_plant/' + sub_category).then(function(response) {
                response.json().then(function(data) {
                    var optionHTML = '';
                    for (var data of data.str_category_data) {
                        optionHTML += '<option value="' + data.id + '">' + data.name + '</option>';
                    }
                    plant_select.innerHTML = optionHTML;
                    plant_select.options[0].disabled = true;
                })
            });
                $("#drp_select_plant")[0].selectedIndex = 0;
                $("#ytdSelect")[0].selectedIndex = 0;
                $("#typeSelect")[0].selectedIndex = 0;
                $("#drp_select_year")[0].selectedIndex = 0;
                $("#drp_select_period")[0].selectedIndex = 0;
                $("#drp_select_function")[0].selectedIndex = 0;
ClearKpiDdl();
        }
//End Fill Plant Drop Down
//Fill Function Drop Down and Type Change Event
var function_select = document.getElementById("drp_select_function");
        var type_select = document.getElementById("typeSelect");
        type_select.onchange = function()
        {
            $("#drp_select_function")[0].selectedIndex = 0;
            selected_type = type_select.value;
            var plant_select = document.getElementById("drp_select_plant").value;
            selected_type = selected_type.concat(';' + plant_select);
            fetch('/drp_select_function/' + selected_type).then(function(response) {
                response.json().then(function(data) {
                    var optionHTML = '';
                    for (var data of data.str_category_data) {
                        optionHTML += '<option value="' + data.id + '">' + data.name + '</option>';
                    }
                    function_select.innerHTML = optionHTML;
                    function_select.options[0].disabled = true;
                })
            });
                $("#drp_select_year")[0].selectedIndex = 0;
                $("#drp_select_period")[0].selectedIndex = 0;
                $("#drp_select_function")[0].selectedIndex = 0;
            if ( type_select.value == "Target" )
            {
              select_year = document.getElementById("drp_select_year");
              select_year.options[0].disabled = true;
              document.getElementById("drp_select_period").disabled=true;
			}
            else
            {
              select_year = document.getElementById("drp_select_year");
              select_year.options[0].disabled = true;
              document.getElementById("drp_select_period").disabled=false;
            }
ClearKpiDdl();
        }
//End Fill Function Drop Down and Type Change Event
//On Delete Button
function OnDeleteClick(clicked_id)
{
  let tailSelect = tail.select("#select_multi_kpi_name", {
    multiShowCount: true,
    multiSelectAll: true,
    search: true,
    width: "30%",
    placeholder: 'Select a KPI'
  });
  //Once remove button is clicked
    tailSelect.options.unselect(clicked_id.toString(), "#");
    selectedKpiArray = selectedKpiArray.filter(e => e !== clicked_id);
}
//End Delete Button
// On Load Form
function OnLoadDisableFirstObject()
{
if("{{window_open}}" === "YES" || "{{admin_access}}" === "YES")
{
    document.getElementById("drp_select_period").options[0].disabled = true;
    document.getElementById("ytdSelect").options[0].disabled = true;
    document.getElementById("drp_select_year").options[0].disabled = true;
    document.getElementById("typeSelect").options[0].disabled = true;
    document.getElementById("drp_select_category").options[0].disabled = true;
    document.getElementById("drp_select_sub_category").options[0].disabled = true;
    document.getElementById("drp_select_function").options[0].disabled = true;
    document.getElementById("drp_select_plant").options[0].disabled = true;
    $("#drp_select_category")[0].selectedIndex = 0;
    $("#drp_select_plant")[0].selectedIndex = 0;
    $("#ytdSelect")[0].selectedIndex = 0;
    $("#typeSelect")[0].selectedIndex = 0;
    $("#drp_select_year")[0].selectedIndex = 0;
    $("#drp_select_period")[0].selectedIndex = 0;
    $("#drp_select_sub_category")[0].selectedIndex = 0;
    $("#drp_select_function")[0].selectedIndex = 0;
}
else if ("{{window_open}}"==="NO")
{
    document.getElementById("drp_select_period").disabled = true;
    document.getElementById("ytdSelect").disabled = true;
    document.getElementById("drp_select_year").disabled = true;
    document.getElementById("typeSelect").disabled = true;
    document.getElementById("drp_select_category").disabled = true;
    document.getElementById("drp_select_sub_category").disabled = true;
    document.getElementById("drp_select_function").disabled = true;
    document.getElementById("drp_select_plant").disabled = true;
	document.getElementById("btn_submit").disabled = true;
	document.getElementById("btn_cancel").disabled = true;
	        let tailSelect = tail.select("#select_multi_kpi_name", {
            multiShowCount: true,
            multiSelectAll: true,
			disabled: true,
            search: true,
            width: "30%",
            placeholder: 'Select a KPI'
            });
	alert("The Window has been closed, Please contact administrator");
}
}
// End On Load Form
// YTD MTD Change event
var ytd_mtd_select = document.getElementById("ytdSelect");
var type_data = document.getElementById("typeSelect");
ytd_mtd_select.onchange=function()
{
  selected_value=ytd_mtd_select.value;
  if (selected_value == "YTD")
  {
  $("#typeSelect")[0].selectedIndex = 0;
  $("#drp_select_period")[0].selectedIndex = 0;
  document.getElementById("drp_select_period").disabled=true;
  type_data.options[2].disabled = false;
  type_data.options[2].style.display = 'block';
  type_data.options[1].disabled = true;
  type_data.options[1].style.display = 'none';
  }
  if (selected_value == "MTD")
  {
  $("#typeSelect")[0].selectedIndex = 0;
  $("#drp_select_period")[0].selectedIndex = 0;
   document.getElementById("drp_select_period").disabled=false;
   type_data.options[2].disabled = true;
   type_data.options[2].style.display = 'none';
   type_data.options[1].disabled = false;
   type_data.options[1].style.display =  'block';
  }
  $("#typeSelect")[0].selectedIndex = 0;
  $("#drp_select_year")[0].selectedIndex = 0;
  $("#drp_select_period")[0].selectedIndex = 0;
  $("#drp_select_function")[0].selectedIndex = 0;
ClearKpiDdl();
}
//END YTD MTD Change event
// All Text box
        function getalltxt() {
            var tg_all_input_tags = document.getElementsByTagName("INPUT");
            var str_all_textbox_name = [];
            for (var cnt = 0; cnt < tg_all_input_tags.length; cnt++)
            {
                if (tg_all_input_tags[cnt].type == "text")
                {
                str_all_textbox_name.push(tg_all_input_tags[cnt].name);
                }
            }
            document.getElementById("dynamic_txtbox_names").value = str_all_textbox_name;
        }
// End All Text Boxes
// Button Cancel
    function refresh_page()
    {
        document.getElementById("drp_select_category").required = false;
        document.getElementById("drp_select_plant").required = false;
        document.getElementById("ytdSelect").required = false;
        document.getElementById("typeSelect").required = false;
        document.getElementById("drp_select_year").required = false;
        document.getElementById("drp_select_period").required = false;
        document.getElementById("drp_select_sub_category").required = false;
        document.getElementById("drp_select_function").required = false;
        document.getElementById("drp_select_sub_category").required = false;
        window.location.reload();
    }
// End Button Cancel
// Only alphabets
        function onlyAlphabets(e, t) {
            try {
                if (window.event) {
                    var charCode = window.event.keyCode;
                }
                else if (e) {
                    var charCode = e.which;
                }
                else { return true; }
                if ((charCode > 64 && charCode < 91) || (charCode > 96 && charCode < 123))
                    return true;
                else
                    return false;
            }
            catch (err) {
                alert(err.Description);
            }
        }
//End Only alphabets
//Only Decimals
		function checkDec(el)
		{
			var ex = /^[0-9]+\.?[0-9]*$/;
			if(ex.test(el.value)==false)
			{
			el.value = el.value.substring(0,el.value.length - 1);
			}
		}
//
//Clear  Kpi Function
function ClearKpiDdl()
{
        $("#kpiValues").empty();
        let tailSelect = tail.select("#select_multi_kpi_name", {
            multiShowCount: true,
            multiSelectAll: true,
            search: true,
            width: "30%",
            placeholder: 'Select a KPI'
            });
        tailSelect.reload();
}
//End Clear  Kpi Function
var selected_plant = document.getElementById("drp_select_plant");
selected_plant.onchange=function()
{
ClearKpiDdl();
  $("#ytdSelect")[0].selectedIndex = 0;
  $("#typeSelect")[0].selectedIndex = 0;
  $("#drp_select_year")[0].selectedIndex = 0;
  $("#drp_select_period")[0].selectedIndex = 0;
  $("#drp_select_function")[0].selectedIndex = 0;
}
// Bookmark function
function setBookmark(cname) {
  let ytd = $("#ytdSelect").val();
  let plant = $("#drp_select_plant").val();
  let category = $("#drp_select_category").val();
  let year = $("#drp_select_year").val();
  let period = $("#drp_select_period").val();
  let cookie = { ytd: ytd, plant: plant, category: category, year: year, period: period, kpi: selectedKpiArray };
  document.cookie = cname + "=" + JSON.stringify(cookie);
}
function getBookmark(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(";");
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == " ") {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      let cookie = JSON.parse(c.substring(name.length, c.length));
      $("#ytdSelect").val(cookie.ytd);
      $("#drp_select_plant").val(cookie.plant);
      $("#drp_select_category").val(cookie.category);
      $("#drp_select_year").val(cookie.year);
      $("#drp_select_period").val(cookie.period);
      let tailSelect = tail.select("#kpiSelect");
      cookie.kpi.forEach(s => tailSelect.options.select(s, "#"));
      return c.substring(name.length, c.length);
    }
  }
  return "";
}
function deleteBookmark(cname) {
  document.cookie = cname + "= ; expires=Thu, 01 Jan 1970 00:00:00 UTC";
}