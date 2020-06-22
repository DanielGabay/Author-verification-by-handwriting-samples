let is_running = false
let file1 = ""
let file2 = ""

eel.expose(print_from_py);
function print_from_py(data) {
  console.log(data)
}

function main_linker() {
	if (is_running)
		return
	
	file1 = document.getElementById("filename1").innerHTML
	file2 = document.getElementById("filename2").innerHTML
	
	if (file1 == "" || file2 == "")
		// TODO: sanity check? pop up error
		return
	document.getElementById("loader").style.display = "block"
	document.getElementById("chartContainer").style.display = "none"
	is_running = true
	eel.gui_entry(file1, file2)(display_result)
}

function plot(preds) {
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
				{ y: preds[0], label: "Different" },
				{ y: preds[1], label: "Same"},
				// { y: preds[2], label: classes[2] },
			]
		}]
	});
	document.getElementById("chartContainer").style.display = "block"
	chart.render();
	window.scrollTo(0,document.body.scrollHeight);
}

function display_result(result) {
	document.getElementById("loader").style.display = "none"
	is_running = false
	console.log(result);
	let preds = [parseFloat(result[1][0]) * 100, parseFloat(result[1][1]) * 100]
	plot(preds)
	return
	document.getElementById("result").innerHTML = result
}