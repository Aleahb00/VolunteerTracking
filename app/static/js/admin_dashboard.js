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

document.addEventListener('DOMContentLoaded', function() {
	const messageContainer = document.querySelector('.dashboard-messages');

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
});

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
				if (data.message) {
					try {
						sessionStorage.setItem('dashboardToast', JSON.stringify({
							message: data.message,
							type: data.message_type || 'success'
						}));
					} catch (error) {
						// ignore storage errors and continue reload
					}
				}
				window.location.reload();
			} else {
				alert('Error toggling flagged status.');
			}
		})
		.catch(() => {
			alert('An error occurred while toggling flagged status.');
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
				if (data.message) {
					try {
						sessionStorage.setItem('dashboardToast', JSON.stringify({
							message: data.message,
							type: data.message_type || 'success'
						}));
					} catch (error) {
						// ignore storage errors and continue reload
					}
				}
				window.location.reload();
			} else {
				alert('Error toggling donation flagged status.');
			}
		})
		.catch(() => {
			alert('An error occurred while toggling donation flagged status.');
		});
}

function renderAnalyticsChartIfNeeded() {
	const canvas = document.getElementById('myChart');
	if (!canvas || typeof Chart === 'undefined') {
		return;
	}

	const volunteerRevenue = Number(canvas.dataset.volunteerRevenue || '0') || 0;
	const donationRevenue = Number(canvas.dataset.donationRevenue || '0') || 0;
	const progressValue = volunteerRevenue + donationRevenue;
	const goalValue = Number(canvas.dataset.goalValue || '0') || 0;
	const remainingValue = Math.max(goalValue - progressValue, 0);
	const percentValue = goalValue > 0 ? Math.min((progressValue / goalValue) * 100, 100) : 0;
	const goalLabel = goalValue.toLocaleString();

	if (window.adminAnalyticsChart) {
		window.adminAnalyticsChart.destroy();
	}

	window.adminAnalyticsChart = new Chart(canvas, {
		type: 'doughnut',
		plugins: [{
			id: 'centerText',
			afterDraw(chart) {
				const { ctx, chartArea } = chart;
				if (!chartArea) {
					return;
				}

				const centerX = (chartArea.left + chartArea.right) / 2;
				const centerY = (chartArea.top + chartArea.bottom) / 2;
				   const percentText = `${percentValue.toFixed(2)}%`;
				   const goalText = `of ${goalLabel}`;
				   const showGoalReached = percentValue >= 100 && goalValue > 0;

				   ctx.save();
				   ctx.textAlign = 'center';
				   ctx.textBaseline = 'middle';
				   ctx.fillStyle = '#143744';
				   ctx.font = '700 2.1rem Arial, sans-serif';
				   ctx.fillText(percentText, centerX, centerY - 16);
				   ctx.font = '600 0.9rem Arial, sans-serif';
				   ctx.fillStyle = '#5c7178';
				   ctx.fillText(goalText, centerX, centerY + 2);
				   if (showGoalReached) {
					   ctx.font = 'bold 1.1rem Arial, sans-serif';
					   ctx.fillStyle = '#2d7552';
					   ctx.fillText('Goal Reached', centerX, centerY + 22);
				   }
				   ctx.restore();
			}
		}],
		data: {
			labels: ['Volunteer Revenue', 'Donation Revenue', 'Remaining to Goal'],
			datasets: [{
				data: [volunteerRevenue, donationRevenue, remainingValue],
				backgroundColor: ['#2d7552', '#1b5c67', '#d9e3e6'],
				borderWidth: 0,
				hoverOffset: 6
			}]
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			cutout: '72%',
			plugins: {
				legend: {
					position: 'bottom'
				},
				tooltip: {
					callbacks: {
						label(context) {
							const value = context.parsed || 0;
							if (context.dataIndex === 0) {
								return `Volunteer Revenue: $${value.toLocaleString()}`;
							}
							if (context.dataIndex === 1) {
								return `Donation Revenue: $${value.toLocaleString()}`;
							}
							return `Remaining to Goal: $${value.toLocaleString()}`;
						}
					}
				}
			}
		}
	});
}

