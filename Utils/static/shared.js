

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
        }
    }

});


// Dark mode toggle logic
const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;

darkModeToggle.addEventListener('click', async () => {
    console.log('Dark mode toggle clicked');
    // Get current dark mode status
    const isDarkMode = body.classList.contains('dark-mode');
    // Update body style and class based on dark mode status
    if (!isDarkMode) {
        body.style.backgroundColor = 'grey';
        body.classList.add('dark-mode');
    } else {
        body.style.backgroundColor = '';
        body.classList.remove('dark-mode');
    }
    // Prepare payload for API call
    const darkModePayload = {
        call: 'darkmode',
        payload: !isDarkMode
    };
    // Make API call to set dark mode status
    try {
        const response = await fetch('/setSettings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(darkModePayload)
        });
        const data = await response.json();
        console.log('Dark mode API response:', data);
    } catch (error) {
        console.error('Error setting dark mode:', error);
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
setInterval(updateCharts, 2000);









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
