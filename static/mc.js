let creditCards = [];

document.addEventListener('DOMContentLoaded', function() {
    const users = JSON.parse(localStorage.getItem('users'));
    const loggedInUserIndex = localStorage.getItem('loggedInUserIndex');

    if (loggedInUserIndex !== null && users) {
        const user = users[loggedInUserIndex];
        creditCards = user.cardDetails || [];
        renderCreditCards();
    }
});

function renderCreditCards() {
    const creditCardList = document.getElementById('creditCardList');
    creditCardList.innerHTML = '';

    creditCards.forEach((card, index) => {
        const li = document.createElement('li');
        li.innerHTML = `
            <span><span class="card-icon">💳</span> ${card.name} [${card.number}]</span>
            <span class="delete-icon" onclick="deleteCard(${index})"><img src="../templates/assets/vectors/minus.svg"></span>
        `;
        creditCardList.appendChild(li);
    });

    // Move the "Add New Card" button after rendering the cards
    const addNewButton = document.getElementById('add-new-button');
    creditCardList.parentNode.insertBefore(addNewButton, creditCardList.nextSibling);
}

function deleteCard(index) {
    creditCards.splice(index, 1);
    updateLocalStorage();
    renderCreditCards();
}

function toggleAddNewForm() {
    const addNewForm = document.getElementById('group1');
    addNewForm.classList.toggle('open-Add');
}

function addNewCard() {
    const newCardName = document.getElementById('newCardName').value;
    const newCardNumber = document.getElementById('newCardNumber').value;

    if (newCardName && newCardNumber) {
        creditCards.unshift({ name: newCardName, number: newCardNumber });
        updateLocalStorage();
        renderCreditCards();
        toggleAddNewForm();

        document.getElementById('newCardName').value = '';
        document.getElementById('newCardNumber').value = '';
    } else {
        alert('Please enter both card name and number.');
    }
}

function updateLocalStorage() {
    const users = JSON.parse(localStorage.getItem('users'));
    const loggedInUserIndex = localStorage.getItem('loggedInUserIndex');
    
    if (loggedInUserIndex !== null && users) {
        users[loggedInUserIndex].noOfCards = creditCards.length;
        users[loggedInUserIndex].cardDetails = creditCards;
        localStorage.setItem('users', JSON.stringify(users));
    }
}

renderCreditCards();