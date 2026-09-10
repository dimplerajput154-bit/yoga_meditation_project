
// =========================================================
// MOOD TRACKER FRONTEND
// =========================================================
//
// API:
// GET    /mood
// POST   /mood
// PUT    /mood/<record_id>
// DELETE /mood/<record_id>
// GET    /mood/summary
//
// =========================================================


// =========================================================
// Global Variables
// =========================================================

let moodRecords = [];

let moodChart = null;

let stressChart = null;

let selectedMood = "";


// =========================================================
// Function: initializeMoodTracker()
// Description:
//     Initializes the Mood Tracker page.
// Input:
//     None
// Output:
//     Loads records and summary.
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    setTodayDate();

    loadMoodRecords();

    loadSummary();

    setupForm();

});


// =========================================================
// Function: setTodayDate()
// Description:
//     Sets today's date in the date input.
// Input:
//     None
// Output:
//     Today's date.
// =========================================================

function setTodayDate() {

    const dateInput =
        document.getElementById("recordDate");

    const today =
        new Date().toISOString().split("T")[0];

    dateInput.value = today;
}


// =========================================================
// Function: setupForm()
// Description:
//     Handles mood form submission.
// Input:
//     Form submit event.
// Output:
//     Creates or updates mood record.
// =========================================================

function setupForm() {

    const form =
        document.getElementById("moodForm");

    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            await saveMood();

        }
    );
}


// =========================================================
// Function: loadMoodRecords()
// Description:
//     Loads user's mood records from backend.
// Input:
//     None
// Output:
//     Displays records in table.
// =========================================================

