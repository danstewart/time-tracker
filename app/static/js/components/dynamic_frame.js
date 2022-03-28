import { DynamicFrame as CoreDynamicFrame } from '/static/js/vendor/binder/core/dynamic_frame.js';

// This is our custom DynamicFrame component
// It emits events when the frame is updated
class DynamicFrame extends CoreDynamicFrame {
    async loadContent(e, mode="replace") {
        await super.loadContent(e, mode);
        this.findAndExecuteScripts();
        this.emit("dynamic-frame:updated", {});
    }

    // TODO: This should be moved to the binder.js DynamicFrame

    /**
     * Called during `loadContent()`
     * Will find all script tags within the frame and execute them
     * Only if the frame has the `execute-scripts` attribute set to true
     */
    findAndExecuteScripts() {
        if (this.executeScripts !== "true") return;

        let scripts = this.querySelectorAll('script');
        if (!scripts) return;

        [ ...scripts ].forEach(script => {

            let newScript = document.createElement("script");
            newScript.setAttribute("type", "text/javascript");

            if (script.getAttribute("src")) {
                newScript.setAttribute("src", script.getAttribute("src"));
                this.appendChild(newScript);
            } else {
                newScript.appendChild(document.createTextNode(script.innerHTML));
                this.appendChild(newScript);
            }
        });
    }
}

export { DynamicFrame };
