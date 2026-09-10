
/* =====================================================
   REMEDIES MODULE FRONTEND

   Backend APIs:

   GET /remedies

   GET /remedies/<id>

   GET /search-remedies?topic=<keyword>

   Flask server:
   http://127.0.0.1:5000
===================================================== */


const API_URL = "http://127.0.0.1:5000";


/* ================= ELEMENTS ================= */

const remedyContainer =
    document.getElementById("remedyContainer");

const searchInput =
    document.getElementById("searchInput");

const clearBtn =
    document.getElementById("clearBtn");

const refreshBtn =
    document.getElementById("refreshBtn");

const resultCount =
    document.getElementById("resultCount");

const status =
    document.getElementById("status");


/* MODAL ELEMENTS */

const modal =
    document.getElementById("modal");

const closeModal =
    document.getElementById("closeModal");

const modalBackground =
    document.querySelector(".modal-background");

const modalTopic =
    document.getElementById("modalTopic");

const modalSymptoms =
    document.getElementById("modalSymptoms");

const modalCare =
    document.getElementById("modalCare");

const modalPrecautions =
    document.getElementById("modalPrecautions");

const modalDoctor =
    document.getElementById("modalDoctor");

const modalIcon =
    document.getElementById("modalIcon");


/* Store all remedies */

let allRemedies = [];


/* =====================================================
   FUNCTION 1
   Name        : showStatus()
   Description : Displays error/status message.
   Input       : message
   Output      : None
===================================================== */

function showStatus(message) {

    status.textContent = message;

    status.classList.remove("hidden");
}


/* =====================================================
   FUNCTION 2
   Name        : hideStatus()
   Description : Hides status message.
   Input       : None
   Output      : None
===================================================== */

function hideStatus() {

    status.classList.add("hidden");
}


/* =====================================================
   FUNCTION 3
   Name        : escapeHTML()
   Description : Makes database text safe for display.
   Input       : text
   Output      : Safe text
===================================================== */

