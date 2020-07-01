//DOM
const DQ = document.querySelector.bind(document);
//APP
let App = {
	fileNames: []
};

let dropDownArray = []
let FOLDER_NAME = "";
let FIRST_FLAG = true;

// run/invoke initApp on startup
initApp();



// run/invoke initApp on startup

function initApp() {

	//Init
	bindElementsEvents();

	$('.ui.dropdown') // drop down settings
		.dropdown({
			on: 'hover',
			onChange: selectedPair
		});

}

function showSelectedFiles(fileNames = []) {

	renderCompletedFiles(fileNames);
	updateAppState({
		action: 'reset'
	});
	updateAppState({
		action: 'add',
		fileNames: fileNames
	});

}

function renderCompletedFiles(fileNames) {
	//files template
	const upload = DQ(`#upload-1`);


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
			DQ(`.file--${fileName.replace('.', '-')}`).querySelector(".progress").classList.remove("active");
			DQ(`.file--${fileName.replace('.', '-')}`).querySelector(".done").classList.add("anim");
		}, load);
	})



}

// bind listeners functions
function bindElementsEvents() {

	//for files

	DQ('#trigger-file-1').addEventListener('click', uploadFiles);
	DQ('#upload-1 .reset').addEventListener('click', resetUpload);
	DQ('#compare').addEventListener('click', compareFiles);

	//for folder

	DQ('#trigger-file-2').addEventListener('click', uploadFolder);
	DQ('#upload-2 .reset').addEventListener('click', resetUploadFolder);
	DQ('#compare-folder').addEventListener('click', compareFolder);
	DQ('#save-results').addEventListener('click', saveResults);

}

function saveResults() {

	if (Array.isArray(dropDownArray) && dropDownArray.length) {

		Swal.fire({
			title: 'Save Results?',
			icon: 'question',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Save'
		}).then((result) => {
			if (result.value) {

				eel.save_result_to_excel(dropDownArray, FOLDER_NAME)(function () {

					Swal.fire({
						icon: 'success',
						title: 'Results has been saved to your current .exe diractory',
						showConfirmButton: false,
						timer: 1500
					})
				})
			}
		})

	}
}


function compareFolder() {
	showLoader();

	eel.gui_entry_folder()(function () {

		$('#save-results').addClass('active');

		Swal.fire({
			icon: 'success',
			title: 'Folder comparison completed',
			text: 'Export an excel file by clicking "Save results" button',
		})
	})
}

function uploadFolder() {
	eel.pyGetFolderPath()(function (result) {

		if (result === "E")
			return;
		handleFolderSelect(result);
	});
}

function uploadFiles() {
	eel.pyGetFilePath()(function (result) {
		showSelectedFiles(result);
	});
}

function resetUpload(evnt) {
	const upload = evnt.currentTarget.closest('.upload');
	updateAppState({
		action: 'reset'
	});
	upload.querySelector('.list-files').innerHTML = '';
	upload.querySelector('footer').classList.remove('hasFiles');
	upload.querySelector('.reset').classList.remove('active');
	upload.querySelector('#compare').classList.remove('active');
	// $('#text').classList.remove('hide');
	setTimeout(() => {
		upload.querySelector('.body').classList.remove('hidden');
	}, 500);
}

function resetUploadFolder(evnt) {
	debugger
	FIRST_FLAG = true;
	const upload = evnt.currentTarget.closest('.upload');
	updateAppState({
		action: 'reset'
	});
	upload.querySelector('.list-files').innerHTML = '';
	upload.querySelector('footer').classList.remove('hasFiles');
	upload.querySelector('.reset').classList.remove('active');
	upload.querySelector('#compare-folder').classList.remove('active');
	// upload.querySelector('#save-results').classList.remove('active');
	// $('#text').classList.remove('hide');
	setTimeout(() => {
		upload.querySelector('.body').classList.remove('hidden');
	}, 500);
}

