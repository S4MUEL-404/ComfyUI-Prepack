import { app } from "../../../scripts/app.js";

class WorkflowScreenshotExporter {
    constructor() {
        this.state = null;
    }

    // Get bounds of all nodes in the workflow
    getBounds() {
        const bounds = app.graph._nodes.reduce(
            (p, n) => {
                if (n.pos[0] < p[0]) p[0] = n.pos[0];
                if (n.pos[1] < p[1]) p[1] = n.pos[1];
                const nodeBounds = n.getBounding();
                const r = n.pos[0] + nodeBounds[2];
                const b = n.pos[1] + nodeBounds[3];
                if (r > p[2]) p[2] = r;
                if (b > p[3]) p[3] = b;
                return p;
            },
            [99999, 99999, -99999, -99999]
        );

        // Add padding: top(2 grid), left(1 grid), bottom(1 grid), right(1 grid)
        // ComfyUI grid size is approximately 10px, so multiply by grid size
        const gridSize = LiteGraph.NODE_SLOT_HEIGHT || 10;
        bounds[0] -= gridSize * 10;  // left: 1 grid
        bounds[1] -= gridSize * 20;  // top: 2 grids
        bounds[2] += gridSize * 10;  // right: 1 grid
        bounds[3] += gridSize * 10;  // bottom: 1 grid
        return bounds;
    }

    // Save current canvas state
    saveState() {
        this.state = {
            scale: app.canvas.ds.scale,
            width: app.canvas.canvas.width,
            height: app.canvas.canvas.height,
            offset: app.canvas.ds.offset,
            transform: app.canvas.canvas.getContext("2d").getTransform(),
        };
    }

    // Restore canvas state
    restoreState() {
        if (!this.state) return;
        app.canvas.ds.scale = this.state.scale;
        app.canvas.canvas.width = this.state.width;
        app.canvas.canvas.height = this.state.height;
        app.canvas.ds.offset = this.state.offset;
        app.canvas.canvas.getContext("2d").setTransform(this.state.transform);
    }

    // Update view to fit entire workflow
    updateView(bounds) {
        const scale = window.devicePixelRatio || 1;
        app.canvas.ds.scale = 1;
        app.canvas.canvas.width = (bounds[2] - bounds[0]) * scale;
        app.canvas.canvas.height = (bounds[3] - bounds[1]) * scale;
        app.canvas.ds.offset = [-bounds[0], -bounds[1]];
        app.canvas.canvas.getContext("2d").setTransform(scale, 0, 0, scale, 0, 0);
    }

    // Generate PNG blob with optional workflow data
    async getBlob(includeWorkflow) {
        return new Promise((resolve) => {
            app.canvasEl.toBlob(async (blob) => {
                if (includeWorkflow) {
                    // Embed workflow data in PNG metadata
                    const workflow = JSON.stringify(app.graph.serialize());
                    const buffer = await blob.arrayBuffer();
                    const typedArr = new Uint8Array(buffer);
                    const view = new DataView(buffer);

                    const data = new TextEncoder().encode(`tEXtworkflow\0${workflow}`);
                    const chunk = this.joinArrayBuffer(
                        this.n2b(data.byteLength - 4),
                        data,
                        this.n2b(this.crc32(data))
                    );

                    const sz = view.getUint32(8) + 20;
                    const result = this.joinArrayBuffer(
                        typedArr.subarray(0, sz),
                        chunk,
                        typedArr.subarray(sz)
                    );

                    blob = new Blob([result], { type: "image/png" });
                }
                resolve(blob);
            });
        });
    }

    // Helper: Convert number to 4-byte array
    n2b(n) {
        return new Uint8Array([
            (n >> 24) & 0xff,
            (n >> 16) & 0xff,
            (n >> 8) & 0xff,
            n & 0xff,
        ]);
    }

    // Helper: Join multiple array buffers
    joinArrayBuffer(...bufs) {
        const result = new Uint8Array(
            bufs.reduce((totalSize, buf) => totalSize + buf.byteLength, 0)
        );
        bufs.reduce((offset, buf) => {
            result.set(buf, offset);
            return offset + buf.byteLength;
        }, 0);
        return result;
    }

    // Helper: Calculate CRC32 checksum
    crc32(data) {
        const crcTable =
            WorkflowScreenshotExporter.crcTable ||
            (WorkflowScreenshotExporter.crcTable = (() => {
                let c;
                const crcTable = [];
                for (let n = 0; n < 256; n++) {
                    c = n;
                    for (let k = 0; k < 8; k++) {
                        c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
                    }
                    crcTable[n] = c;
                }
                return crcTable;
            })());
        let crc = 0 ^ -1;
        for (let i = 0; i < data.byteLength; i++) {
            crc = (crc >>> 8) ^ crcTable[(crc ^ data[i]) & 0xff];
        }
        return (crc ^ -1) >>> 0;
    }

    // Download the generated PNG
    download(blob, filename = "workflow_screenshot.png") {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        Object.assign(a, {
            href: url,
            download: filename,
            style: "display: none",
        });
        document.body.append(a);
        a.click();
        setTimeout(function () {
            a.remove();
            window.URL.revokeObjectURL(url);
        }, 0);
    }

    // Main export function
    async export(includeWorkflow = true, filename = null) {
        try {
            // Save current state
            this.saveState();

            // Update view to show entire workflow
            const bounds = this.getBounds();
            this.updateView(bounds);

            // Render canvas
            app.canvas.draw(true, true);

            // Generate PNG blob
            const blob = await this.getBlob(includeWorkflow);

            // Restore state
            this.restoreState();
            app.canvas.draw(true, true);

            // Generate filename with timestamp if not provided
            if (!filename) {
                const timestamp = new Date()
                    .toISOString()
                    .replace(/[:.]/g, "-")
                    .slice(0, -5);
                filename = `workflow_${timestamp}.png`;
            }

            // Download
            this.download(blob, filename);

            return true;
        } catch (error) {
            console.error("Export workflow screenshot failed:", error);
            this.restoreState();
            app.canvas.draw(true, true);
            return false;
        }
    }
}

// Register extension
app.registerExtension({
    name: "Prepack.ExportWorkflowPNG",
    
    async setup() {
        const exporter = new WorkflowScreenshotExporter();

        // Add menu options
        const orig = LGraphCanvas.prototype.getCanvasMenuOptions;
        LGraphCanvas.prototype.getCanvasMenuOptions = function () {
            const options = orig.apply(this, arguments);

            options.push(null, {
                content: "💀Export Workflow as PNG",
                submenu: {
                    options: [
                        {
                            content: "With workflow data",
                            callback: () => {
                                exporter.export(true);
                            },
                        },
                        {
                            content: "Image Only",
                            callback: () => {
                                exporter.export(false);
                            },
                        },
                    ],
                },
            });

            return options;
        };
    },
});
