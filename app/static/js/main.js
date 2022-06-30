import flatpickr from "https://cdn.jsdelivr.net/npm/flatpickr/+esm";
import spacetime from "https://cdn.jsdelivr.net/npm/spacetime/+esm";
import { registerControllers } from "/static/js/vendor/binder/binder.js";
import { DynamicFrame } from "/static/js/components/dynamic_frame.js";
import { ModalFrame } from "/static/js/components/modal_frame.js";

window.initDatePicker = picker => {
    const tz = document.getElementById("timezone")?.innerText;
    if (!tz) return;

    const today = spacetime.now(tz);
    let date = today.format("Y-m-d");
    let hour = today.hour();
    let mins = today.minute();
    mins = Math.floor(mins / 5) * 5; // Round minutes to nearest 5 mins

    const pickerType = picker.getAttribute("data-date-type");
    let value = picker.getAttribute("data-date-value");
    let setDefault = picker.hasAttribute("data-set-default");

    // If we have a number then it will be an epoch in seconds
    // Flatpickr expects an epoch to be in milliseconds
    if (value && !isNaN(value)) {
        value = Number(value) * 1000;
    }

    if (pickerType === "time") {
        let defaultValue = value;
        if (!value && setDefault) defaultValue = `${date} ${hour}:${mins}`;
        flatpickr(picker, {
            enableTime: true,
            noCalendar: true,
            altInput: true,
            altFormat: "H:i",
            dateFormat: "Y-m-d H:i",
            time_24hr: true,
            defaultDate: defaultValue,
        });
    } else if (pickerType === "date") {
        let defaultValue = value;
        if (!value && setDefault) defaultValue = date;
        flatpickr(picker, {
            altInput: true,
            altFormat: "F j, Y",
            dateFormat: "Y-m-d",
            defaultDate: defaultValue,
            locale: {
                firstDayOfWeek: 1,
            },
        });
    } else if (pickerType === "datetime") {
        let defaultValue = value;
        if (!value && setDefault) defaultValue = `${date} ${hour}:${mins}`;
        flatpickr(picker, {
            altInput: true,
            altFormat: "H:i o\\n F j, Y",
            enableTime: true,
            time_24hr: true,
            dateFormat: "Y-m-d H:i",
            defaultDate: defaultValue,
            locale: {
                firstDayOfWeek: 1,
            },
        });
    }
};

window.addEventListener("DOMContentLoaded", () => {
    const pickers = document.querySelectorAll(".flatpickr");
    pickers.forEach(picker => window.initDatePicker(picker));
    registerControllers(DynamicFrame, ModalFrame);
});

// Whenever a dynamic-frame updates re-initialise the datepickers and lightboxes
window.addEventListener("dynamic-frame:updated", e => {
    const pickers = e.target.querySelectorAll(".flatpickr");
    pickers.forEach(picker => window.initDatePicker(picker));
});