function compareFiles() {
	showLoader();
	eel.gui_entry()(function (result) {

		hideLoader();
		changeSubTitle(result[2][0] + " & " + result[2][1]);
		console.log(result);

		let preds = [(result[1][0] * 100).toFixed(2), (result[1][1] * 100).toFixed(2)]
		console.log(preds)
		preds = preds.map(Number);
		console.log(preds)
		buildGraph(preds);
	})

}


function showLoader() {
	DQ('.overlay').classList.remove('hide');
}

function hideLoader() {
	DQ('.overlay').classList.add('hide');
	// $('#text').classList.add('hide');
}

function updateAppState(options) {
	const {
		action,
		fileNames
	} = options;

	if (action === 'add') {
		App.fileNames = fileNames;
	}

	if (action === 'reset') {
		App.files = [];
	}

}

function buildGraph(scoresPercents) {
	const [diffPer, samePer] = scoresPercents;

	DQ('#graph-container').classList.remove('hide');
	const secondaryColor = getComputedStyle(document.documentElement)
		.getPropertyValue('--secondary-color');
	const quaternaryColor = getComputedStyle(document.documentElement)
		.getPropertyValue('--quaternary-color');
	const resultsTitle = (diffPer > samePer) ? "Different Author" : "Same Author";

	// remove last graph and creates a new graph container
	d3chart = $('#d3chartContainer')
	d3chart.empty();
	d3chart.append(`<br/><h1>${resultsTitle}</h1>`);
	d3chart.append('<svg id="d3ChartSvg" viewBox="0 0 400 220"></svg>');

	const data = [{
		name: "Same",
		percentage: samePer,
		color: secondaryColor,
		value: samePer * 100,
	},
	{
		name: "Different",
		percentage: diffPer,
		color: quaternaryColor,
		value: diffPer * 100,
	}
	]

	const svg = d3
		.select('#d3ChartSvg');

	// identify the dimensions of the viewBox to establish the svg canvas
	const viewBox = svg.attr('viewBox');
	const regexViewBox = /\d+ \d+ (\d+) (\d+)/;
	// ! .match() returns string values
	const [, viewBoxWidth, viewBoxHeight] = viewBox.match(regexViewBox).map(item => Number.parseInt(item, 10));

	// with the margin convention include a group element translated within the svg canvas
	const margin = {
		top: 20,
		right: 20,
		bottom: 20,
		left: 20,
	};
	// compute the width and height of the actual viz from the viewBox dimensions and considering the margins
	// this to later work with width and height attributes directly through the width and height variables
	const width = viewBoxWidth - (margin.left + margin.right);
	const height = viewBoxHeight - (margin.top + margin.bottom);

	// compute the radius as half the minor size between the width and height
	const radius = Math.min(width, height) / 3;
	// initialize a variable to have the multiple elements share the same stroke-width property
	const strokeWidth = 10;

	const group = svg
		.append('g')
		.attr('transform', `translate(${margin.left} ${margin.top})`);


	// DEFAULT CIRCLE
	// circle used as a background for the colored donut chart
	// add a group to center the circle in the canvas (this to rotate the circle from the center)
	const groupDefault = group
		.append('g')
		.attr('transform', `translate(${width / 2} ${height / 2})`);

	// append the circle showing only the stroke
	groupDefault
		.append('circle')
		.attr('cx', 0)
		.attr('cy', 0)
		.attr('r', radius)
		.attr('transform', 'rotate(-90)')
		.attr('fill', 'none')
		.attr('stroke', 'hsla(0, 0%, 0%, 0.08')
		.attr('stroke-width', strokeWidth)
		.attr('stroke-linecap', 'round')
		// hide the stroke of the circle using the radius
		// this to compute the circumference of the shape
		.attr('stroke-dasharray', radius * 3.14 * 4)
		.attr('stroke-dashoffset', radius * 3.14 * 4);


	// COLORED CIRCLES
	// pie function to compute the arcs
	const pie = d3
		.pie()
		.sort(null)
		.padAngle(0.12)
		// use either the value or the percentage in the dataset
		.value(d => d.value);

	// arc function to create the d attributes for the path elements
	const arc = d3
		.arc()
		// have the arc overlaid on top of the stroke of the circle
		.innerRadius(radius)
		.outerRadius(radius);

	/* for each data point include the following structure
	g             // wrapping all arcs
	  g           // wrapping each arc
	    arc       // actual shape
	    line      // connecting line
	    text      // text label
	  g
	    arc
	    ...
	*/
	// wrapping group, horizontally centered
	const groupArcs = group
		.append('g')
		.attr('transform', `translate(${width / 2} ${height / 2})`);

	const groupsArcs = groupArcs
		.selectAll('g')
		.data(pie(data))
		.enter()
		.append('g');

	// include the arcs specifying the stroke with the same width of the circle element
	groupsArcs
		.append('path')
		.attr('d', arc)
		.attr('fill', 'none')
		.attr('stroke', d => d.data.color)
		.attr('stroke-width', strokeWidth * 0.8)
		.attr('stroke-linecap', 'round')
		.attr('stroke-linejoin', 'round')
		// hide the segments by applying a stroke-dasharray/stroke-dashoffset equal to the circle circumference
		// ! the length of the element varies, and it considered afterwords
		// for certain the paths are less than the circumference of the entire circle
		.attr('stroke-dasharray', radius * 3.14 * 2)
		.attr('stroke-dashoffset', radius * 3.14 * 2)
		.style('opacity', 0)
		.style('visibility', 'hidden');

	// include line elements visually connecting the text labels with the arcs
	groupsArcs
		.append('line')
		.attr('x1', 0)
		.attr('x2', (d) => {
			const [x] = arc.centroid(d);
			return x > 0 ? '25' : '-25';
		})
		.attr('y1', 0)
		.attr('y2', 0)
		.attr('stroke', ({
			data: d
		}) => d.color)
		.attr('stroke-width', 1.5)
		.attr('transform', (d) => {
			const [x, y] = arc.centroid(d);
			const offset = x > 0 ? 20 : -20;
			return `translate(${x + offset} ${y})`;
		})
		.attr('stroke-dasharray', 25)
		.attr('stroke-dashoffset', 25);

	// include text elements associated with the arcs
	groupsArcs
		.append('text')
		.attr('x', 0)
		.attr('y', 0)
		.attr('font-size', 8)
		.attr('text-anchor', (d) => {
			const [x] = arc.centroid(d);
			return x > 0 ? 'start' : 'end';
		})
		.attr('transform', (d) => {
			const [x, y] = arc.centroid(d);
			const offset = x > 0 ? 50 : -50;
			return `translate(${x + offset} ${y})`;
		})
		.html(({
			data: d
		}) => `
    <tspan x="0">${d.name}:</tspan><tspan x="0" dy="10" font-size="12">${d.percentage}%</tspan>
  `)
		.style('opacity', 0)
		.style('visibility', 'hidden');


	// TRANSITIONS
	// once the elements are set up
	// draw the stroke of the larger circle element
	groupDefault
		.select('circle')
		.transition()
		.ease(d3.easeExp)
		.delay(200)
		.duration(1300)
		.attr('stroke-dashoffset', '0')
		// once the transition is complete
		// draw the smaller strokes one after the other
		.on('end', () => {
			// immediately set the stroke-dasharray and stroke-dashoffset properties to match the length of the path elements
			// using vanilla JavaScript
			const paths = document.querySelectorAll('svg g g path');
			paths.forEach((path) => {
				const length = path.getTotalLength();
				path.setAttribute('stroke-dasharray', length);
				path.setAttribute('stroke-dashoffset', length);
			});

			const duration = 800;
			// transition the path elements to stroke-dashoffset 0
			d3
				.selectAll('svg g g path')
				.transition()
				.ease(d3.easeLinear)
				.delay((d, i) => i * duration)
				.duration(duration)
				.style('opacity', 1)
				.style('visibility', 'visible')
				.attr('stroke-dashoffset', 0);


			// transition the line elements elements to stroke-dashoffset 0
			d3
				.selectAll('svg g g line')
				.transition()
				.ease(d3.easeLinear)
				.delay((d, i) => i * duration + duration / 2.5)
				.duration(duration / 3)
				.style('opacity', 1)
				.style('visibility', 'visible')
				.attr('stroke-dashoffset', 0);

			// transition the text elements to opacity 1 and visibility visible
			d3
				.selectAll('svg g g text')
				.transition()
				.ease(d3.easeLinear)
				.delay((d, i) => i * duration + duration / 2)
				.duration(duration / 2)
				.style('opacity', 1)
				.style('visibility', 'visible');
		});


}

