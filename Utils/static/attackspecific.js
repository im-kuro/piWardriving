

// Dark mode toggle logic
const darkModeToggle = document.getElementById('darkModeToggle');
const maindiv = document.getElementById('mainDiv');
const body = document.body;

// Function to update dark mode styles based on API response
async function updateDarkModeStyles() {
    try {

        // Make API call to check if dark mode is enabled
        const response = await fetch('/eventhandler', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({event: "getsettings"})
        });
        const data = await response.json();
        

        // Update body style and class based on dark mode status
        if (data.settings.darkmode) {
            body.classList.add('bg-secondary');
            body.classList.add('dark-mode');
            maindiv.classList.add('text-white');   

        } else {
            body.classList.remove('bg-secondary');
            body.classList.remove('dark-mode');
            maindiv.classList.remove('text-white');         
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
            payload: !isDarkMode,
            event: "setsettings"
        };

        // Make API call to set dark mode status
        const setSettingsResponse = await fetch('/eventhandler', {
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

            // Make API call using fetch
            fetch('/eventhandler', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                interfaceIdx: selectedInterfaceIdx,
                interfaceName: selectedInterfaceName,
                event: "setinterface"
            })
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