async function loadMoodRecords() {

    try {

        const response =
            await fetch(
                "/mood",
                {
                    method: "GET",
                    credentials: "include"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            console.error(data.message);

            if (response.status === 401) {

                showLoginMessage();

            }

            return;
        }


        if (data.success) {

            moodRecords =
                data.records || [];

            displayMoodRecords(
                moodRecords
            );

            updateTodayMood();

        }

    }
    catch (error) {

        console.error(
            "Error loading mood records:",
            error
        );

    }
}


// =========================================================
// Function: displayMoodRecords()
// Description:
//     Displays mood records in table.
// Input:
//     records - Array of mood records.
// Output:
//     Updated table.
// =========================================================

function displayMoodRecords(records) {

    const tbody =
        document.getElementById(
            "moodTableBody"
        );


    if (!records || records.length === 0) {

        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-row">
                    No mood records found.
                </td>
            </tr>
        `;

        return;
    }


    tbody.innerHTML = "";


    records.forEach(function (record) {

        const row =
            document.createElement("tr");


        const moodEmoji =
            getMoodEmoji(record.mood);


        const moodName =
            capitalize(record.mood);


        const stress =
            record.stress_level !== null &&
            record.stress_level !== undefined
                ? `${record.stress_level}/10`
                : "--";


        const notes =
            record.notes || "--";


        row.innerHTML = `

            <td>
                ${formatDate(record.record_date)}
            </td>

            <td>
                <span class="mood-badge">
                    ${moodEmoji}
                    ${moodName}
                </span>
            </td>

            <td>
                <span class="stress-badge">
                    ${stress}
                </span>
            </td>

            <td>
                <div class="notes-cell"
                     title="${escapeHtml(notes)}">
                    ${escapeHtml(notes)}
                </div>
            </td>

            <td>

                <div class="action-buttons">

                    <button
                        class="edit-btn"
                        onclick="editMood(${record.record_id})"
                    >
                        Edit
                    </button>

                    <button
                        class="delete-btn"
                        onclick="deleteMood(${record.record_id})"
                    >
                        Delete
                    </button>

                </div>

            </td>

        `;


        tbody.appendChild(row);

    });

}


// =========================================================
// Function: saveMood()
// Description:
//     Creates or updates mood record.
// Input:
//     Form values.
// Output:
//     Backend API response.
// =========================================================

async function saveMood() {

    const recordId =
        document.getElementById(
            "recordId"
        ).value;


    const recordDate =
        document.getElementById(
            "recordDate"
        ).value;


    const mood =
        document.getElementById(
            "mood"
        ).value;


    const stressLevel =
        document.getElementById(
            "stressLevel"
        ).value;


    const notes =
        document.getElementById(
            "notes"
        ).value.trim();


    const errorBox =
        document.getElementById(
            "formError"
        );


    errorBox.textContent = "";


    // -----------------------------------------------------
    // Frontend Validation
    // -----------------------------------------------------

    if (!recordDate) {

        errorBox.textContent =
            "Please select a date.";

        return;
    }


    if (!mood) {

        errorBox.textContent =
            "Please select your mood.";

        return;
    }


    if (
        stressLevel < 1 ||
        stressLevel > 10
    ) {

        errorBox.textContent =
            "Stress level must be between 1 and 10.";

        return;
    }


    const requestData = {

        record_date: recordDate,

        mood: mood,

        stress_level:
            parseInt(stressLevel),

        notes:
            notes || null

    };


    try {

        let response;


        // -------------------------------------------------
        // Update
        // -------------------------------------------------

        if (recordId) {

            response =
                await fetch(
                    `/mood/${recordId}`,
                    {
                        method: "PUT",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        credentials: "include",

                        body:
                            JSON.stringify(
                                requestData
                            )
                    }
                );

        }

        // -------------------------------------------------
        // Create
        // -------------------------------------------------

        else {

            response =
                await fetch(
                    "/mood",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        credentials: "include",

                        body:
                            JSON.stringify(
                                requestData
                            )
                    }
                );

        }


        const data =
            await response.json();


        if (!response.ok) {

            errorBox.textContent =
                data.message ||
                "Something went wrong.";

            return;
        }


        if (data.success) {

            closeMoodModal();

            await loadMoodRecords();

            await loadSummary();

        }

    }
    catch (error) {

        console.error(
            "Error saving mood:",
            error
        );

        errorBox.textContent =
            "Unable to connect to server.";

    }

}


// =========================================================
// Function: editMood()
// Description:
//     Opens selected mood record for editing.
// Input:
//     recordId - Mood record ID.
// Output:
//     Filled modal.
// =========================================================

function editMood(recordId) {

    const record =
        moodRecords.find(
            item =>
                item.record_id == recordId
        );


    if (!record) {

        return;
    }


    document.getElementById(
        "recordId"
    ).value =
        record.record_id;


    document.getElementById(
        "recordDate"
    ).value =
        record.record_date;


    document.getElementById(
        "mood"
    ).value =
        record.mood;


    document.getElementById(
        "stressLevel"
    ).value =
        record.stress_level || 5;


    document.getElementById(
        "notes"
    ).value =
        record.notes || "";


    document.getElementById(
        "modalTitle"
    ).textContent =
        "Edit Mood";


    updateStressValue();

    selectFormMood(
        record.mood
    );


    document.getElementById(
        "moodModal"
    ).classList.add("show");

}


// =========================================================
// Function: deleteMood()
// Description:
//     Deletes a mood record.
// Input:
//     recordId - Mood record ID.
// Output:
//     Deleted record.
// =========================================================

async function deleteMood(recordId) {

    const confirmDelete =
        confirm(
            "Are you sure you want to delete this mood record?"
        );


    if (!confirmDelete) {

        return;
    }


    try {

        const response =
            await fetch(
                `/mood/${recordId}`,
                {
                    method: "DELETE",
                    credentials: "include"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            alert(
                data.message ||
                "Failed to delete record."
            );

            return;
        }


        if (data.success) {

            await loadMoodRecords();

            await loadSummary();

        }

    }
    catch (error) {

        console.error(
            "Delete error:",
            error
        );

        alert(
            "Unable to connect to server."
        );

    }

}


// =========================================================
// Function: openMoodModal()
// Description:
//     Opens modal for new mood record.
// Input:
//     None
// Output:
//     Empty mood form.
// =========================================================

function openMoodModal() {

    document.getElementById(
        "moodModal"
    ).classList.add("show");


    document.getElementById(
        "moodForm"
    ).reset();


    document.getElementById(
        "recordId"
    ).value = "";


    document.getElementById(
        "mood"
    ).value = "";


    selectedMood = "";


    document.getElementById(
        "modalTitle"
    ).textContent =
        "Log Your Mood";


    document.getElementById(
        "stressLevel"
    ).value = 5;


    updateStressValue();


    document
        .querySelectorAll(".form-mood")
        .forEach(function (button) {

            button.classList.remove(
                "selected"
            );

        });


    setTodayDate();

}


// =========================================================
// Function: closeMoodModal()
// Description:
//     Closes mood modal.
// Input:
//     None
// Output:
//     Hidden modal.
// =========================================================

function closeMoodModal() {

    document.getElementById(
        "moodModal"
    ).classList.remove("show");


    document.getElementById(
        "formError"
    ).textContent = "";

}


// =========================================================
// Function: selectMood()
// Description:
//     Selects mood from main mood section.
// Input:
//     mood - selected mood.
// Output:
//     Highlighted mood.
// =========================================================

function selectMood(mood) {

    document
        .querySelectorAll(".mood-option")
        .forEach(function (button) {

            button.classList.remove(
                "selected"
            );

        });


    const selectedButton =
        document.querySelector(
            `.mood-option[data-mood="${mood}"]`
        );


    if (selectedButton) {

        selectedButton.classList.add(
            "selected"
        );

    }


    selectedMood = mood;


    openMoodModal();


    selectFormMood(mood);

}


// =========================================================
// Function: selectFormMood()
// Description:
//     Selects mood inside modal.
// Input:
//     mood - selected mood.
// Output:
//     Selected mood stored in hidden input.
// =========================================================

function selectFormMood(mood) {

    selectedMood = mood;


    document.getElementById(
        "mood"
    ).value =
        mood;


    document
        .querySelectorAll(".form-mood")
        .forEach(function (button) {

            button.classList.remove(
                "selected"
            );

        });


    const selectedButton =
        document.querySelector(
            `.form-mood[data-mood="${mood}"]`
        );


    if (selectedButton) {

        selectedButton.classList.add(
            "selected"
        );

    }

}


// =========================================================
// Function: updateStressValue()
// Description:
//     Updates displayed stress value.
// Input:
//     Slider value.
// Output:
//     Current stress level.
// =========================================================

function updateStressValue() {

    const value =
        document.getElementById(
            "stressLevel"
        ).value;


    document.getElementById(
        "stressValue"
    ).textContent =
        value;

}


// =========================================================
// Function: loadSummary()
// Description:
//     Loads weekly/monthly mood summary.
// Input:
//     Selected period.
// Output:
//     Summary cards and charts.
// =========================================================

async function loadSummary() {

    const period =
        document.getElementById(
            "moodPeriod"
        ).value;


    try {

        const response =
            await fetch(
                `/mood/summary?period=${period}`,
                {
                    method: "GET",
                    credentials: "include"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            return;
        }


        if (!data.success) {

            return;
        }


        document.getElementById(
            "averageStress"
        ).textContent =
            data.average_stress !== null
                ? data.average_stress
                : "--";


        document.getElementById(
            "totalRecords"
        ).textContent =
            data.total_records || 0;


        document.getElementById(
            "dominantMood"
        ).textContent =
            data.dominant_mood
                ? capitalize(
                    data.dominant_mood
                  )
                : "--";


        createMoodChart(
            data.trend || []
        );


        createStressChart(
            data.trend || []
        );

    }
    catch (error) {

        console.error(
            "Summary error:",
            error
        );

    }

}


// =========================================================
// Function: createMoodChart()
// Description:
//     Creates mood trend chart.
// Input:
//     trend - mood trend records.
// Output:
//     Mood chart.
// =========================================================

function createMoodChart(trend) {

    const canvas =
        document.getElementById(
            "moodChart"
        );


    const labels =
        trend.map(
            item => formatShortDate(
                item.date
            )
        );


    const moodValues =
        trend.map(
            item => moodToNumber(
                item.mood
            )
        );


    if (moodChart) {

        moodChart.destroy();

    }


    moodChart =
        new Chart(
            canvas,
            {
                type: "line",

                data: {

                    labels: labels,

                    datasets: [

                        {
                            label: "Mood",

                            data: moodValues,

                            borderWidth: 2,

                            tension: 0.35,

                            pointRadius: 4
                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    scales: {

                        y: {

                            min: 1,

                            max: 5,

                            ticks: {

                                stepSize: 1,

                                callback:
                                    function(value) {

                                        return moodNumberToName(
                                            value
                                        );

                                    }

                            }

                        }

                    },

                    plugins: {

                        legend: {
                            display: false
                        }

                    }

                }

            }
        );

}


// =========================================================
// Function: createStressChart()
// Description:
//     Creates stress trend chart.
// Input:
//     trend - mood trend records.
// Output:
//     Stress chart.
// =========================================================

function createStressChart(trend) {

    const canvas =
        document.getElementById(
            "stressChart"
        );


    const labels =
        trend.map(
            item => formatShortDate(
                item.date
            )
        );


    const stressValues =
        trend.map(
            item =>
                item.stress_level !== null
                    ? item.stress_level
                    : null
        );


    if (stressChart) {

        stressChart.destroy();

    }


    stressChart =
        new Chart(
            canvas,
            {
                type: "line",

                data: {

                    labels: labels,

                    datasets: [

                        {
                            label:
                                "Stress Level",

                            data:
                                stressValues,

                            borderWidth: 2,

                            tension: 0.35,

                            pointRadius: 4

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    scales: {

                        y: {

                            min: 1,

                            max: 10,

                            ticks: {
                                stepSize: 1
                            }

                        }

                    },

                    plugins: {

                        legend: {
                            display: false
                        }

                    }

                }

            }
        );

}


// =========================================================
// Function: updateTodayMood()
// Description:
//     Displays latest mood in summary.
// Input:
//     None
// Output:
//     Today's/latest mood.
// =========================================================

function updateTodayMood() {

    if (!moodRecords.length) {

        document.getElementById(
            "todayMood"
        ).textContent = "--";

        return;
    }


    const today =
        new Date()
            .toISOString()
            .split("T")[0];


    const todayRecord =
        moodRecords.find(
            record =>
                record.record_date === today
        );


    const record =
        todayRecord ||
        moodRecords[0];


    document.getElementById(
        "todayMood"
    ).textContent =
        capitalize(record.mood);

}


// =========================================================
// Function: filterHistory()
// Description:
//     Filters mood history by mood.
// Input:
//     Selected filter.
// Output:
//     Filtered table.
// =========================================================

function filterHistory() {

    const filter =
        document.getElementById(
            "historyFilter"
        ).value;


    if (filter === "all") {

        displayMoodRecords(
            moodRecords
        );

        return;
    }


    const filtered =
        moodRecords.filter(
            record =>
                record.mood === filter
        );


    displayMoodRecords(
        filtered
    );

}


// =========================================================
// Function: getMoodEmoji()
// Description:
//     Returns emoji for mood.
// Input:
//     mood
// Output:
//     Emoji.
// =========================================================

function getMoodEmoji(mood) {

    const emojis = {

        happy: "😊",

        good: "🙂",

        neutral: "😐",

        stressed: "😣",

        sad: "😔"

    };


    return emojis[mood] || "🙂";

}


// =========================================================
// Function: moodToNumber()
// Description:
//     Converts mood into numeric value.
// Input:
//     mood
// Output:
//     Number 1-5.
// =========================================================

function moodToNumber(mood) {

    const values = {

        sad: 1,

        stressed: 2,

        neutral: 3,

        good: 4,

        happy: 5

    };


    return values[mood] || 3;

}


// =========================================================
// Function: moodNumberToName()
// Description:
//     Converts chart number to mood name.
// Input:
//     number
// Output:
//     Mood name.
// =========================================================

function moodNumberToName(number) {

    const names = {

        1: "Sad",

        2: "Stressed",

        3: "Neutral",

        4: "Good",

        5: "Happy"

    };


    return names[number] || "";

}


// =========================================================
// Function: capitalize()
// Description:
//     Capitalizes first character.
// Input:
//     text
// Output:
//     Capitalized text.
// =========================================================

function capitalize(text) {

    if (!text) {

        return "";

    }


    return text.charAt(0).toUpperCase()
        + text.slice(1);

}


// =========================================================
// Function: formatDate()
// Description:
//     Formats date for table.
// Input:
//     dateString
// Output:
//     Formatted date.
// =========================================================

function formatDate(dateString) {

    if (!dateString) {

        return "--";

    }


    const date =
        new Date(
            dateString + "T00:00:00"
        );


    return date.toLocaleDateString(
        "en-IN",
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    );

}


// =========================================================
// Function: formatShortDate()
// Description:
//     Formats date for charts.
// Input:
//     dateString
// Output:
//     Short date.
// =========================================================

function formatShortDate(dateString) {

    if (!dateString) {

        return "";

    }


    const date =
        new Date(
            dateString + "T00:00:00"
        );


    return date.toLocaleDateString(
        "en-IN",
        {
            day: "2-digit",
            month: "short"
        }
    );

}


// =========================================================
// Function: escapeHtml()
// Description:
//     Prevents HTML injection in notes.
// Input:
//     text
// Output:
//     Safe text.
// =========================================================

function escapeHtml(text) {

    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


// =========================================================
// Function: showLoginMessage()
// Description:
//     Shows message when user is not logged in.
// Input:
//     None
// Output:
//     Console message.
// =========================================================

function showLoginMessage() {

    const tbody =
        document.getElementById(
            "moodTableBody"
        );


    tbody.innerHTML = `
        <tr>
            <td colspan="5"
                class="empty-row">
                Please login to view your mood records.
            </td>
        </tr>
    `;

}


// =========================================================
// Close modal when clicking outside
// =========================================================

document
    .getElementById("moodModal")
    .addEventListener(
        "click",
        function(event) {

            if (
                event.target ===
                this
            ) {

                closeMoodModal();

            }

        }
    );