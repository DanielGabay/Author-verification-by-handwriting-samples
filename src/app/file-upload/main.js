//DOM
const $ = document.querySelector.bind(document);


//APP
let App = {
	files: {}
};
// run/invoke initApp on startup
initApp();

function initApp() {
	//Init

	bindElementsEvents();
}

function handleFileSelect(fileName, fileNum) {
	updateAppState({ action: 'delete', fileNum: fileNum });
	updateAppState({ action: 'add', fileNum: fileNum });

	const upload = $(`#upload-${fileNum}`);

	const template = `<div class="file file--${fileNum}">
				<div class="name"><span>${fileName}</span></div>
				<div class="progress active"></div>
				<div class="done">
				 <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" x="0px" y="0px" viewBox="0 0 1000 1000">
				   <g><path id="path" d="M500,10C229.4,10,10,229.4,10,500c0,270.6,219.4,490,490,490c270.6,0,490-219.4,490-490C990,229.4,770.6,10,500,10z M500,967.7C241.7,967.7,32.3,758.3,32.3,500C32.3,241.7,241.7,32.3,500,32.3c258.3,0,467.7,209.4,467.7,467.7C967.7,758.3,758.3,967.7,500,967.7z M748.4,325L448,623.1L301.6,477.9c-4.4-4.3-11.4-4.3-15.8,0c-4.4,4.3-4.4,11.3,0,15.6l151.2,150c0.5,1.3,1.4,2.6,2.5,3.7c4.4,4.3,11.4,4.3,15.8,0l308.9-306.5c4.4-4.3,4.4-11.3,0-15.6C759.8,320.7,752.7,320.7,748.4,325z"</g>
				   </svg>
				</div>
			   </div>`;

	upload.querySelector('.body').classList.add('hidden');
	upload.querySelector('footer').classList.add('hasFiles');
	upload.querySelector('.reset').classList.add('active');
	upload.querySelector('.list-files').innerHTML = template;

	const load = 3000;
	setTimeout(() => {
		upload.querySelector('.progress').classList.remove('active');
		upload.querySelector('.done').classList.add('anim');
	}, load);
}

function updateFile1(result) {
	handleFileSelect(result, 1);
}

function updateFile2(result) {
	handleFileSelect(result, 2);
}

// bind listeners functions
function bindElementsEvents() {
	// file browse events
	$('#trigger-file-1').addEventListener('click', () => {
		eel.pyGetFilePath(1)(updateFile1);
		// TODO: this needs to open python file explorer
		// handleFileSelect('test1', 1);
	});

	$('#trigger-file-2').addEventListener('click', (evt) => {
		eel.pyGetFilePath(2)(updateFile2);
		// handleFileSelect('test2', 2);
	});

	//reset for first element
	$('#upload-1 .reset').addEventListener('click', (evnt) => {
		
		d3.select('.graph-container svg').remove();
		const upload = evnt.currentTarget.closest('.upload');
		updateAppState({ action: 'delete', fileNum: 1 });
		upload.querySelector('.list-files').innerHTML = '';
		upload.querySelector('footer').classList.remove('hasFiles');
		upload.querySelector('.reset').classList.remove('active');
		setTimeout(() => {
			upload.querySelector('.body').classList.remove('hidden');
		}, 200);
	});

	//reset for second element
	$('#upload-2 .reset').addEventListener('click', (evnt) => {
		const upload = evnt.currentTarget.closest('.upload');
		debugger;
		updateAppState({ action: 'delete', fileNum: 2 });
		upload.querySelector('.list-files').innerHTML = '';
		upload.querySelector('footer').classList.remove('hasFiles');
		upload.querySelector('.reset').classList.remove('active');
		setTimeout(() => {
			upload.querySelector('.body').classList.remove('hidden');
		}, 200);
	});



	$('#compare').addEventListener('click', (evt) => {
		// alert('starting comparing');

		showLoader();
		eel.gui_entry()(display_result)

		// setTimeout(() => {
		// 	// remove timeout instead use python
		// 	hideLoader();
		// 	const compareScore = [ 50, 50 ];
		// 	buildGraph(compareScore);
		// }, 5000);
	});
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
	// const compareScore = [ 50, 50 ];
	buildGraph(preds);


	// $("#result").text(result_text);  / not working?!
}


function showLoader() {
	$('.overlay').classList.remove('hide');
}

function hideLoader() {
	$('.overlay').classList.add('hide');
}

function compareValidation() {
	const { 1: first, 2: second } = App.files;
	const areBothFilesReady = first && second;
	const DISABLED = 'disabled';
	const compareBtn = $('#compare');

	if (areBothFilesReady) {
		compareBtn.removeAttribute(DISABLED);
	} else {
		compareBtn.setAttribute(DISABLED, DISABLED);
	}
}

function updateAppState(options) {
	const { action, fileNum } = options;
	if (action === 'delete') {
		delete App.files[fileNum];
	}

	if (action === 'add') {
		App.files[fileNum] = true;
	}

	if (action === 'reset') {
		App.files = {};
	}

	compareValidation();
}



function buildGraph(scoresPercents) {
	// first element in the array is the same
	// second element in the array is the different
	const [ diffPer,samePer ] = scoresPercents;

	result_text = (diffPer > samePer) ? "Diffrent Author" : "Same Author";
	console.log(result_text)

	$('.graph-container').classList.remove('hide');
	
		let chart = new CanvasJS.Chart("chartContainer", {
			exportEnabled: true,
			animationEnabled: true,
			title:{
				text: result_text
			},
			legend:{
				cursor: "pointer",
			},
			data: [{
				type: "pie",
				showInLegend: true,
				toolTipContent: "{name}: <strong>{y}%</strong>",
				indexLabel: "{name} - {y}%",
				dataPoints: [
					{ y: diffPer, name: "Diffrenet Author" },
					{ y: samePer, name: "Same Author",exploded: true },
	
				]
			}]
		});
		chart.render();
		}
