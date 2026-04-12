document.addEventListener('DOMContentLoaded', function() {
    // Helper: Open Modal
    function openModal(m) {
        if (!m) return;
        m.style.display = 'block';
        m.setAttribute('aria-hidden', 'false');
    }

    // Helper: Close Modal
    function closeModal(m) {
        if (!m) return;
        m.style.display = 'none';
        m.setAttribute('aria-hidden', 'true');
    }
    function isAjaxActionForm(form) {
        if (!form) {
            return false;
        }

        if (form.classList.contains('js-ajax-action')) {
            return true;
        }

        const action = form.action || '';
        return /toggle_(donation_)?flagged_status|delete-volunteer|delete-donation|restore-volunteer|restore-donation|permanent-delete-volunteer|permanent-delete-donation/i.test(action);
    }

    function storeDashboardToast(payload) {
        if (!payload || !payload.message) {
            return;
        }

        try {
            sessionStorage.setItem('dashboardToast', JSON.stringify({
                message: payload.message,
                type: payload.message_type || 'success',
            }));
        } catch (error) {
            if (typeof window.showDashboardMessage === 'function') {
                window.showDashboardMessage(payload.message, payload.message_type || 'success');
            }
        }
    }

    // 1. UNIVERSAL OPENER: Works for Create and Edit buttons
    document.addEventListener('click', function(event) {
        // Look for the Create button ID or the Edit button Class
        const trigger = event.target.closest('#openFormButton, .open-modal-btn');
        
        if (trigger) {
            // If it's the Create button, target 'formModal'. 
            // If it's Edit, get the target from data-target attribute.
            const targetId = trigger.id === 'openFormButton' ? 'formModal' : trigger.getAttribute('data-target');
            const targetModal = document.getElementById(targetId);
            openModal(targetModal);
        }
    });

    // 2. UNIVERSAL CLOSER: Handles 'X' buttons and clicking outside the modal
    document.addEventListener('click', function(event) {
        // If they clicked the 'X' (close class)
        if (event.target.classList.contains('close')) {
            closeModal(event.target.closest('.modal'));
        }
        
        // If they clicked the dark backdrop (the modal div itself)
        if (event.target.classList.contains('modal')) {
            closeModal(event.target);
        }
    });

    // 3. AUTO-SHOW LOGIC: For when Django reloads the page with errors
    const autoShowModal = document.querySelector('.modal[data-autoshow="true"]');
    if (autoShowModal) {
        openModal(autoShowModal);
    }

    document.addEventListener('submit', async function(event) {
        const form = event.target.closest('form');
        if (!isAjaxActionForm(form)) {
            return;
        }

        event.preventDefault();

        const confirmMessage = form.dataset.confirmMessage;
        if (confirmMessage && !window.confirm(confirmMessage)) {
            return;
        }

        const submitButton = form.querySelector('[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
        }

        try {
            const response = await fetch(form.action, {
                method: form.method || 'POST',
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            const payload = await response.json().catch(() => ({}));
            if (!response.ok || payload.status !== 'success') {
                if (payload.message && typeof window.showDashboardMessage === 'function') {
                    window.showDashboardMessage(payload.message, payload.message_type || 'error');
                } else {
                    window.alert(payload.error || 'The action could not be completed. Please try again.');
                }
                return;
            }

            storeDashboardToast(payload);
            window.location.reload();
        } catch (error) {
            console.error(error);
            window.alert('The action could not be completed. Please try again.');
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
            }
        }
    });
});

// Apparently this code isn't being used and is suggested to remove

// document.querySelectorAll('.volunteer-details').forEach(link => {
//     link.addEventListener('click', function(e) {
//         e.preventDefault();
//         const volunteerId = this.getAttribute('data-id');
//         const modal = document.getElementById('popupModal');

//         // Dynamically change content based on ID
//         document.getElementById('modalBody').innerHTML =
//             `<p>Viewing details for ID: ${volunteerId}</p>
//             <a href="/volunteer/pdf/${volunteerId}" target="_blank">Download PDF</a>`;

//         modal.style.display = 'block'; // Show modal
//     });
//     });

//     // Close functionality
//     document.querySelector('.close-btn').addEventListener('click', function() {
//     document.getElementById('popupModal').style.display = 'none';
//     });

