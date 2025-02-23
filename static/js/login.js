// Toggle Password Visibility
function togglePassword() {
    let passwordField = document.getElementById("password");
    let toggleIcon = document.querySelector(".toggle-password");

    if (passwordField.type === "password") {
        passwordField.type = "text";
        toggleIcon.innerText = "🔒"; // Change icon when password is visible
    } else {
        passwordField.type = "password";
        toggleIcon.innerText = "👁"; // Change icon back when hidden
    }
}


// Remember Me (Optional: Store email in localStorage)
document.addEventListener("DOMContentLoaded", function() {
    let emailInput = document.getElementById("email");
    let rememberMeCheckbox = document.querySelector("input[name='remember']");

    // Load saved email
    if (localStorage.getItem("rememberedEmail")) {
        emailInput.value = localStorage.getItem("rememberedEmail");
        rememberMeCheckbox.checked = true;
    }

    // Save email on form submission
    document.querySelector("form").addEventListener("submit", function() {
        if (rememberMeCheckbox.checked) {
            localStorage.setItem("rememberedEmail", emailInput.value);
        } else {
            localStorage.removeItem("rememberedEmail");
        }
    });
});
