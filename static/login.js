// Initialize users array from localStorage or use default if empty
const users = JSON.parse(localStorage.getItem('users')) || [
    { email: "user@example.com", password: "password123", noOfCards: 0, cardDetails: [] },
    { email: "admin@perkpulse.com", password: "adminpass", noOfCards: 0, cardDetails: [] }
];

document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        errorMessage.textContent = "Please enter a valid email address.";
        errorMessage.style.display = "block";
        return;
    }
    
    // Password validation (example: at least 8 characters)
    if (password.length < 8) {
        errorMessage.textContent = "Password must be at least 8 characters long.";
        errorMessage.style.display = "block";
        return;
    }
    
    // Check credentials
    const user = users.find(u => u.email === email && u.password === password);
    
    if (user) {
        // Store the index of the logged-in user for later reference
        const userIndex = users.findIndex(u => u.email === email && u.password === password);
        localStorage.setItem('loggedInUserIndex', userIndex);
        
        // Successful login
        window.location.href = "main.html";
    } else {
        // Failed login
        errorMessage.textContent = "Invalid email or password.";
        errorMessage.style.display = "block";
    }
});