function escapeHTML(text) {

    return String(text ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* =====================================================
   FUNCTION 4
   Name        : getIcon()
   Description : Gives icon according to remedy topic.
   Input       : topic
   Output      : Emoji icon
===================================================== */

function getIcon(topic) {

    const name = topic.toLowerCase();


    if (
        name.includes("cold") ||
        name.includes("nasal") ||
        name.includes("sneez")
    ) {
        return "🌿";
    }


    if (
        name.includes("cough") ||
        name.includes("throat") ||
        name.includes("hoarse")
    ) {
        return "🍵";
    }


    if (name.includes("headache")) {
        return "🧠";
    }


    if (name.includes("eye")) {
        return "👁️";
    }


    if (
        name.includes("skin") ||
        name.includes("itch") ||
        name.includes("sunburn") ||
        name.includes("insect")
    ) {
        return "🌱";
    }


    if (name.includes("sleep")) {
        return "🌙";
    }


    if (
        name.includes("stress") ||
        name.includes("anxiety")
    ) {
        return "🧘";
    }


    if (name.includes("menstrual")) {
        return "🌸";
    }


    if (
        name.includes("muscle") ||
        name.includes("neck") ||
        name.includes("back")
    ) {
        return "🧘‍♀️";
    }


    if (
        name.includes("gas") ||
        name.includes("bloating") ||
        name.includes("acidity") ||
        name.includes("indigestion") ||
        name.includes("nausea")
    ) {
        return "🍃";
    }


    if (
        name.includes("dehydration") ||
        name.includes("fever")
    ) {
        return "💧";
    }


    return "🌿";
}


/* =====================================================
   FUNCTION 5
   Name        : renderRemedies()
   Description : Displays remedies as cards.
   Input       : remedies array
   Output      : None
===================================================== */

function renderRemedies(remedies) {

    remedyContainer.innerHTML = "";


    if (remedies.length === 0) {

        resultCount.textContent =
            "No remedies found.";

        remedyContainer.innerHTML = `
            <div class="status">
                No matching remedy found.
                Try another keyword.
            </div>
        `;

        return;
    }


    resultCount.textContent =
        `${remedies.length} remedies available`;


    remedies.forEach(remedy => {

        const icon =
            getIcon(remedy.topic);


        const card =
            document.createElement("div");


        card.className =
            "remedy-card";


        card.innerHTML = `

            <div class="card-top">

                <div class="remedy-icon">
                    ${icon}
                </div>

                <div>

                    <h3>
                        ${escapeHTML(remedy.topic)}
                    </h3>

                    <p class="symptoms">
                        ${escapeHTML(remedy.symptoms)}
                    </p>

                </div>

            </div>


            <p class="preview">

                ${escapeHTML(
                    remedy.self_care_info
                )}

            </p>


            <button
                class="view-btn"
                data-id="${remedy.remedy_id}"
            >

                View Details →

            </button>
        `;


        remedyContainer.appendChild(card);

    });


    /* Add click event to View Details */

    document
        .querySelectorAll(".view-btn")
        .forEach(button => {

            button.addEventListener(
                "click",
                function () {

                    const id =
                        this.getAttribute("data-id");

                    getRemedyDetails(id);

                }
            );

        });
}


/* =====================================================
   FUNCTION 6
   Name        : loadAllRemedies()
   Description : Gets all remedies from Flask.
   Input       : None
   Output      : None
===================================================== */

async function loadAllRemedies() {

    hideStatus();

    resultCount.textContent =
        "Loading remedies...";


    try {

        const response =
            await fetch(`${API_URL}/remedies`);


        if (!response.ok) {

            throw new Error(
                "Server error: " + response.status
            );

        }


        const result =
            await response.json();


        if (!result.success) {

            throw new Error(
                result.message ||
                "Unable to load remedies."
            );

        }


        allRemedies =
            result.data || [];


        renderRemedies(allRemedies);


    }

    catch (error) {

        console.error(
            "Remedies API Error:",
            error
        );


        resultCount.textContent =
            "Unable to load remedies.";


        showStatus(
            "Could not connect to Flask backend. " +
            "Make sure python app.py is running " +
            "and database is connected."
        );

    }
}


/* =====================================================
   FUNCTION 7
   Name        : searchRemedies()
   Description : Searches remedies using backend API.
   Input       : keyword
   Output      : None
===================================================== */

async function searchRemedies(keyword) {

    keyword =
        keyword.trim();


    /* Empty search */

    if (keyword === "") {

        renderRemedies(allRemedies);

        return;
    }


    hideStatus();

    resultCount.textContent =
        "Searching...";


    try {

        const response =
            await fetch(
                `${API_URL}/search-remedies?topic=` +
                encodeURIComponent(keyword)
            );


        if (!response.ok) {

            throw new Error(
                "Search error: " +
                response.status
            );

        }


        const result =
            await response.json();


        if (!result.success) {

            throw new Error(
                result.message ||
                "Search failed."
            );

        }


        renderRemedies(
            result.data || []
        );

    }

    catch (error) {

        console.error(
            "Search API Error:",
            error
        );


        showStatus(
            "Search failed. " +
            "Check Flask backend."
        );

    }
}


/* =====================================================
   FUNCTION 8
   Name        : getRemedyDetails()
   Description : Gets complete remedy details.
   Input       : remedyId
   Output      : Opens details popup.
===================================================== */

async function getRemedyDetails(remedyId) {

    try {

        const response =
            await fetch(
                `${API_URL}/remedies/${remedyId}`
            );


        if (!response.ok) {

            throw new Error(
                "Server error: " +
                response.status
            );

        }


        const result =
            await response.json();


        if (!result.success) {

            throw new Error(
                result.message ||
                "Remedy not found."
            );

        }


        const remedy =
            result.data;


        /* Fill modal */

        modalTopic.textContent =
            remedy.topic || "Remedy";


        modalSymptoms.textContent =
            remedy.symptoms ||
            "Information not available.";


        modalCare.textContent =
            remedy.self_care_info ||
            "Information not available.";


        modalPrecautions.textContent =
            remedy.precautions ||
            "Information not available.";


        modalDoctor.textContent =
            remedy.when_to_consult_doctor ||
            "Consult a healthcare professional if required.";


        modalIcon.textContent =
            getIcon(remedy.topic || "");


        /* Show modal */

        modal.classList.remove("hidden");

    }

    catch (error) {

        console.error(
            "Details API Error:",
            error
        );


        showStatus(
            "Unable to load remedy details."
        );

    }
}


/* =====================================================
   FUNCTION 9
   Name        : closeDetails()
   Description : Closes remedy details popup.
   Input       : None
   Output      : None
===================================================== */

function closeDetails() {

    modal.classList.add("hidden");
}


/* =====================================================
   SEARCH EVENT
===================================================== */

searchInput.addEventListener(
    "input",
    function () {

        clearTimeout(
            window.searchTimer
        );


        window.searchTimer =
            setTimeout(
                () => {

                    searchRemedies(
                        searchInput.value
                    );

                },
                300
            );

    }
);


/* =====================================================
   CLEAR SEARCH
===================================================== */

clearBtn.addEventListener(
    "click",
    function () {

        searchInput.value = "";

        loadAllRemedies();

    }
);


/* =====================================================
   REFRESH
===================================================== */

refreshBtn.addEventListener(
    "click",
    function () {

        loadAllRemedies();

    }
);


/* =====================================================
   FILTER BUTTONS
===================================================== */

document
    .querySelectorAll(".filter")
    .forEach(button => {

        button.addEventListener(
            "click",
            function () {

                /* Remove active */

                document
                    .querySelectorAll(".filter")
                    .forEach(item => {

                        item.classList.remove(
                            "active"
                        );

                    });


                /* Add active */

                this.classList.add("active");


                const keyword =
                    this.getAttribute(
                        "data-keyword"
                    );


                searchInput.value =
                    keyword;


                if (keyword === "") {

                    loadAllRemedies();

                }

                else {

                    searchRemedies(
                        keyword
                    );

                }

            }
        );

    });


/* =====================================================
   MODAL CLOSE
===================================================== */

closeModal.addEventListener(
    "click",
    closeDetails
);


modalBackground.addEventListener(
    "click",
    closeDetails
);


/* ESC KEY */

document.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Escape") {

            closeDetails();

        }

    }
);


/* =====================================================
   LOAD DATA WHEN PAGE OPENS
===================================================== */

loadAllRemedies();