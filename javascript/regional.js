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

  let tailSelect = tail.select("#select_global_multi_kpi_name", {
    multiShowCount: true,
    multiSelectAll: true,
    search: true,
    width: "73%",
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
        selectedKpiArray.push(remove_spl_char);
        var str_all_textbox_name = [];
        var val_category = document.getElementById("drp_select_region").value ;
        var val_plant = document.getElementById("drp_select_global_function").value ;
        var all_values = val_category.concat(';' + val_plant);
        all_values = all_values.concat(';' + item.value.replace(/[\/]/g,'~'));
        input_type="";

        if (str_kpi_data_type.length >0)
        {
        	for (i = 0; i < str_kpi_data_type.length; i++)
        	{
        		if (item.value == str_kpi_data_type[i])
        		{
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
        		}
        		else
        		{
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
        		}
        	}
        }
        else
        {
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

        }

       }

    }
    else if (state === "unselect")
    {
        selectedKpiArray = selectedKpiArray.filter(e => e !== remove_spl_char);
        $("#kpi" + remove_spl_char).remove();
    }
  });

});


	//On Delete Button

function OnDeleteClick(clicked_id)
{

  let tailSelect = tail.select("#select_global_multi_kpi_name", {
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
        document.getElementById("drp_select_region").required = false;
		document.getElementById("drp_select_global_function").required = false;
		document.getElementById("drp_select_year").required = false;
		document.getElementById("ytdSelect").required = false;
		document.getElementById("drp_select_period").required = false;
		document.getElementById("drp_global_type_select").required = false;
		window.location.reload();
    }

// End Button Cancel


// On Load Form
function OnLoadDisableFirstObject()
{
if("{{window_open}}" === "YES" || "{{admin_access}}" === "YES")
{
    document.getElementById("drp_select_period").options[0].disabled = true;
    document.getElementById("ytdSelect").options[0].disabled = true;
    document.getElementById("drp_select_year").options[0].disabled = true;
    document.getElementById("drp_global_type_select").options[0].disabled = true;
    document.getElementById("drp_select_region").options[0].disabled = true;
    document.getElementById("drp_select_global_function").options[0].disabled = true;
    $("#ytdSelect")[0].selectedIndex = 0;
    $("#drp_global_type_select")[0].selectedIndex = 0;
    $("#drp_select_year")[0].selectedIndex = 0;
    $("#drp_select_period")[0].selectedIndex = 0;
    $("#drp_select_region")[0].selectedIndex = 0;
    $("#drp_select_global_function")[0].selectedIndex = 0;
  let tailSelect = tail.select("#select_global_multi_kpi_name", {
    multiShowCount: true,
    multiSelectAll: true,
    search: true,
    width: "73%",
    placeholder: 'Select a KPI'
  });
    tailSelect.reload();
}
else if ("{{window_open}}"==="NO")
{
    document.getElementById("drp_select_period").disabled = true;
    document.getElementById("ytdSelect").disabled = true;
    document.getElementById("drp_select_year").disabled = true;


    document.getElementById("drp_global_type_select").disabled = true;
    document.getElementById("drp_select_region").disabled = true;
    document.getElementById("drp_select_global_function").disabled = true;
	document.getElementById("btn_submit").disabled = true;
	document.getElementById("btn_cancel").disabled = true;
	        let tailSelect = tail.select("#select_global_multi_kpi_name", {
            multiShowCount: true,
            multiSelectAll: true,
			disabled: true,
            search: true,
            width: "73%",
            placeholder: 'Select a KPI'
            });
	alert("The Window has been closed, Please contact administrator");
}
}

// End On Load Form



//Fill Function Drop Down


        var function_select = document.getElementById("drp_select_global_function");
        var region_select = document.getElementById("drp_select_region");
        region_select.onchange = function()
        {
            var region_select = document.getElementById("drp_select_region");
            $("#drp_select_global_function")[0].selectedIndex = 0;
            selected_region = region_select.value;

            fetch('/drp_select_global_function/' + selected_region).then(function(response) {

                response.json().then(function(data) {
                    var optionHTML = '';

                    for (var data of data.str_function_data) {
                        optionHTML += '<option value="' + data.id + '">' + data.name + '</option>';
                    }

                    function_select.innerHTML = optionHTML;
                    function_select.options[0].disabled = true;
                })

            });

                $("#ytdSelect")[0].selectedIndex = 0;
                $("#drp_global_type_select")[0].selectedIndex = 0;
                $("#drp_select_year")[0].selectedIndex = 0;
                $("#drp_select_period")[0].selectedIndex = 0;
                $("#drp_select_global_function")[0].selectedIndex = 0;

        }

//End Fill Function Drop Down


//Clear  Kpi Function

function ClearKpiDdl()
{
            var tg_all_input_tags = document.getElementsByTagName("INPUT");
            var str_all_textbox_name = [];

            for (var cnt = 0; cnt < tg_all_input_tags.length; cnt++)
            {
                if (tg_all_input_tags[cnt].type === "text" && tg_all_input_tags[cnt].name != "")
                {
                         $("#kpiValues").empty();

                        let tailSelect = tail.select("#select_global_multi_kpi_name", {
                            multiShowCount: true,
                            multiSelectAll: true,
                            search: true,
                            width: "30%",
                            placeholder: 'Select a KPI'
                            });

                        tailSelect.reload();
                        break;

                }
            }

}

//End Clear  Kpi Function


//Only Decimals

		function checkDec(el)
		{
			var ex = /^[0-9]+\.?[0-9]*$/;
			if(ex.test(el.value)==false)
			{
			el.value = el.value.substring(0,el.value.length - 1);
			}
		}

//Clear  Kpi Function


//Fill KPI values
$(document).ready(function(){

 $('#drp_select_global_function').change(function(){
    if (this.selectedIndex !== 0) {
        function_name = $(this).val();
		var select_period = document.getElementById("drp_select_period");
        var selected_type = document.getElementById("drp_global_type_select").value;
        var selected_region = document.getElementById("drp_select_region").value;
        function_name = function_name.concat(";" + selected_type);
        function_name = function_name.concat(";" + selected_region);


        $("#kpiValues").empty();

        let tailSelect = tail.select("#select_global_multi_kpi_name", {
            multiShowCount: true,
            multiSelectAll: true,
            search: true,
            width: "30%",
            placeholder: 'Select a KPI'
            });

        tailSelect.reload();

        fetch('/select_global_multi_kpi_name/' + function_name).then(function(response) {

                response.json().then(function(data) {

                    var instance = tail.select("#select_global_multi_kpi_name", {
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
  $("#drp_global_type_select")[0].selectedIndex = 0;
  $("#drp_select_year")[0].selectedIndex = 0;
  $("#drp_select_period")[0].selectedIndex = 0;
  $("#ytdSelect")[0].selectedIndex = 0;
 })

});



//Fill Type Change Event


        var type_select = document.getElementById("drp_global_type_select");
        var type_data = document.getElementById("drp_global_type_select");
        type_select.onchange = function()
        {

            selected_type = type_select.value;

               $("#drp_select_year")[0].selectedIndex = 0;
                $("#drp_select_period")[0].selectedIndex = 0;

            if ( type_select.value == "Target")
            {
              select_year = document.getElementById("drp_select_year");
              select_year.options[0].disabled = true;
              document.getElementById("drp_select_period").disabled=true;
              select_year.options[1].disabled = true;
              select_year.options[1].style.display = 'none';
              select_year.options[2].disabled = false;
              select_year.options[2].style.display = 'block';
              select_year.options[3].disabled = false;
              select_year.options[3].style.display = 'block';
			}
			else if(type_select.value == "Previous Year YTD")
			{
			  select_year = document.getElementById("drp_select_year");
              select_year.options[0].disabled = true;
              document.getElementById("drp_select_period").disabled=true;
              select_year.options[1].disabled = false;
              select_year.options[1].style.display = 'block';
              select_year.options[2].disabled = true;
              select_year.options[2].style.display = 'none';
              select_year.options[3].disabled = true;
              select_year.options[3].style.display = 'none';
			}
			else if(type_select.value == "Current Month YTD")
			{
			  select_year = document.getElementById("drp_select_year");
              select_year.options[0].disabled = true;
              document.getElementById("drp_select_period").disabled=false;
              select_year.options[1].disabled = true;
              select_year.options[1].style.display = 'none';
              select_year.options[2].disabled = false;
              select_year.options[2].style.display = 'block';
              select_year.options[3].disabled = false;
              select_year.options[3].style.display = 'block';
			}
            else
            {
              select_year = document.getElementById("drp_select_year");
              select_year.options[0].disabled = true;
              document.getElementById("drp_select_period").disabled=false;
              select_year.options[1].disabled = true;
              select_year.options[1].style.display = 'none';
              select_year.options[2].disabled = false;
              select_year.options[2].style.display = 'block';
              select_year.options[3].disabled = false;
              select_year.options[3].style.display = 'block';
            }
ClearKpiDdl();
        }

//End  Type Change Event



// YTD MTD Change event

var ytd_mtd_select = document.getElementById("ytdSelect");
var type_data = document.getElementById("drp_global_type_select");
ytd_mtd_select.onchange=function()
{
  selected_value=ytd_mtd_select.value;
  if (selected_value == "YTD")
  {
  $("#drp_global_type_select")[0].selectedIndex = 0;
  $("#drp_select_period")[0].selectedIndex = 0;
  document.getElementById("drp_select_period").disabled=true;
  type_data.options[2].disabled = false;
  type_data.options[2].style.display = 'block';
  type_data.options[3].disabled = false;
  type_data.options[3].style.display = 'block';
  type_data.options[4].disabled = false;
  type_data.options[4].style.display = 'block';
  type_data.options[1].disabled = true;
  type_data.options[1].style.display = 'none';
  }
  if (selected_value == "MTD")
  {
  $("#drp_global_type_select")[0].selectedIndex = 0;
  $("#drp_select_period")[0].selectedIndex = 0;
   document.getElementById("drp_select_period").disabled=false;
   type_data.options[2].disabled = true;
   type_data.options[2].style.display = 'none';
   type_data.options[1].disabled = false;
   type_data.options[1].style.display =  'block';
   type_data.options[3].disabled = true;
   type_data.options[3].style.display = 'none';
   type_data.options[4].disabled = true;
   type_data.options[4].style.display = 'none';
  }

  $("#drp_global_type_select")[0].selectedIndex = 0;
  $("#drp_select_year")[0].selectedIndex = 0;
  $("#drp_select_period")[0].selectedIndex = 0;
  
ClearKpiDdl();
}