const API_URL = window.location.origin;

let organizations = [];
let currentOrganization = null;
let currentCategory = "all";

const storedUser = JSON.parse(localStorage.getItem("user") || "null");
const USER_ID = Number(storedUser?.id || storedUser?.user_id || new URLSearchParams(window.location.search).get("user_id") || 1);

document.addEventListener("DOMContentLoaded", () => {
    loadOrganizations();

    document.getElementById("searchInput").addEventListener("input", debounce(loadOrganizations, 300));

    document.querySelectorAll(".category-btn").forEach(button => {
        button.addEventListener("click", () => {
            document.querySelectorAll(".category-btn").forEach(btn => btn.classList.remove("active"));
            button.classList.add("active");
            currentCategory = button.dataset.category;
            renderOrganizations();
        });
    });

    document.querySelectorAll(".profile-tab").forEach(tab => {
        tab.addEventListener("click", () => switchProfileTab(tab.dataset.tab));
    });

    document.getElementById("followBtn").addEventListener("click", toggleFollow);
    document.getElementById("createOrganizationForm").addEventListener("submit", createOrganization);
    document.getElementById("myOrganizationsBtn").addEventListener("click", loadMyOrganizations);

    document.getElementById("logoFile").addEventListener("change", previewImage);
    document.getElementById("coverFile").addEventListener("change", previewImage);
    document.getElementById("programImageFile").addEventListener("change", previewImage);
});

