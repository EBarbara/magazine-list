document.addEventListener('DOMContentLoaded', () => {
    const dialog = document.getElementById('generic-modal');
    const modalContent = dialog.querySelector('.modal-content');
    const closeBtn = dialog.querySelector('.modal-close');

    // Close modal function
    const closeModal = () => {
        dialog.close();
        modalContent.innerHTML = ''; // Clear content
    };

    closeBtn.addEventListener('click', closeModal);
    dialog.addEventListener('click', (e) => {
        if (e.target === dialog) closeModal();
    });

    // Handle Open Modal Clicks
    document.addEventListener('click', async (e) => {
        const trigger = e.target.closest('.open-modal');
        if (!trigger) return;

        e.preventDefault();
        const url = trigger.href;

        try {
            const response = await fetch(url);
            const html = await response.text();

            // Extract content from main block (assumes template structure)
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const mainContent = doc.querySelector('main.container') || doc.body; // Fallback

            // Handle Cancel Button in Modal
            const cancelBtn = modalContent.querySelector('.btn-cancel');
            if (cancelBtn) {
                cancelBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    closeModal();
                });
            }

            modalContent.innerHTML = mainContent.innerHTML;
            dialog.showModal();

            // Setup Form Interception
            const form = modalContent.querySelector('form');
            if (form) {
                setupFormSubmission(form, url);
            }
        } catch (err) {
            console.error('Error loading modal content:', err);
        }
    });

    // Handle Form Submission via AJAX
    async function setupFormSubmission(form, actionUrl) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);

            try {
                const response = await fetch(actionUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                if (response.redirected) {
                    // Success! Redirect to the target URL (e.g. list view after delete, or reload current)
                    window.location.href = response.url;
                } else {
                    // Validation errors? Replace content
                    const html = await response.text();
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const mainContent = doc.querySelector('main.container') || doc.body;

                    const cancelBtn = modalContent.querySelector('.btn-cancel');
                    if (cancelBtn) {
                        cancelBtn.addEventListener('click', (e) => {
                            e.preventDefault();
                            closeModal();
                        });
                    }

                    modalContent.innerHTML = mainContent.innerHTML;

                    // Re-attach listener to new form
                    const newForm = modalContent.querySelector('form');
                    if (newForm) setupFormSubmission(newForm, actionUrl);
                }
            } catch (err) {
                console.error('Error submitting form:', err);
            }
        });
    }

    // Helper to get CSRF token
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
});
