// Initialize users array from localStorage or use default if empty
let users = JSON.parse(localStorage.getItem('users')) || [
    { email: "user@example.com", password: "password123", noOfCards: 0, cardDetails: [] },
    { email: "admin@perkpulse.com", password: "adminpass", noOfCards: 0, cardDetails: [] }
];

document.getElementById('signupForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    
    // Clear previous messages
    errorMessage.textContent = "";
    successMessage.textContent = "";
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        errorMessage.textContent = "Please enter a valid email address.";
        return;
    }
    
    // Check if email is already registered
    if (users.some(user => user.email === email)) {
        errorMessage.textContent = "This email is already registered.";
        return;
    }
    
    // Password validation (example: at least 8 characters)
    if (password.length < 8) {
        errorMessage.textContent = "Password must be at least 8 characters long.";
        return;
    }
    
    // Confirm password validation
    if (password !== confirmPassword) {
        errorMessage.textContent = "Passwords do not match.";
        return;
    }
    
    // If all validations pass, create the account
    users.push({ email: email, password: password, noOfCards: 0, cardDetails: [] });
    
    // Save updated users array to localStorage
    localStorage.setItem('users', JSON.stringify(users));
    
    // Display success message
    successMessage.textContent = "Account created successfully! Redirecting to login page...";
    
    // Clear the form
    document.getElementById('signupForm').reset();
    
    // Redirect to login page after a short delay (1 second)
    setTimeout(() => {
        window.location.href = "login.html";
    }, 1000);
});
