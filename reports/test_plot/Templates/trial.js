function getData() {
	var dData = new jQuery.Deferred();

	$.ajax({
		type: "GET",
		url: "/data",
		dataType: "json",
		success: function(data) {
			dData.resolve(data)
			},
		complete: function(xhr, textStatus) {
			console.log("AJAX Request complete -> ", xhr, " -> ", textStatus);
		}
	});
	return dData;
};