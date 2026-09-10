const API_URL = "http://127.0.0.1:5002";

const userIdInput = document.getElementById("userId");
const fullNameInput = document.getElementById("fullName");
const emailInput = document.getElementById("email");
const roleInput = document.getElementById("role");
const profileImageInput = document.getElementById("profileImage");
const accountStatusInput = document.getElementById("accountStatus");

const message = document.getElementById("message");

const loadBtn = document.getElementById("loadBtn");
const profileForm = document.getElementById("profileForm");


// =========================================================
// Show Message
// =========================================================

function showMessage(text, type) {

    message.textContent = text;

    message.className = "message " + type;
}


// =========================================================
// Load Profile
// =========================================================

async function loadProfile() {

    const userId = userIdInput.value;

    showMessage("Loading profile...", "success");

    try {

        const response = await fetch(
            ${API_URL}/api/profile/${userId}
        );

        const data = await response.json();


        if (!response.ok) {

            showMessage(
                data.message || "Unable to load profile.",
                "error"
            );

            return;
        }


        const profile = data.profile;


        fullNameInput.value =
            profile.full_name || "";

        emailInput.value =
            profile.email || "";

        roleInput.value =
            profile.role || "";

        profileImageInput.value =
            profile.profile_image || "";


        accountStatusInput.value =
            profile.is_active == 1
                ? "Active"
                : "Inactive";


        showMessage(
            "Profile loaded successfully.",
            "success"
        );

    }
    catch (error) {

        console.error(error);

        showMessage(
            "Cannot connect to Profile Server.",
            "error"
        );
    }
}


// =========================================================
// Update Profile
// =========================================================

profileForm.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();


        const userId = userIdInput.value;

        const fullName = fullNameInput.value.trim();

        const email = emailInput.value.trim();

        const profileImage =
            profileImageInput.value.trim();


        if (!fullName || !email) {

            showMessage(
                "Full name and email are required.",
                "error"
            );

            return;
        }


        showMessage(
            "Updating profile...",
            "success"
        );


        try {

            const response = await fetch(
                ${API_URL}/api/profile/${userId},
                {
                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        full_name: fullName,

                        email: email,

                        profile_image:
                            profileImage

                    })
                }
            );


            const data =
                await response.json();


            if (!response.ok) {

                showMessage(
                    data.message ||
                    "Unable to update profile.",
                    "error"
                );

                return;
            }


            showMessage(
                "Profile updated successfully.",
                "success"
            );


            loadProfile();

        }
        catch (error) {

            console.error(error);

            showMessage(
                "Cannot connect to Profile Server.",
                "error"
            );
        }

    }
);


// =========================================================
// Load Button
// =========================================================

loadBtn.addEventListener(
    "click",
    loadProfile
);


// =========================================================
// Load Profile Automatically
// =========================================================

window.addEventListener(
    "DOMContentLoaded",
    loadProfile
);