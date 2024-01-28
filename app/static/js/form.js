/**
 * Find all forms on the page and call `attachValidation` on them
 */
function autoAttachValidation() {
    const forms = document.querySelectorAll("form");
    forms.forEach(form => attachValidation(form));
}

/**
 * Reset the errors on a form
 * @param {*} formEl The form element to reset
 */
function resetFormValidation(formEl) {
    formEl.querySelectorAll(".is-invalid").forEach(fieldEl => {
        fieldEl.classList.remove("is-invalid");
    });

    formEl.querySelectorAll("div.invalid-feedback").forEach(feedbackEl => {
        feedbackEl.remove();
    });

    const alert = formEl.querySelector("div.alert.alert-danger");
    if (alert) alert.remove();
}

/**
 * Intercept the submit event for the given form
 * Submits the form manually via fetch first in validation mode
 * If it fails the submission is prevented and the errors are shown
 * If it passes then the form is submitted
 * @param {*} formEl
 */
function attachValidation(formEl) {
    formEl.addEventListener("submit", async e => {
        e.preventDefault();
        e.stopPropagation();

        resetFormValidation(formEl);
        const validation = await validateForm(formEl);

        if (validation.success) {
            // All good, actually submit
            formEl.submit();
        } else {
            // Show errors
            formEl.insertAdjacentHTML(
                "afterbegin",
                `
                    <div class="alert alert-danger"
                    role="alert"
                    aria-live="assertive"
                    aria-atomic="true"
                    data-bs-autohide="true">
                        <div class="d-flex">
                            <div class="toast-body">There was an error with your submission, please review the errors below.</div>
                            <button onclick="this.parentNode.parentNode.remove()"
                                type="button"
                                class="btn-close me-2 m-auto"
                                data-bs-dismiss="toast"
                                aria-label="Close">
                            </button>
                        </div>
                    </div>`
            );

            for (const [field, messages] of Object.entries(validation)) {
                const fieldEl = document.getElementById(field);
                fieldEl.classList.add("is-invalid");

                for (const message of messages) {
                    fieldEl.insertAdjacentHTML("afterend", "<div class='invalid-feedback'>" + message + "</div>");
                }
            }
        }
    });
}

/**
 * Submit the form in validation mode via fetch
 * @param {*} formEl The form element to submit
 * @returns The validation object, the keys are the fields and the value is an array of error messages. On success it will be `{success: true}`
 */
async function validateForm(formEl) {
    // TODO: We can pull most of this from binder since dynamic-frame.js does this too
    const method = formEl.getAttribute("method") || "GET";
    const action = formEl.getAttribute("action") || "/";
    const encoding = formEl.getAttribute("enctype") || "application/x-www-form-urlencoded";
    const skipValidation = formEl.getAttribute("novalidate") !== undefined;

    // Base HTML5 validation
    if (!skipValidation && !formEl.checkValidity()) {
        return false;
    }

    // Build the form data to send
    const formData = new FormData(formEl);
    let params = new URLSearchParams();
    for (const pair of formData) {
        params.append(pair[0], pair[1]);
    }

    if (method.toUpperCase() == "POST") {
        let request = {
            method: "POST",
            headers: {},
        };

        if (encoding === "application/x-www-form-urlencoded") {
            params.append("validate", "1");
            request.body = params;
            request.headers["Content-Type"] = "application/x-www-form-urlencoded";
        } else {
            // If sending as multipart then we omit the content-type
            let multipartData = new FormData();
            for (const pair of formData) {
                multipartData.append(pair[0], pair[1]);
            }

            multipartData.append("validate", "1");
            request.body = multipartData;
        }

        let response = await fetch(action, request);
        return await response.json();
    } else if (method.toUpperCase() == "GET") {
        // TODO: Handle GET
        const query = Object.fromEntries(new URLSearchParams(formData));
        this.setParams(query);
        this.args.url = action;
        window.history.pushState({}, "", action);
        this.refresh();
    }

    return { success: true };
}

export { attachValidation, autoAttachValidation, validateForm };
