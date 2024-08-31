document.addEventListener('DOMContentLoaded', function () {
    const predictionButton = document.querySelector('.ai-recommendation');

    predictionButton.addEventListener('click', function () {
        // Retrieve the logged-in user’s credit cards from local storage
        const users = JSON.parse(localStorage.getItem('users'));
        const loggedInUserIndex = localStorage.getItem('loggedInUserIndex');

        let creditCards = [];
        if (loggedInUserIndex !== null && users) {
            creditCards = users[loggedInUserIndex].cardDetails || [];
        }

        console.log("Retrieved credit cards from local storage:", creditCards);

        // Check if creditCards is null or not an array
        if (!Array.isArray(creditCards)) {
            console.error("Credit cards retrieved from local storage is not an array or is null.");
            alert('No credit cards available for prediction.');
            return;
        }

        // Ensure there are credit cards to send
        if (creditCards.length === 0) {
            console.warn("Credit cards array is empty.");
            alert('No credit cards available for prediction.');
            return;
        }

        // Prepare the data to send in the request
        const requestData = {
            type: 'movie',
            credit_cards: creditCards
        };

        console.log("Sending request data to server:", requestData);

        // Send the POST request to the Flask server
        fetch('http://127.0.0.1:5000/predict', {  // Updated URL to point to Flask server
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            console.log("Received response from server:", data);
            if (data.error) {
                displayPredictions([{ card: 'Error', offer: data.error, score: 0 }]); // Display error message on the page
            } else {
                displayPredictions(data.predictions);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            displayPredictions([{ card: 'Error', offer: 'An error occurred while making the prediction.', score: 0 }]); // Display error message on the page
        });
    });

    function displayPredictions(predictions) {
        const predictionsContainer = document.getElementById('predictions-container');
        predictionsContainer.innerHTML = '';  // Clear only the predictions container
        
        // Sort predictions by score in descending order (if needed)
        predictions.sort((a, b) => b.score - a.score);
    
        predictions.forEach((prediction) => {
            const predictionElement = document.createElement('div');
            predictionElement.classList.add('offer-box');
        
            // Check if the offer is null or empty
            if (!prediction.offer || prediction.offer.trim() === '') {
                prediction.offer = 'No offer available';
            }
    
            predictionElement.innerHTML = `
                <div class="offer-text">${prediction.offer}</div>
                <div class="card-name">${prediction.card}</div>
            `;
            predictionsContainer.appendChild(predictionElement);
        });
    }
});
