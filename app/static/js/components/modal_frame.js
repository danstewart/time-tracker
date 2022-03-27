import { Controller, html } from '/static/js/vendor/binder.js';

// A Bootstrap 5 modal with a dynamic-frame as it's content
// The dynamic-frame is lazily loaded the first time the modal is shown
// It is not re-requested on susbsequent shows
class ModalFrame extends Controller {
    init() {
        this.innerHTML = html`
            <section class="modal fade" id="${this.modalId}">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${this.modalTitle}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <dynamic-frame :render-on-init="false" :url="${this.url}"></dynamic-frame>
                        </div>
                         <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary">Save changes</button>
                        </div>
                    </div>
                </div>
            </section>
        `;

        this.loaded = false;
        this.modal = this.querySelector('.modal');
        this.modal.addEventListener("show.bs.modal", e => this.onShow(e));
    }

    onShow(e) {
        if (this.loaded) return;
        this.querySelector("dynamic-frame").loadContent(e);
        this.loaded = true;
    }
}

export { ModalFrame };
