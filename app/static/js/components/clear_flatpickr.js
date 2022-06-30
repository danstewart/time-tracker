import { Controller, html, css } from "/static/js/vendor/binder/binder.js";

/**
 * A button designed to be combined with a flatpickr input to clear the value
 * Example
 * ```html
 * <input class="flatpickr" />
 * <clear-flatpickr></clear-flatpickr>
 * ```
 */
class ClearFlatpickr extends Controller {
    init() {
        this.innerHTML = html`
            <button class="btn btn-outline-secondary" type="button" data-toggle="tooltip" data-placement="top" @click="clearPickr" title="Clear End Time">
                <i class="bi bi-x"></i>
            </button>
        `;

        this.querySelector("button").style.cssText = css`
            border-top-left-radius: 0;
            border-bottom-left-radius: 0;
        `;

        this.bind();
    }

    clearPickr() {
        this.previousElementSibling.previousElementSibling._flatpickr.clear();
    }
}

export { ClearFlatpickr };
