let currentNoteId = null;

function openNotesModal(id, notes) {
    currentNoteId = id;

    const textarea = document.getElementById("notesTextarea");
    textarea.value = notes;

    const modal = new bootstrap.Modal(
        document.getElementById("notesModal")
    );

    modal.show();
}

function saveNotes() {
    const form = document.getElementById("notesForm");
    form.action = `/update-notes/${currentNoteId}`;
    form.submit();
}
