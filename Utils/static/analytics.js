let showSSIDs = false; // Initial state

function toggleSSIDs() {
    showSSIDs = !showSSIDs; // Toggle the state

    updateNetworkCharts(); // Call the chart update function
}



function toggleSSIDs() {
    showSSIDs = !showSSIDs; // Toggle the state
    // Check if the container element exists before trying to access its style
    const container = document.getElementById('strongestSignalsContainer');
    

    if (showSSIDs) {
        document.getElementById('toggleSSIDsBtn').innerText = 'Hide SSIDs';
    } else {
        document.getElementById('toggleSSIDsBtn').innerText = 'Show SSIDs';
    }
    updateNetworkCharts(); // Call the chart update function
}



// Initialize the bar chart
const strongestSignalsBarChart = new Chart(strongestSignalsChart, {
    type: 'bar',
    data: {
        labels: [], // Will contain SSIDs of nearest networks
        datasets: [{
            label: 'Signal Strength (0 highest, -100 lowest))',
            data: [], // Will contain signal strength values
            backgroundColor: 'blue', // Customize the bar color
        }]
    },
    options: {
        indexAxis: 'x', // Display bars on the bottom and go up based on signal strength
        scales: {
            y: {
               
                title: {
                    display: true,
                    text: 'Network SSID'
                }
            },
            x: {
                beginAtZero: true, // Display highest signal strength at the top
                title: {
                    display: true,
                    text: 'Signal Strength'
                }
            }
        },

    }
});


// Initialize the pie chart for encryption in range
const encryptionPieChartInRangeCanvas = document.getElementById('encryptionPieChartInRange');
const encryptionPieChartInRange = new Chart(encryptionPieChartInRangeCanvas, {
    type: 'pie',
    data: {
        labels: ['WEP', 'WPA', 'WPA2', 'Unknown'],
        datasets: [{
            label: 'In Range',
            data: [],
            backgroundColor: ['red', 'blue', 'green', 'purple', 'gray'], // Customize the colors
        }]
    },
    options: {
        aspectRatio: 2, // Adjust this value to control the chart's aspect ratio
        // Other options can be added here as needed
    }
});
// Initialize the pie chart for total encryption
const encryptionPieChartTotalCanvas = document.getElementById('encryptionChartSaved');
const encryptionPieChartTotal = new Chart(encryptionPieChartTotalCanvas, {
    type: 'pie',
    data: {
        labels: ['WEP', 'WPA', 'WPA2', 'Unknown'],
        datasets: [{
            label: 'In Total',
            data: [],
            backgroundColor: ['red', 'blue', 'green', 'purple', 'gray'], // Customize the colors
        }]
    },
    options: {
        aspectRatio: 2, // Adjust this value to control the chart's aspect ratio
        // Other options can be added here as needed
    }
});







// Function to fetch and update the encryption data for the pie chart
async function updateNetworkCharts() {
    
    const response = await fetch('/networks');
    const data = await response.json();

    // Update the pie chart data
    const wpaCount = data.WPA || 0;
    const wpa2Count = data.WPA2 || 0;
    const wepCount = data.WEP || 0;
    const unknownCount = data.unknownEnc || 0;

    // Update the pie chart data
    const wpaCountSaved = data.savedWPA || 0;
    const wpa2CountSaved = data.savedWPA2 || 0;
    const wepCountSaved = data.savedWEP || 0;
    const unknownCountSaved = data.unknownEnc || 0;


    // Update pie chart data
    encryptionPieChartInRange.data.datasets[0].data = [wepCount, wpaCount, wpa2Count, unknownCount];
    encryptionPieChartInRange.data.labels = [
        `WEP (${wepCount})`,
        `WPA (${wpaCount})`,
        `WPA2 (${wpa2Count})`,
        `Unknown (${unknownCount})`
    ];
    encryptionPieChartInRange.update();

    // Update pie chart data
    encryptionPieChartTotal.data.datasets[0].data = [wepCountSaved, wpaCountSaved, wpa2CountSaved, unknownCountSaved];
    encryptionPieChartTotal.data.labels = [
        `WEP (${wepCountSaved})`,
        `WPA (${wpaCountSaved})`,
        `WPA2 (${wpa2CountSaved})`,
        `Unknown (${unknownCountSaved})`
    ];
    encryptionPieChartTotal.update();

    // Update the content of HTML elements with the received data
    document.getElementById('networkCount').innerText = `In Range: ${data.networkCount}`;
    document.getElementById('totalNetworks').innerText = `Total Networks: ${data.savedNetworksCount}`;
    document.getElementById('unknownNetworks').innerText = `Unknown: ${data.unknownEnc}`;
    document.getElementById('wepNetworks').innerText = `WEP: ${data.WEP}`;
    document.getElementById('wpaNetworks').innerText = `WPA: ${data.WPA}`;
    document.getElementById('wpa2Networks').innerText = `WPA2: ${data.WPA2}`;
    document.getElementById('unknownNetworksSaved').innerText = `Unknown: ${data.unknownSaved}`;
    document.getElementById('wepNetworksSaved').innerText = `WEP: ${data.savedWEP}`;
    document.getElementById('wpaNetworksSaved').innerText = `WPA: ${data.savedWPA}`;
    document.getElementById('wpa2NetworksSaved').innerText = `WPA2: ${data.savedWPA2}`;

    // Update the strongest signals bar chart data
    const nearestNetworks = Object.values(data.networks) || [];
    const sortedNetworks = nearestNetworks.sort((a, b) => b.signalStrength - a.signalStrength);
    const limitedNetworks = sortedNetworks.slice(0, 10); // Limit to max 10 data points

    const signalData = limitedNetworks.map(network => (showSSIDs ? network.signalStrength : 0));
    const ssidData = limitedNetworks.map(network => (showSSIDs ? network.ssid : '')); // Update this line


    // Update chart data
    strongestSignalsBarChart.data.labels = ssidData;
    strongestSignalsBarChart.data.datasets[0].data = signalData;
    strongestSignalsBarChart.update();
}

// Initial call to update the chart and set interval for updates
updateNetworkCharts();
setInterval(updateNetworkCharts, 7000); // Update every 7 seconds
