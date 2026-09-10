
/* =====================================================
   HEALTH PROFILE JAVASCRIPT
   Backend API:
   GET  /health-profile
   POST /health-profile
   PUT  /health-profile
   ===================================================== */


const API_URL = "/health-profile";


const form =
    document.getElementById("healthForm");

const saveBtn =
    document.getElementById("saveBtn");

const messageBox =
    document.getElementById("messageBox");

const statusPill =
    document.getElementById("statusPill");

const lastUpdated =
    document.getElementById("lastUpdated");


let profileExists = false;


/*
=========================================================
Function Name: showMessage

Description:
Displays success or error message to the user.

Input:
message - Message text
isError - true for error, false for success

Output:
None
=========================================================
*/

function showMessage(message, isError = false) {

    messageBox.textContent = message;

    messageBox.classList.remove(
        "hidden",
        "error"
    );


    if (isError) {

        messageBox.classList.add("error");

    }

}


/*
=========================================================
Function Name: clearMessages

Description:
Clears previous messages and validation errors.

Input:
None

Output:
None
=========================================================
*/

function clearMessages() {

    messageBox.classList.add("hidden");

    messageBox.textContent = "";


    document
        .querySelectorAll(".error")
        .forEach(error => {

            error.textContent = "";

        });

}


/*
=========================================================
Function Name: getFormData

Description:
Collects health profile values from the form.

Input:
Form field values

Output:
Object containing backend-compatible health data
=========================================================
*/

function getFormData() {

    return {

        age:
            document.getElementById("age").value || "",

        gender:
            document.getElementById("gender").value || "",

        height_cm:
            document.getElementById("height_cm").value || "",

        weight_kg:
            document.getElementById("weight_kg").value || "",

        activity_level:
            document.getElementById(
                "activity_level"
            ).value || "",

        diet_preference:
            document.getElementById(
                "diet_preference"
            ).value || "",

        allergies:
            document.getElementById(
                "allergies"
            ).value || "",

        existing_conditions:
            document.getElementById(
                "existing_conditions"
            ).value || ""

    };

}


/*
=========================================================
Function Name: fillForm

Description:
Displays database health profile data in the form.

Input:
Profile object returned by backend

Output:
None
=========================================================
*/

function fillForm(profile) {

    document.getElementById("age").value =
        profile.age ?? "";


    document.getElementById("gender").value =
        profile.gender ?? "";


    document.getElementById("height_cm").value =
        profile.height_cm ?? "";


    document.getElementById("weight_kg").value =
        profile.weight_kg ?? "";


    document.getElementById("activity_level").value =
        profile.activity_level ?? "sedentary";


    document.getElementById("diet_preference").value =
        profile.diet_preference ?? "";


    document.getElementById("allergies").value =
        profile.allergies ?? "";


    document.getElementById(
        "existing_conditions"
    ).value =
        profile.existing_conditions ?? "";


    updateBMI();


    if (profile.updated_at) {

        lastUpdated.textContent =
            "Last updated: " +
            profile.updated_at;

    }

}


/*
=========================================================
Function Name: displayValidationErrors

Description:
Displays validation errors returned by backend.

Input:
errors - Backend validation error object

Output:
None
=========================================================
*/

function displayValidationErrors(errors) {

    Object.entries(errors || {})
        .forEach(([field, message]) => {

            const errorElement =
                document.getElementById(
                    `${field}Error`
                );


            if (errorElement) {

                errorElement.textContent =
                    message;

            }

        });

}


/*
=========================================================
Function Name: calculateBMI

Description:
Calculates BMI using height and weight.

Input:
height_cm - Height in centimeters
weight_kg - Weight in kilograms

Output:
BMI value or null
=========================================================
*/

function calculateBMI(
    height_cm,
    weight_kg
) {

    const height =
        Number(height_cm);

    const weight =
        Number(weight_kg);


    if (
        !height ||
        !weight ||
        height <= 0 ||
        weight <= 0
    ) {

        return null;

    }


    const heightMeters =
        height / 100;


    return (
        weight /
        (heightMeters * heightMeters)
    );

}


/*
=========================================================
Function Name: getBMILabel

Description:
Returns BMI category.

Input:
bmi - BMI value

Output:
BMI category
=========================================================
*/

function getBMILabel(bmi) {

    if (bmi < 18.5) {

        return "Underweight";

    }

    if (bmi < 25) {

        return "Normal";

    }

    if (bmi < 30) {

        return "Overweight";

    }

    return "Obesity";

}


/*
=========================================================
Function Name: updateBMI

Description:
Updates BMI displayed on the page.

Input:
Current height and weight

Output:
None
=========================================================
*/

function updateBMI() {

    const bmi =
        calculateBMI(

            document.getElementById(
                "height_cm"
            ).value,

            document.getElementById(
                "weight_kg"
            ).value

        );


    const bmiValue =
        document.getElementById(
            "bmiValue"
        );


    const bmiLabel =
        document.getElementById(
            "bmiLabel"
        );


    const sideBmi =
        document.getElementById(
            "sideBmi"
        );


    if (bmi === null) {

        bmiValue.textContent = "--";

        bmiLabel.textContent =
            "Enter height & weight";

        sideBmi.textContent = "--";

        return;

    }


    const rounded =
        bmi.toFixed(1);


    bmiValue.textContent =
        rounded;


    bmiLabel.textContent =
        getBMILabel(bmi);


    sideBmi.textContent =
        rounded;

}