function setupHourlyRateButtons() {
	const hourlyRateBtn = document.getElementById('hourly-rate-btn');
	const skilledHourlyRateBtn = document.getElementById('skilled-hourly-rate-btn');
	const hourlyRateInput = document.getElementById('hourly-rate');
	const skilledHourlyRateInput = document.getElementById('skilled-hourly-rate');
	const hourlyRateDisplay = document.getElementById('hourly-rate-display');
	const skilledHourlyRateDisplay = document.getElementById('skilled-hourly-rate-display');

	if (!hourlyRateBtn || !skilledHourlyRateBtn) {
		return;
	}

	const disasterId = new URLSearchParams(window.location.search).get('disaster_id') ||
		window.location.pathname.split('/').filter(Boolean).find((part, idx, arr) =>
			arr[idx - 1] === 'admin-dashboard' && /^\d+$/.test(part));

	if (!disasterId) {
		return;
	}

	async function updateRate(fieldName, inputElement, button) {
		const newValue = inputElement.value;

		if (!newValue) {
			alert('Please enter a valid value');
			return;
		}

		const originalText = button.textContent;
		button.textContent = 'Saving...';
		button.disabled = true;

		try {
			const formData = new FormData();
			formData.append(fieldName, newValue);

			const response = await fetch(`/admin-dashboard/${disasterId}/update-hourly-rate/`, {
				method: 'POST',
				credentials: 'same-origin',
				headers: {
					'X-CSRFToken': getCookie('csrftoken')
				},
				body: formData
			});

			const data = await response.json();

			if (data.status === 'success') {
				alert(`${fieldName === 'hourly_rate' ? 'Hourly rate' : 'Skilled hourly rate'} updated successfully!`);
				if (fieldName === 'hourly_rate') {
					inputElement.value = data.hourly_rate;
					hourlyRateDisplay.textContent = '$' + data.hourly_rate;
				} else {
					inputElement.value = data.skilled_hourly_rate;
					skilledHourlyRateDisplay.textContent = '$' + data.skilled_hourly_rate;
				}
			} else {
				alert('Error updating rate: ' + (data.message || 'Unknown error'));
			}
		} catch (error) {
			alert('An error occurred while updating the rate: ' + error.message);
		} finally {
			button.textContent = originalText;
			button.disabled = false;
		}
	}

	hourlyRateBtn.addEventListener('click', () => updateRate('hourly_rate', hourlyRateInput, hourlyRateBtn));
	skilledHourlyRateBtn.addEventListener('click', () => updateRate('skilled_hourly_rate', skilledHourlyRateInput, skilledHourlyRateBtn));
}

function setupCloseDisasterConfirmation() {
	const forms = document.querySelectorAll('form.inline-form');

	forms.forEach(form => {
		form.addEventListener('submit', function (e) {
			e.preventDefault();

			const modal = document.createElement('div');
			modal.style.position = 'fixed';
			modal.style.top = 0;
			modal.style.left = 0;
			modal.style.width = '100%';
			modal.style.height = '100%';
			modal.style.background = 'rgba(0,0,0,0.8)';
			modal.style.display = 'flex';
			modal.style.justifyContent = 'center';
			modal.style.alignItems = 'center';
			modal.style.zIndex = 10000;

			const content = document.createElement('div');
			content.style.background = '#fff';
			content.style.border = '3px solid #b71c1c';
			content.style.padding = '2rem';
			content.style.borderRadius = '0.5rem';
			content.style.textAlign = 'center';
			content.style.maxWidth = '400px';
			content.style.animation = 'shake 0.3s';

			content.innerHTML = `
				<h2 style="color:#b71c1c;">⚠️ WARNING!</h2>
				<p>This action cannot be undone! Are you sure you want to close this disaster?</p>
				<div style="margin-top:1.5rem; display:flex; justify-content:space-around;">
					<button id="cancel-btn" style="padding:0.5rem 1rem; border-radius:0.35rem; cursor:pointer;">Cancel</button>
					<button id="confirm-btn" style="padding:0.5rem 1rem; background:#e53935; color:white; font-weight:bold; border:1px solid #b71c1c; border-radius:0.35rem; cursor:pointer;">Yes, Close</button>
				</div>
			`;

			modal.appendChild(content);
			document.body.appendChild(modal);

			const style = document.createElement('style');
			style.innerHTML = `
				@keyframes shake {
					0% { transform: translateX(0); }
					25% { transform: translateX(-5px); }
					50% { transform: translateX(5px); }
					75% { transform: translateX(-5px); }
					100% { transform: translateX(0); }
				}
			`;
			document.head.appendChild(style);

			modal.querySelector('#cancel-btn').addEventListener('click', () => {
				document.body.removeChild(modal);
			});

			modal.querySelector('#confirm-btn').addEventListener('click', () => {
				form.submit();
			});
		});
	});
}

