// Dark mode toggle logic
const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;
const topDiv = document.getElementById('topDiv');
var darkmodeValue = false;
// Function to update dark mode styles based on API response
async function updateDarkModeStyles() {
    try {
        // Make API call to check if dark mode is enabled
        const response = await fetch('/getsettings', {
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
        const setSettingsResponse = await fetch('/setsettings', {
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







const MAX_DATA_POINTS = 20;
const temperatureChart = document.getElementById('temperatureChart').getContext('2d');
const cpuUsageChart = document.getElementById('cpuUsageChart').getContext('2d');



const temperatureChartInstance = new Chart(temperatureChart, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Temperature',
            data: [],
            borderColor: 'red',
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
const cpuUsageChartInstance = new Chart(cpuUsageChart, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'CPU Usage',
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
async function updateCharts() {

    const networksResponse = await fetch('/networks');
    const networksdata = await networksResponse.json();

    if (networksdata.message == "noInterfaceSelected"){
        // If no interface is chosen, show the modal
        const interfaceModal = new bootstrap.Modal(document.getElementById('interfaceModal'));
        interfaceModal.show();
    }
    // Update the content of HTML elements with the received data
    document.getElementById('networkCount').innerText = `In Range: ${networksdata.networkCount}`;
    document.getElementById('totalNetworks').innerText = `Total Networks: ${networksdata.savedNetworksCount}`;
    document.getElementById('unknownNetworks').innerText = `Unknown: ${networksdata.unknownEnc}`;
    document.getElementById('wepNetworks').innerText = `WEP: ${networksdata.WEP}`;
    document.getElementById('wpaNetworks').innerText = `WPA: ${networksdata.WPA}`;
    document.getElementById('wpa2Networks').innerText = `WPA2: ${networksdata.WPA2}`;
    document.getElementById('unknownNetworksSaved').innerText = `Unknown: ${networksdata.unknownSaved}`;
    document.getElementById('wepNetworksSaved').innerText = `WEP: ${networksdata.savedWEP}`;
    document.getElementById('wpaNetworksSaved').innerText = `WPA: ${networksdata.savedWPA}`;
    document.getElementById('wpa2NetworksSaved').innerText = `WPA2: ${networksdata.savedWPA2}`;

    // Update the pie chart data
    const wpaCount = networksdata.WPA || 0;
    const wpa2Count = networksdata.WPA2 || 0;
    const wepCount = networksdata.WEP || 0;
    const unknownCount = networksdata.unknownEnc || 0;

    // Update the pie chart data
    const wpaCountSaved = networksdata.savedWPA || 0;
    const wpa2CountSaved = networksdata.savedWPA2 || 0;
    const wepCountSaved = networksdata.savedWEP || 0;
    const unknownCountSaved = networksdata.unknownEnc || 0;


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
    const nearestNetworks = Object.values(networksdata.networks) || [];
    const sortedNetworks = nearestNetworks.sort((a, b) => b.signalStrength - a.signalStrength);
    const limitedNetworks = sortedNetworks.slice(0, 10); // Limit to max 10 data points

    const signalData = limitedNetworks.map(network => (showSSIDs ? network.signalStrength : 0));
    const ssidData = limitedNetworks.map(network => (showSSIDs ? network.ssid : '')); // Update this line


    // Update chart data
    strongestSignalsBarChart.data.labels = ssidData;
    strongestSignalsBarChart.data.datasets[0].data = signalData;
    strongestSignalsBarChart.update();

    document.getElementById('upload').innerText = `Upload: ${networksdata.interfaceUsage.upload}`;
    document.getElementById('download').innerText = `Download: ${networksdata.interfaceUsage.download}`;
    // Update upload and download chart data
    const uploadData = parseFloat(networksdata.interfaceUsage.upload);
    const downloadData = parseFloat(networksdata.interfaceUsage.download);

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

    const dataresponse = await fetch('/data');
    const datadata = await dataresponse.json();
    
    document.getElementById('temp').innerHTML = "CPU Temp: " + datadata.temperature;
    document.getElementById('cpu').innerHTML = "CPU Usage: " + datadata.cpuUsage;
    // Update temperature chart
    temperatureChartInstance.data.labels.push(new Date().toLocaleTimeString());
    temperatureChartInstance.data.datasets[0].data.push(datadata.temperature);
    temperatureChartInstance.update();
    // Update CPU usage chart
    cpuUsageChartInstance.data.labels.push(new Date().toLocaleTimeString());
    cpuUsageChartInstance.data.datasets[0].data.push(datadata.cpuUsage);
    cpuUsageChartInstance.update();
    // Limit the number of data points to the defined maximum
    if (temperatureChartInstance.data.datasets[0].data.length > MAX_DATA_POINTS) {
        temperatureChartInstance.data.datasets[0].data.shift();
        temperatureChartInstance.data.labels.shift(); // Also shift corresponding label
    }
    if (cpuUsageChartInstance.data.datasets[0].data.length > MAX_DATA_POINTS) {
        cpuUsageChartInstance.data.datasets[0].data.shift();
        cpuUsageChartInstance.data.labels.shift(); // Also shift corresponding label
    }
}

// Initial call to update the chart and set interval for updates
updateCharts();
setInterval(updateCharts, 6000); // Update every 6 seconds





document.addEventListener("DOMContentLoaded", function () {
    const interfaceForm = document.getElementById('interfaceForm');
    const interfaceSelect = document.getElementById('interfaceSelect');
    const selectedInterfaceLabel = document.getElementById('selectedInterface');
    // Check if an interface is already chosen
    const currentInterface = selectedInterfaceLabel.getAttribute('value'); // Use getAttribute to get the value
    if (currentInterface == "None") {
        // If no interface is chosen, show the modal
        const interfaceModal = new bootstrap.Modal(document.getElementById('interfaceModal'));
        interfaceModal.show();
        // Add submit event listener to the form
        interfaceForm.addEventListener('submit', function (event) {
            event.preventDefault(); // Prevent default form submission
            const selectedInterfaceIdx = interfaceSelect.value;
            const selectedInterfaceName = interfaceSelect.options[interfaceSelect.selectedIndex].text; // Get selected option text
            // Create JSON payload
            const payload = {
                interfaceIdx: selectedInterfaceIdx,
                interfaceName: selectedInterfaceName
            };
            // Make API call using fetch
            fetch('/setInterface', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                // Handle API response if needed
                console.log(data);
                // Close the modal after submitting
                interfaceModal.hide();
                selectedInterfaceLabel.textContent = `Using Interface: ${selectedInterfaceName}`;
            })
            .catch(error => {
                // Handle error if needed
                console.error('Error:', error);
            });
        });
    } else {
        // If an interface is already chosen, update the label
        selectedInterfaceLabel.textContent = `Using Interface: ${selectedInterfaceLabel.textContent}`;
    }
});



let showSSIDs = false; // Initial state


function toggleSSIDs() {
    showSSIDs = !showSSIDs; // Toggle the state
    // Check if the container element exists before trying to access its style
    const container = document.getElementById('strongestSignalsContainer');


    if (showSSIDs) {
        document.getElementById('toggleSSIDsBtn').innerText = 'Hide SSIDs';
    } else {
        document.getElementById('toggleSSIDsBtn').innerText = 'Show SSIDs';
    }
    updateCharts(); // Call the chart update function
}

