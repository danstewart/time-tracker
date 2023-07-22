import { DynamicFrame as CoreDynamicFrame } from "/static/js/vendor/binder/core/dynamic_frame.js";

// This is our custom DynamicFrame component
// It emits events when the frame is updated
class DynamicFrame extends CoreDynamicFrame {
    async loadContent(e, method = "get") {
        await super.loadContent(e, method);
        this.emit("dynamic-frame:updated", {});
    }
}

export { DynamicFrame };
