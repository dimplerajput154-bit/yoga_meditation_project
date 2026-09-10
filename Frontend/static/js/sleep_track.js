
"use strict";


/* =========================================================
   API CONFIGURATION
   ========================================================= */

const API_URL = "/sleep-tracker";


/* =========================================================
   GLOBAL VARIABLES
   ========================================================= */

let sleepRecords = [];

let sleepChart = null;


/* =========================================================
   Function-1: showMessage()
   Description:
       Displays success or error message.
   Input:
       message - Message text
       type - success or error
   Output:
       Message displayed on screen.
   ========================================================= */

function showMessage(message, type = "success") {

    const box = document.getElementById("messageBox");

    box.textContent = message;

    box.className = "message-box " + type;

    setTimeout(() => {

        box.className = "message-box";

    }, 3500);
}


/* =========================================================
   Function-2: formatDuration()
   Description:
       Converts minutes into hours and minutes.
   Input:
       minutes - Sleep duration in minutes.
   Output:
       Formatted duration string.
   ========================================================= */

function formatDuration(minutes) {

    if (minutes === null || minutes === undefined) {
        return "--";
    }

    const totalMinutes = Number(minutes);

    const hours = Math.floor(totalMinutes / 60);

    const mins = totalMinutes % 60;

    if (mins === 0) {
        return `${hours}h`;
    }

    return `${hours}h ${mins}m`;
}


/* =========================================================
   Function-3: calculateDuration()
   Description:
       Calculates sleep duration from sleep and wake time.
   Input:
       sleepTime, wakeTime - HH:MM values.
   Output:
       Duration in minutes.
   ========================================================= */

function calculateDuration(sleepTime, wakeTime) {

    if (!sleepTime || !wakeTime) {
        return null;
    }

    const sleepParts = sleepTime.split(":");
    const wakeParts = wakeTime.split(":");

    let sleepMinutes =
        Number(sleepParts[0]) * 60 +
        Number(sleepParts[1]);

    let wakeMinutes =
        Number(wakeParts[0]) * 60 +
        Number(wakeParts[1]);


    /* Wake-up is next day */

    if (wakeMinutes <= sleepMinutes) {

        wakeMinutes += 24 * 60;

    }

    return wakeMinutes - sleepMinutes;
}


/* =========================================================
   Function-4: updateDurationPreview()
   Description:
       Shows calculated duration in Add Record form.
   Input:
       Sleep time and wake time fields.
   Output:
       Duration shown in modal.
   ========================================================= */

function updateDurationPreview() {

    const sleepTime =
        document.getElementById("sleepTime").value;

    const wakeTime =
        document.getElementById("wakeTime").value;

    const duration =
        calculateDuration(sleepTime, wakeTime);

    const preview =
        document.getElementById("durationPreview");


    if (duration === null) {

        preview.textContent = "--";

        return;
    }

    preview.textContent =
        formatDuration(duration);
}


/* =========================================================
   Function-5: formatDate()
   Description:
       Converts YYYY-MM-DD into readable date.
   Input:
       dateString.
   Output:
       Formatted date.
   ========================================================= */

function formatDate(dateString) {

    if (!dateString) {
        return "--";
    }

    const date = new Date(dateString + "T00:00:00");

    return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    });
}


/* =========================================================
   Function-6: formatTime()
   Description:
       Converts 24-hour time into 12-hour format.
   Input:
       timeString - HH:MM:SS or HH:MM.
   Output:
       Formatted time.
   ========================================================= */

function formatTime(timeString) {

    if (!timeString) {
        return "--";
    }

    const parts = timeString.split(":");

    let hour = Number(parts[0]);

    const minute = parts[1];

    const suffix = hour >= 12 ? "PM" : "AM";

    hour = hour % 12;

    if (hour === 0) {
        hour = 12;
    }

    return `${hour}:${minute} ${suffix}`;
}


/* =========================================================
   Function-7: loadSleepRecords()
   Description:
       Gets sleep records from Flask backend.
   Input:
       None.
   Output:
       Updates sleepRecords array and UI.
   ========================================================= */

