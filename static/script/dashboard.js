
// Event listener for symptom form submission to predict disease
document.getElementById('symptom-form').addEventListener('submit', function (event) {
    event.preventDefault();  // Prevent the default form submission behavior

    // Collect symptoms from the form inputs, default to 'No Symptoms' if not provided
    const symptoms = {
        symptom1: document.getElementById('symptom1').value || 'No Symptoms',
        symptom2: document.getElementById('symptom2').value || 'No Symptoms',
        symptom3: document.getElementById('symptom3').value || 'No Symptoms',
        symptom4: document.getElementById('symptom4').value || 'No Symptoms',
        symptom5: document.getElementById('symptom5').value || 'No Symptoms',
        symptom6: document.getElementById('symptom6').value || 'No Symptoms'
    };

    // Ensure all symptoms are selected, otherwise show an alert and prevent submission
    for (let i = 1; i <= 6; i++) {
        if (!document.getElementById(`symptom${i}`).value) {
            alert(`Please select symptom ${i}.`);
            return;
        }
    }

    // Show loading message while waiting for prediction
    document.getElementById('prediction-result').innerHTML = '<p>Loading...</p>';

    // Make a POST request to the server with the symptoms
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(symptoms)
    })
    .then(response => response.json())  // Parse the JSON response from the server
    .then(data => {
        if (data.disease) {
            // If the disease is predicted, display the result
            document.getElementById('prediction-result').innerHTML = `
            <h3><span style="color: black;">You Might Be Suffering From </span><span style="color: red; font-weight: bold;">${data.disease}</span></h3>
            `;
        } else {
            // If no disease is predicted, show an error message
            document.getElementById('prediction-result').innerHTML = `
                <p>Error: Unable to predict disease. Please check the symptoms entered.</p>
            `;
        }
    })
    .catch(error => {
        // If there's an error in the request, show an error message
        document.getElementById('prediction-result').innerHTML = `
            <p>Error: Could not reach the server. Please try again later.</p>
        `;
        console.error("Error in the fetch request:", error);
    });
});

// Event listener for showing antibiotics information based on selected disease
document.getElementById("show-antibiotics-btn").addEventListener("click", function() {
    const selectedDisease = document.getElementById("disease-select").value;
    const antibioticsResult = document.getElementById("antibiotics-result");
    const antibioticsTable = document.getElementById("antibiotics-table");

    // Clear any existing table rows and prepare for new data
    antibioticsTable.innerHTML = `
        <tr>
            <th>Attribute</th>
            <th>Details</th>
        </tr>
    `;

    // If a disease is selected, fetch the antibiotics information
    if (selectedDisease) {
        antibioticsResult.style.display = "block";
        disclaimer.style.display = "block";

        // Make a POST request to fetch antibiotics information based on the selected disease
        fetch('/get_antibiotics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'Disease': selectedDisease })
        })
        .then(response => response.json())  // Parse the JSON response
        .then(data => {
            if (data.success) {
                // If the data is successful, populate the antibiotics table with the details
                const antibioticData = data.data;
                for (const [attribute, value] of Object.entries(antibioticData)) {
                    const row = antibioticsTable.insertRow();
                    const cell1 = row.insertCell(0);  
                    const cell2 = row.insertCell(1);
                    cell1.textContent = attribute;
                    cell2.textContent = value;
                }
            } else {
                // If there's an error, display the error message in the table
                antibioticsTable.innerHTML = `
                    <tr>
                        <td colspan="2">${data.error}</td>
                    </tr>
                `;
            }
        })
        .catch(error => {
            // If there's an error while fetching the data, display a generic error message
            antibioticsTable.innerHTML = `
                <tr>
                    <td colspan="2">An error occurred while fetching data.</td>
                </tr>
            `;
        });
    } else {
        // If no disease is selected, hide the antibiotics result and prompt the user to select a disease
        antibioticsResult.style.display = "none";
        alert("Please select a disease to see antibiotics information.");
    }
});
