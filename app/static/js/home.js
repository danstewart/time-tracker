import { Application } from 'https://cdn.jsdelivr.net/gh/danstewart/binder-js@0.0.5/src/binder/application.min.js';
import { FormSwitcherController } from './controllers/form.js';
import flatpickr from 'https://cdn.jsdelivr.net/npm/flatpickr/+esm';
import spacetime from 'https://cdn.jsdelivr.net/npm/spacetime/+esm';


window.addEventListener('DOMContentLoaded', () => {
    const app = new Application();
    app.register(FormSwitcherController);

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

    initDatePickers();
});


function initDatePickers() {
    const tz = document.getElementById('timezone').innerText;
    const today = spacetime.now(tz);
    let hour = today.hour();
    let mins = today.minute();
    mins = Math.floor(mins / 5) * 5;  // Round minutes to nearest 5 mins

    flatpickr('#form-date', {
        altInput: true,
        altFormat: "F j, Y",
        dateFormat: "Y-m-d",
        defaultDate: today.d,
        locale: {
            firstDayOfWeek: 1
        }
    });

    flatpickr('#form-time', {
        enableTime: true,
        noCalendar: true,
        dateFormat: 'H:i',
        time_24hr: true,
        defaultDate: `${hour}:${mins}`,
    });

    flatpickr('#form-start-time', {
        enableTime: true,
        noCalendar: true,
        dateFormat: 'H:i',
        time_24hr: true,
        defaultDate: `${hour}:${mins}`,
    });

    flatpickr('#form-end-time', {
        enableTime: true,
        noCalendar: true,
        dateFormat: 'H:i',
        time_24hr: true,
        defaultDate: `${hour}:${mins}`,
    });
}