async function loadSleepRecords() {

    try {

        const response = await fetch(API_URL, {
            method: "GET",
            credentials: "include"
        });


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.message || "Unable to load sleep records."
            );
        }


        sleepRecords = data.records || [];


        renderSleepTable(sleepRecords);

        updateSummaryCards(sleepRecords);

        updateTodaySleep(sleepRecords);

        updateChart(sleepRecords);

    }

    catch (error) {

        console.error(error);

        showMessage(
            error.message,
            "error"
        );

        renderEmptyTable(
            "Unable to load sleep records."
        );
    }
}


/* =========================================================
   Function-8: renderSleepTable()
   Description:
       Displays sleep records inside history table.
   Input:
       records - Array of sleep records.
   Output:
       Updated HTML table.
   ========================================================= */

function renderSleepTable(records) {

    const tbody =
        document.getElementById("sleepTableBody");


    if (!records || records.length === 0) {

        renderEmptyTable(
            "No sleep records found."
        );

        return;
    }


    tbody.innerHTML = "";


    records.forEach(record => {

        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>
                ${formatDate(record.record_date)}
            </td>

            <td>
                ${formatTime(record.sleep_time)}
            </td>

            <td>
                ${formatTime(record.wake_time)}
            </td>

            <td>
                <strong>
                    ${formatDuration(record.duration_minutes)}
                </strong>
            </td>

            <td>

                <span class="quality ${record.quality || ""}">
                    ${record.quality || "--"}
                </span>

            </td>

            <td>
                ${record.notes || "--"}
            </td>

            <td>

                <button
                    class="action-btn edit-btn"
                    onclick="editSleepRecord(${record.record_id})">
                    ✎
                </button>

                <button
                    class="action-btn delete-btn"
                    onclick="deleteSleepRecord(${record.record_id})">
                    🗑
                </button>

            </td>

        `;

        tbody.appendChild(row);

    });
}


/* =========================================================
   Function-9: renderEmptyTable()
   Description:
       Displays empty table message.
   Input:
       message - Message text.
   Output:
       Empty state shown.
   ========================================================= */

function renderEmptyTable(message) {

    const tbody =
        document.getElementById("sleepTableBody");


    tbody.innerHTML = `

        <tr>

            <td colspan="7"
                class="empty-row">

                ${message}

            </td>

        </tr>

    `;
}


/* =========================================================
   Function-10: updateSummaryCards()
   Description:
       Updates average duration and record count.
   Input:
       records - Sleep records.
   Output:
       Summary cards updated.
   ========================================================= */

function updateSummaryCards(records) {

    const total =
        records.length;


    document.getElementById("totalRecords")
        .textContent = total;


    if (total === 0) {

        document.getElementById("averageSleep")
            .textContent = "--";

        document.getElementById("qualityValue")
            .textContent = "--";

        document.getElementById("lastSleep")
            .textContent = "--";

        return;
    }


    const validRecords =
        records.filter(
            r => r.duration_minutes !== null
        );


    if (validRecords.length > 0) {

        const totalMinutes =
            validRecords.reduce(
                (sum, record) =>
                    sum + Number(record.duration_minutes),
                0
            );


        const average =
            Math.round(
                totalMinutes / validRecords.length
            );


        document.getElementById("averageSleep")
            .textContent =
            formatDuration(average);

    }


    const latest =
        records[0];


    document.getElementById("lastSleep")
        .textContent =
        formatDuration(
            latest.duration_minutes
        );


    const qualityList =
        records
            .map(r => r.quality)
            .filter(Boolean);


    if (qualityList.length > 0) {

        document.getElementById("qualityValue")
            .textContent =
            qualityList[0]
                .charAt(0)
                .toUpperCase() +
            qualityList[0].slice(1);

    }

}


/* =========================================================
   Function-11: updateTodaySleep()
   Description:
       Displays latest sleep record.
   Input:
       records - Sleep records.
   Output:
       Today's/latest sleep card updated.
   ========================================================= */

function updateTodaySleep(records) {

    if (!records || records.length === 0) {

        document.getElementById("todayDuration")
            .textContent = "--";

        document.getElementById("todaySleepTime")
            .textContent = "--";

        document.getElementById("todayWakeTime")
            .textContent = "--";

        document.getElementById("todayDate")
            .textContent = "No record";

        document.getElementById("todayQuality")
            .textContent = "--";

        return;
    }


    const latest = records[0];


    document.getElementById("todayDuration")
        .textContent =
        formatDuration(
            latest.duration_minutes
        );


    document.getElementById("todaySleepTime")
        .textContent =
        formatTime(latest.sleep_time);


    document.getElementById("todayWakeTime")
        .textContent =
        formatTime(latest.wake_time);


    document.getElementById("todayDate")
        .textContent =
        formatDate(latest.record_date);


    document.getElementById("todayQuality")
        .textContent =
        latest.quality || "--";

}


/* =========================================================
   Function-12: updateChart()
   Description:
       Creates weekly sleep duration chart.
   Input:
       records - Sleep records.
   Output:
       Chart displayed on screen.
   ========================================================= */

function updateChart(records) {

    const canvas =
        document.getElementById("sleepChart");


    const latestRecords =
        [...records]
            .sort(
                (a, b) =>
                    new Date(a.record_date) -
                    new Date(b.record_date)
            )
            .slice(-7);


    const labels =
        latestRecords.map(
            record => {

                const date =
                    new Date(
                        record.record_date +
                        "T00:00:00"
                    );

                return date.toLocaleDateString(
                    "en-IN",
                    { weekday: "short" }
                );

            }
        );


    const values =
        latestRecords.map(
            record =>
                record.duration_minutes
                    ? Number(record.duration_minutes) / 60
                    : 0
        );


    if (sleepChart) {

        sleepChart.destroy();

    }


    sleepChart =
        new Chart(
            canvas,
            {
                type: "bar",

                data: {

                    labels: labels,

                    datasets: [

                        {
                            label: "Sleep Hours",

                            data: values,

                            backgroundColor:
                                "#4d8f4c",

                            borderRadius: 6,

                            borderSkipped: false

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {
                            display: false
                        }

                    },

                    scales: {

                        y: {

                            beginAtZero: true,

                            max: 12,

                            ticks: {
                                font: {
                                    size: 9
                                }
                            },

                            title: {
                                display: true,
                                text: "Hours",
                                font: {
                                    size: 9
                                }
                            }

                        },

                        x: {

                            ticks: {
                                font: {
                                    size: 9
                                }
                            }

                        }

                    }

                }

            }
        );
}


/* =========================================================
   Function-13: openAddModal()
   Description:
       Opens blank sleep record form.
   Input:
       None.
   Output:
       Add sleep modal displayed.
   ========================================================= */

function openAddModal() {

    document.getElementById("modalTitle")
        .textContent =
        "Add Sleep Record";


    document.getElementById("sleepForm")
        .reset();


    document.getElementById("recordId")
        .value = "";


    document.getElementById("durationPreview")
        .textContent = "--";


    document.getElementById("sleepModal")
        .classList.add("show");
}


/* =========================================================
   Function-14: closeModal()
   Description:
       Closes sleep form modal.
   Input:
       None.
   Output:
       Modal hidden.
   ========================================================= */

function closeModal() {

    document.getElementById("sleepModal")
        .classList.remove("show");
}


/* =========================================================
   Function-15: saveSleepRecord()
   Description:
       Adds or updates sleep record using backend.
   Input:
       Form values.
   Output:
       Database record created or updated.
   ========================================================= */

async function saveSleepRecord(event) {

    event.preventDefault();


    const recordId =
        document.getElementById("recordId").value;


    const recordDate =
        document.getElementById("recordDate").value;


    const sleepTime =
        document.getElementById("sleepTime").value;


    const wakeTime =
        document.getElementById("wakeTime").value;


    const quality =
        document.getElementById("quality").value;


    const notes =
        document.getElementById("notes").value;


    const reportFile =
        document.getElementById("reportFile").value;


    const payload = {

        record_date: recordDate,

        sleep_time: sleepTime,

        wake_time: wakeTime,

        quality: quality || null,

        notes: notes || null,

        report_file: reportFile || null

    };


    const isEditing =
        recordId !== "";


    const url =
        isEditing
            ? `${API_URL}/${recordId}`
            : API_URL;


    const method =
        isEditing
            ? "PUT"
            : "POST";


    try {

        const response =
            await fetch(
                url,
                {
                    method: method,

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    credentials: "include",

                    body:
                        JSON.stringify(payload)
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.message ||
                "Unable to save sleep record."
            );

        }


        showMessage(
            data.message ||
            "Sleep record saved successfully.",
            "success"
        );


        closeModal();


        await loadSleepRecords();

    }

    catch (error) {

        console.error(error);

        showMessage(
            error.message,
            "error"
        );

    }

}


/* =========================================================
   Function-16: editSleepRecord()
   Description:
       Loads selected record into edit form.
   Input:
       recordId - Sleep record ID.
   Output:
       Edit modal populated.
   ========================================================= */

function editSleepRecord(recordId) {

    const record =
        sleepRecords.find(
            r => Number(r.record_id) === Number(recordId)
        );


    if (!record) {

        showMessage(
            "Sleep record not found.",
            "error"
        );

        return;
    }


    document.getElementById("modalTitle")
        .textContent =
        "Edit Sleep Record";


    document.getElementById("recordId")
        .value =
        record.record_id;


    document.getElementById("recordDate")
        .value =
        record.record_date;


    document.getElementById("sleepTime")
        .value =
        record.sleep_time.substring(0, 5);


    document.getElementById("wakeTime")
        .value =
        record.wake_time.substring(0, 5);


    document.getElementById("quality")
        .value =
        record.quality || "";


    document.getElementById("notes")
        .value =
        record.notes || "";


    document.getElementById("reportFile")
        .value =
        record.report_file || "";


    updateDurationPreview();


    document.getElementById("sleepModal")
        .classList.add("show");
}


/* =========================================================
   Function-17: deleteSleepRecord()
   Description:
       Deletes selected sleep record.
   Input:
       recordId - Sleep record ID.
   Output:
       Record deleted from database.
   ========================================================= */

async function deleteSleepRecord(recordId) {

    const confirmed =
        confirm(
            "Are you sure you want to delete this sleep record?"
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/${recordId}`,
                {
                    method: "DELETE",
                    credentials: "include"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.message ||
                "Unable to delete record."
            );

        }


        showMessage(
            data.message ||
            "Sleep record deleted successfully.",
            "success"
        );


        await loadSleepRecords();

    }

    catch (error) {

        console.error(error);

        showMessage(
            error.message,
            "error"
        );

    }

}


