import { Controller, html } from "/static/js/vendor/binder/binder.js";

// A Bootstrap 5 modal with a dynamic-frame as it's content
// The dynamic-frame is lazily loaded the first time the modal is shown
// It is not re-requested on susbsequent shows
class ModalFrame extends Controller {
    init() {
        this.innerHTML = html`
            <section class="modal fade" id="${this.modalId}">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <dynamic-frame :execute-scripts="true" :render-on-init="false" :url="${this.url}"></dynamic-frame>
                    </div>
                </div>
            </section>
        `;

        this.loaded = false;
        this.modal = this.querySelector(".modal");
        this.modal.addEventListener("show.bs.modal", e => this.onShow(e));

        this.listenFor(`${this.modalId}:close`, e => this.modal("hide"));
    }

    onShow(e) {
        if (this.loaded) return;
        this.querySelector("dynamic-frame").loadContent(e);
        this.loaded = true;
    }
}

export { ModalFrame };
