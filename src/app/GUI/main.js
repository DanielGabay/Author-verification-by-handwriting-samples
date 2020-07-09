//DOM
const DQ = document.querySelector.bind(document);
//APP
let App = {
    fileNames: []
};

// globals
let dropDownArray = []
let FOLDER_NAME = "";

/***  init functions ***/

initApp();

function initApp() {
    eel.init_py_main_global()(function(err) {
        console.log(err)
        if (err != null) {
            console.log(err)
            Swal.fire({
                icon: 'error',
                title: 'Error on init',
                text: err,
                heightAuto: false
            });
        }
    });

    bindElementsEvents();
    enableInfoEvents();

    $('.ui.dropdown') // drop down settings
        .dropdown({
            on: 'hover',
            onChange: displaySelectedPair
        });
}


function enableInfoEvents() {
    $('.help-button').click(function(event) {
        event.preventDefault();
        Swal.fire({
            title: 'Welcome to the handwriting similarity checker',
            html: $("#help-button-popup").html(),
            showCloseButton: true,
            grow: 'fullscreen',
            confirmButtonText: 'Close',
            heightAuto: false
        });
    });

    var animTime = 300,
        clickPolice = false;

    $(document).on('touchstart click', '.acc-btn', function() {
        if (!clickPolice) {
            clickPolice = true;

            var currIndex = $(this).index('.acc-btn'),
                targetHeight = $('.acc-content-inner').eq(currIndex).outerHeight();

            $('.acc-btn h4').removeClass('selected');
            $(this).find('h4').addClass('selected');

            $('.acc-content').stop().animate({
                height: 0
            }, animTime);
            $('.acc-content').eq(currIndex).stop().animate({
                height: targetHeight
            }, animTime);

            setTimeout(function() {
                clickPolice = false;
            }, animTime);
        }

    });


}

// bind listeners functions
function bindElementsEvents() {
    //for files
    DQ('#trigger-file-1').addEventListener('click', uploadFiles);
    DQ('#upload-1 .reset').addEventListener('click', resetFilesUpload);
    DQ('#compare').addEventListener('click', compareFiles);

    //for folder
    DQ('#trigger-file-2').addEventListener('click', uploadFolder);
    DQ('#upload-2 .reset').addEventListener('click', resetFolderUpload);
    DQ('#compare-folder').addEventListener('click', compareFolder);
    DQ('#stop-compare').addEventListener('click', stopComparing);

    DQ('#save-results').addEventListener('click', saveResults);
    // DQ('#info-button').addEventListener('click', showInfo);
}

function disableButtons() {
    $('#compare-folder').addClass('ui basic disabled loading button');
    if ($("#compare-folder").hasClass("loading")) {
        $("#compare").addClass("ui basic disabled button")
    }
}

function enableButtons() {
    if ($("#compare-folder").hasClass("loading")) {
        $("#compare").removeClass("ui basic disabled button")
    }
    $('#stop-compare').removeClass('ui basic disabled loading button active');
    $('#compare-folder').removeClass('ui basic disabled loading button active');
}


/***  files comparision functions ***/

function uploadFiles() {
    eel.pyGetFilePath()(function(result) {
        renderSelectedFiles(result);
    });
}

