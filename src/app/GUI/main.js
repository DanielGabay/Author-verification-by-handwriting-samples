function main_linker() {
	file1 = document.getElementById("filename1").innerHTML
	file2 = document.getElementById("filename2").innerHTML
	
	if (file1 == "" || file2 == "")
		// TODO: sanity check? pop up error
		return
	document.getElementById("loader").style.display = "block"
	eel.gui_entry(file1, file2)(display_result)
}

// function plot(preds) {
function plot() {
	//TODO: get preds to display from display_result
	let preds = [70, 30]
	file1 = document.getElementById("filename1").innerHTML
	file2 = document.getElementById("filename2").innerHTML
	text = "Comparing: " + file1 + " " + file2
	let chart = new CanvasJS.Chart("chartContainer", {
		theme: "light1", // "light1", "light2", "dark1", "dark2"
		exportEnabled: true,
		animationEnabled: true,
		title: {
			text: text
		},
		backgroundColor: "#fff",
		data: [{
			type: "bar",
			legendText: "{label}",
			indexLabelFontSize: 16,
			indexLabel: "{label} - {y}%",
			dataPoints: [
				{ y: preds[1], label: "Different" },
				{ y: preds[0], label: "Same"},
				// { y: preds[2], label: classes[2] },
			]
		}]
	});
	chart.render();
	window.scrollTo(0,document.body.scrollHeight);
}

function display_result(result) {
	document.getElementById("loader").style.display = "none"
	// let preds = parseFloat(result[1]) * 100
	// plot_preds = [100-preds, preds]
	// plot(plot_preds)
	plot()
	console.log(result)
	return
	document.getElementById("result").innerHTML = result
}