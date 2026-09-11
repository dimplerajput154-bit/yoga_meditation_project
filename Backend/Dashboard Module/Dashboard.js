const API_URL = "http://127.0.0.1:5000";
const AUTH_URL = "http://127.0.0.1:5001";
const ORGANIZATION_URL = "http://127.0.0.1:5002";

let currentUser = null;


/* =========================================================
   Sidebar Navigation
   ========================================================= */

function openOrganizations() {
    window.location.href = `${ORGANIZATION_URL}/`;
}


/* =========================================================
   Load Dashboard
   ========================================================= */

async function loadDashboard() {

    currentUser = await getLoggedInUser();

    if (!currentUser) {
        localStorage.removeItem("user");
        window.location.href = `${AUTH_URL}/`;
        return;
    }

    localStorage.setItem(
        "user",
        JSON.stringify(currentUser)
    );

    if (currentUser.name) {
        document.getElementById("userName").textContent = currentUser.name;
    }

    const params = new URLSearchParams(window.location.search);

    if (params.get("new") === "1") {
        document.getElementById("welcomeText").textContent = "Welcome";
        params.delete("new");
        const nextUrl = `${window.location.pathname}${params.toString() ? `?${params}` : ""}`;
        window.history.replaceState({}, "", nextUrl);
    }

    try {

        const response = await fetch(
            `${API_URL}/api/dashboard/${currentUser.id}`
        );

        const data = await response.json();

        if (!response.ok) {

            alert(data.message || "Unable to load dashboard.");

            return;
        }

        displayUser(data.user);

        displayMetrics(data.metric);

        displayTasks(data.tasks);

    } catch (error) {

        console.error("Dashboard Error:", error);

        alert(
            "Unable to connect with Dashboard Server."
        );
    }
}


/* =========================================================
   Authenticated User
   ========================================================= */

async function getLoggedInUser() {

    try {

        const response = await fetch(
            `${AUTH_URL}/check-login`,
            {
                credentials: "include"
            }
        );

        const data = await response.json();

        if (response.ok && data.logged_in && data.user?.id) {
            return data.user;
        }

    } catch (error) {

        console.error("Auth Check Error:", error);
    }

    return null;
}


/* =========================================================
   Display User
   ========================================================= */

function displayUser(user) {

    document.getElementById("userName").textContent =
        currentUser?.name || user.name;
}


/* =========================================================
   Display Wellness Metrics
   ========================================================= */

function displayMetrics(metric) {

    if (!metric) {
        return;
    }


    document.getElementById("sleepHours").textContent =
        metric.sleep_hours;

    document.getElementById("sleepStatus").textContent =
        metric.sleep_status;


    document.getElementById("moodScore").textContent =
        metric.mood_score;

    document.getElementById("moodPercentage").textContent =
        metric.mood_percentage;


    document.getElementById("yogaMinutes").textContent =
        metric.yoga_minutes;

    document.getElementById("yogaGoal").textContent =
        metric.yoga_goal;


    document.getElementById("waterGlasses").textContent =
        metric.water_glasses;

    document.getElementById("waterGoal").textContent =
        metric.water_goal;


    document.getElementById("stepsCount").textContent =
        metric.steps_count;

    document.getElementById("stepsGoal").textContent =
        metric.steps_goal;


    document.getElementById("waterCount").textContent =
        metric.water_glasses;


    updateProgress(
        "stepsProgress",
        metric.steps_count,
        metric.steps_goal
    );


    updateProgress(
        "waterProgress",
        metric.water_glasses,
        metric.water_goal
    );
}


/* =========================================================
   Progress Bar
   ========================================================= */

function updateProgress(elementId, value, goal) {

    let percentage = 0;

    if (goal > 0) {

        percentage = (value / goal) * 100;
    }

    percentage = Math.min(percentage, 100);

    document.getElementById(elementId).style.width =
        percentage + "%";
}


/* =========================================================
   Display Tasks
   ========================================================= */

function displayTasks(tasks) {

    const container =
        document.getElementById("tasksContainer");

    container.innerHTML = "";


    if (!tasks || tasks.length === 0) {

        container.innerHTML =
            "<p>No wellness tasks available.</p>";

        return;
    }


    let completed = 0;


    tasks.forEach(task => {

        if (task.is_completed) {
            completed++;
        }


        const taskDiv =
            document.createElement("div");

        taskDiv.className =
            "task" +
            (task.is_completed ? " completed" : "");


        taskDiv.innerHTML = `

            <input
                type="checkbox"
                ${task.is_completed ? "checked" : ""}
                onchange="toggleTask(${task.id}, this)"
            >

            <span>${task.task_name}</span>

        `;


        container.appendChild(taskDiv);
    });


    document.getElementById("taskCount").textContent =
        `${completed}/${tasks.length} Completed`;
}


/* =========================================================
   Toggle Task
   ========================================================= */

async function toggleTask(taskId, checkbox) {

    try {

        const response = await fetch(
            `${API_URL}/api/toggle-task/${taskId}`,
            {
                method: "POST"
            }
        );


        const data = await response.json();


        if (!response.ok) {

            alert(
                data.message || "Unable to update task."
            );

            checkbox.checked = !checkbox.checked;

            return;
        }


        loadDashboard();

    } catch (error) {

        console.error("Task Error:", error);

        checkbox.checked = !checkbox.checked;

        alert(
            "Unable to connect with Dashboard Server."
        );
    }
}


/* =========================================================
   Logout
   ========================================================= */

async function logout() {

    const confirmLogout =
        confirm("Are you sure you want to logout?");


    if (!confirmLogout) {
        return;
    }


    try {

        const response = await fetch(
            `${AUTH_URL}/logout`,
            {
                method: "GET",
                credentials: "include"
            }
        );


        localStorage.removeItem("user");
        window.location.href = `${AUTH_URL}/`;

    } catch (error) {

        console.error("Logout Error:", error);
        localStorage.removeItem("user");
        window.location.href = `${AUTH_URL}/`;
    }
}


/* =========================================================
   Start Dashboard
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    loadDashboard
);
