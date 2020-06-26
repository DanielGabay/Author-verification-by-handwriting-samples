let is_running = false
let file1 = ""
let file2 = ""

eel.expose(print_from_py);
function print_from_py(data) {
  console.log(data)
}

function getFilePath(num) {
	if (num == 1)
		eel.pyGetFilePath(1)(updateFile1);
	else if (num == 2)
		eel.pyGetFilePath(2)(updateFile2);
}

function updateFile1(result) {
	if (result == "")
		return

	f1 = document.getElementById("filename1")
	f1.classList.add("fname_disp")
	f1.innerHTML = result
	file1 = result
}
function updateFile2(result) {
	if (result == "")
		return

	f2 = document.getElementById("filename2")
	f2.classList.add("fname_disp")
	f2.innerHTML = result
	file2 = result
}

function main_linker() {
	if (is_running)
		return
	
	if (file1 == "" || file2 == "")
		return 
	document.getElementById("loader").style.display = "block"
	document.getElementById("chartContainer").style.display = "none"
	is_running = true
	eel.gui_entry()(display_result)
}

function plot(preds) {
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
	if (result == null){
		console.log("Error");
		return
	}
	console.log(result);
	let preds = [parseFloat(result[1][0]) * 100, parseFloat(result[1][1]) * 100]
	plot(preds)
}