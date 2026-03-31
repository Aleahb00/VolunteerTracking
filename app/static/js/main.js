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
});

document.querySelectorAll('.volunteer-details').forEach(link => {
  link.addEventListener('click', function(e) {
    e.preventDefault();
    const volunteerId = this.getAttribute('data-id');
    const modal = document.getElementById('popupModal');

    // Dynamically change content based on ID
    document.getElementById('modalBody').innerHTML =
        `<p>Viewing details for ID: ${volunteerId}</p>
         <a href="/volunteer/pdf/${volunteerId}" target="_blank">Download PDF</a>`;

    modal.style.display = 'block'; // Show modal
  });
});

// Close functionality
document.querySelector('.close-btn').addEventListener('click', function() {
  document.getElementById('popupModal').style.display = 'none';
});

