// Wait until the DOM is fully loaded before running the script
document.addEventListener("DOMContentLoaded", function() {
    const accordionItems = document.querySelectorAll('.accordion .card-header button');
    
    // Loop through each accordion button
    accordionItems.forEach(item => {
        item.addEventListener('click', function() {

            // Find the currently active (opened) accordion item
            const currentActive = document.querySelector('.accordion .collapse.show');

            // Get the target content of the clicked button (the corresponding content to open)
            const targetContent = item.getAttribute('data-target');
            
            // If there is an active accordion item, and it's not the one clicked, close it
            if (currentActive && currentActive !== document.querySelector(targetContent)) {
                
                // Hide the currently active content
                currentActive.classList.remove('show');  
            }
        });
    });
});

// Add a click event listener to all accordion buttons
document.querySelectorAll('.accordion button').forEach(button => {
    button.addEventListener('click', function() {

        // After a short delay (300ms), scroll the clicked accordion's content into view smoothly
        setTimeout(function() {
            
            // Get the content that corresponds to the clicked button using its data-target attribute
            const target = document.querySelector(button.getAttribute('data-target'));
            
            // Scroll the target content into view with smooth scrolling
            target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);  // 300ms delay to ensure the accordion transition finishes before scrolling
    });
});
