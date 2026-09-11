const $ = (id) => document.getElementById(id);

let discussions = [];
let organizations = [];
let selectedDiscussionId = null;
let searchTimer = null;

let currentUser = JSON.parse(localStorage.getItem("user") || "{}");
let currentUserId = Number(currentUser.id || currentUser.user_id);

function safe(value) {
    return String(value || "").replace(/[&<>'"]/g, (character) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "'": "&#39;",
        '"': "&quot;"
    }[character]));
}

function toast(message) {
    $("toast").textContent = message;
    $("toast").classList.add("show");
    setTimeout(() => $("toast").classList.remove("show"), 2800);
}

function getInitials(name) {
    return String(name || "U")
        .trim()
        .split(/\s+/)
        .slice(0, 2)
        .map((part) => part.charAt(0).toUpperCase())
        .join("") || "U";
}

async function requireLoggedInUser() {
    if (Number.isInteger(currentUserId) && currentUserId > 0) {
        return true;
    }

    try {
        const response = await fetch("http://127.0.0.1:5001/check-login", {
            credentials: "include"
        });
        const data = await response.json();

        if (data.logged_in && data.user?.id) {
            currentUser = data.user;
            currentUserId = Number(data.user.id);
            localStorage.setItem("user", JSON.stringify(data.user));
            return true;
        }
    } catch (error) {
        console.error("Login check failed:", error);
    }

    window.location.href = "http://127.0.0.1:5001/";
    return false;
}

function buildQuery() {
    const params = new URLSearchParams();
    params.set("user_id", currentUserId);

    const search = $("searchInput").value.trim();
    const orgId = $("organizationFilter").value;

    if (search) {
        params.set("search", search);
    }

    if (orgId) {
        params.set("org_id", orgId);
    }

    return params.toString();
}

function renderOrganizationOptions() {
    const filterOptions = ['<option value="">All organizations</option>'];
    const formOptions = ['<option value="">Choose organization</option>'];

    organizations.forEach((organization) => {
        const option = `<option value="${organization.org_id}">${safe(organization.name)}</option>`;
        filterOptions.push(option);
        formOptions.push(option);
    });

    $("organizationFilter").innerHTML = filterOptions.join("");
    $("discussionOrganization").innerHTML = formOptions.join("");
    $("orgCount").textContent = organizations.length;
}

function renderStats() {
    $("totalCount").textContent = discussions.length;
    $("myCount").textContent = discussions.filter((discussion) => discussion.is_owner).length;
}

function renderEmptyDetail() {
    selectedDiscussionId = null;
    $("detailPanel").innerHTML = `
        <div class="empty-detail">
            <i class="fa-solid fa-comments"></i>
            <h2>Select a discussion</h2>
            <p>Open a discussion to read the full post and manage your own entries.</p>
        </div>
    `;
}

function renderDiscussions() {
    renderStats();

    if (!discussions.length) {
        $("discussionList").innerHTML = '<p class="state-message">No discussions found. Start the first conversation for your community.</p>';
        renderEmptyDetail();
        return;
    }

    $("discussionList").innerHTML = discussions.map((discussion) => `
        <button class="discussion-card ${discussion.discussion_id === selectedDiscussionId ? "active" : ""}" type="button" onclick="openDiscussion(${discussion.discussion_id})">
            <div class="discussion-meta">
                <span class="pill"><i class="fa-solid fa-building-user"></i> ${safe(discussion.organization_name)}</span>
                <span><i class="fa-regular fa-calendar"></i> ${safe(discussion.created_at)}</span>
            </div>
            <h3>${safe(discussion.title)}</h3>
            <p>${safe(discussion.content)}</p>
        </button>
    `).join("");
}

function renderDiscussionDetail(discussion) {
    selectedDiscussionId = discussion.discussion_id;
    renderDiscussions();

    $("detailPanel").innerHTML = `
        <div class="detail-header">
            <div class="detail-title-row">
                <div>
                    <span class="eyebrow">${safe(discussion.organization_category)}</span>
                    <h2>${safe(discussion.title)}</h2>
                </div>
                <span class="pill"><i class="fa-solid fa-building-user"></i> ${safe(discussion.organization_name)}</span>
            </div>
            <div class="author-row">
                <span class="author-avatar">${safe(getInitials(discussion.author))}</span>
                <span>Posted by <strong>${safe(discussion.author)}</strong> on ${safe(discussion.created_at)}</span>
            </div>
        </div>
        <div class="detail-content">${safe(discussion.content)}</div>
        <div class="detail-actions">
            ${discussion.is_owner ? `
                <button class="secondary-button" type="button" onclick="openEditPanel(${discussion.discussion_id})">
                    <i class="fa-solid fa-pen"></i> Edit
                </button>
                <button class="danger-button" type="button" onclick="deleteDiscussion(${discussion.discussion_id})">
                    <i class="fa-solid fa-trash"></i> Delete
                </button>
            ` : '<span class="pill"><i class="fa-solid fa-lock"></i> Author only controls</span>'}
        </div>
    `;
}

