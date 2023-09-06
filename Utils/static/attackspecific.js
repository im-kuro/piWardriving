

// Dark mode toggle logic
const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;

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

            darkmodeValue = true;
        } else {
            topDiv.classList.remove('text-white');
            body.classList.remove('bg-secondary');

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