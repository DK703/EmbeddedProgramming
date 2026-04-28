const API_BASE = '';
let distributionChart = null;
totalFrames = 0;
emptyCount = 0;
presentCount = 0;
    //create the table and its rows already.
    const table = document.getElementById("leaderboard").getElementsByTagName('tbody')[0];
            const row1 = table.insertRow();
            ca1 = row1.insertCell(0);
            ca2 = row1.insertCell(1)
            ca3 = row1.insertCell(2)
            ca1.innerHTML = "1";
            ca2.innerHTML = "No student";
            ca3.innerHTML = "No frames";
            const row2 = table.insertRow();
            cb1 = row2.insertCell(0);
            cb2 = row2.insertCell(1)
            cb3 = row2.insertCell(2)
            cb1.innerHTML = "2";
            cb2.innerHTML = "No student";
            cb3.innerHTML = "No frames";
            const row3 = table.insertRow();
            cc1 = row3.insertCell(0);
            cc2 = row3.insertCell(1)
            cc3 = row3.insertCell(2)
            cc1.innerHTML = "3";
            cc2.innerHTML = "No student";
            cc3.innerHTML = "No frames";

async function fetchStats() {
    // TODO: Implement - fetch from /api/stats and update the page
    // - Update #total-frames, #empty-count, #present-count 
    // are thes the class names from index html?
    // - Update the distribution chart
    // - Update the leaderboard

     //is method and headers correct?
     //fetch would be a request,not a response
     const response = await fetch('/api/stats', {
        method: 'GET',
        headers: {'Content-Type': 'application/json'},
        //body: JSON.stringify({label: formData})
    });

    //document.getElementById('total').textContent = parseJson.stats.total;
    document.getElementById('total-frames').textContent = totalFrames;
    document.getElementById('empty-count').textContent = emptyCount;

    document.getElementById('present-count').textContent = presentCount;




}

async function fetchSamples() {
    // TODO: Implement - fetch from /api/sample and render heatmaps
    // - Fetch 6 samples (3 empty, 3 present)
    // - Render each as an 8x8 canvas heatmap

      const response = await fetch('/api/sample', {
        method: 'GET',
        headers: {'Content-Type': 'application/json'},
        //body: JSON.stringify({label: formData})
    });
    const data = await response.json();

    array = data.result;
    //decided just to create 5 separate heat maps in index.html and go from there
    canvas = document.getElementById('heatmap') 
    renderHeatmap(canvas, array[0].pixels, array[0].element)
    document.getElementById('label').textContent = array[0].label;
    canvas2 = document.getElementById('heatmap2') 
    renderHeatmap(canvas2, array[1].pixels, array[1].element)
    document.getElementById('label2').textContent = array[1].label;
    canvas3 = document.getElementById('heatmap3') 
    renderHeatmap(canvas3, array[2].pixels, array[2].element)
    document.getElementById('label3').textContent = array[2].label;
    canvas4 = document.getElementById('heatmap4') 
    renderHeatmap(canvas4, array[3].pixels, array[3].element)
    document.getElementById('label4').textContent = array[3].label;
    canvas5 = document.getElementById('heatmap5') 
    renderHeatmap(canvas5, array[4].pixels, array[4].element)
    document.getElementById('label5').textContent = array[4].label;

    

    console.log(data)
    
}

function renderHeatmap(canvas, pixels, label) {

    //sample-gallery
    //need to test what canvas is to udnerstand what to do
    
    const chart = document.getElementById('heatmap');
    //created a heatmap object at html
    //     //canvas = chart;
    
    const ctx = canvas.getContext('2d');
    const cellSize = canvas.width / 8;

    const minTemp = Math.min(...pixels);
    const maxTemp = Math.max(...pixels);
    const range = maxTemp - minTemp || 1;

    //just copy and pasted the challenge 1 heatmap code.
    
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const temp = pixels[row * 8 + col];
            const norm = (temp - minTemp) / range;
            const r = Math.floor(255 * Math.min(1, norm * 2));
            const g = Math.floor(255 * Math.max(0, (norm - 0.5) * 2));
            const b = Math.floor(255 * (1 - norm));
            ctx.fillStyle = `rgb(${r},${g},${b})`;
            ctx.fillRect(col * cellSize, row * cellSize, cellSize, cellSize);
        }
    }

   // document.getElementById('label').textContent = label;

    
    


}

