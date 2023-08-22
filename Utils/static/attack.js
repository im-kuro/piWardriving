
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



// JavaScript code for dynamic population of interface options and form submission
document.addEventListener('DOMContentLoaded', function () {
    // Populate the interface selection dropdown based on data
    const interfaceSelect = document.getElementById('interfaceSelect');

    // Handle form submission
    const attackSetupForm = document.getElementById('attackSetupForm');
    const startAttackBtn = document.getElementById('startAttackBtn');
    
    attackSetupForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const interfaceValue = interfaceSelect.value;
        const selectedAction = document.querySelector('input[name="attackAction"]:checked').value;
        
        // Perform AJAX request to start war driving
        try {
            startAttackBtn.disabled = true;
            startAttackBtn.textContent = 'Starting...';
            const response = await fetch('/startwardriving', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    interface: interfaceValue,
                    action: selectedAction
                })
            });
            
            if (response.ok) {
                startAttackBtn.textContent = 'War Driving Started';
                startAttackBtn.classList.remove('btn-primary');
                startAttackBtn.classList.add('btn-danger');
            } else {
                startAttackBtn.textContent = 'Error Starting War Driving';
            }
        } catch (error) {
            console.error('Error starting war driving:', error);
            startAttackBtn.textContent = 'Error Starting War Driving';
        }
        
        startAttackBtn.disabled = false;
    });
});
