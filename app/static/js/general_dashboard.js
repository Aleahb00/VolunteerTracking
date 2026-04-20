document.addEventListener('DOMContentLoaded', function () {
	function getCookie(name) {
		let cookieValue = null;
		if (document.cookie && document.cookie !== '') {
			const cookies = document.cookie.split(';');
			for (let i = 0; i < cookies.length; i++) {
				const cookie = cookies[i].trim();
				if (cookie.substring(0, name.length + 1) === (name + '=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
		return cookieValue;
	}

	function updateFlagButtonIcon(button, flagged) {
		if (!button) {
			return;
		}

		button.innerHTML = flagged ? '<i data-lucide="flag-off"></i>' : '<i data-lucide="flag"></i>';
		button.setAttribute('aria-label', flagged ? 'Unflag submission' : 'Flag submission');
		if (typeof lucide !== 'undefined' && typeof lucide.createIcons === 'function') {
			lucide.createIcons();
		}
	}

	function toggleFlaggedStatus(volunteerId, triggerButton) {
		fetch(`/toggle_flagged_status/${volunteerId}/`, {
			method: 'POST',
			credentials: 'same-origin',
			headers: {
				'X-CSRFToken': getCookie('csrftoken'),
				'Content-Type': 'application/json'
			}
		})
			.then(response => response.json())
			.then(data => {
				if (data.status === 'success') {
					updateFlagButtonIcon(triggerButton, data.flagged);
				} else {
					showDashboardMessage('Error toggling flagged status.', 'error');
				}
			})
			.catch(() => {
				showDashboardMessage('An error occurred while toggling flagged status.', 'error');
			});
	}

	function toggleDonationFlaggedStatus(donationId, triggerButton) {
		fetch(`/toggle_donation_flagged_status/${donationId}/`, {
			method: 'POST',
			credentials: 'same-origin',
			headers: {
				'X-CSRFToken': getCookie('csrftoken'),
				'Content-Type': 'application/json'
			}
		})
			.then(response => response.json())
			.then(data => {
				if (data.status === 'success') {
					updateFlagButtonIcon(triggerButton, data.flagged);
				} else {
					showDashboardMessage('Error toggling donation flagged status.', 'error');
				}
			})
			.catch(() => {
				showDashboardMessage('An error occurred while toggling donation flagged status.', 'error');
			});
	}

	const messageContainer = document.querySelector('.dashboard-messages');
	const projectToggle = document.getElementById('show-inactive-projects');
	const projectSearchInput = document.getElementById('disaster-search-input');
	const projectItems = Array.from(document.querySelectorAll('.disaster-item[data-active]'));
	const projectsEmptyState = document.querySelector('.js-projects-empty');

	function showDashboardMessage(message, type = 'success') {
		if (!messageContainer || !message) {
			return;
		}

		const toast = document.createElement('p');
		toast.className = `dashboard-message ${type}`;
		toast.setAttribute('role', 'status');

		const text = document.createElement('span');
		text.textContent = message;

		const closeButton = document.createElement('button');
		closeButton.type = 'button';
		closeButton.className = 'dashboard-message-close';
		closeButton.setAttribute('aria-label', 'Dismiss');
		closeButton.textContent = '×';

		closeButton.addEventListener('click', () => {
			toast.style.animation = 'dashboard-toast-out 180ms ease forwards';
			window.setTimeout(() => toast.remove(), 180);
		});

		toast.appendChild(text);
		toast.appendChild(closeButton);
		messageContainer.appendChild(toast);

		window.setTimeout(() => {
			if (!toast.isConnected) {
				return;
			}

			toast.style.animation = 'dashboard-toast-out 180ms ease forwards';
			window.setTimeout(() => toast.remove(), 180);
		}, 5000);
	}

	window.showDashboardMessage = showDashboardMessage;

	try {
		const queuedToast = sessionStorage.getItem('dashboardToast');
		if (queuedToast) {
			const parsedToast = JSON.parse(queuedToast);
			showDashboardMessage(parsedToast.message, parsedToast.type || 'success');
			sessionStorage.removeItem('dashboardToast');
		}
	} catch (error) {
		sessionStorage.removeItem('dashboardToast');
	}

	function updateProjectVisibility() {
		if (!projectToggle) {
			return;
		}

		const showInactiveProjects = projectToggle.checked;
		const searchTerm = (projectSearchInput?.value || '').trim().toLowerCase();
		let visibleProjectCount = 0;

		projectItems.forEach(item => {
			const isInactiveProject = item.dataset.active === 'false';
			const searchSource = (item.dataset.search || item.textContent || '').toLowerCase();
			const matchesSearch = !searchTerm || searchSource.includes(searchTerm);
			const shouldHide = (!showInactiveProjects && isInactiveProject) || !matchesSearch;
			item.hidden = shouldHide;

			if (!shouldHide) {
				visibleProjectCount += 1;
			}
		});

		if (projectsEmptyState) {
			projectsEmptyState.hidden = visibleProjectCount !== 0;
			if (visibleProjectCount === 0) {
				projectsEmptyState.textContent = searchTerm ? 'No matching projects.' : 'No active projects.';
			}
		}
	}

	if (projectToggle) {
		updateProjectVisibility();
		projectToggle.addEventListener('change', updateProjectVisibility);
	}

	if (projectSearchInput) {
		projectSearchInput.addEventListener('input', updateProjectVisibility);
	}


	function updateTabCountsFromDocument(doc) {
		document.querySelectorAll('.js-tab-count[data-count-target]').forEach(current => {
			const target = current.getAttribute('data-count-target');
			const incoming = doc.querySelector(`.js-tab-count[data-count-target="${target}"]`);
			if (incoming) {
				current.textContent = incoming.textContent;
			}
		});
	}

	async function submitPanelGetForm(form) {
		const panelTarget = form?.dataset?.panelTarget;
		if (!panelTarget) {
			return;
		}

		const currentPanel = document.getElementById(panelTarget);
		if (!currentPanel) {
			form.submit();
			return;
		}

		const requestUrl = new URL(form.getAttribute('action') || window.location.href, window.location.origin);
		requestUrl.search = new URLSearchParams(new FormData(form)).toString();
		requestUrl.searchParams.set('_ts', Date.now().toString());

		try {
			const response = await fetch(requestUrl.toString(), {
				method: 'GET',
				cache: 'no-store',
				headers: {
					'X-Requested-With': 'XMLHttpRequest'
				}
			});
			if (!response.ok) {
				throw new Error('Request failed');
			}

			const html = await response.text();
			const doc = new DOMParser().parseFromString(html, 'text/html');
			const incomingPanel = doc.getElementById(panelTarget);
			if (!incomingPanel) {
				window.location.assign(requestUrl.toString());
				return;
			}

			currentPanel.innerHTML = incomingPanel.innerHTML;
			updateTabCountsFromDocument(doc);
			bindLiveGetFormEnhancements(currentPanel);
			window.history.replaceState({}, '', requestUrl.toString());
			if (typeof lucide !== 'undefined' && typeof lucide.createIcons === 'function') {
				lucide.createIcons();
			}
		} catch (error) {
			window.location.assign(requestUrl.toString());
		}
	}

	function bindLiveGetFormEnhancements(scope = document) {
		scope.querySelectorAll('form[data-panel-target][method="get"], form[data-panel-target][method="GET"]').forEach(form => {
			if (form.dataset.boundLiveGetSubmit !== 'true') {
				form.dataset.boundLiveGetSubmit = 'true';
				form.addEventListener('submit', function (event) {
					if (event.submitter) {
						return;
					}
					event.preventDefault();
					submitPanelGetForm(form);
				});
			}

			// const inlineSearchInput = form.querySelector('input.search-input[name="q"], input[name="q"][type="search"], input[name="q"][type="text"]');
			// if (inlineSearchInput) {
			//     setupAutoSubmitSearch(inlineSearchInput, form);
			// }

			// if (form.id) {
			//     scope.querySelectorAll(`input[form="${form.id}"][name="q"]`).forEach(externalSearchInput => {
			//         setupAutoSubmitSearch(externalSearchInput, form);
			//     });
			// }
		});
	}

	bindLiveGetFormEnhancements(document);

	document.querySelectorAll('.submissions-tabs').forEach(container => {
		const tabs = container.querySelectorAll('[role="tab"]');
		const panels = container.querySelectorAll('[role="tabpanel"]');
		const headerTitle = document.getElementById('submissions-header-title');
		const headerSubtitle = document.getElementById('submissions-header-subtitle');
		const flagIcon = document.getElementById('submissions-flag-icon');
		const trashIcon = document.getElementById('submissions-trash-icon');

		function updateSubmissionsHeader(targetId) {
			const isTrash = targetId === 'trash-panel';

			if (headerTitle) {
				headerTitle.textContent = isTrash ? 'Trashed Submissions' : 'Flagged Submissions';
			}

			if (headerSubtitle) {
				headerSubtitle.textContent = isTrash
					? 'Review submissions moved to trash. You can restore them or permanently delete them.'
					: 'Review submissions flagged for potential issues. Most of these forms aren\'t appended to a disaster.';
			}

			if (flagIcon) {
				flagIcon.classList.toggle('is-hidden', isTrash);
			}

			if (trashIcon) {
				trashIcon.classList.toggle('is-hidden', !isTrash);
			}
		}

		const activeTab = Array.from(tabs).find(tab => tab.getAttribute('aria-selected') === 'true');
		if (activeTab) {
			updateSubmissionsHeader(activeTab.dataset.target);
		}

		tabs.forEach(tab => {
			tab.addEventListener('click', () => {
				const targetId = tab.dataset.target;
				const currentUrl = new URL(window.location.href);
				currentUrl.searchParams.set('active_tab', targetId);
				window.history.replaceState({}, '', currentUrl.toString());

				tabs.forEach(currentTab => {
					const isActive = currentTab === tab;
					currentTab.dataset.state = isActive ? 'active' : 'inactive';
					currentTab.setAttribute('aria-selected', String(isActive));
				});

				panels.forEach(panel => {
					const isActive = panel.id === targetId;
					panel.hidden = !isActive;
					panel.classList.toggle('is-active', isActive);
				});

				updateSubmissionsHeader(targetId);
			});
		});
	});

	document.querySelectorAll('.tabs-list').forEach(tabGroup => {
		const tabs = tabGroup.querySelectorAll('[role="tab"], .tab-trigger');
		const container = tabGroup.closest('.submissions-tabs, #trash-panel, body');
		const panels = container.querySelectorAll(':scope > .tab-panel, :scope .tab-panel');

		tabs.forEach(tab => {
			tab.addEventListener('click', () => {
				const targetId = tab.dataset.target;

				tabs.forEach(t => t.classList.remove('is-active'));
				tab.classList.add('active');

				panels.forEach(panel => {
					panel.hidden = panel.id !== targetId;
				});
			});
		});
	});

	document.querySelectorAll('.open-modal-btn').forEach(btn => {
		btn.addEventListener('click', function () {
			const target = document.getElementById(btn.dataset.target);
			if (target) {
				target.style.display = 'block';
				target.setAttribute('aria-hidden', 'false');
			}
		});
	});

	document.querySelectorAll('.modal .close').forEach(closeBtn => {
		closeBtn.addEventListener('click', function () {
			const modal = closeBtn.closest('.modal');
			if (modal) {
				modal.style.display = 'none';
				modal.setAttribute('aria-hidden', 'true');
			}
		});
	});

	window.addEventListener('click', function (event) {
		document.querySelectorAll('.modal').forEach(modal => {
			if (event.target === modal) {
				modal.style.display = 'none';
				modal.setAttribute('aria-hidden', 'true');
			}
		});
	});

	const openBtn = document.getElementById('open-settings');
	const closeBtn = document.getElementById('close-settings');
	const modal = document.getElementById('settings-modal');

	if (openBtn && modal) {
		openBtn.addEventListener('click', () => {
			modal.style.display = 'block';
			modal.setAttribute('aria-hidden', 'false');
		});
	}

	if (closeBtn && modal) {
		closeBtn.addEventListener('click', () => {
			modal.style.display = 'none';
			modal.setAttribute('aria-hidden', 'true');
		});
	}

	if (modal) {
		modal.addEventListener('click', (e) => {
			if (e.target === modal) {
				modal.style.display = 'none';
				modal.setAttribute('aria-hidden', 'true');
			}
		});
	}

	document.querySelectorAll('.js-toggle-flag').forEach(function (btn) {
		btn.addEventListener('click', function () {
			const volunteerId = btn.getAttribute('data-volunteer-id');
			if (volunteerId) {
				toggleFlaggedStatus(volunteerId, btn);
			}
		});
	});

	document.querySelectorAll('.js-toggle-donation-flag').forEach(function (btn) {
		btn.addEventListener('click', function () {
			const donationId = btn.getAttribute('data-donation-id');
			if (donationId) {
				toggleDonationFlaggedStatus(donationId, btn);
			}
		});
	});

	if (typeof lucide !== 'undefined' && typeof lucide.createIcons === 'function') {
		lucide.createIcons();
	}
});
