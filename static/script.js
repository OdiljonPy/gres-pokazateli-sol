document.addEventListener("DOMContentLoaded", () => {
    const updateContainer = document.getElementById("update-container");

    const fetchUpdates = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/get_updates/");
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            updateContainer.innerHTML = JSON.stringify(data, null, 2); // Format and display JSON data
            console.log("ok")

        } catch (error) {
            console.error('Error fetching updates:', error);
        }
    };

    // Fetch updates every 2 seconds
    setInterval(fetchUpdates, 2000);
});
