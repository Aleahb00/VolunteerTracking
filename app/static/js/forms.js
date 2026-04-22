document.addEventListener('DOMContentLoaded', function () {
(function () {
	// Tab switching logic
	const tabs = document.querySelectorAll('.forms-tab');
	const panels = document.querySelectorAll('.forms-panel');

	tabs.forEach((tab) => {
		tab.addEventListener('click', () => {
			const target = tab.getAttribute('data-tab-target');

			tabs.forEach((item) => {
				item.classList.remove('is-active');
				item.setAttribute('aria-selected', 'false');
			});

			panels.forEach((panel) => {
				panel.classList.remove('is-active');
				panel.setAttribute('hidden', 'hidden');
			});

			tab.classList.add('is-active');
			tab.setAttribute('aria-selected', 'true');

			const activePanel = document.getElementById(target);
			if (activePanel) {
				activePanel.classList.add('is-active');
				activePanel.removeAttribute('hidden');
			}
		});
	});

	// Conditional field visibility logic
	function setupConditionalFields(formSelector) {
		const form = document.querySelector(formSelector);
		if (!form) return;

		const conditionalFields = form.querySelectorAll('.conditional-field');

		function updateVisibility() {
			conditionalFields.forEach((field) => {
				const showWhen = field.getAttribute('data-show-when');
				if (!showWhen) return;

				const [fieldName, fieldValue] = showWhen.split('=');
				const triggerField = form.querySelector(`select[name="${fieldName}"]`);

				if (triggerField && triggerField.value === fieldValue) {
					field.style.display = 'flex';
				} else {
					field.style.display = 'none';
				}
			});
		}

		const selectFields = form.querySelectorAll('select');
		selectFields.forEach((select) => {
			select.addEventListener('change', updateVisibility);
		});

		updateVisibility();
	}

	function setupRadioGroups(formSelector) {
		const form = document.querySelector(formSelector);
		if (!form) return;

		const groups = form.querySelectorAll('.radio-group');

		groups.forEach((group) => {
			const radios = group.querySelectorAll('input[type="radio"]');

			function syncSelection() {
				group.querySelectorAll('.radio-option').forEach((option) => {
					const input = option.querySelector('input[type="radio"]');
					option.classList.toggle('is-selected', Boolean(input && input.checked));
				});
			}

			radios.forEach((radio) => {
				radio.addEventListener('change', syncSelection);
			});

			syncSelection();
		});
	}

	setupConditionalFields('#volunteer-panel .forms-grid-form');
	setupConditionalFields('#donation-panel .forms-grid-form');
	setupRadioGroups('#volunteer-panel .forms-grid-form');
	setupRadioGroups('#donation-panel .forms-grid-form');

	const toastContainer = document.querySelector('.forms-messages');
	if (toastContainer) {
		const toasts = Array.from(toastContainer.querySelectorAll('.forms-message'));
		toasts.forEach((toast) => {
			const timeout = setTimeout(() => {
				toast.style.animation = 'toast-out 220ms ease forwards';
				setTimeout(() => toast.remove(), 250);
			}, 6000);

			const closeBtn = toast.querySelector('.toast-close');
			if (closeBtn) {
				closeBtn.addEventListener('click', () => {
					clearTimeout(timeout);
					toast.style.animation = 'toast-out 180ms ease forwards';
					setTimeout(() => toast.remove(), 220);
				});
			}
		});
	}

	// Activate tab based on URL query param
function activateTabFromURL() {
	const params = new URLSearchParams(window.location.search);
	const tab = params.get('tab');

	if (!tab) return;

	const targetId = `${tab}-panel`;
	const targetTab = document.querySelector(`[data-tab-target="${targetId}"]`);
	const targetPanel = document.getElementById(targetId);

	if (targetTab && targetPanel) {
		// Reset all tabs
		tabs.forEach((item) => {
			item.classList.remove('is-active');
			item.setAttribute('aria-selected', 'false');
		});

		panels.forEach((panel) => {
			panel.classList.remove('is-active');
			panel.setAttribute('hidden', 'hidden');
		});

		// Activate correct one
		targetTab.classList.add('is-active');
		targetTab.setAttribute('aria-selected', 'true');

		targetPanel.classList.add('is-active');
		targetPanel.removeAttribute('hidden');
	}
}

	activateTabFromURL();

	})();
});
