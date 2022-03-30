import { DynamicFrame as CoreDynamicFrame } from '/static/js/vendor/binder/core/dynamic_frame.js';

// This is our custom DynamicFrame component
// It emits events when the frame is updated
class DynamicFrame extends CoreDynamicFrame {
    async loadContent(e, mode="replace") {
        await super.loadContent(e, mode);
        this.emit("dynamic-frame:updated", {});
    }
}

export { DynamicFrame };
