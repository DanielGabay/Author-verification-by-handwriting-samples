//DOM
const $ = document.querySelector.bind(document);
//APP
let App = {
	fileNames: []
};
// run/invoke initApp on startup
initApp();

function initApp() {
	//Init
	bindElementsEvents();
}

function showSelectedFiles(fileNames = []) {

	renderCompletedFiles(fileNames);
	updateAppState({ action: 'reset' });
	updateAppState({ action: 'add', fileNames: fileNames });

}

function renderCompletedFiles(fileNames) {
	//files template
	const upload = $(`#upload-1`);

	
	const template = `${fileNames
		.map(fileName => `<div class="file file--${fileName.replace('.', '-')}">
     <div class="name"><span>${fileName}</span></div>
     <div class="progress active"></div>
     <div class="done">
	
      <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" x="0px" y="0px" viewBox="0 0 1000 1000">
		<g><path id="path" d="M500,10C229.4,10,10,229.4,10,500c0,270.6,219.4,490,490,490c270.6,0,490-219.4,490-490C990,229.4,770.6,10,500,10z M500,967.7C241.7,967.7,32.3,758.3,32.3,500C32.3,241.7,241.7,32.3,500,32.3c258.3,0,467.7,209.4,467.7,467.7C967.7,758.3,758.3,967.7,500,967.7z M748.4,325L448,623.1L301.6,477.9c-4.4-4.3-11.4-4.3-15.8,0c-4.4,4.3-4.4,11.3,0,15.6l151.2,150c0.5,1.3,1.4,2.6,2.5,3.7c4.4,4.3,11.4,4.3,15.8,0l308.9-306.5c4.4-4.3,4.4-11.3,0-15.6C759.8,320.7,752.7,320.7,748.4,325z"</g>
		</svg>
						
     </div>
    </div>`)
		.join("")}`;
	upload.querySelector('.body').classList.add('hidden');
	upload.querySelector('footer').classList.add('hasFiles');
	upload.querySelector('#compare').classList.add('active');
	upload.querySelector('.reset').classList.add('active');

	setTimeout(() => {
		upload.querySelector('.list-files').innerHTML = template;
	}, 1000);

	fileNames.forEach((fileName, index) => {

		let load = 1500 + (index * 1000); // fake load
		setTimeout(() => {
			$(`.file--${fileName.replace('.', '-')}`).querySelector(".progress").classList.remove("active");
			$(`.file--${fileName.replace('.', '-')}`).querySelector(".done").classList.add("anim");
		}, load);
	})



}

// bind listeners functions
function bindElementsEvents() {
	$('#trigger-file-1').addEventListener('click', uploadFiles);
	$('#upload-1 .reset').addEventListener('click', resetUpload);
	$('#compare').addEventListener('click', compareFiles);
}

function uploadFiles() {

	eel.pyGetFilePath()(updateFile);
}

function updateFile(result) {
	console.log(result)
	if (result === "E")
	{
		Swal.fire({
			icon: 'error',
			title: 'Error!',
			text: 'Please select two diffrenet files to compare',
		  })
		//alert("Please select two diffrenet files to compare")
		return;
	}
	showSelectedFiles(result);
}


function resetUpload(evnt) {
	const upload = evnt.currentTarget.closest('.upload');
	updateAppState({ action: 'reset' });
	upload.querySelector('.list-files').innerHTML = '';
	upload.querySelector('footer').classList.remove('hasFiles');
	upload.querySelector('.reset').classList.remove('active');
	upload.querySelector('#compare').classList.remove('active');
	$('#text').classList.remove('hide');
	setTimeout(() => {
		upload.querySelector('.body').classList.remove('hidden');
	}, 500);
}

function compareFiles() {
	showLoader();
	eel.gui_entry()(display_result)
	// setTimeout(() => {
	// 	// remove timeout instead use python
	// 	hideLoader();
	// 	const compareScore = [50, 50];
	// 	buildGraph(compareScore);
	// }, 5000);
}

eel.expose(print_from_py);
function print_from_py(data) {
	console.log(data)
}

function display_result(result) {
	hideLoader();
	
	console.log(result);

	let preds = [(Math.round(result[1][0] * 100)).toFixed(1),(Math.round(result[1][1] * 100)).toFixed(1)]
	console.log(preds)
	preds = preds.map(Number);
	console.log(preds)
	debugger
	const compareScore = [ 99.0, 1.0 ];
	buildGraph(preds);


	// $("#result").text(result_text);  / not working?!
}

function showLoader() {
	$('.overlay').classList.remove('hide');
}

function hideLoader() {
	$('.overlay').classList.add('hide');
	$('#text').classList.add('hide');
}

function updateAppState(options) {
	const { action, fileNames } = options;

	if (action === 'add') {
		App.fileNames = fileNames;
	}

	if (action === 'reset') {
		App.files = [];
	}

}

function buildGraph(scoresPercents) {
	// first element in the array is the same
	// second element in the array is the different
	const [diffPer, samePer] = scoresPercents;

	const resultsTitle = (diffPer > samePer) ? "Diffrent Author" : "Same Author";

	$('#graph-container').classList.remove('hide');
	const secondaryColor = getComputedStyle(document.documentElement)
		.getPropertyValue('--secondary-color');
	const quaternaryColor = getComputedStyle(document.documentElement)
		.getPropertyValue('--quaternary-color');

	let chart = new CanvasJS.Chart("chartContainer", {
		backgroundColor: null,
		// exportEnabled: true,
		animationEnabled: true,
		title: {
			text: resultsTitle,
			verticalAlign: "bottom",
		},
		legend: {
			cursor: "pointer",
			// itemclick: explodePie
		},

		data: [{
			type: "doughnut",
			startAngle: 60,
			innerRadius: 120,
			indexLabelFontSize: 17,
			indexLabel: "{label} - #percent%",
			toolTipContent: "<strong>{label}:</strong> (#percent%)",
			dataPoints: [
				{ y: diffPer, label: "Diffrenet Author", color: secondaryColor },
				{ y: samePer, label: "Same Author", color: quaternaryColor },

			]
		}]

	});
	chart.render();
}
