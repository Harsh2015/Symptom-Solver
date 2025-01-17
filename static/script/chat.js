// Get the necessary DOM elements for the chat functionality
const chatForm = document.getElementById('chatForm');
const chatMessages = document.getElementById('chatMessages');
const loadingAnimation = document.getElementById('loadingAnimation');
const responseContainer = document.getElementById('responseContainer');
const responseText = document.getElementById('responseText');

// Listen for the form submit event
chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get the user's input from the prompt field
    const promptInput = document.getElementById('prompt');
    const userMessage = promptInput.value;

    // Display the user's message in the chat window (aligned to the right)
    chatMessages.innerHTML += `
        <div class="flex justify-end">
            <div class="bg-blue-500 text-white p-3 rounded-lg max-w-xs text-sm shadow">
                ${userMessage}
            </div>
        </div>
    `;

    promptInput.value = '';
    loadingAnimation.classList.remove('hidden');
    
    // Send a POST request to the server with the user's prompt
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'prompt': userMessage  // Send the user's message as 'prompt' in the request body
        })
    })
    .then(response => response.json())  // Parse the JSON response from the server
    .then(data => {
        loadingAnimation.classList.add('hidden');
        
        // Display the chatbot's response in the chat window (aligned to the left)
        chatMessages.innerHTML += `
            <div class="flex justify-start">
                <div class="bg-gray-300 text-gray-800 p-3 rounded-lg max-w-xs text-sm shadow">
                    ${data.response}  // The chatbot's response text
                </div>
            </div>
        `;
        
        // Scroll to the bottom of the chat messages to show the latest message
        chatMessages.scrollTop = chatMessages.scrollHeight;
    })
    .catch(error => {
        loadingAnimation.classList.add('hidden');
        alert('Error: ' + error);
    });
});
