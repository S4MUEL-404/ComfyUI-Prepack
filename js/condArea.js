import { app } from "../../../scripts/app.js";

const PREPACK_COND_AREA_NODE = "PrepackCondArea";

const COLORS = [
    { fill: "rgba(168, 85, 247, 0.8)", stroke: "#a855f7", name: "Purple" },
    { fill: "rgba(59, 130, 246, 0.8)", stroke: "#3b82f6", name: "Blue" },
    { fill: "rgba(34, 197, 94, 0.8)", stroke: "#22c55e", name: "Green" },
    { fill: "rgba(234, 179, 8, 0.8)", stroke: "#eab308", name: "Yellow" },
    { fill: "rgba(239, 68, 68, 0.8)", stroke: "#ef4444", name: "Red" }
];

function addCondAreaCanvas(node, app) {
    const widget = {
        type: "customCanvas",
        name: "PrepackCondArea-Canvas",
        get value() {
            return "";
        },
        set value(x) {},
        draw: function (ctx, node, widgetWidth, widgetY) {
            const canvasHeight = this.computeSize()[1];
            if (canvasHeight < 40) return;

            const values = node.properties["values"];
            if (!values) return;
            
            // Convert from 1-5 to 0-4 for storage index
            const displayIndex = Math.floor(node.widgets[node.indexWidget].value);
            const currentIndex = Math.max(0, Math.min(4, displayIndex - 1));

            const MARGIN_LR = 10;  // Left and right margin
            const MARGIN_TOP = 10;  // Top margin
            const MARGIN_BOTTOM = 0;  // Bottom margin (flush with node bottom)
            
            const previewW = widgetWidth - MARGIN_LR * 2;
            const previewH = canvasHeight - MARGIN_TOP - MARGIN_BOTTOM;
            const xOffset = MARGIN_LR;
            const yOffset = widgetY + MARGIN_TOP;

            // Background
            ctx.fillStyle = "#1a1a1a";
            ctx.fillRect(xOffset, yOffset, previewW, previewH);
            ctx.strokeStyle = "#555555";
            ctx.lineWidth = 1;
            ctx.strokeRect(xOffset, yOffset, previewW, previewH);

            // Check if the selected conditioning index is connected
            const condInputName = `conditioning_${displayIndex}`;
            const condInput = node.inputs?.find(inp => inp.name === condInputName);
            const hasConditioning = condInput?.link !== null && condInput?.link !== undefined;

            if (!hasConditioning) {
                ctx.fillStyle = "#888";
                ctx.font = "12px Arial";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText("No conditioning", xOffset + previewW / 2, yOffset + previewH / 2);
                return;
            }

            // Grid
            ctx.strokeStyle = "#353535";
            ctx.lineWidth = 0.5;
            for (let i = 20; i < previewW; i += 20) {
                ctx.beginPath();
                ctx.moveTo(xOffset + i, yOffset);
                ctx.lineTo(xOffset + i, yOffset + previewH);
                ctx.stroke();
            }
            for (let i = 20; i < previewH; i += 20) {
                ctx.beginPath();
                ctx.moveTo(xOffset, yOffset + i);
                ctx.lineTo(xOffset + previewW, yOffset + i);
                ctx.stroke();
            }

            // Clipping
            ctx.save();
            ctx.beginPath();
            ctx.rect(xOffset, yOffset, previewW, previewH);
            ctx.clip();

            // Draw all conditioning areas in two passes
            // First pass: draw non-current areas with 40% opacity
            for (let idx = 0; idx < 5; idx++) {
                const condInputName = `conditioning_${idx + 1}`;
                const condInput = node.inputs?.find(inp => inp.name === condInputName);
                const isConnected = condInput?.link !== null && condInput?.link !== undefined;
                
                if (!isConnected) continue;
                if (idx === currentIndex) continue; // Skip current index in first pass
                
                const v = values[idx];
                if (!v) continue;
                
                const x = v[0];
                const y = v[1];
                const width = v[2];
                const height = v[3];
                const strength = v[4];

                if (strength > 0 && width > 0 && height > 0) {
                    const color = COLORS[idx];
                    const areaX = xOffset + (x * previewW);
                    const areaY = yOffset + (y * previewH);
                    const areaW = width * previewW;
                    const areaH = height * previewH;

                    if (areaW > 0.1 && areaH > 0.1) {
                        // Other areas: 40% opacity
                        const fillColor = color.fill.replace(/, 0\.8\)/, ", 0.4)");
                        
                        ctx.fillStyle = fillColor;
                        ctx.fillRect(areaX, areaY, areaW, areaH);
                        
                        ctx.strokeStyle = color.stroke + "80";
                        ctx.lineWidth = 1;
                        ctx.strokeRect(areaX, areaY, areaW, areaH);
                    }
                }
            }
            
            // Second pass: draw current area last (so it's on top)
            const currentV = values[currentIndex];
            if (currentV) {
                const condInputName = `conditioning_${currentIndex + 1}`;
                const condInput = node.inputs?.find(inp => inp.name === condInputName);
                const isConnected = condInput?.link !== null && condInput?.link !== undefined;
                
                if (isConnected) {
                    const x = currentV[0];
                    const y = currentV[1];
                    const width = currentV[2];
                    const height = currentV[3];
                    const strength = currentV[4];
                    
                    if (strength > 0 && width > 0 && height > 0) {
                        const color = COLORS[currentIndex];
                        const areaX = xOffset + (x * previewW);
                        const areaY = yOffset + (y * previewH);
                        const areaW = width * previewW;
                        const areaH = height * previewH;
                        
                        if (areaW > 0.1 && areaH > 0.1) {
                            // Current area: 100% opacity
                            ctx.fillStyle = color.fill.replace(/, 0\.8\)/, ", 1.0)");
                            ctx.fillRect(areaX, areaY, areaW, areaH);
                            
                            ctx.strokeStyle = color.stroke;
                            ctx.lineWidth = 2;
                            ctx.strokeRect(areaX, areaY, areaW, areaH);
                        }
                    }
                }
            }

            ctx.restore();

            // Info text - show current index info
            if (currentV) {
                ctx.fillStyle = "#aaaaaa";
                ctx.font = "0px monospace";
                ctx.textAlign = "left";
                ctx.textBaseline = "top";
                const colorName = COLORS[currentIndex].name;
                ctx.fillText(`[${displayIndex}] ${colorName} (100%)`, xOffset + 5, yOffset + 5);
                ctx.fillText(`X:${currentV[0].toFixed(2)} Y:${currentV[1].toFixed(2)} W:${currentV[2].toFixed(2)} H:${currentV[3].toFixed(2)} S:${currentV[4].toFixed(2)}`, xOffset + 5, yOffset + 16);
            }
        },
        computeSize: function() {
            if (!this.parent) return [200, 440];
            const node = this.parent;
            return [node.size[0], 440];
        }
    };

    node.addCustomWidget(widget);

    node.onRemoved = function() {
        // Cleanup when node is deleted
    };

    // Force immediate redraw on resize
    node.onResize = function (size) {
        if (app?.canvas?.draw) app.canvas.draw(true);
    };

    return { minWidth: 200, minHeight: 350, widget };
}

