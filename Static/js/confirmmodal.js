let currentAppId = null;

    function showStatusDropdown(id) {
        document.getElementById(`badge-${id}`).style.display = "none";
        const select = document.getElementById(`select-${id}`);
        select.style.display = "inline-block";
        select.focus();
    }

    function openConfirmModal(id) {
        currentAppId = id;
        const modal = new bootstrap.Modal(document.getElementById("confirmModal"));
        modal.show();
    }

    // Confirm button logic
    document.getElementById("confirmBtn").addEventListener("click", () => {
        document.getElementById(`form-${currentAppId}`).submit();
    });

    