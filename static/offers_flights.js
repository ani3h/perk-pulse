document.addEventListener('DOMContentLoaded', function () {
    const predictionButton = document.querySelector('.ai-recommendation');

    predictionButton.addEventListener('click', function () {
        // Retrieve the credit cards from local storage
        let creditCards = JSON.parse(localStorage.getItem('credit_cards')) || [];

        // Ensure there are credit cards to send
        if (creditCards.length === 0) {
            alert('No credit cards available for prediction.');
            return;
        }

        // Prepare the data to send in the request
        const requestData = {
            type: 'flight',  // Set the type to "flight"
            credit_cards: creditCards
        };

        // Send the POST request to the Flask server
        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                displayPredictions(data.predictions);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while making the prediction.');
        });
    });

    function displayPredictions(predictions) {
        // Clear existing predictions
        const container = document.querySelector('.container');
        container.innerHTML = '';

        // Display new predictions
        predictions.forEach(prediction => {
            const predictionElement = document.createElement('div');
            predictionElement.classList.add('prediction');
            predictionElement.innerHTML = `
                <div class="save">${prediction.savings}</div>
                <div class="using-hdfc-card">${prediction.offer_details}</div>
            `;
            container.appendChild(predictionElement);
        });
    }
});