app.registerExtension({
    name: "prepack.condArea",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== PREPACK_COND_AREA_NODE) return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

            this.size = [260, 510];
            
            // Initialize properties
            if (!this.properties) this.properties = {};
            if (!this.properties.values) {
                this.properties.values = [
                    [0, 0, 1, 1, 1.0],
                    [0, 0, 1, 1, 1.0],
                    [0, 0, 1, 1, 1.0],
                    [0, 0, 1, 1, 1.0],
                    [0, 0, 1, 1, 1.0],
                ];
            }

            // Add canvas widget (will be positioned after all parameters)
            addCondAreaCanvas(this, app);
            
            // Store reference for parameter tracking
            this.paramNames = ["width", "height", "x", "y", "strength"];
            this.indexWidget = this.widgets.findIndex(w => w.name === "index");
            
            // Helper to save current index parameters to properties
            const saveCurrentIndexParams = () => {
                const indexW = this.widgets[this.indexWidget];
                const currentIndex = Math.floor(indexW.value) - 1;
                
                if (currentIndex >= 0 && currentIndex < 5) {
                    const xW = this.widgets.find(w => w.name === "x");
                    const yW = this.widgets.find(w => w.name === "y");
                    const widthW = this.widgets.find(w => w.name === "width");
                    const heightW = this.widgets.find(w => w.name === "height");
                    const strengthW = this.widgets.find(w => w.name === "strength");
                    
                    this.properties.values[currentIndex] = [
                        xW?.value ?? 0,
                        yW?.value ?? 0,
                        widthW?.value ?? 1,
                        heightW?.value ?? 1,
                        strengthW?.value ?? 1.0
                    ];
                }
            };
            
            // Save current index before switching
            const savePrevIndexParams = () => {
                if (this._lastIndex !== undefined) {
                    const xW = this.widgets.find(w => w.name === "x");
                    const yW = this.widgets.find(w => w.name === "y");
                    const widthW = this.widgets.find(w => w.name === "width");
                    const heightW = this.widgets.find(w => w.name === "height");
                    const strengthW = this.widgets.find(w => w.name === "strength");
                    
                    this.properties.values[this._lastIndex] = [
                        xW?.value ?? 0,
                        yW?.value ?? 0,
                        widthW?.value ?? 1,
                        heightW?.value ?? 1,
                        strengthW?.value ?? 1.0
                    ];
                }
            };
            
            // Helper to load parameters from properties for given index
            const loadIndexParams = (indexValue) => {
                const idx = Math.floor(indexValue) - 1;
                if (idx >= 0 && idx < 5) {
                    const values = this.properties.values[idx] || [0, 0, 1, 1, 1.0];
                    const xW = this.widgets.find(w => w.name === "x");
                    const yW = this.widgets.find(w => w.name === "y");
                    const widthW = this.widgets.find(w => w.name === "width");
                    const heightW = this.widgets.find(w => w.name === "height");
                    const strengthW = this.widgets.find(w => w.name === "strength");
                    
                    if (xW) xW.value = values[0];
                    if (yW) yW.value = values[1];
                    if (widthW) widthW.value = values[2];
                    if (heightW) heightW.value = values[3];
                    if (strengthW) strengthW.value = values[4];
                }
            };
            
            // Setup index widget callback
            if (this.indexWidget !== -1) {
                const indexW = this.widgets[this.indexWidget];
                const origIndexCallback = indexW.callback;
                this._lastIndex = Math.floor(indexW.value) - 1;
                
                indexW.callback = (v) => {
                    // Save previous index parameters first
                    savePrevIndexParams();
                    
                    // Update index value
                    indexW.value = v;
                    this._lastIndex = Math.floor(v) - 1;
                    
                    // Load new index parameters
                    loadIndexParams(v);
                    
                    // Call original callback if present
                    if (origIndexCallback) origIndexCallback.call(indexW, v);
                    
                    if (app?.canvas?.draw) app.canvas.draw(true);
                };
                
                // Initial load of current index parameters
                loadIndexParams(this._lastIndex + 1);
            }
            
            // Setup parameter callbacks to save on every change
            this.paramNames.forEach(name => {
                const w = this.widgets.find(x => x.name === name);
                if (w) {
                    const origCallback = w.callback;
                    w.callback = (v) => {
                        // Call original callback first
                        if (origCallback) origCallback.call(w, v);
                        
                        // Immediately save to properties
                        saveCurrentIndexParams();
                        
                        if (app?.canvas?.draw) app.canvas.draw(true);
                    };
                }
            });

            return r;
        };
    },
});