async function loadOrganizations() {
    const search = document.getElementById("searchInput").value.trim();

    showLoading(true);

    try {
        const url = `${API_URL}/api/organizations?user_id=${encodeURIComponent(USER_ID)}&search=${encodeURIComponent(search)}`;
        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Unable to load organizations.");
        }

        organizations = data.organizations || [];
        renderOrganizations();
    } catch (error) {
        console.error(error);
        document.getElementById("organizationGrid").innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger">${escapeHtml(error.message)}</div>
            </div>`;
    } finally {
        showLoading(false);
    }
}

function renderOrganizations() {
    const grid = document.getElementById("organizationGrid");

    let list = organizations;
    if (currentCategory !== "all") {
        list = list.filter(org => String(org.category || "") === currentCategory);
    }

    grid.innerHTML = "";

    if (!list.length) {
        document.getElementById("emptyState").classList.remove("d-none");
        return;
    }

    document.getElementById("emptyState").classList.add("d-none");

    list.forEach(org => {
        const coverStyle = org.cover_image_url
            ? `style="background-image:url('${safeCssUrl(org.cover_image_url)}')"`
            : "";

        const logo = org.logo_url
            ? `<img src="${safeUrl(org.logo_url)}" alt="${escapeHtml(org.name)} logo">`
            : `<i class="bi bi-people-fill"></i>`;

        grid.insertAdjacentHTML("beforeend", `
            <div class="col-md-6 col-xl-4">
                <article class="org-card" onclick="openOrganization(${Number(org.org_id)})">
                    <div class="org-cover" ${coverStyle}>
                        <span class="org-category">${escapeHtml(org.category || "Wellness")}</span>
                    </div>
                    <div class="org-card-body">
                        <div class="org-logo">${logo}</div>
                        <h4>${escapeHtml(org.name)}</h4>
                        <p>${escapeHtml(shortText(org.description || "A wellness community for mindful living.", 105))}</p>
                        <div class="org-meta">
                            <span><i class="bi bi-people"></i> ${formatNumber(org.follower_count || 0)} followers</span>
                            <span class="org-follow">
                                ${Number(org.is_following) ? "Following" : "Follow"}
                            </span>
                        </div>
                    </div>
                </article>
            </div>
        `);
    });
}

async function openOrganization(orgId) {
    try {
        const response = await fetch(`${API_URL}/api/organizations/${orgId}?user_id=${encodeURIComponent(USER_ID)}`);
        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Organization not found.");
        }

        currentOrganization = data.organization;
        renderProfile(currentOrganization);

        document.getElementById("discoverPage").classList.add("d-none");
        document.getElementById("profilePage").classList.remove("d-none");
        window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
        showToast(error.message, true);
    }
}

function renderProfile(org) {
    document.getElementById("profileName").textContent = org.name || "Organization";
    document.getElementById("profileCategory").textContent = org.category || "Wellness";
    document.getElementById("profilePrivacy").textContent = org.privacy === "private" ? "Private" : "Public";
    document.getElementById("profileDescription").textContent = org.description || "";
    document.getElementById("aboutText").textContent = org.description || "This organization provides wellness programs and community activities.";

    const cover = document.getElementById("profileCover");
    cover.style.backgroundImage = org.cover_image_url ? `url("${safeCssUrl(org.cover_image_url)}")` : "";

    const logo = document.getElementById("profileLogo");
    logo.innerHTML = org.logo_url
        ? `<img src="${safeUrl(org.logo_url)}" alt="${escapeHtml(org.name)} logo">`
        : `<i class="bi bi-people-fill"></i>`;

    const programs = org.programs || [];
    const members = org.members || [];

    document.getElementById("profileProgramCount").textContent = programs.length;
    document.getElementById("profileFollowerCount").textContent = formatNumber(org.follower_count || 0);
    document.getElementById("profileMemberCount").textContent = members.length || formatNumber(org.follower_count || 0);
    document.getElementById("profileRating").textContent = org.rating || "4.9";
    document.getElementById("reviewRating").textContent = org.rating || "4.9";

    const followBtn = document.getElementById("followBtn");
    if (Number(org.is_following)) {
        followBtn.classList.add("following");
        followBtn.innerHTML = `<i class="bi bi-check2"></i> Following`;
    } else {
        followBtn.classList.remove("following");
        followBtn.innerHTML = `<i class="bi bi-person-plus"></i> Follow`;
    }

    document.getElementById("aboutPoints").innerHTML = `
        <li><i class="bi bi-check-circle-fill"></i> Community-led wellness programs</li>
        <li><i class="bi bi-check-circle-fill"></i> Programs for different experience levels</li>
        <li><i class="bi bi-check-circle-fill"></i> Supportive wellness community</li>
    `;

    renderPrograms(programs);
    renderMembers(members);
    renderSocialLinks(org);
    updateOwnerControls(org);
    switchProfileTab("about");
}

function renderPrograms(programs) {
    const popular = document.getElementById("popularPrograms");
    const all = document.getElementById("allPrograms");
    const free = document.getElementById("freeSessions");

    if (!programs.length) {
        const empty = `<div class="col-12"><div class="alert alert-light border">No programs added yet.</div></div>`;
        popular.innerHTML = empty;
        all.innerHTML = empty;
        free.innerHTML = empty;
        return;
    }

    popular.innerHTML = programs.slice(0, 4).map(programCard).join("");
    all.innerHTML = programs.map(programCard).join("");

    const freePrograms = programs.filter(p => String(p.access_type).toLowerCase() === "free");
    free.innerHTML = freePrograms.length
        ? freePrograms.map(programCard).join("")
        : `<div class="col-12"><div class="alert alert-light border">No free sessions available.</div></div>`;
}

function programCard(program) {
    const image = program.image_url
        ? `style="background-image:url('${safeCssUrl(program.image_url)}')"`
        : `class="program-image program-image-fallback"`;

    const isFree = String(program.access_type || "").toLowerCase() === "free";
    const price = isFree ? "FREE" : (program.price || "Premium");

    return `
        <div class="col-md-6 col-xl-3">
            <div class="program-card">
                <div ${image.startsWith("class=") ? image : `class="program-image" ${image}`}></div>
                <div class="program-body">
                    <h5>${escapeHtml(program.title || "Wellness Program")}</h5>
                    <p>${escapeHtml(shortText(program.description || "Wellness program by this organization.", 85))}</p>
                    <div class="d-flex justify-content-between align-items-center gap-2">
                        <span class="program-price ${isFree ? "program-free" : ""}">${escapeHtml(price)}</span>
                        <small class="text-muted">${escapeHtml(program.duration || "")}</small>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderMembers(members) {
    const container = document.getElementById("memberPreview");

    if (!members.length) {
        container.innerHTML = `<small class="text-muted">No members to display yet.</small>`;
        return;
    }

    container.innerHTML = members.slice(0, 5).map(member => {
        const name = member.full_name || "Member";
        const avatar = member.profile_image
            ? `<img src="${safeUrl(member.profile_image)}" alt="">`
            : escapeHtml(name.charAt(0).toUpperCase());

        return `
            <div class="member-mini">
                <div class="member-mini-avatar">${avatar}</div>
                <div>
                    <strong>${escapeHtml(name)}</strong>
                    <small>${escapeHtml(member.role || "member")}</small>
                </div>
            </div>
        `;
    }).join("");
}

function renderSocialLinks(org) {
    const container = document.getElementById("socialLinks");
    const links = [
        ["instagram", org.instagram, "bi-instagram"],
        ["youtube", org.youtube, "bi-youtube"],
        ["facebook", org.facebook, "bi-facebook"],
        ["twitter", org.twitter, "bi-twitter-x"]
    ];

    container.innerHTML = links
        .filter(item => item[1])
        .map(item => `<a href="${safeUrl(item[1])}" target="_blank" rel="noopener" aria-label="${item[0]}"><i class="bi ${item[2]}"></i></a>`)
        .join("") || `<span class="text-muted small">Social links not added.</span>`;

    const website = document.getElementById("websiteLink");
    if (org.website) {
        website.href = safeUrl(org.website);
        website.textContent = org.website;
    } else {
        website.removeAttribute("href");
        website.textContent = "Website not added";
    }
}

function updateOwnerControls(org) {
    const button = document.getElementById("addProgramBtn");
    if (Number(org.is_owner)) {
        button.classList.remove("d-none");
    } else {
        button.classList.add("d-none");
    }
}

async function toggleFollow() {
    if (!currentOrganization) return;

    try {
        const response = await fetch(
            `${API_URL}/api/organizations/${currentOrganization.org_id}/follow?user_id=${encodeURIComponent(USER_ID)}`,
            { method: "POST" }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Unable to follow organization.");
        }

        await openOrganization(currentOrganization.org_id);
        showToast(data.message || "Updated.");
    } catch (error) {
        showToast(error.message, true);
    }
}

async function createOrganization(event) {
    event.preventDefault();

    const form = document.getElementById("createOrganizationForm");
    const formData = new FormData(form);
    formData.append("created_by", USER_ID);

    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    button.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Creating...`;

    try {
        const response = await fetch(`${API_URL}/api/organizations`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Unable to create organization.");
        }

        const modalElement = document.getElementById("createOrganizationModal");
        bootstrap.Modal.getOrCreateInstance(modalElement).hide();

        form.reset();
        resetPreviews();

        showToast("Organization created successfully.");
        await loadOrganizations();

        if (data.organization_id) {
            await openOrganization(data.organization_id);
        }
    } catch (error) {
        document.getElementById("createMessage").innerHTML =
            `<div class="alert alert-danger">${escapeHtml(error.message)}</div>`;
    } finally {
        button.disabled = false;
        button.innerHTML = `<i class="bi bi-check2-circle"></i> Create Organization`;
    }
}

async function loadMyOrganizations() {
    const list = organizations.filter(org => Number(org.is_owner) === 1);

    if (!list.length) {
        showToast("You have not created an organization yet.");
        return;
    }

    const first = list[0];
    await openOrganization(first.org_id);
}

function switchProfileTab(tabName) {
    document.querySelectorAll(".profile-tab").forEach(tab => {
        tab.classList.toggle("active", tab.dataset.tab === tabName);
    });

    document.querySelectorAll(".profile-tab-content").forEach(content => {
        content.classList.add("d-none");
    });

    const target = document.getElementById(`${tabName}Tab`);
    if (target) target.classList.remove("d-none");
}

function showDiscover() {
    document.getElementById("profilePage").classList.add("d-none");
    document.getElementById("discoverPage").classList.remove("d-none");
    loadOrganizations();
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function goBack() {
    if (!document.getElementById("profilePage").classList.contains("d-none")) {
        showDiscover();
    } else {
        window.history.back();
    }
}

function previewImage(event) {
    const input = event.target;
    const previewId = input.id === "logoFile" ? "logoPreview" : "coverPreview";
    const preview = document.getElementById(previewId);
    const file = input.files[0];

    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
        preview.innerHTML = `<img src="${reader.result}" alt="Preview">`;
    };
    reader.readAsDataURL(file);
}

function resetPreviews() {
    document.getElementById("logoPreview").innerHTML = `<i class="bi bi-image"></i>`;
    document.getElementById("coverPreview").innerHTML = `<i class="bi bi-image"></i>`;
    document.getElementById("createMessage").innerHTML = "";
}

function showLoading(show) {
    document.getElementById("loadingState").style.display = show ? "block" : "none";
}

function showToast(message, error = false) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.style.background = error ? "#b42318" : "#1f2d26";
    toast.classList.add("show");

    setTimeout(() => toast.classList.remove("show"), 2800);
}

function formatNumber(value) {
    const number = Number(value) || 0;
    if (number >= 1000000) return (number / 1000000).toFixed(1).replace(".0", "") + "M";
    if (number >= 1000) return (number / 1000).toFixed(1).replace(".0", "") + "K";
    return number.toString();
}

function shortText(text, length) {
    return text.length > length ? text.substring(0, length - 3) + "..." : text;
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function safeUrl(value) {
    const url = String(value || "");
    if (url.startsWith("/") || url.startsWith("http://") || url.startsWith("https://")) {
        return escapeHtml(url);
    }
    return "";
}

function safeCssUrl(value) {
    return String(value || "")
        .replaceAll("\\", "")
        .replaceAll("'", "%27")
        .replaceAll('"', "%22")
        .replaceAll("(", "%28")
        .replaceAll(")", "%29");
}

function debounce(fn, delay) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}
