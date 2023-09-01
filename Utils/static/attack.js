
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

// code for dynamic population of interface options and form submission
document.addEventListener('DOMContentLoaded', function () {
    // Populate the interface selection dropdown based on data
    const interfaceSelect = document.getElementById('interfaceSelect');
    // Handle form submission
    const attackSetupForm = document.getElementById('attackSetupForm');
    const startAttackBtn = document.getElementById('startAttackBtn');
    let isWarDrivingStarted = false; // Track the war driving state
    
    attackSetupForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission
        const selectedInterfaceIdx = interfaceSelect.value;
        const selectedInterfaceName = interfaceSelect.options[interfaceSelect.selectedIndex].text; // Get selected option text


        const selectedActionInput = document.querySelector('input[name="attackAction"]:checked');
        if (selectedActionInput === null) {
            alert('Please select an action');
        } else {
            const selectedAction = selectedActionInput.value;
            // Perform AJAX request to start or stop war driving
            try {
                
                if (!isWarDrivingStarted) {
                    startAttackBtn.textContent = 'Starting...';
                    const response = await fetch('/startwardriving', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            interface: selectedInterfaceIdx,
                            interfaceName: selectedInterfaceName,
                            action: selectedAction
                        })
                    });
                    const responseMessage = await response.json();
                    if (responseMessage.message == "noInterfaceSelected"){
                        // If no interface is chosen, show the modal
                        const interfaceModal = new bootstrap.Modal(document.getElementById('interfaceModal'));
                        interfaceModal.show();
                    }else if(responseMessage.status == "error"){
                        // If no interface is chosen, show the modal
                        const interfaceModal = new bootstrap.Modal(document.getElementById('interfaceModal'));

                        const alertContainer = document.getElementById('alertContainer');

                        // Create a new alert element
                        const alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
                        alertDiv.setAttribute('role', 'alert');

                        // Add alert content
                        alertDiv.innerHTML = `
                            <strong>Error:</strong> ${responseMessage.message}<br>
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        `;

                        // Append the alert to the container
                        alertContainer.appendChild(alertDiv);

                        // Scroll to the top where the alert is displayed
                        alertContainer.scrollIntoView();

                        // Automatically close the alert after a certain time (e.g., 5 seconds)
                        setTimeout(() => {
                            alertDiv.remove();
                        }, 10000);
                    }
                    if (response.ok) {
                        startAttackBtn.textContent = 'War Driving Started';
                        startAttackBtn.classList.remove('btn-primary');
                        startAttackBtn.classList.add('btn-danger');
                        isWarDrivingStarted = true; // Update the war driving state
                    } else {
                        startAttackBtn.textContent = 'Error Starting War Driving';
                    }
                } else {
                    startAttackBtn.textContent = 'Stopping...';
                    // Perform AJAX request to stop war driving
                    // Modify the fetch request accordingly
                    const response = await fetch('/startwardriving', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            interface: selectedInterfaceIdx,
                            interfaceName: selectedInterfaceName,
                            action: "terminate"
                        })
                    });
                    
                    if (response.ok) {
                        startAttackBtn.textContent = 'Start War Driving';
                        startAttackBtn.classList.remove('btn-danger');
                        startAttackBtn.classList.add('btn-primary');
                        isWarDrivingStarted = false; // Update the war driving state
                    } else {
                        startAttackBtn.textContent = 'Error Stopping War Driving';
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                startAttackBtn.textContent = 'Error';
            }
        }

        startAttackBtn.disabled = false;
    });
});



// Dark mode toggle logic
const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;
const attackOptions = document.getElementById('attackSetupDiv');
const filterOptionsDiv = document.getElementById('filterOptionsDiv');
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
            body.classList.add('text-white');
            attackOptions.classList.add('bg-secondary');
            attackOptions.classList.add('text-white');
            filterOptionsDiv.classList.add('bg-secondary');
            filterOptionsDiv.classList.add('text-white');
        } else {
            body.classList.remove('bg-secondary');
            body.classList.remove('text-white');
            attackOptions.classList.remove('bg-secondary');
            attackOptions.classList.remove('text-white');
            filterOptionsDiv.classList.remove('bg-secondary');
            filterOptionsDiv.classList.remove('text-white');
        }
    } catch (error) {
        console.error('Error updating dark mode styles:', error);
    }
}

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



// Get references to the form elements
const filterWEP = document.getElementById('filterWEP');
const filterWPA = document.getElementById('filterWPA');
const filterWPA2 = document.getElementById('filterWPA2');
const filterUnknown = document.getElementById('filterUnknown');
const signalStrengthFilter = document.getElementById('signalStrengthFilter');
const alertWEP = document.getElementById('alertWEP');
const alertWPA = document.getElementById('alertWPA');
const alertWPA2 = document.getElementById('alertWPA2');

signalStrengthFilter.addEventListener('input', updateSignalStrength);




// Function to update signal strength filter
async function updateSignalStrength() {
    const signalStrength = parseInt(signalStrengthFilter.value, 10);
    try {
        // Prepare payload for API call
        const optionPayload = {
            call: 'setoption',
            payload: {
                option: "signalStrengthFilter",
                value: signalStrength
            }
        };

        // Make API call to set option status
        const setSettingsResponse = await fetch('/setsettings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(optionPayload)
        });
        const setData = await setSettingsResponse.json();

    } catch (error) {
        console.error('Error setting option:', error);
    }
}


[filterWEP, filterWPA, filterWPA2, filterUnknown, alertWEP, alertWPA, alertWPA2].forEach(element => {
    element.addEventListener('change', async () => {
        try {
            const optionId = element.id;
            const optionValue = element.checked;

            // Prepare payload for API call
            const optionPayload = {
                call: 'setoption',
                payload: {
                    option: optionId,
                    value: optionValue
                }
            };

            // Make API call to set option status
            const setSettingsResponse = await fetch('/setsettings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(optionPayload)
            });
            const setData = await setSettingsResponse.json();
            
        } catch (error) {
            console.error('Error setting option:', error);
        }
    });

});