/*
=========================================================
Function Name: loadHealthProfile

Description:
Fetches logged-in user's health profile
from Flask backend.

Input:
None

Output:
Loads profile data into form
=========================================================
*/

async function loadHealthProfile() {

    try {

        statusPill.textContent =
            "Loading...";


        const response =
            await fetch(
                API_URL,
                {
                    method: "GET",

                    credentials:
                        "same-origin"
                }
            );


        const result =
            await response.json();


        /*
        USER NOT LOGGED IN
        */

        if (response.status === 401) {

            statusPill.textContent =
                "Login required";


            showMessage(
                result.message ||
                "Please login first.",
                true
            );

            return;

        }


        /*
        OTHER BACKEND ERROR
        */

        if (
            !response.ok ||
            !result.success
        ) {

            statusPill.textContent =
                "Error";


            showMessage(
                result.message ||
                "Unable to load profile.",
                true
            );

            return;

        }


        /*
        PROFILE EXISTS
        */

        profileExists =
            result.profile_exists === true;


        if (
            profileExists &&
            result.profile
        ) {

            fillForm(
                result.profile
            );


            statusPill.textContent =
                "Profile saved";

        }


        /*
        PROFILE DOES NOT EXIST
        */

        else {

            document.getElementById(
                "activity_level"
            ).value =
                "sedentary";


            updateBMI();


            statusPill.textContent =
                "New profile";

        }

    }

    catch (error) {

        console.error(error);


        statusPill.textContent =
            "Connection error";


        showMessage(
            "Unable to connect to Health Profile API.",
            true
        );

    }

}


/*
=========================================================
Function Name: saveHealthProfile

Description:
Creates or updates health profile.

Input:
Health profile form data

Output:
Backend success/error message
=========================================================
*/

async function saveHealthProfile() {

    clearMessages();


    const data =
        getFormData();


    saveBtn.disabled = true;

    saveBtn.textContent =
        "Saving...";


    /*
    If profile exists -> PUT

    If profile doesn't exist -> POST
    */

    const method =
        profileExists
            ? "PUT"
            : "POST";


    try {

        const response =
            await fetch(
                API_URL,
                {

                    method: method,

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    credentials:
                        "same-origin",

                    body:
                        JSON.stringify(data)

                }
            );


        const result =
            await response.json();


        /*
        LOGIN CHECK
        */

        if (response.status === 401) {

            showMessage(
                result.message ||
                "Please login first.",
                true
            );

            return;

        }


        /*
        VALIDATION ERROR
        */

        if (response.status === 400) {

            displayValidationErrors(
                result.errors
            );


            showMessage(
                "Please correct the highlighted fields.",
                true
            );

            return;

        }


        /*
        PROFILE ALREADY EXISTS
        */

        if (response.status === 409) {

            profileExists = true;


            showMessage(
                result.message ||
                "Health profile already exists.",
                true
            );

            return;

        }


        /*
        PROFILE NOT FOUND
        */

        if (response.status === 404) {

            profileExists = false;


            showMessage(
                result.message ||
                "Health profile not found.",
                true
            );

            return;

        }


        /*
        OTHER ERROR
        */

        if (
            !response.ok ||
            !result.success
        ) {

            showMessage(
                result.message ||
                "Unable to save profile.",
                true
            );

            return;

        }


        /*
        SUCCESS
        */

        profileExists = true;


        statusPill.textContent =
            "Profile saved";


        showMessage(
            result.message ||
            "Health profile saved successfully."
        );


        /*
        Reload data from database
        */

        await loadHealthProfile();

    }

    catch (error) {

        console.error(error);


        showMessage(
            "Unable to connect to backend.",
            true
        );

    }

    finally {

        saveBtn.disabled = false;

        saveBtn.textContent =
            "Save Changes";

    }

}


/*
=========================================================
FORM SUBMIT
=========================================================
*/

form.addEventListener(
    "submit",
    function(event) {

        event.preventDefault();

        saveHealthProfile();

    }
);


/*
=========================================================
LIVE BMI
=========================================================
*/

document
    .getElementById("height_cm")
    .addEventListener(
        "input",
        updateBMI
    );


document
    .getElementById("weight_kg")
    .addEventListener(
        "input",
        updateBMI
    );


/*
=========================================================
TAB NAVIGATION
=========================================================
*/

document
    .querySelectorAll(".tab")
    .forEach(tab => {

        tab.addEventListener(
            "click",
            function() {

                document
                    .querySelectorAll(".tab")
                    .forEach(t => {

                        t.classList.remove(
                            "active"
                        );

                    });


                this.classList.add(
                    "active"
                );


                const section =
                    document.getElementById(
                        this.dataset.section
                    );


                if (section) {

                    section.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });

                }

            }
        );

    });


/*
=========================================================
LOAD PROFILE WHEN PAGE OPENS
=========================================================
*/

loadHealthProfile();