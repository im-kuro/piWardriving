

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
        ;

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