/* =========================================================
   Function-18: applyFilter()
   Description:
       Filters sleep history records.
   Input:
       filterType - all, week or month.
   Output:
       Filtered records displayed.
   ========================================================= */

function applyFilter(filterType) {

    if (filterType === "all") {

        renderSleepTable(sleepRecords);

        return;
    }


    const today =
        new Date();

    let filteredRecords = [];


    if (filterType === "week") {

        const weekAgo =
            new Date();

        weekAgo.setDate(
            today.getDate() - 7
        );


        filteredRecords =
            sleepRecords.filter(
                record =>
                    new Date(
                        record.record_date
                    ) >= weekAgo
            );

    }


    if (filterType === "month") {

        const monthAgo =
            new Date();

        monthAgo.setDate(
            today.getDate() - 30
        );


        filteredRecords =
            sleepRecords.filter(
                record =>
                    new Date(
                        record.record_date
                    ) >= monthAgo
            );

    }


    renderSleepTable(filteredRecords);
}


/* =========================================================
   Function-19: initializeSleepTracker()
   Description:
       Initializes Sleep Tracker frontend.
   Input:
       None.
   Output:
       Event listeners added and data loaded.
   ========================================================= */

function initializeSleepTracker() {


    /* Add button */

    document.getElementById("addSleepBtn")
        .addEventListener(
            "click",
            openAddModal
        );


    /* Close button */

    document.getElementById("closeModal")
        .addEventListener(
            "click",
            closeModal
        );


    /* Cancel button */

    document.getElementById("cancelBtn")
        .addEventListener(
            "click",
            closeModal
        );


    /* Form submit */

    document.getElementById("sleepForm")
        .addEventListener(
            "submit",
            saveSleepRecord
        );


    /* Duration calculation */

    document.getElementById("sleepTime")
        .addEventListener(
            "change",
            updateDurationPreview
        );


    document.getElementById("wakeTime")
        .addEventListener(
            "change",
            updateDurationPreview
        );


    /* Filter buttons */

    document.querySelectorAll(".filter-btn")
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    document
                        .querySelectorAll(".filter-btn")
                        .forEach(btn =>
                            btn.classList.remove("active")
                        );


                    button.classList.add("active");


                    applyFilter(
                        button.dataset.filter
                    );

                }
            );

        });


    /* Load backend data */

    loadSleepRecords();

}


/* =========================================================
   APPLICATION START
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initializeSleepTracker
);