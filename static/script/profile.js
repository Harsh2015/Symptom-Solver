// Wait until the DOM is fully loaded before executing the script
document.addEventListener('DOMContentLoaded', function () {

    // Get references to the HTML elements (age, location fields, edit button, and save button)
    const ageField = document.getElementById('age');
    const locationField = document.getElementById('location');
    const editButton = document.getElementById('editButton');
    const saveButton = document.getElementById('saveButton');
  
    // Initially, disable the age and location fields, and the save button
    ageField.disabled = true;
    locationField.disabled = true;
    saveButton.disabled = true;
  
    // Event listener when the edit button is clicked
    editButton.addEventListener('click', function () {
        // Enable the age and location fields and the save button when the edit button is clicked
        ageField.disabled = false;
        locationField.disabled = false;
        saveButton.disabled = false;
    });
  
    // Event listener for when the save button is clicked
    saveButton.addEventListener('click', function () {
        // Get the values entered in the age and location fields
        const age = ageField.value;
        const location = locationField.value;
  
        // Send the updated age and location to the server via a POST request
        fetch('/update-profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ age, location }),  // Send the data in the request body as JSON
        })
            .then(response => response.json())  // Parse the JSON response from the server
            .then(data => {
                // If the profile update was successful, disable the fields again and show a success message
                if (data.status === 'success') {
                    alert(data.message);
  
                    // Disable the fields and save button after saving
                    ageField.disabled = true;
                    locationField.disabled = true;
                    saveButton.disabled = true;
                } else {
                    // If there was an error, show an alert with the error message
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                // If there’s an error with the fetch request, log the error and show an alert
                console.error('Error:', error);
                alert('An error occurred while updating the profile.');
            });
    });
});