function updateChart(empty, present, total) {
    emptyRatio = empty/total;
    presentRatio = present/total;
    if (distributionChart) {
        distributionChart.data.datasets[0].data = [emptyRatio, presentRatio];
        distributionChart.update();
    }
    console.log("chart is updated by");
    console.log(empty);
    console.log(present);
    console.log(total)
}

function initChart()
{
    //distribution-chart
    const ctx = document.getElementById('distribution-chart')
    distributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Empty', 'Present'],
            datasets:[{data: [0, 0]}]

        }})
}

function connectWebSocket() {
    // TODO: Implement - connect to /ws/live
    // - Update #ws-status on connect/disconnect
    // - Parse incoming messages and update stats



    const ws = new WebSocket('ws://localhost:8000/ws/live');
    
    ws.onopen = () => {
        document.getElementById('ws-status').textContent = 'Connected';
      
        document.getElementById('ws-status').className = 'connected';
    };

    ws.onclose = () => 
        {
        document.getElementById('ws-status').textContent = 'Disconnected';
        document.getElementById('ws-status').className = 'disconnected';
        setTimeout(connectWebSocket, 1000);
        };

    ws.onmessage = (event) => 
        {
            console.log("ws")
            const parseJson = JSON.parse(event.data);
            console.log('message is:', parseJson);
            console.log('how to parse...:', parseJson.result.total_frames);
            updateChart(parseJson.result.by_label.empty, parseJson.result.by_label.present, parseJson.result.total_frames)
            console.log('person 0 should be', parseJson.result.by_student[0]);

            document.getElementById('total-frames').textContent = parseJson.result.total_frames;
            document.getElementById('empty-count').textContent = parseJson.result.by_label.empty;
            document.getElementById('present-count').textContent = parseJson.result.by_label.present;


            //this block of code just updates the inner html of the rows that already exist. If it
            //changes the rankings will change accordingly
            

            ca1.innerHTML = "1";
            ca2.innerHTML = parseJson.result.by_student[0].student_id;
            ca3.innerHTML = parseJson.result.by_student[0].count;
            cb1.innerHTML = "2";
            cb2.innerHTML = parseJson.result.by_student[1].student_id;
            cb3.innerHTML = parseJson.result.by_student[1].count;
            cc1.innerHTML = "3";
            cc2.innerHTML = parseJson.result.by_student[2].student_id;
            cc3.innerHTML = parseJson.result.by_student[2].count;

        }

}

async function uploadFrame(formData) {
    // TODO: Implement - POST to /api/upload
    // - Show success/error in #upload-status

    const response = await fetch('/api/upload', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
    });

     const result = await response.json();

    document.getElementById('upload-status').textContent = result.success
    ? `label as as ${label}!`
    : `Errorrrrrrrr: ${result.error}`;
}

function initChart() {
    const ctx = document.getElementById('distribution-chart').getContext('2d');
    distributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Empty', 'Present'],
            datasets: [{
                label: 'Frame Count',
                data: [0, 0],
                backgroundColor: ['#2ecc71', '#e74c3c']
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initChart();
    fetchStats();
    fetchSamples();
    connectWebSocket();

    document.getElementById('refresh-samples').addEventListener('click', fetchSamples);

    document.getElementById('upload-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;

        const pixelString = form.pixels.value;
        const pixels = pixelString.split(',').map(v => parseFloat(v.trim()));

        if (pixels.length !== 64 || pixels.some(isNaN)) {
            document.getElementById('upload-status').textContent = 'Error: Need exactly 64 numeric values';
            return;
        }

        const formData = {
            label: form.label.value,
            pixels: pixels
        };

        await uploadFrame(formData);
    });
});
