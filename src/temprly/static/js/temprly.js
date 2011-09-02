function setupGlobals(){
	Temprly.menu = $('#location_menu');
	Temprly.dataview = $('#dataview');
	Temprly.outer_layout = null;
	Temprly.inner_layout = null;
	
	Temprly.resize = function () {
							Temprly.outer_layout.resizeAll();
							
							if (Temprly.inner_layout != null) {
								Temprly.inner_layout.resizeAll();
								Temprly.menu.accordion("resize");
								showReadings();
							} 
							
						};

	Temprly.activeLocation = function(){return Temprly.menu.accordion( "option", "active" );}
	Temprly.activeLocationId = function(){ 
									loc = Temprly.menu.find("h3")
									if (loc.size() > 0) {
										return loc[ Temprly.activeLocation() ].id;
									}else{
										return -1;
									}
								 }
}



function showReadings(sensor_id){
		// default to the currently active location
	 	// TODO: undefined check still needed?
	 	sensor_id = (typeof sensor_id == "undefined") ? Temprly.activeLocationId() : sensor_id;
		
		// no locations defined yet
		if(sensor_id < 0) return;
		
		$.get('readings/' + sensor_id + '?format=gviz', function(response) {
			container = Temprly.dataview;
		  					
			var evalledData = eval("("+response+")");
			var datatable = new google.visualization.DataTable(evalledData, 0.6);
		
			h = $(".outer-center").height()
			w = container.width()
			t = 'Sensor Readings'
			
			// var table = new google.visualization.Table(container);
			// table.draw(datatable, {showRowNumber: true, width: w, height: h,
			// title: t});
			
			var chart = new google.visualization.LineChart(container.get(0));
			chart.draw(datatable, {width: w, height: h, title: t});
			
	});	
}



function refresh_menu(){
	// update the accordeon menu
	$.get('get_locations', function(data) {
		menu = Temprly.menu;
		
		var active = menu.accordion( "option", "active" );
		
		menu.html(data);
		menu.accordion('destroy').accordion({fillSpace: true});
		menu.accordion("resize");
		menu.accordion( "option", "active", active );
	});	
	
}

function deluser(){
			msg = "WARNING: this will *COMPLETELY* delete your account and all associated data.  Are you sure?"
			yes_fun = function() {
						$.get('deluser', 
							function(data) {
								window.location.replace("/");
							});
				  };
				  
			confirm_dialog("Delete account", msg, yes_fun)
};

function dellocation(loc_id, loc_name){
		msg = "Are you sure you want to remove the location " + loc_name + " and *ALL* associated sensor data?"
		yes_fun = function() {
						$.get('locations/del/' + loc_id, 
						// TODO: handle failure
							function(data) {
								// delete the html tag (cheaper than doing a
								// refresh)
								$( '#' + loc_id).remove()
								$( '#' + loc_id + '_div').remove()
							});
				  };
		
		confirm_dialog("Remove location " + loc_name, msg, yes_fun)
};

function msg_dialog(msg, closefun){
		
	var s = '<div id="dialog-message" title="Message">'
	 	+ '<p>'
	 	+ msg
	 	+ '</p></div>';
	
	$(s).dialog({
		height: "auto",
		width: "auto",
		resize : "auto",
		modal: true,
		buttons: {
			"Ok": function() {
				$( this ).dialog( "close" );
				if (closefun != null) { closefun(); }
			}
		}
	});
}

function confirm_dialog(title, msg, yes_fun){
	var s = '<div id="dialog-confirm" title="' + title + '">'
		 	+ '<p><span class="ui-icon ui-icon-alert" style="float:left; margin:0 7px 20px 0;"></span>'
		 	+ msg
		 	+ '</p></div>'
	
	$(s).dialog({
			height: "auto",
			width: "auto",
			resize : "auto",
			modal: true,
			buttons: {
				"Yes": function() {
					yes_fun()
					$( this ).dialog( "close" );
				},
				Cancel: function() {
					$( this ).dialog( "close" );
				}
			}
		});
}

function ajax_form(title_str, get_url, csrf_token, success_fun, post_url){
	
	if(!post_url){
		var post_url = get_url;
	}
	
	$.get(get_url, function(data) {
			var s = '<div id="dialog-div" title="' + title_str + '">'
			+   '<form id="dialog-form">'
			+      csrf_token
			+	   data
			+   '</form>'
			+ '</div>'
	
		// create the buttons first so we can set the button text dynamically
		var dialog_buttons = {};
		dialog_buttons[title_str] = function(){ 
										// post the data
										$.ajax({
							        		type:"POST",
							        		url:post_url,
											data:$(this).find('form').serialize(),
											context: $(this),
											success: function(data,textStatus){
												// reshow the form if it
												// contains an error message
												
												if ($('<span>'+data+'</span>').find('.errorlist').size() > 0) {
													$(this).find('form').replaceWith(data);
												}else{
													// TODO: handle failures
													$(this).dialog( "close" );
													if(success_fun) success_fun(data);
												}
	
											}
							            });
							        }
		
		dialog_buttons['Cancel'] = function(){ $(this).dialog('close'); }

		$(s).dialog({
			autoOpen: true,
			height: "auto",
			width: "auto",
			resize : "auto",
			modal: true,
			buttons: dialog_buttons
		});
	});
}