function renderSelectedFiles(fileNames = []) {
    //files template
    updateAppState({
        action: 'reset'
    });
    updateAppState({
        action: 'add',
        fileNames: fileNames
    });

    const upload = DQ(`#upload-1`);
    const fileIcon = "<i class='id badge icon' aria-hidden='true'></i>";
    const template = `${fileNames
		.map(fileName => `<div class="file file--${fileName.replace('.', '-')}">
     <div class="name"><span>${fileIcon} ${fileName}</span></div>
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

function compareFiles() {
	showLoader();
	eel.gui_entry_files()(function (list) {
		hideLoader();
		const [err, result] = list
		let pair = result[0]; // the names of the files

		title = get_title(pair, err)
		preds = resultToPreds(result)
		preds = preds.map(Number);

		updateResultsSubtitle("files");
		insert_dropdown(pair, preds, err)
		createChart(title, preds,err);
	})

}

function resetFilesUpload(evnt) {
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
	uploadFiles()
}

/***  folder comparision functions ***/

function uploadFolder() {
	let folderPath = "";
	let excelPath = "";
	Swal.mixin({
		showCancelButton: true,
		heightAuto: false,
		showLoaderOnConfirm: true,
		progressSteps: ['1', '2']
	}).queue([({
		title: 'Upload a Folder',
		text: 'a folder that contain all the pairs you want to compare	 ',
		confirmButtonText: 'Upload Folder',
		preConfirm: () => {
			return new Promise((resolve) => {
				eel.pyGetFolderPath()(function (result) {
					if (result === "E") {
						resolve(false)
						Swal.showValidationMessage(
							`No Folder Selected, try again`
						)
						return;
					}
					folderPath = result;
					renderSelectedFolder(result);
					resolve(true);
				});
			}).then(flag => {
				return flag;
			})
		}
	}),
	{
		title: 'Upload an excel file. Example:',
		text: 'need to be an image here!!!',
		confirmButtonText: 'Upload an excel ',
		preConfirm: () => {
			return new Promise((resolve) => {
				eel.pyGetexcelFilePath()(function (excelFile) {
					console.log(excelPath)
					if (excelFile === "E") {
						console.log("no excell")
						resolve(false)
						Swal.showValidationMessage(
							`No excel file Selected, try again`
						)
						return;
					}
					excelPath = excelFile;
					resolve(true);
				});

			}).then(flag => {
				return flag;
			})
		}
	}

	]).then(() => {

		if(excelPath != ""){
			addExelProgressEffect(excelPath);
		}
		else if (folderPath != ""){   // compare by difference_sign

			Swal.fire({
				icon: 'info',
				title: "No Excel file provided",
				text:  "Using the deafult comparison method",
				showConfirmButton: false,
				heightAuto: false,
				timer: 2500
			})
		}

		const upload = DQ('#upload-2');
		upload.querySelector('.reset').classList.add('active');
		upload.querySelector('#compare-folder').classList.add('active');

	})
}


function stopComparing() {
	Swal.fire({
		title: "Stop comparing?",
		icon: 'question',
		showCancelButton: true,
		confirmButtonColor: '#3085d6',
		cancelButtonColor: '#d33',
		confirmButtonText: 'Yes',
		heightAuto: false
	}).then((result) => {
		if (result.value) {

			$('#stop-compare').addClass('ui basic disabled loading button');
			eel.disable_folder_comparing()()
		}
	})
}

function addExelProgressEffect(excelPath){
	const excelIcon = "<i class='columns icon' aria-hidden='true'></i>";
	DQ('#upload-2').querySelector('.list-files').innerHTML += addLoadedHtml(excelIcon, excelPath);
	DQ(`.file--${excelPath.replace('.', '-')}`).querySelector(".progress").classList.remove("active");
	DQ(`.file--${excelPath.replace('.', '-')}`).querySelector(".done").classList.add("anim");

}


function renderSelectedFolder(folderName, folderNum) {
	updateAppState({
		action: 'delete',
		// folderNum: folderNum
	});
	updateAppState({
		action: 'add',
		// folderNum: folderNum
	});
	FOLDER_NAME = folderName;
	const upload = DQ('#upload-2');

	const template = addLoadedHtml("<i class='folder open icon' aria-hidden='true'></i>", folderName);

	upload.querySelector('.body').classList.add('hidden');
	upload.querySelector('footer').classList.add('hasFiles');
	upload.querySelector('.list-files').innerHTML = template;

	const load = 1000;
	setTimeout(() => {
		upload.querySelector('.progress').classList.remove('active');
		upload.querySelector('.done').classList.add('anim');
	}, load);
}

function addLoadedHtml(icon, objectName) {
	return `<div class="file file--${objectName.replace('.', '-')}">
				<div class="name"><span>${icon} ${objectName}</span></div>
				<div class="progress active"></div>
				<div class="done">
				 <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" x="0px" y="0px" viewBox="0 0 1000 1000">
				   <g><path id="path" d="M500,10C229.4,10,10,229.4,10,500c0,270.6,219.4,490,490,490c270.6,0,490-219.4,490-490C990,229.4,770.6,10,500,10z M500,967.7C241.7,967.7,32.3,758.3,32.3,500C32.3,241.7,241.7,32.3,500,32.3c258.3,0,467.7,209.4,467.7,467.7C967.7,758.3,758.3,967.7,500,967.7z M748.4,325L448,623.1L301.6,477.9c-4.4-4.3-11.4-4.3-15.8,0c-4.4,4.3-4.4,11.3,0,15.6l151.2,150c0.5,1.3,1.4,2.6,2.5,3.7c4.4,4.3,11.4,4.3,15.8,0l308.9-306.5c4.4-4.3,4.4-11.3,0-15.6C759.8,320.7,752.7,320.7,748.4,325z"</g>
				   </svg>
				</div>
			   </div>`;
}


function compareFolder() {
	disableButtons();
	showLoader();
	eel.gui_entry_folder()(function (err) {
		console.log(err);
		if(err != "")
		{
			hideLoader();
			Swal.fire({
                icon: 'error',
                title: 'Error!',
                text: err,
                heightAuto: false
			});

		}
		else{
		$('#save-results').addClass('active');
		Swal.fire({
			icon: 'success',
			title: 'Folder comparison completed',
			text: 'Export an excel file by clicking "Save results" button',
			heightAuto: false
		})
	}
		enableButtons();
	})
}



function resetFolderUpload(evnt) {
	const upload = evnt.currentTarget.closest('.upload');
	updateAppState({
		action: 'reset'
	});
	upload.querySelector('.list-files').innerHTML = '';
	upload.querySelector('footer').classList.remove('hasFiles');
	upload.querySelector('.reset').classList.remove('active');
	upload.querySelector('#compare-folder').classList.remove('active');
	upload.querySelector('#stop-compare').classList.remove('active');
	// upload.querySelector('#save-results').classList.remove('active');
	// $('#text').classList.remove('hide');
	setTimeout(() => {
		upload.querySelector('.body').classList.remove('hidden');
	}, 500);
	uploadFolder()
}

/***  misc functions ***/




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

/*** loader ***/

function showLoader() {
	DQ('.overlay').classList.remove('hide');
}

function hideLoader() {
	DQ('.overlay').classList.add('hide');
	// $('#text').classList.add('hide');
}

function isLoaderOn() {
	return !DQ('.overlay').classList.contains('hide')
}

/*** dropdown ***/

function insert_dropdown(pair, preds, err) {
	item_in_dropdown = false;
	dropDownArray.every((item) => {
		// check if new pair is already in dropdown
		if (item.preds[0] == preds[0] &&
			((item.file1 == pair[0] && item.file2 == pair[1]) ||
				(item.file1 == pair[1] && item.file2 == pair[0]))) {
			item_in_dropdown = true;
			return false
		}
		return true;
	})
	if (item_in_dropdown) {
		return;
	}

	let index = dropDownArray.push({
		file1: pair[0],
		file2: pair[1],
		preds: preds,
		error: err
	});
	let resultsIcon

	const [diffPer, samePer] = preds;

	resultsIcon = (diffPer > samePer) ? "times" : "check";

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

	transition_dropdown();
}

function transition_dropdown() {
	$('#drop-down').transition({
		animation: 'glow',
		duration: '2.5s',
	});

	let title = `Comparison results: ${dropDownArray.length} <i class="angle down icon"></i>`;
	var div = document.getElementById('drop-down-title');
	div.innerHTML = title;
}

/*** results ***/

function resultToPreds(result) {
	// ------Different preds------------------Same preds
	return [(result[1][0] * 100).toFixed(2), (result[1][1] * 100).toFixed(2)]
}

function saveResults() {
	if (Array.isArray(dropDownArray) && dropDownArray.length) {
		Swal.fire({
			title: 'Enter excel file name',
			input: 'text',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Save',
			showLoaderOnConfirm: true,
			heightAuto: false,
			inputValidator: (value) => {
				if (!value) {
					return 'Please insert a file name'
				}
			}
		}).then((result) => {
			if (result.value) {
				eel.save_result_to_excel(dropDownArray, result.value)(function () {
					Swal.fire({
						icon: 'success',
						title: `${result.value} has been saved to your current .exe diractory`,
						showConfirmButton: false,
						heightAuto: false,
						timer: 2500
					})
				})
			}
		})
	} else {
		alert("empty")
	}
}

function displaySelectedPair(value, text, $choise) {
	let itemId = $choise.attr('id');
	let index = itemId.split("_")[1]
	let preds = dropDownArray[index].preds
	let pair = [dropDownArray[index].file1, dropDownArray[index].file2]
	err = dropDownArray[index].error
	title = `${pair[0]} & ${pair[1]}`;
	createChart(title, preds,err)
}

function updateResultsSubtitle(title) {
	var div = document.getElementById('result-sub-title');
	div.innerHTML = "&nbsp;" + title;
}

/* eel exposed functions to python */

eel.expose(set_pair_result);

function set_pair_result(err, result) {
	/* file_names , res_proba
	[ [1b.tiff,1.tiff], [0.1,0.9] ]
	*/
	let pair = result[0]; // the names of the files
	let preds;

	title = `${pair[0]} & ${pair[1]}`;

	preds = resultToPreds(result)
	preds = preds.map(Number);

	insert_dropdown(pair, preds, err)

	if (isLoaderOn()) {
		hideLoader();
		updateResultsSubtitle(FOLDER_NAME)
		DQ('#stop-compare').classList.add('active');
		DQ('#chart-container').classList.remove('hide');
		createChart(pair, preds,err)
	}
}



/***  Display results chart ***/

function createChart(title, scoresPercents,err) {
	const [diffPer, samePer] = scoresPercents;

	DQ('#chart-container').classList.remove('hide');
	const secondaryColor = getComputedStyle(document.documentElement)
		.getPropertyValue('--secondary-color');
	const quaternaryColor = getComputedStyle(document.documentElement)
		.getPropertyValue('--quaternary-color');

	// remove last graph and creates a new graph container
	d3chart = $('#d3chartContainer')
	d3chart.empty();
	d3chart.append(`<br/><h1 id="pair-result"> ${title}</h1>`);
	if (err != ""){
		console.log(err)
		const errTitle = "**ERROR OCCURED**" ;
		d3chart.append(`<br/><h2 id="error-result"> ${errTitle}</h2>`);
	}
	d3chart.append('<svg id="d3ChartSvg" viewBox="0 0 400 220"></svg>');


	$('#result-title')
		.transition('pulse')
	$('#pair-result')
		.transition('pulse')
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
		.delay(150)
		.duration(1000)
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