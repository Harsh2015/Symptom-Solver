document.addEventListener("DOMContentLoaded", function () {
    const diseaseSelect = document.getElementById("disease-select");
    const testListDiv = document.getElementById("test-list");
    const recommendationsDiv = document.getElementById("recommendations");

    // Fetch diseases for dropdown
    fetch('/get_diseases')
        .then(response => response.json())
        .then(data => {
            console.log("Fetched Diseases:", data);
            diseaseSelect.innerHTML = '<option value="">Select a disease</option>'; // Default option
            if (data.diseases && Array.isArray(data.diseases)) {
                data.diseases.forEach(disease => {
                    const option = document.createElement("option");
                    option.value = disease;
                    option.textContent = disease;
                    diseaseSelect.appendChild(option);
                });
            } else {
                console.error("Error: Diseases data is not in expected format", data);
            }
        })
        .catch(error => console.error("Error fetching diseases:", error));

    // Fetch and display tests + recommendations when disease is selected
    diseaseSelect.addEventListener("change", function () {
        const selectedDisease = diseaseSelect.value;

        if (!selectedDisease) {
            testListDiv.innerHTML = "";
            recommendationsDiv.innerHTML = "<p>Please select a disease to see recommendations.</p>";
            return;
        }

        fetch('/get_tests', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 'Disease': selectedDisease })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Received Data:", data);
            testListDiv.innerHTML = ""; // Clear previous results
            recommendationsDiv.innerHTML = ""; // Clear previous recommendations

            /** Display Test List **/
            if (data.tests && Array.isArray(data.tests) && data.tests.length > 0) {
                testListDiv.innerHTML = `
                    <h2 style="color: #007BFF;">Suggested Tests for ${selectedDisease}</h2>
                    <p><strong>Outcome:</strong> ${data.outcome || "No outcome available."}</p>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid #ddd;">
                        <tr style="background-color: #f2f2f2;">
                            <th style="border: 1px solid #ddd; padding: 10px;">Test Name</th>
                            <th style="border: 1px solid #ddd; padding: 10px;">Definition</th>
                        </tr>
                        ${data.tests.map(test => `
                            <tr>
                                <td style="border: 1px solid #ddd; padding: 10px;">${test}</td>
                                <td style="border: 1px solid #ddd; padding: 10px;">
                                    ${data.definition && data.definition[test] ? data.definition[test] : "No definition available."}
                                </td>
                            </tr>
                        `).join("")}
                    </table>
                `;
            } else {
                testListDiv.innerHTML = "<p>No tests available for this disease.</p>";
            }

            /** Display Diet & Lifestyle Recommendations **/
            if (data.recommendations) {
                recommendationsDiv.innerHTML = `
                    <h2 style="color: #28A745;">Diet & Lifestyle Tips for ${selectedDisease}</h2>
                    <p><strong>Foods to Eat:</strong> ${data.recommendations.foods_to_eat?.length ? data.recommendations.foods_to_eat.join(", ") : "No recommendations available."}</p>
                    <p><strong>Foods to Avoid:</strong> ${data.recommendations.foods_to_avoid?.length ? data.recommendations.foods_to_avoid.join(", ") : "No recommendations available."}</p>
                    <p><strong>Lifestyle Tips:</strong> ${data.recommendations.lifestyle_tips?.length ? data.recommendations.lifestyle_tips.join(", ") : "No recommendations available."}</p>
                `;
            } else {
                recommendationsDiv.innerHTML = "<p>No recommendations available.</p>";
            }
        })
        .catch(error => {
            console.error("Error fetching test & recommendations data:", error);
            testListDiv.innerHTML = "<p>Error fetching data. Please try again.</p>";
            recommendationsDiv.innerHTML = "<p>Error fetching recommendations.</p>";
        });
    });
});
