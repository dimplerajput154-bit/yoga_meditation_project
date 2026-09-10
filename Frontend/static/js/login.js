const API_URL = "http://127.0.0.1:5001";

// =========================================================
// Show Login
// =========================================================

function showLogin() {

document.getElementById("loginBox").classList.remove("hidden");
document.getElementById("registerBox").classList.add("hidden");

document.getElementById("loginTab").classList.add("active");
document.getElementById("registerTab").classList.remove("active");

clearMessages();

}

// =========================================================
// Show Register
// =========================================================

function showRegister() {

document.getElementById("registerBox").classList.remove("hidden");
document.getElementById("loginBox").classList.add("hidden");

document.getElementById("registerTab").classList.add("active");
document.getElementById("loginTab").classList.remove("active");

clearMessages();

}

// =========================================================
// Clear Messages
// =========================================================

function clearMessages() {

document.getElementById("loginMessage").textContent = "";
document.getElementById("registerMessage").textContent = "";

document.getElementById("loginMessage").className = "message";
document.getElementById("registerMessage").className = "message";

}

// =========================================================
// Toggle Password
// =========================================================

function togglePassword(inputId, icon) {

const input = document.getElementById(inputId);

if (input.type === "password") {

    input.type = "text";

    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");

} else {

    input.type = "password";

    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
}

}

// =========================================================
// Registration
// =========================================================

async function registerUser(event) {

event.preventDefault();

const name =
    document.getElementById("registerName").value.trim();

const email =
    document.getElementById("registerEmail").value.trim();

const password =
    document.getElementById("registerPassword").value;


const message =
    document.getElementById("registerMessage");


message.textContent = "Creating account...";
message.className = "message";


try {

    const response = await fetch(
        '${API_URL}/register,'
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            credentials: "include",

            body: JSON.stringify({

                full_name: name,

                email: email,

                password: password

            })
        }
    );


    const data = await response.json();


    if (response.ok) {

        message.textContent =
            "Registration successful! Please login.";

        message.className =
            "message success";


        document.getElementById("registerName").value = "";
        document.getElementById("registerEmail").value = "";
        document.getElementById("registerPassword").value = "";


        setTimeout(() => {

            document.getElementById("loginEmail").value = email;

            showLogin();

        }, 1200);


    } else {

        message.textContent =
            data.message || "Registration failed.";

        message.className =
            "message error";
    }


} catch (error) {

    console.error(error);

    message.textContent =
        "Cannot connect to backend. Start Login.py first.";

    message.className =
        "message error";
}

}

// =========================================================
// Login
// =========================================================

async function loginUser(event) {

event.preventDefault();

const email =
    document.getElementById("loginEmail").value.trim();

const password =
    document.getElementById("loginPassword").value;


const message =
    document.getElementById("loginMessage");


message.textContent = "Logging in...";
message.className = "message";


try {

    const response = await fetch(
        '${API_URL}/login,'
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            credentials: "include",

            body: JSON.stringify({

                email: email,

                password: password

            })
        }
    );


    const data = await response.json();


    if (response.ok) {

        message.textContent =
            "Login successful!";

        message.className =
            "message success";


        localStorage.setItem(
            "user",
            JSON.stringify(data.user)
        );


        setTimeout(() => {

            alert(
                "Welcome " +
                data.user.name +
                "!"
            );

        }, 500);


    } else {

        message.textContent =
            data.message || "Login failed.";

        message.className =
            "message error";
    }


} catch (error) {

    console.error(error);

    message.textContent =
        "Cannot connect to backend. Start Login.py first.";

    message.className =
        "message error";
}

}