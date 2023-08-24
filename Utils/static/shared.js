

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



// Function to fetch and update the encryption data for the pie chart
async function updateNetworkCharts() {
    
    const response = await fetch('/networks');
    const data = await response.json();
    if (data.message == "noInterfaceSelected"){
        // If no interface is chosen, show the modal
        const interfaceModal = new bootstrap.Modal(document.getElementById('interfaceModal'));
        interfaceModal.show();
    }
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
updateNetworkCharts();
setInterval(updateNetworkCharts, 6000); // Update every 6 seconds





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
