let ws;
let currentPixels = null;
let progressChart = null;

function renderHeatmap(pixels) {
    console.log(pixels);
    const canvas = document.getElementById('heatmap');
    const ctx = canvas.getContext('2d');
    const cellSize = canvas.width / 8;

    const minTemp = Math.min(...pixels);
    const maxTemp = Math.max(...pixels);
    const range = maxTemp - minTemp || 1;

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
}

function updateChart(empty, present) {
    if (progressChart) {
        progressChart.data.datasets[0].data = [empty, present];
        progressChart.update();
    }
}

function initChart() {
    const ctx = document.getElementById('progress-chart').getContext('2d');
    progressChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Empty', 'Present'],
            datasets: [
                {
                    label: 'Collected',
                    data: [0, 0],
                    backgroundColor: ['#2ecc71', '#e74c3c']
                },
                {
                    label: 'Target',
                    data: [50, 50],
                    backgroundColor: ['rgba(46,204,113,0.2)', 'rgba(231,76,60,0.2)'],
                    borderColor: ['#2ecc71', '#e74c3c'],
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 60
                }
            }
        }
    });
}

function connect() {
    // TODO: Create WebSocket connection to ws://${window.location.host}/ws
    // TODO: Set status to "Connected" on open, "Disconnected" on close
    // TODO: Auto-reconnect on close after 1 second
    // TODO: On message, parse JSON and:
    //   - Update currentPixels
    //   - Call renderHeatmap(data.pixels)
    //   - Update stat displays (total, empty, present)
    //   - Call updateChart(data.stats.empty, data.stats.present)

    const ws = new WebSocket('ws://localhost:8000/ws');

    //ws.send('Update stock price');

    //addEventListener("open", (event) => { }) is the same as onopen = (event) => { }
    ws.onopen = () => {
        document.getElementById('status').textContent = 'Connected';
        //class is needed to determine css
        document.getElementById('status').className = 'connected';
    };

    ws.onclose = () => 
        {
        document.getElementById('status').textContent = 'Disconnected';
        document.getElementById('status').className = 'disconnected';
        setTimeout(connect, 1000);
        };
    // TODO: On message, parse JSON and:
    //   - Update currentPixels
    //   - Call renderHeatmap(data.pixels)
    //   - Update stat displays (total, empty, present)
    //   - Call updateChart(data.stats.empty, data.stats.present)
    ws.onmessage = (event) => 
        {
            

            const parseJson = JSON.parse(event.data);
            console.log('Received:', parseJson);
            currentPixels = parseJson.pixels;
            //console.log(currentPixels)
            renderHeatmap(currentPixels);
            updateChart(parseJson.stats.empty, parseJson.stats.present);

            document.getElementById('total').textContent = parseJson.stats.total;
            document.getElementById('empty').textContent = parseJson.stats.empty;
            document.getElementById('present').textContent = parseJson.stats.present;
            
        };

}

//This is needed for the api/collect function to run.
async function collect(labelType) {
    // TODO: Check if currentPixels is available
    // TODO: POST to /api/collect with {label: labelType, pixels: currentPixels}
    // TODO: Display success or error message
    // TODO: Clear currentPixels after submission

    if(!currentPixels)
        {
            document.getElementById('message').textContent = 'No frame to label';
            return;
        }
    //need to review/ask, what type of response is this??
    const response = await fetch('/api/collect', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({label: labelType, pixels: currentPixels})
    });
    console.log(response)
    const result = await response.json();

    document.getElementById('message').textContent = result.success
    ? `Labeleddddddd as ${labelType}!`
    : `Errorrrrrrrr: ${result.error}`;
    //need to reset it i guess....
    currentPixels = null;
    
}

document.addEventListener('keydown', (e) => {
    if (e.key === '0') collect('empty');
    if (e.key === '1') collect('present');
});

document.addEventListener('DOMContentLoaded', () => {
    initChart();
    connect();
});