document.addEventListener('DOMContentLoaded', function () {
	const tabs = document.querySelectorAll('.dash-tab');
	const panels = document.querySelectorAll('.tab-panel');

	const activeTab = new URLSearchParams(window.location.search).get('active_tab');
	if (
		activeTab === 'analytics-panel' ||
		document.querySelector('.dash-tab[data-target="analytics-panel"]')?.getAttribute('aria-selected') === 'true'
	) {
		renderAnalyticsChartIfNeeded();
	}


	async function submitAdminPanelGetForm(form) {
		const panelTarget = form?.dataset?.panelTarget;
		if (!panelTarget) {
			return;
		}

		const currentPanel = document.getElementById(panelTarget);
		if (!currentPanel) {
			form.submit();
			return;
		}

		// Save the position of the focused element (if any)
		let focusedSelector = null;
		let focusedOffset = null;
		const active = document.activeElement;
		if (active && active !== document.body && active !== document.documentElement) {
			if (active.id) {
				focusedSelector = `#${active.id}`;
			} else if (active.name) {
				focusedSelector = `${active.tagName.toLowerCase()}[name="${active.name}"]`;
			}
			if (focusedSelector) {
				const rect = active.getBoundingClientRect();
				focusedOffset = rect.top;
			}
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
			document.querySelectorAll('.js-tab-count[data-count-target]').forEach(current => {
				const target = current.getAttribute('data-count-target');
				const incoming = doc.querySelector(`.js-tab-count[data-count-target="${target}"]`);
				if (incoming) {
					current.textContent = incoming.textContent;
				}
			});
			bindAdminLiveGetFormEnhancements(currentPanel);
			window.history.replaceState({}, '', requestUrl.toString());
			if (typeof lucide !== 'undefined' && typeof lucide.createIcons === 'function') {
				lucide.createIcons();
			}
			// Restore scroll position to keep the previously focused element in view
			if (focusedSelector && focusedOffset !== null) {
				// Try to find the same element after update
				const newElem = document.querySelector(focusedSelector);
				if (newElem) {
					const newRect = newElem.getBoundingClientRect();
					const delta = newRect.top - focusedOffset;
					window.scrollBy({ top: delta });
					newElem.focus();
				}
			}
		} catch (error) {
			window.location.assign(requestUrl.toString());
		}
	}

	function bindAdminLiveGetFormEnhancements(scope = document) {
		scope.querySelectorAll('form[data-panel-target][method="get"], form[data-panel-target][method="GET"]').forEach(form => {
			if (form.dataset.boundLiveGetSubmit !== 'true') {
				form.dataset.boundLiveGetSubmit = 'true';
				form.addEventListener('submit', function (event) {
					if (event.submitter) {
						return;
					}
					event.preventDefault();
					submitAdminPanelGetForm(form);
				});
			}

			// const searchInput = form.querySelector('input[name="q"]');
			// if (searchInput) {
			//     setupAutoSubmitSearch(searchInput, form);
			// }
		});
	}

	bindAdminLiveGetFormEnhancements(document);

	tabs.forEach(tab => {
		tab.addEventListener('click', function () {
			const targetId = tab.dataset.target;
			const currentUrl = new URL(window.location.href);
			currentUrl.searchParams.set('active_tab', targetId);
			window.history.replaceState({}, '', currentUrl.toString());

			tabs.forEach(currentTab => {
				const isActive = currentTab === tab;
				currentTab.classList.toggle('is-active', isActive);
				currentTab.setAttribute('aria-selected', String(isActive));
			});

			panels.forEach(panel => {
				panel.hidden = panel.id !== targetId;
			});

			if (targetId === 'analytics-panel') {
				window.setTimeout(renderAnalyticsChartIfNeeded, 0);
			}
		});
	});

	document.querySelectorAll('.js-select-all-rows').forEach(function (checkbox) {
		checkbox.addEventListener('change', function () {
			const panelId = checkbox.getAttribute('data-panel-target');
			if (!panelId) {
				return;
			}

			const checkboxes = Array.from(document.querySelectorAll(`#${panelId} .js-admin-select-row`));
			if (!checkboxes.length) {
				return;
			}

			const shouldCheck = checkbox.checked;

			checkboxes.forEach(function (rowCheckbox) {
				rowCheckbox.checked = shouldCheck;
				const row = rowCheckbox.closest('tr');
				if (row) {
					row.classList.toggle('is-selected', rowCheckbox.checked);
				}
			});

			checkbox.indeterminate = false;
		});
	});

	document.querySelectorAll('.js-admin-select-row').forEach(function (checkbox) {
		checkbox.addEventListener('change', function () {
			const row = checkbox.closest('tr');
			if (row) {
				row.classList.toggle('is-selected', checkbox.checked);
			}

			const panel = checkbox.closest('.tab-panel');
			if (!panel) {
				return;
			}

			const panelId = panel.id;
			const rowCheckboxes = Array.from(document.querySelectorAll(`#${panelId} .js-admin-select-row`));
			const selectAll = document.querySelector(`.js-select-all-rows[data-panel-target="${panelId}"]`);

			if (selectAll && rowCheckboxes.length) {
				const checkedCount = rowCheckboxes.filter(function (rowCheckbox) {
					return rowCheckbox.checked;
				}).length;

				selectAll.checked = checkedCount === rowCheckboxes.length;
				selectAll.indeterminate = checkedCount > 0 && checkedCount < rowCheckboxes.length;
			}
		});
	});

	document.querySelectorAll('.js-export-selected').forEach(function (button) {
		button.addEventListener('click', function () {
			const panelId = button.getAttribute('data-panel-target');
			const exportUrl = button.getAttribute('data-export-url');
			const disasterId = button.getAttribute('data-disaster-id');
			if (!panelId || !exportUrl) {
				return;
			}

			const selected = Array.from(document.querySelectorAll(`#${panelId} .js-admin-select-row:checked`));
			const selectedIds = selected
				.map(function (checkbox) { return checkbox.getAttribute('data-record-id'); })
				.filter(function (id) { return id; });

			if (!selectedIds.length) {
				alert('Select at least one form to export.');
				return;
			}

			const query = new URLSearchParams({ ids: selectedIds.join(',') });
			if (disasterId) {
				query.set('disaster_id', disasterId);
			}
			window.location.href = `${exportUrl}?${query.toString()}`;
		});
	});

	document.querySelectorAll('.js-toggle-flag').forEach(function (btn) {
		btn.addEventListener('click', function () {
			const vid = btn.getAttribute('data-volunteer-id');
			if (vid) {
				toggleFlaggedStatus(vid, btn);
			}
		});
	});

	document.querySelectorAll('.js-toggle-donation-flag').forEach(function (btn) {
		btn.addEventListener('click', function () {
			const did = btn.getAttribute('data-donation-id');
			if (did) {
				toggleDonationFlaggedStatus(did, btn);
			}
		});
	});

	document.querySelectorAll('.js-toggle-skilled').forEach(function (btn) {
		btn.addEventListener('click', function () {
			const vid = btn.getAttribute('data-volunteer-id');
			if (vid) {
				fetch(`/toggle_skilled_worker_status/${vid}/`, {
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
							if (data.message) {
								try {
									sessionStorage.setItem('dashboardToast', JSON.stringify({
										message: data.message,
										type: data.message_type || 'success'
									}));
								} catch (error) {
									// ignore storage errors and continue reload
								}
							}
							location.reload();
						} else {
							alert('Error toggling skilled worker status.');
						}
					})
					.catch(() => {
						alert('An error occurred while toggling skilled worker status.');
					});
			}
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

	setupCloseDisasterConfirmation();
	setupHourlyRateButtons();

	if (typeof lucide !== 'undefined' && typeof lucide.createIcons === 'function') {
		lucide.createIcons();
	}
});
