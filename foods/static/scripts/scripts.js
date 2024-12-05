// Basic interactivity for the Food Calorie Finder app

document.addEventListener("DOMContentLoaded", () => {
    // Toggle form sections based on input
    const goalInputs = document.querySelectorAll('input[name="goal"]');
    const activitySelect = document.querySelector('select[name="activity"]');

    goalInputs.forEach(input => {
        input.addEventListener("change", () => {
            console.log(`Goal selected: ${input.value}`);
        });
    });

    activitySelect.addEventListener("change", () => {
        console.log(`Activity level selected: ${activitySelect.value}`);
    });

    const recommendationForm = document.querySelector('form');
    if (recommendationForm) {
        recommendationForm.addEventListener("submit", event => {
            alert("Form submitted! Generating recommendations...");
        });
    }
});
    