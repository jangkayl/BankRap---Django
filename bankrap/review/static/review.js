document.addEventListener("DOMContentLoaded", function () {
    const writeBtn = document.getElementById("writeBtn");
    const reviewForm = document.getElementById("reviewForm");
    const resetBtn = document.getElementById("resetBtn");
    const form = document.getElementById("mainReviewForm");
    const givenReceivedContainer = document.getElementById("givenReceivedContainer");
    const tabGiven = document.getElementById("tabGiven");
    const tabReceived = document.getElementById("tabReceived");
    const givenPanel = document.getElementById("givenPanel");
    const receivedPanel = document.getElementById("receivedPanel");
    const messages = document.getElementById("messages");
    const submitBtn = document.getElementById("submitBtn");
    const reviewIdInput = document.getElementById("review_id_input");
    const revieweeSelect = document.getElementById("reviewee_select");
    const reviewTypeSelect = document.getElementById("review_type_select");
    const commentTextarea = document.getElementById("comment_textarea");
    const deleteForm = document.getElementById("deleteForm");
    const deleteReviewIdInput = document.getElementById("delete_review_id");

    // Track whether a server-message was shown after submission
    let messageShown = false;

    // Hide messages by default
    if (messages) messages.style.display = "none";

    // -------------------- WRITE / CREATE FORM --------------------
    if (writeBtn) {
        writeBtn.addEventListener("click", () => {
            const isVisible = reviewForm && reviewForm.classList && reviewForm.classList.contains("show");
            if (!isVisible) openFormForCreate();
            else cancelEditMode();
            if (messages) messages.style.display = "none";
        });
    }

    function openFormForCreate() {
        if (!reviewForm) return;
        reviewForm.style.display = "flex";
        setTimeout(() => reviewForm.classList.add("show"), 10);
        if (givenReceivedContainer) givenReceivedContainer.style.display = "none";
        if (givenPanel) givenPanel.style.display = "none";
        if (receivedPanel) receivedPanel.style.display = "none";
        if (writeBtn) writeBtn.textContent = "Cancel";
        if (form) form.reset();
        if (reviewIdInput) reviewIdInput.value = "";
        if (submitBtn) submitBtn.textContent = "Submit Review";
    }

    function cancelEditMode() {
        if (!reviewForm) return;
        reviewForm.classList.remove("show");
        setTimeout(() => (reviewForm.style.display = "none"), 300);
        if (givenReceivedContainer) givenReceivedContainer.style.display = "flex";
        if (givenPanel) givenPanel.style.display = "grid";
        if (receivedPanel) receivedPanel.style.display = "none";
        if (writeBtn) writeBtn.textContent = "Write a Review";
        if (form) form.reset();
        if (reviewIdInput) reviewIdInput.value = "";
        if (submitBtn) submitBtn.textContent = "Submit Review";
    }

    // -------------------- RESET BUTTON --------------------
    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            if (form) form.reset();
            if (reviewIdInput) reviewIdInput.value = "";
            if (submitBtn) submitBtn.textContent = "Submit Review";
            if (messages) messages.style.display = "none";
        });
    }

    // -------------------- TABS --------------------
    function showGiven() {
        if (tabGiven) tabGiven.classList.add("active");
        if (tabReceived) tabReceived.classList.remove("active");
        if (givenPanel) givenPanel.style.display = "grid";
        if (receivedPanel) receivedPanel.style.display = "none";
        if (messageShown && messages) messages.style.display = "none";
    }

    function showReceived() {
        if (tabGiven) tabGiven.classList.remove("active");
        if (tabReceived) tabReceived.classList.add("active");
        if (givenPanel) givenPanel.style.display = "none";
        if (receivedPanel) receivedPanel.style.display = "grid";
        if (messageShown && messages) messages.style.display = "none";
    }

    if (tabGiven) tabGiven.addEventListener("click", showGiven);
    if (tabReceived) tabReceived.addEventListener("click", showReceived);
    showGiven();

    // -------------------- EDIT BUTTON --------------------
    function wireEditButtons() {
        const editButtons = document.querySelectorAll(".btn-edit[data-review-id]");
        editButtons.forEach(btn => {
            if (btn.dataset.wired) return;
            btn.dataset.wired = "1";

            btn.addEventListener("click", function (e) {
                e.preventDefault();
                const reviewId = this.getAttribute("data-review-id");
                const revieweeId = this.getAttribute("data-reviewee-id");
                const reviewType = this.getAttribute("data-review-type");
                const rating = this.getAttribute("data-rating");
                const comment = this.getAttribute("data-comment") || "";

                if (reviewIdInput) reviewIdInput.value = reviewId;
                if (revieweeSelect) revieweeSelect.value = revieweeId;
                if (reviewTypeSelect) reviewTypeSelect.value = reviewType;
                if (commentTextarea) commentTextarea.value = comment;

                if (rating) {
                    const radio = document.querySelector(`#star${rating}`);
                    if (radio) radio.checked = true;
                }

                if (submitBtn) submitBtn.textContent = "Update Review";
                if (reviewForm) {
                    reviewForm.style.display = "flex";
                    setTimeout(() => reviewForm.classList.add("show"), 10);
                }
                if (givenReceivedContainer) givenReceivedContainer.style.display = "none";
                if (givenPanel) givenPanel.style.display = "none";
                if (receivedPanel) receivedPanel.style.display = "none";
                if (writeBtn) writeBtn.textContent = "Cancel";
                try { if (reviewForm) reviewForm.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch(e){}
                if (messages) messages.style.display = "none";
            });
        });
    }
    wireEditButtons();

    // -------------------- DELETE BUTTON --------------------
    function wireDeleteButtons() {
        const deleteButtons = document.querySelectorAll(".btn-delete[data-review-id]");
        deleteButtons.forEach(btn => {
            if (btn.dataset.wiredDelete) return;
            btn.dataset.wiredDelete = "1";

            btn.addEventListener("click", function () {
                const reviewId = this.getAttribute("data-review-id");
                const revieweeName = this.getAttribute("data-reviewee-name") || "this user";

                if (!confirm(`Are you sure you want to delete the review for ${revieweeName}?`)) return;

                if (deleteForm && deleteReviewIdInput) {
                    deleteReviewIdInput.value = reviewId;
                    deleteForm.submit();
                }
            });
        });
    }
    wireDeleteButtons();

    // -------------------- FORM SUBMIT (reset flags for server messages) --------------------
    if (form) {
        form.addEventListener("submit", () => {
            messageShown = false;
        });
    }

    // -------------------- SERVER MESSAGES --------------------
    if (messages && messages.children.length > 0) {
        messages.style.display = "block";
        messageShown = true;
        setTimeout(() => {
            messages.style.display = "none";
        }, 5000);
    }
});
