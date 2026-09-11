(() => {
	"use strict";

	const currentUserId = 1;
	const maxImageSize = 5 * 1024 * 1024;
	const allowedImageTypes = ["image/png", "image/jpeg", "image/jpg", "image/webp"];
	const state = {
		organizations: [],
		selectedCategory: "all",
		selectedOrganization: null,
		selectedDiscussion: null
	};
	const courseCatalog = {
		Yoga: [
			["Morning mobility flow", "Wake up the body with a 14-day guided practice.", "bi-sunrise"],
			["Foundations of balance", "Build strength, steadiness and confidence on the mat.", "bi-person-arms-up"]
		],
		Meditation: [
			["The calm mind series", "Short guided practices for a clearer, quieter day.", "bi-moon-stars"],
			["Breathwork basics", "Learn simple breathing patterns for everyday regulation.", "bi-wind"]
		],
		Fitness: [
			["Strong at home", "A progressive plan for strength, mobility and recovery.", "bi-lightning-charge"],
			["Move without pain", "Practical mobility sessions for a capable body.", "bi-universal-access"]
		],
		Ayurveda: [
			["Seasonal living 101", "Simple rituals for a more balanced daily rhythm.", "bi-leaf"],
			["Kitchen remedies", "Explore nourishing, everyday Ayurvedic ingredients.", "bi-cup-hot"]
		]
	};
	const starterOrganizations = [
		["Morning Flow Collective", "Yoga", "A welcoming community for energising morning yoga and mindful movement.", "public"],
		["Stillness Circle", "Meditation", "Guided meditation, breathwork and simple practices for a calmer mind.", "public"],
		["Mindful Living Guild", "Lifestyle", "Practical conversations for building a more present and intentional life.", "public"],
		["Rooted Ayurveda Community", "Ayurveda", "Explore seasonal wellbeing and balanced living with a supportive community.", "public"],
		["Strong Body, Soft Mind", "Fitness", "Sustainable fitness, recovery, mobility and the habits that keep us going.", "public"],
		["The Inner Compass", "Spirituality", "Thoughtful discussions about spirituality, reflection and personal growth.", "public"],
		["Breathe Well Network", "Mental Wellness", "Peer support for stress management and mindful breathing practices.", "public"],
		["Sunrise Yoga Studio", "Yoga", "Accessible yoga sessions for every experience level and every body.", "public"],
		["Quiet Minds Fellowship", "Meditation", "A respectful private community for deeper meditation and reflection.", "private"],
		["Wellness Makers Hub", "Lifestyle", "Share realistic wellbeing goals, useful resources and encouragement.", "public"]
	].map(([name, category, description, privacy], index) => ({
		org_id: `starter-${index + 1}`,
		name,
		category,
		description,
		privacy,
		member_count: 0,
		discussion_count: 0,
		created_at: new Date().toISOString()
	}));

	const $ = (id) => document.getElementById(id);

	const escapeText = (value) => String(value ?? "");

	async function apiRequest(url, options = {}) {
		const response = await fetch(url, options);
		let payload = {};
		try {
			payload = await response.json();
		} catch (error) {
			payload = {};
		}
		if (!response.ok) {
			const messages = {
				401: "Please sign in to continue.",
				403: "You do not have permission to do that.",
				404: "The requested item could not be found.",
				409: "You are already a member of this organization."
			};
			throw new Error(messages[response.status] || payload.message || "Something went wrong.");
		}
		return payload;
	}

	function showToast(message, isError = false) {
		const toast = $("appToast");
		$("toastMessage").textContent = message;
		toast.classList.toggle("text-bg-danger", isError);
		toast.classList.toggle("text-bg-success", !isError);
		bootstrap.Toast.getOrCreateInstance(toast, { delay: 3500 }).show();
	}

	function setLoading(isLoading) {
		$("loading").classList.toggle("d-none", !isLoading);
	}

	function imageOrFallback(url, kind = "cover") {
		const wrapper = document.createElement("div");
		wrapper.className = kind === "cover" ? "card-cover-placeholder" : "card-logo-placeholder";
		const icon = document.createElement("i");
		icon.className = kind === "cover" ? "bi bi-flower1" : "bi bi-people-fill";
		wrapper.appendChild(icon);
		if (url) {
			const image = document.createElement("img");
			image.src = url;
			image.alt = kind === "cover" ? "" : "Organization logo";
			image.addEventListener("error", () => image.replaceWith(wrapper.cloneNode(true)), { once: true });
			wrapper.appendChild(image);
		}
		return wrapper;
	}

	function renderOrganizations() {
		const container = $("organizationContainer");
		const query = $("searchInput").value.trim().toLowerCase();
		container.replaceChildren();
		const organizations = state.organizations.filter((organization) => {
			const matchesCategory = state.selectedCategory === "all"
				|| String(organization.category || "").toLowerCase() === state.selectedCategory.toLowerCase();
			const searchable = `${organization.name || ""} ${organization.description || ""} ${organization.category || ""}`.toLowerCase();
			return matchesCategory && searchable.includes(query);
		});
		$("noResults").classList.toggle("d-none", organizations.length > 0);
		organizations.forEach((organization) => container.appendChild(createOrganizationCard(organization)));
	}

	function createOrganizationCard(organization) {
		const column = document.createElement("div");
		column.className = "col-md-6 col-lg-4";
		const card = document.createElement("article");
		card.className = "organization-card";
		const cover = imageOrFallback(organization.cover_image_url, "cover");
		cover.classList.add("card-cover");
		const logo = imageOrFallback(organization.logo_url, "logo");
		logo.classList.add("card-logo");
		const body = document.createElement("div");
		body.className = "card-body";
		const title = document.createElement("h3");
		title.className = "org-title";
		title.textContent = escapeText(organization.name);
		const category = document.createElement("span");
		category.className = "org-category";
		category.textContent = escapeText(organization.category || "Wellness");
		const description = document.createElement("p");
		description.className = "org-description";
		description.textContent = escapeText(organization.description || "A welcoming wellness community.");
		const meta = document.createElement("div");
		meta.className = "org-meta";
		meta.textContent = `${organization.privacy || "public"} community`;
		const button = document.createElement("button");
		button.className = "btn btn-outline-success w-100 mt-3";
		button.type = "button";
		button.innerHTML = '<i class="bi bi-arrow-up-right me-1"></i> View Profile';
		button.addEventListener("click", () => loadOrganizationDetails(organization.org_id));
		body.append(title, category, description, meta, button);
		card.append(cover, logo, body);
		column.appendChild(card);
		return column;
	}

	async function loadOrganizations() {
		setLoading(true);
		try {
			const payload = await apiRequest("/api/organisations");
			state.organizations = payload.organisations || payload.organizations || [];
			const existingNames = new Set(state.organizations.map((organization) => organization.name));
			if (state.organizations.length < 10) {
				state.organizations = state.organizations.concat(
					starterOrganizations.filter((organization) => !existingNames.has(organization.name))
				).slice(0, 10);
			}
			renderOrganizations();
		} catch (error) {
			state.organizations = starterOrganizations;
			renderOrganizations();
			showToast("Showing starter communities. Connect the database to load live organizations.");
		} finally {
			setLoading(false);
		}
	}

	async function loadOrganizationDetails(orgId) {
		try {
			const payload = await apiRequest(`/api/organisations/${orgId}`);
			state.selectedOrganization = payload.organisation || payload.organization;
			renderOrganizationDetails(state.selectedOrganization);
			await loadMembers(orgId);
			const modal = bootstrap.Modal.getOrCreateInstance($("organizationModal"));
			modal.show();
		} catch (error) {
			const fallback = state.organizations.find((organization) => String(organization.org_id) === String(orgId));
			if (!fallback) {
				showToast(error.message, true);
				return;
			}
			state.selectedOrganization = fallback;
			renderOrganizationDetails(fallback);
			$("memberContainer").innerHTML = '<p class="text-muted">Connect the database to load members.</p>';
			bootstrap.Modal.getOrCreateInstance($("organizationModal")).show();
		}
	}

	function renderOrganizationDetails(organization) {
		$("organizationModalTitle").textContent = organization.name || "Organization Details";
		$("detailName").textContent = organization.name || "";
		$("detailCategory").textContent = organization.category || "Wellness";
		$("detailPrivacy").textContent = organization.privacy || "public";
		$("detailDescription").textContent = organization.description || "No description provided.";
		$("detailMembers").textContent = organization.member_count ?? 0;
		$("detailDiscussions").textContent = organization.discussion_count ?? 0;
		$("detailCreated").textContent = organization.created_at ? new Date(organization.created_at).toLocaleDateString() : "-";
		$("organizationCover").replaceChildren(imageOrFallback(organization.cover_image_url, "cover"));
		$("organizationCover").firstElementChild.classList.add("organization-cover-image");
		$("organizationLogo").replaceChildren(imageOrFallback(organization.logo_url, "logo"));
		$("joinLeaveBtn").dataset.orgId = organization.org_id;
		renderCourses(organization.category);
	}

	function renderCourses(category) {
		const courses = courseCatalog[category] || [
			["Mindful everyday habits", "A practical collection of routines for lasting wellbeing.", "bi-stars"],
			["Community reset", "A gentle guided path to reconnect with your intention.", "bi-heart"]
		];
		const container = $("courseContainer");
		container.replaceChildren();
		courses.forEach(([title, description, icon]) => {
			const card = document.createElement("article");
			card.className = "course-card";
			const iconElement = document.createElement("span");
			iconElement.className = "course-card-icon";
			iconElement.innerHTML = `<i class="bi ${icon}"></i>`;
			const heading = document.createElement("h6");
			heading.textContent = title;
			const text = document.createElement("p");
			text.textContent = description;
			card.append(iconElement, heading, text);
			container.appendChild(card);
		});
	}

	async function loadMembers(orgId) {
		const container = $("memberContainer");
		container.textContent = "Loading members...";
		try {
			const payload = await apiRequest(`/api/organisations/${orgId}/members`);
			const members = payload.members || [];
			container.replaceChildren();
			if (!members.length) {
				container.textContent = "No members yet.";
				return;
			}
			members.forEach((member) => {
				const item = document.createElement("div");
				item.className = "member-item";
				const avatar = document.createElement("div");
				avatar.className = "member-avatar";
				avatar.textContent = escapeText((member.name || member.full_name || "M").charAt(0).toUpperCase());
				const info = document.createElement("div");
				const name = document.createElement("p");
				name.className = "member-name";
				name.textContent = member.name || member.full_name || `User ${member.user_id}`;
				const role = document.createElement("span");
				role.className = "member-role";
				role.textContent = member.role || "Member";
				info.append(name, role);
				item.append(avatar, info);
				container.appendChild(item);
			});
		} catch (error) {
			container.textContent = "Members could not be loaded.";
		}
	}

	async function joinOrLeaveOrganization() {
		const button = $("joinLeaveBtn");
		const orgId = button.dataset.orgId;
		const leaving = button.dataset.member === "true";
		try {
			await apiRequest(`/api/organisations/${orgId}/${leaving ? "leave" : "join"}`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ user_id: currentUserId })
			});
			showToast(leaving ? "Left organization successfully." : "Joined organization successfully.");
			await loadOrganizationDetails(orgId);
		} catch (error) {
			showToast(error.message, true);
		}
	}

	function showImagePreview(input, previewId) {
		const file = input.files[0];
		const preview = $(previewId);
		if (!file) return;
		if (!allowedImageTypes.includes(file.type) || file.size > maxImageSize) {
			input.value = "";
			preview.replaceChildren();
			preview.classList.add("d-none");
			showToast("Choose a PNG, JPG, JPEG or WEBP image up to 5 MB.", true);
			return;
		}
		const image = document.createElement("img");
		image.src = URL.createObjectURL(file);
		image.alt = "Selected image preview";
		const name = document.createElement("span");
		name.className = "upload-preview-name";
		name.textContent = file.name;
		const remove = document.createElement("button");
		remove.className = "upload-preview-remove";
		remove.type = "button";
		remove.textContent = "Remove";
		remove.addEventListener("click", () => {
			input.value = "";
			preview.replaceChildren();
			preview.classList.add("d-none");
		});
		preview.replaceChildren(image, name, remove);
		preview.classList.remove("d-none");
	}

	async function createOrganization(event) {
		event.preventDefault();
		const form = $("createOrganisationForm");
		const organizationData = {
			name: $("orgName").value.trim(),
			category: $("orgCategory").value,
			privacy: $("orgPrivacy").value,
			description: $("orgDescription").value.trim(),
			created_by: Number($("createdBy").value || currentUserId)
		};
		try {
			await apiRequest("/api/organisations", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(organizationData)
			});
			showToast("Organization created successfully.");
			form.reset();
			$("orgLogoPreview").replaceChildren();
			$("orgCoverPreview").replaceChildren();
			$("orgLogoPreview").classList.add("d-none");
			$("orgCoverPreview").classList.add("d-none");
			closeCreateOrganisationModal();
			await loadOrganizations();
		} catch (error) {
			showToast(error.message, true);
		}
	}

	async function loadDiscussions(orgId) {
		const container = $("discussionContainer");
		container.replaceChildren();
		try {
			const payload = await apiRequest(`/api/organisations/${orgId}/discussions`);
			const discussions = payload.discussions || [];
			discussions.forEach((discussion) => {
				const column = document.createElement("div");
				column.className = "col-md-6 col-lg-4";
				const card = document.createElement("article");
				card.className = "discussion-card";
				const title = document.createElement("h5");
				title.textContent = discussion.title || "Untitled discussion";
				const content = document.createElement("p");
				content.textContent = discussion.content || "";
				const button = document.createElement("button");
				button.className = "btn btn-sm btn-outline-success";
				button.type = "button";
				button.textContent = "View comments";
				button.addEventListener("click", () => loadComments(discussion.discussion_id));
				card.append(title, content, button);
				column.appendChild(card);
				container.appendChild(column);
			});
		} catch (error) {
			showToast(error.message, true);
		}
	}

	async function loadComments(discussionId) {
		try {
			const payload = await apiRequest(`/api/discussions/${discussionId}/comments`);
			state.selectedDiscussion = discussionId;
			const comments = payload.comments || [];
			const list = $("discussionList");
			list.replaceChildren();
			comments.forEach((comment) => {
				const item = document.createElement("div");
				item.className = "discussion-list-item";
				const author = document.createElement("h6");
				author.textContent = comment.author_name || `User ${comment.user_id}`;
				const text = document.createElement("p");
				text.textContent = comment.content || "";
				item.append(author, text);
				list.appendChild(item);
			});
			bootstrap.Modal.getOrCreateInstance($("discussionModal")).show();
		} catch (error) {
			showToast(error.message, true);
		}
	}

	async function createDiscussion(event) {
		event.preventDefault();
		const orgId = $("discussionOrgId").value;
		try {
			await apiRequest(`/api/organisations/${orgId}/discussions`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ user_id: currentUserId, title: $("discussionTitle").value.trim(), content: $("discussionContent").value.trim() })
			});
			showToast("Discussion created successfully.");
			$("createDiscussionForm").reset();
			await loadDiscussions(orgId);
		} catch (error) {
			showToast(error.message, true);
		}
	}

	function bindUpload(inputId, previewId) {
		const input = $(inputId);
		const zone = input.closest(".upload-zone");
		input.addEventListener("change", () => showImagePreview(input, previewId));
		["dragenter", "dragover"].forEach((eventName) => zone.addEventListener(eventName, (event) => {
			event.preventDefault();
			zone.classList.add("is-dragover");
		}));
		["dragleave", "drop"].forEach((eventName) => zone.addEventListener(eventName, (event) => {
			event.preventDefault();
			zone.classList.remove("is-dragover");
		}));
		zone.addEventListener("drop", (event) => {
			input.files = event.dataTransfer.files;
			input.dispatchEvent(new Event("change"));
		});
	}

	function openCreateOrganisationModal() {
		const modalElement = $("createOrganisationModal");
		if (window.bootstrap && bootstrap.Modal) {
			bootstrap.Modal.getOrCreateInstance(modalElement).show();
			return;
		}
		modalElement.classList.add("show");
		modalElement.style.display = "block";
		modalElement.removeAttribute("aria-hidden");
		modalElement.setAttribute("aria-modal", "true");
		document.body.classList.add("modal-open");
		const backdrop = document.createElement("div");
		backdrop.className = "modal-backdrop fade show frontend-modal-backdrop";
		backdrop.addEventListener("click", closeCreateOrganisationModal);
		document.body.appendChild(backdrop);
	}

	function closeCreateOrganisationModal() {
		const modalElement = $("createOrganisationModal");
		if (window.bootstrap && bootstrap.Modal) {
			bootstrap.Modal.getOrCreateInstance(modalElement).hide();
			return;
		}
		modalElement.classList.remove("show");
		modalElement.style.display = "none";
		modalElement.setAttribute("aria-hidden", "true");
		document.body.classList.remove("modal-open");
		document.querySelector(".frontend-modal-backdrop")?.remove();
	}

	document.addEventListener("DOMContentLoaded", () => {
		loadOrganizations();
		$("openCreateOrganisationButton").addEventListener("click", openCreateOrganisationModal);
		$("createOrganisationForm").addEventListener("submit", createOrganization);
		$("createDiscussionForm").addEventListener("submit", createDiscussion);
		$("joinLeaveBtn").addEventListener("click", joinOrLeaveOrganization);
		$("searchInput").addEventListener("input", renderOrganizations);
		$("searchBtn").addEventListener("click", renderOrganizations);
		document.querySelectorAll(".category-btn").forEach((button) => button.addEventListener("click", () => {
			state.selectedCategory = button.dataset.category;
			document.querySelectorAll(".category-btn").forEach((item) => item.classList.toggle("active", item === button));
			renderOrganizations();
		}));
		$("viewDiscussionBtn").addEventListener("click", () => {
			if (state.selectedOrganization) {
				$("discussionOrgId").value = state.selectedOrganization.org_id;
				loadDiscussions(state.selectedOrganization.org_id);
				document.querySelector("#discussions").scrollIntoView({ behavior: "smooth" });
			}
		});
		bindUpload("orgLogo", "orgLogoPreview");
		bindUpload("orgCover", "orgCoverPreview");
		document.querySelectorAll("#createOrganisationModal [data-bs-dismiss='modal']").forEach((button) => {
			button.addEventListener("click", closeCreateOrganisationModal);
		});
	});
})();
