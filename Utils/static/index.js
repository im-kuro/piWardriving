

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




async function updateCharts() {
    console.log("Updating charts...");
    const response = await fetch('/data');
    const data = await response.json();

    
    document.getElementById('temp').innerHTML = "CPU Temp: " + data.temperature;
    document.getElementById('cpu').innerHTML = "CPU Usage: " + data.cpuUsage;
    // Update temperature chart
    temperatureChartInstance.data.labels.push(new Date().toLocaleTimeString());
    temperatureChartInstance.data.datasets[0].data.push(data.temperature);
    temperatureChartInstance.update();
    // Update CPU usage chart
    cpuUsageChartInstance.data.labels.push(new Date().toLocaleTimeString());
    cpuUsageChartInstance.data.datasets[0].data.push(data.cpuUsage);
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


updateCharts();
setInterval(updateCharts, 1000);



// Dark mode toggle logic
const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;
const deviceInfoDiv = document.getElementById('deviceInfoDiv');
const chartsDiv = document.getElementById('chartsDiv');
const netInfoDiv = document.getElementById('netInfoDiv');
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
        

        // Update body style and class based on dark mode status
        if (data.settings.darkmode) {
            body.classList.add('bg-secondary');
            deviceInfoDiv.classList.add('bg-secondary');
            body.classList.add('dark-mode');
            chartsDiv.classList.add('text-white')
            netInfoDiv.classList.add('bg-secondary');

        } else {
            deviceInfoDiv.classList.remove('bg-secondary');
            body.classList.remove('bg-secondary');
            body.classList.remove('dark-mode');
            chartsDiv.classList.remove('text-white')
            netInfoDiv.classList.add('bg-secondary');
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
        const isDarkMode = body.classList.contains('bg-secondary');

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
        
        // Update styles after toggling
        updateDarkModeStyles();
    } catch (error) {
        console.error('Error toggling dark mode:', error);
    }
});





// Function to fetch and update the encryption data for the pie chart
async function updateNetworkInfo() {
    
    const response = await fetch('/networks');
    const data = await response.json();

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

}

// Initial call to update the chart and set interval for updates
updateNetworkInfo();
setInterval(updateNetworkInfo, 6000); // Update every 6 seconds





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
