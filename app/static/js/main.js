import flatpickr from 'https://cdn.jsdelivr.net/npm/flatpickr/+esm';
import spacetime from 'https://cdn.jsdelivr.net/npm/spacetime/+esm';
import { registerControllers } from '/static/js/vendor/binder.js';
import { DynamicFrame } from '/static/js/components/dynamic_frame.js';


window.addEventListener('DOMContentLoaded', () => {
    // Events
    initDatePickers();
    initLightBoxes();

    registerControllers(DynamicFrame);
});

// Whenever a dyanmic-frame updates re-initialise the datepickers and lightboxes
window.addEventListener("dynamic-frame:updated", () => {
    console.log("CAUGHT UPDATE!")
    initDatePickers();
    initLightBoxes();
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

function initLightBoxes() {
    // glightbox init for loading pages in lightwindows
    const lightbox = GLightbox({
        slideEffect: 'none',
        openEffect: 'none',
        closeEffect: 'none',
        touchNavigation: false,
        width: '80vw',
        height: '80vh',
        preload: false,
        closeOnOutsideClick: false
    });

    const boxes = document.querySelectorAll('.glightbox') || [];

    [ ...boxes ].forEach(function(box) {
        box.addEventListener('click', function(e) {
            e.preventDefault();
            let targetHref = this.getAttribute('href');
            lightbox.setElements([{'href': targetHref}]);
            lightbox.open();
        });
    });
}
