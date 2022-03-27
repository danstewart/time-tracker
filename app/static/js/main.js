import flatpickr from 'https://cdn.jsdelivr.net/npm/flatpickr/+esm';
import spacetime from 'https://cdn.jsdelivr.net/npm/spacetime/+esm';
import { registerControllers } from '/static/js/vendor/binder.js';
import { DynamicFrame } from '/static/js/components/dynamic_frame.js';
import { ModalFrame } from '/static/js/components/modal_frame.js';


window.addEventListener('DOMContentLoaded', () => {
    initDatePickers();
    registerControllers(DynamicFrame, ModalFrame);
});

// Whenever a dyanmic-frame updates re-initialise the datepickers and lightboxes
window.addEventListener("dynamic-frame:updated", () => {
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