function buildGraph2(scoresPercents) {
	// first element in the array is the same
	// second element in the array is the different
	const [diffPer, samePer] = scoresPercents;

	const resultsTitle = (diffPer > samePer) ? "Different Author" : "Same Author";

	DQ('#graph-container').classList.remove('hide');
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
			//verticalAlign: "bottom",
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
			dataPoints: [{
				y: diffPer,
				label: "Different Author",
				color: secondaryColor
			},
			{
				y: samePer,
				label: "Same Author",
				color: quaternaryColor
			},
			]
		}]

	});
	chart.render();
}

function handleFolderSelect(folderName, folderNum) {
	updateAppState({
		action: 'delete',
		folderNum: folderNum
	});
	updateAppState({
		action: 'add',
		folderNum: folderNum
	});
	FOLDER_NAME = folderName;
	const upload = DQ('#upload-2');

	const template = `<div class="file file--2">
				<div class="name"><span>${folderName}</span></div>
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
	upload.querySelector('#compare-folder').classList.add('active');
	upload.querySelector('.list-files').innerHTML = template;

	const load = 1000;
	setTimeout(() => {
		upload.querySelector('.progress').classList.remove('active');
		upload.querySelector('.done').classList.add('anim');
	}, load);
}

eel.expose(get_pair_result);
function get_pair_result(err, result) { /// [ ... , [0.8,0.2], [1b.tiff,1.tiff] ]

	if (FIRST_FLAG) {
		changeSubTitle(FOLDER_NAME)
		console.log("only 1");
		hideLoader();
		DQ('#drop-down').classList.remove('hide');
		DQ('#graph-container').classList.remove('hide');
		FIRST_FLAG = false;
	}

	let pair = result[2]; // the names of the files
	let preds;
	if (err != "") {
		console.log(err)
		preds = [50, 50]
	}
	else {
		preds = [(Math.round(result[1][0] * 100)).toFixed(1), (Math.round(result[1][1] * 100)).toFixed(1)]
		preds = preds.map(Number);
	}
	add_to_drop_down(pair, preds, err)
}

function add_to_drop_down(pair, preds, err) {
	let index = dropDownArray.push({
		file1: pair[0],
		file2: pair[1],
		preds: preds,
		error: err
	});

	const [diffPer, samePer] = preds;
	let resultsIcon = (diffPer > samePer) ? "times" : "check";
	if (err != "") {
		resultsIcon = "ban";
	}
	let str = "";
	str += "<div id='item_" + (index - 1) + "' class='item'>";
	str += " <i class='" + resultsIcon + " icon'></i>";
	str += pair[0] + " & " + pair[1];
	str += "</div>";

	var div = document.getElementById('drop-menu');
	div.innerHTML += str;

	dropDownTransition();

}

function dropDownTransition() {
	$('#drop-down').transition({
		animation: 'pulse',
		duration: '3s', // default setting
	});
}

function selectedPair(value, text, $choise) {

	//buildGraph([50,50])
	console.log("select!")
	let itemId = $choise.attr('id');
	let index = itemId.split("_")[1]
	if (dropDownArray[index].error != "") {
		console.log("dont let choose err")
		return;
	}
	let preds = dropDownArray[index].preds
	console.log(preds)
	buildGraph(preds)
}

function changeSubTitle(title) {
	var div = document.getElementById('result-sub-title');
	div.innerHTML = "&nbsp;" + title;
}