function autoAttachValidation() {
    const forms = document.querySelectorAll("form");
    forms.forEach(form => attachValidation(form));
}

function resetFormValidation(formEl) {
    formEl.querySelectorAll(".is-invalid").forEach(fieldEl => {
        fieldEl.classList.remove("is-invalid");
    });

    formEl.querySelectorAll("div.invalid-feedback").forEach(feedbackEl => {
        feedbackEl.remove();
    });
}

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

async function validateForm(formEl) {
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