async function loadOrganizations() {
    try {
        const response = await fetch("/api/organizations");
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.message || "Unable to load organizations.");
        }

        organizations = data.organizations || [];
        renderOrganizationOptions();
    } catch (error) {
        organizations = [];
        renderOrganizationOptions();
        toast(error.message || "Organizations could not be loaded.");
    }
}

async function loadDiscussions() {
    $("discussionList").innerHTML = '<p class="state-message">Loading discussions...</p>';

    try {
        const response = await fetch(`/api/discussions?${buildQuery()}`);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.message || "Unable to load discussions.");
        }

        discussions = data.discussions || [];
        const selected = discussions.find((discussion) => discussion.discussion_id === selectedDiscussionId);
        renderDiscussions();

        if (selected) {
            renderDiscussionDetail(selected);
        } else if (!discussions.length) {
            renderEmptyDetail();
        }
    } catch (error) {
        discussions = [];
        renderStats();
        $("discussionList").innerHTML = '<p class="state-message">Discussions could not be loaded. Please check the Flask server and database.</p>';
        renderEmptyDetail();
        toast(error.message || "Unable to load discussions.");
    }
}

async function openDiscussion(discussionId) {
    try {
        const response = await fetch(`/api/discussions/${discussionId}?user_id=${currentUserId}`);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.message || "Unable to open discussion.");
        }

        renderDiscussionDetail(data.discussion);
    } catch (error) {
        toast(error.message || "Unable to open discussion.");
    }
}

function openCreatePanel() {
    $("discussionForm").reset();
    $("discussionId").value = "";
    $("discussionOrganization").disabled = false;
    $("modalEyebrow").textContent = "Start a conversation";
    $("modalTitle").textContent = "Create discussion";
    $("saveButton").textContent = "Create discussion";
    $("discussionModal").classList.add("show");
}

function openEditPanel(discussionId) {
    const discussion = discussions.find((item) => item.discussion_id === discussionId);
    if (!discussion) {
        toast("Please open this discussion again before editing.");
        return;
    }

    $("discussionId").value = discussion.discussion_id;
    $("discussionOrganization").value = discussion.org_id;
    $("discussionOrganization").disabled = true;
    $("discussionTitle").value = discussion.title;
    $("discussionContent").value = discussion.content;
    $("modalEyebrow").textContent = "Update your post";
    $("modalTitle").textContent = "Edit discussion";
    $("saveButton").textContent = "Save changes";
    $("discussionModal").classList.add("show");
}

function closeDiscussionModal() {
    $("discussionModal").classList.remove("show");
    $("discussionOrganization").disabled = false;
}

async function saveDiscussion(event) {
    event.preventDefault();

    const discussionId = $("discussionId").value;
    const payload = {
        org_id: Number($("discussionOrganization").value),
        title: $("discussionTitle").value.trim(),
        content: $("discussionContent").value.trim(),
        user_id: currentUserId
    };

    const url = discussionId ? `/api/discussions/${discussionId}` : "/api/discussions";
    const method = discussionId ? "PUT" : "POST";

    try {
        const response = await fetch(url, {
            method,
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.message || "Unable to save discussion.");
        }

        closeDiscussionModal();
        selectedDiscussionId = data.discussion.discussion_id;
        toast(data.message || "Discussion saved.");
        await loadDiscussions();
        renderDiscussionDetail(data.discussion);
    } catch (error) {
        toast(error.message || "Unable to save discussion.");
    }
}

async function deleteDiscussion(discussionId) {
    if (!confirm("Delete this discussion?")) {
        return;
    }

    try {
        const response = await fetch(`/api/discussions/${discussionId}?user_id=${currentUserId}`, {
            method: "DELETE"
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.message || "Unable to delete discussion.");
        }

        selectedDiscussionId = null;
        toast(data.message || "Discussion deleted.");
        await loadDiscussions();
    } catch (error) {
        toast(error.message || "Unable to delete discussion.");
    }
}

async function logoutUser() {
    localStorage.removeItem("user");
    try {
        await fetch("http://127.0.0.1:5001/logout", {
            method: "GET",
            credentials: "include"
        });
    } catch (error) {
        console.error("Logout failed:", error);
    }
    window.location.href = "http://127.0.0.1:5001/";
}

function scheduleSearch() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(loadDiscussions, 250);
}

document.addEventListener("DOMContentLoaded", async () => {
    const loggedIn = await requireLoggedInUser();
    if (!loggedIn) {
        return;
    }

    await loadOrganizations();
    await loadDiscussions();

    $("searchInput").addEventListener("input", scheduleSearch);
    $("organizationFilter").addEventListener("change", loadDiscussions);
    $("discussionForm").addEventListener("submit", saveDiscussion);
    $("discussionModal").addEventListener("click", (event) => {
        if (event.target === $("discussionModal")) {
            closeDiscussionModal();
        }
    });
});
