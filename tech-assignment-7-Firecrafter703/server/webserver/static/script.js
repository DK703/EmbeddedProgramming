//needed to render heatmap. Got it from collection client
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

//my own implementation of connect
function connect() {
   
    const ws = new WebSocket('ws://localhost:8000/ws');



    //addEventListener("open", (event) => { }) is the same as onopen = (event) => { }
    ws.onopen = () => {
        document.getElementById('status').textContent = 'Connected';
        //class is needed to determine css
        console.log("open")
        document.getElementById('status').className = 'connected';
    };

    ws.onclose = () => 
        {
        document.getElementById('status').textContent = 'Disconnected';
        document.getElementById('status').className = 'disconnected';
        console.log("close")
        setTimeout(connect, 1000);
        };

    ws.onmessage = (event) => 
        {
            
            //goes over the heatmap
            const parseJson = JSON.parse(event.data);
            console.log('Received:', parseJson);
            currentPixels = parseJson.pixels;
            //needed join cuz you cant just set do const copy = currentPixels to create a copy,
            //since javascript will still make it point to the value
            document.getElementById('pixels').textContent = currentPixels.join(', ');
            renderHeatmap(currentPixels);
            console.log(parseJson.stats.mac_address)
            console.log(parseJson.stats.mac_address)
            console.log(currentPixels)

            document.getElementById('message').textContent = parseJson.stats.temperature;
            //document.getElementById('pixels').textContent = currentPixels;
            document.getElementById('mc').textContent = parseJson.stats.mac_address;
            document.getElementById('prediction').textContent = parseJson.stats.prediction;
            document.getElementById('confidence').textContent = parseJson.stats.confidence;
            
        };

        

}
async function command(command)
{
    const response = await fetch('/api/command', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: command })
    });
    console.log(response)
    const result = await response.json();

}

document.addEventListener('DOMContentLoaded', () => {
    connect();
});

