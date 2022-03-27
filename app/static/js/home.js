window.addEventListener('DOMContentLoaded', () => {
    // Events
    [...document.querySelectorAll('.delete-time-entry')].forEach(btn => btn.addEventListener('click', async e => {
        const id = e.target.getAttribute('data-time-id');
        let response = await fetch(`/time/delete/${id}`, {
            method: 'delete'
        });

        if (response.status == 200) {
            window.location.reload();
        } else {
            console.error(`Failed to delete time record ${id}: ${await response.text}`)
        }
    }));
});
