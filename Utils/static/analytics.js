// Dark mode toggle logic
const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;
const topDiv = document.getElementById('topDiv');
var darkmodeValue = false;
// Function to update dark mode styles based on API response
async function updateDarkModeStyles() {
    try {
        // Make API call to check if dark mode is enabled
        const response = await fetch('/getSettings', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
        });
        const data = await response.json();
        console.log('Dark mode API response:', data);

        // Update body style and class based on dark mode status
        if (data.settings.darkmode) {
            body.classList.add('bg-secondary');
            topDiv.classList.add('text-white');
            body.classList.add('dark-mode');
            darkmodeValue = true;
        } else {
            topDiv.classList.remove('text-white');
            body.classList.remove('bg-secondary');
            body.classList.remove('dark-mode');
            darkmodeValue = false;
        }
    } catch (error) {
        console.error('Error updating dark mode styles:', error);
    }
}

// Call the function to update styles on initial load
updateDarkModeStyles();


darkModeToggle.addEventListener('click', async () => {
    try {
        console.log('Dark mode toggle clicked');
        // Get current dark mode status
        const isDarkMode = body.classList.contains('dark-mode');

        // Prepare payload for API call
        const darkModePayload = {
            call: 'darkmode',
            payload: !isDarkMode
        };

        // Make API call to set dark mode status
        const setSettingsResponse = await fetch('/setSettings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(darkModePayload)
        });
        const setData = await setSettingsResponse.json();
        console.log('Dark mode set response:', setData);

        // Update styles after toggling
        updateDarkModeStyles();
    } catch (error) {
        console.error('Error toggling dark mode:', error);
    }
});


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
        }],


    },
    options: {
        indexAxis: 'x', // Display bars on the bottom and go up based on signal strength
        scales: {
            y: {

                title: {
                    display: true,
                    text: 'Network SSID',
                    color: "lightgrey", // Set legend text color
                },
                ticks: {
                    fontSize: 26, // Set the font size for x-axis labels
                }
            },
            x: {
                beginAtZero: true, // Display highest signal strength at the top
                title: {
                    display: true,
                    text: 'Signal Strength',
                    color: "lightgrey", // Set legend text color
                },
                ticks: {
                    fontSize: 40
                }

            }
        },
        plugins: {
            legend: {
                labels: {
                    color: "lightgrey", // Set legend text color
                }
            }
        }
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
        aspectRatio: 1.4, // Adjust this value to control the chart's aspect ratio
        plugins: {
            legend: {
                labels: {
                    color: "lightgrey", // Set legend text color
                }
            }
        }
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
        aspectRatio: 1.4, // Adjust this value to control the chart's aspect ratio
        plugins: {
            legend: {
                labels: {
                    color: "lightgrey", // Set legend text color
                }
            }
        }
    }
});


const uploadDownloadChart = document.getElementById('uploadanddownload').getContext('2d');
const uploadanddownload = new Chart(uploadDownloadChart, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Upload',
            data: [],
            borderColor: 'red',
            fill: false,
        },
        {
            label: 'Download',
            data: [],
            borderColor: 'blue',
            fill: false,
        }]
    },
    options: {
        animation: {
            duration: 1 // Set animation duration to 0 to disable animation
        },
        plugins: {
            legend: {
                labels: {
                    color: "lightgrey", // Set legend text color
                }
            }
        }
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

    document.getElementById('upload').innerText = `Upload: ${data.interfaceUsage.upload}`;
    document.getElementById('download').innerText = `Download: ${data.interfaceUsage.download}`;
    // Update upload and download chart data
    const uploadData = parseFloat(data.interfaceUsage.upload);
    const downloadData = parseFloat(data.interfaceUsage.download);

    uploadanddownload.data.labels.push(new Date().toLocaleTimeString()); // Update labels with timestamp
    uploadanddownload.data.datasets[0].data.push(uploadData);
    uploadanddownload.data.datasets[1].data.push(downloadData);

    // Limit the number of data points displayed on the chart
    const maxDataPoints = 20;
    if (uploadanddownload.data.labels.length > maxDataPoints) {
        uploadanddownload.data.labels.shift();
        uploadanddownload.data.datasets[0].data.shift();
        uploadanddownload.data.datasets[1].data.shift();
    }

    uploadanddownload.update();

}

// Initial call to update the chart and set interval for updates
updateNetworkCharts();
setInterval(updateNetworkCharts, 7000); // Update every 7 seconds





