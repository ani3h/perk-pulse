document.addEventListener('DOMContentLoaded', function() {
    const users = JSON.parse(localStorage.getItem('users'));
    const loggedInUserIndex = localStorage.getItem('loggedInUserIndex');

    if (loggedInUserIndex !== null && users) {
        const user = users[loggedInUserIndex];
        const cardsAddedElement = document.getElementById('cardsAdded');
        
        if (cardsAddedElement) {
            cardsAddedElement.innerText = `${user.noOfCards || 0}`;
        }
    }
});
