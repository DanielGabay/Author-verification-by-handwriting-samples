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

// bind listeners functions
function bindElementsEvents() {
	// file browse events
	$('#trigger-file-1').addEventListener('click', () => {
		// this is the f-i-r-s-t input
		// TODO: this needs to open python file explorer
		handleFileSelect('test1', 1);
	});

	$('#trigger-file-2').addEventListener('click', (evt) => {
		// this is the s-e-c-o-n-d input
		// TODO: this needs to open python file explorer
		handleFileSelect('test2', 2);
	});

	//reset for first element
	$('#upload-1 .reset').addEventListener('click', (evnt) => {
		const upload = evnt.currentTarget.closest('.upload');
		updateAppState({ action: 'delete', fileNum: 1 });
		upload.querySelector('.list-files').innerHTML = '';
		upload.querySelector('footer').classList.remove('hasFiles');
		upload.querySelector('.reset').classList.remove('active');
		setTimeout(() => {
			upload.querySelector('.body').classList.remove('hidden');
		}, 500);
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
		}, 500);
	});

	$('#compare').addEventListener('click', (evt) => {
		// alert('starting comparing');

		showLoader();
		setTimeout(() => {
			// remove timeout instead use python
			hideLoader();
			const compareScore = [ 50, 50 ];
			buildGraph(compareScore);
		}, 5000);
	});
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
	const [ samePer, diffPer ] = scoresPercents;
	$('.graph-container').classList.remove('hide');
	// input data
	const data = [
		{
			name: 'same',
			percentage: samePer, // percentage
			value: 100, // millions
			color: '#0789F8'
		},
		{
			name: 'diff',
			percentage: diffPer,
			value: 100,
			color: '#F9BA00'
		}
	];

	// retrieve the svg in which to plot the viz
	const svg = d3.select('.graph-container svg');
	debugger;

	// identify the dimensions of the viewBox to establish the svg canvas
	const viewBox = svg.attr('viewBox');
	const regexViewBox = /\d+ \d+ (\d+) (\d+)/;
	// ! .match() returns string values
	const [ , viewBoxWidth, viewBoxHeight ] = viewBox.match(regexViewBox).map((item) => Number.parseInt(item, 10));

	// with the margin convention include a group element translated within the svg canvas
	const margin = {
		top: 20,
		right: 20,
		bottom: 20,
		left: 20
	};
	// compute the width and height of the actual viz from the viewBox dimensions and considering the margins
	// this to later work with width and height attributes directly through the width and height variables
	const width = viewBoxWidth - (margin.left + margin.right);
	const height = viewBoxHeight - (margin.top + margin.bottom);

	// compute the radius as half the minor size between the width and height
	const radius = Math.min(width, height) / 2;
	// initialize a variable to have the multiple elements share the same stroke-width property
	const strokeWidth = 10;

	const group = svg.append('g').attr('transform', `translate(${margin.left} ${margin.top})`);

	// DEFAULT CIRCLE
	// circle used as a background for the colored donut chart
	// add a group to center the circle in the canvas (this to rotate the circle from the center)
	const groupDefault = group.append('g').attr('transform', `translate(${width / 2} ${height / 2})`);

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
		.attr('stroke-dasharray', radius * 3.14 * 2)
		.attr('stroke-dashoffset', radius * 3.14 * 2);

	// COLORED CIRCLES
	// pie function to compute the arcs
	const pie = d3
		.pie()
		.sort(null)
		.padAngle(0.12) // use either the value or the percentage in the dataset
		.value((d) => d.value);

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
	const groupArcs = group.append('g').attr('transform', `translate(${width / 2} ${height / 2})`);

	const groupsArcs = groupArcs.selectAll('g').data(pie(data)).enter().append('g');

	// include the arcs specifying the stroke with the same width of the circle element
	groupsArcs
		.append('path')
		.attr('d', arc)
		.attr('fill', 'none')
		.attr('stroke', (d) => d.data.color)
		.attr('stroke-width', strokeWidth * 0.8)
		.attr('stroke-linecap', 'round')
		.attr('stroke-linejoin', 'round')
		// hide the segments by applying a stroke-dasharray/stroke-dashoffset equal to the circle circumference
		// ! the length of the element varies, and it considered afterwords
		// for certain the paths are less than the circumference of the entire circle
		.attr('stroke-dasharray', radius * 3.14 * 2)
		.attr('stroke-dashoffset', radius * 3.14 * 2);

	// include line elements visually connecting the text labels with the arcs
	groupsArcs
		.append('line')
		.attr('x1', 0)
		.attr('x2', (d) => {
			const [ x ] = arc.centroid(d);
			return x > 0 ? '25' : '-25';
		})
		.attr('y1', 0)
		.attr('y2', 0)
		.attr('stroke', ({ data: d }) => d.color)
		.attr('stroke-width', 1.5)
		.attr('transform', (d) => {
			const [ x, y ] = arc.centroid(d);
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
		.attr('font-size', 15)
		.attr('text-anchor', (d) => {
			const [ x ] = arc.centroid(d);
			return x > 0 ? 'start' : 'end';
		})
		.attr('transform', (d) => {
			const [ x, y ] = arc.centroid(d);
			const offset = x > 0 ? 50 : -50;
			return `translate(${x + offset} ${y})`;
		})
		.html(
			({ data: d }) => `
	  <tspan x="0">${d.name}:</tspan><tspan x="0" dy="30" font-size="20">${d.percentage}%</tspan>
	`
		)
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
		.duration(2000)
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

			const duration = 1000;
			// transition the path elements to stroke-dashoffset 0
			d3
				.selectAll('svg g g path')
				.transition()
				.ease(d3.easeLinear)
				.delay((d, i) => i * duration)
				.duration(duration)
				.attr('stroke-dashoffset', 0);

			// transition the line elements elements to stroke-dashoffset 0
			d3
				.selectAll('svg g g line')
				.transition()
				.ease(d3.easeLinear)
				.delay((d, i) => i * duration + duration / 2.5)
				.duration(duration / 3)
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

	[];
}
