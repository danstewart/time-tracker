import { Controller } from 'https://cdn.jsdelivr.net/gh/danstewart/binder-js@0.0.5/src/binder/controller.js';

class FormSwitcherController extends Controller {
    init() {
        this.selectedTab = 0;
    }

    changeTab(e) {
        this.getBindAll('tab').forEach((tab, index) => {
            if (tab == e.target) {
                this.selectedTab = index;
                tab.classList.add("active");
            } else {
                tab.classList.remove("active");
            }
        });

        this.getBindAll('content').forEach((content, index) => {
            if (index == this.selectedTab)
                content.classList.remove("d-none")
            else
                content.classList.add("d-none")
        });
    }
}

export { FormSwitcherController };
