 function confirmStatusChange(selectElement) {
        const form = selectElement.form;
        const row = selectElement.closest("tr");
        const previousValue = selectElement.getAttribute("data-prev");

        if (confirm("Are you sure you want to change the status?")) {
            form.submit();
        } else {
            selectElement.value = previousValue;
            updateRowColor(row, previousValue);
        }
    }

    // Save previous value
    document.addEventListener("focusin", function (e) {
        if (e.target.classList.contains("status-select")) {
            e.target.setAttribute("data-prev", e.target.value);
        }
    });

    // Update row color instantly
    document.addEventListener("change", function (e) {
        if (e.target.classList.contains("status-select")) {
            const row = e.target.closest("tr");
            updateRowColor(row, e.target.value);
        }
    });

    function updateRowColor(row, status) {
        row.className = "status-row status-" + status.toLowerCase();
    }
   
    function enableStatusEdit(id) {
        document.getElementById(`badge-${id}`).style.display = "none";
        document.getElementById(`form-${id}`).style.display = "inline";
    }

    function handleStatusChange(id) {
        const select = document.getElementById(`select-${id}`);
        const confirmed = confirm("Are you sure you want to change the status?");

        if (confirmed) {
            document.getElementById(`form-${id}`).submit();
        } else {
            // Revert selection
            location.reload();
        }
    }