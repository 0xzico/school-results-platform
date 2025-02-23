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
