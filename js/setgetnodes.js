import { app } from "../../scripts/app.js";

// Minimal Set/Get nodes as virtual (frontend-only) tunnel helpers
// No extra features (no colors, no virtual link rendering, no settings)

app.registerExtension({
	name: "ComfyUI-Prepack.SetGet",
	async setup() {
		console.log("[ComfyUI-Prepack] Set/Get virtual nodes loaded");
	},
	registerCustomNodes(app) {
		const LGraphNode = LiteGraph.LGraphNode;

		// Type -> color mapping (fallback to deterministic palette)
		const TYPE_COLOR_MAP = {
			"*": { color: "#363636", bgcolor: "#1C1C1C" },
			IMAGE: { color: "#2E5EA6", bgcolor: "#234880" },
			MASK: { color: "#3A7A3A", bgcolor: "#295629" },
			LATENT: { color: "#0d3b66", bgcolor: "#56cfe1" },
			MODEL: { color: "#6E3A8C", bgcolor: "#522B69" },
			CLIP: { color: "#C7A63A", bgcolor: "#9F842D" },
			VAE: { color: "#A63A3A", bgcolor: "#812D2D" },
			CONDITIONING: { color: "#C75E2E", bgcolor: "#9D4A24" },
			STRING: { color: "#6E4A3A", bgcolor: "#4D3428" },
			PIPE: { color: "#A63A3A", bgcolor: "#812D2D" },
			INT: { color: "#6E4A3A", bgcolor: "#4D3428" },
		};

		const FALLBACK_BG_PALETTE = [
			"#2b2b2b", "#1c1c1c", "#3a3a3a"
		];

		function getTypeColors(type) {
			const t = String(type || "*").toUpperCase();
			if (TYPE_COLOR_MAP[t]) return TYPE_COLOR_MAP[t];
			if (!FALLBACK_BG_PALETTE.length) return { color: "#2f2f2f", bgcolor: "#1c1c1c" };
			let sum = 0;
			for (let i = 0; i < t.length; i++) sum = (sum + t.charCodeAt(i)) % 997;
			const bgcolor = FALLBACK_BG_PALETTE[sum % FALLBACK_BG_PALETTE.length];
			return { color: "#2f2f2f", bgcolor };
		}

		function applyNodeColors(node, type) {
			const { color, bgcolor } = getTypeColors(type);
			node.color = color;
			node.bgcolor = bgcolor;
			// request redraw if available
			node.graph?.setDirtyCanvas?.(true, true);
		}

		// Normalize a user-provided name: trim, take first line, remove quotes
		function normalizeName(s) {
			if (typeof s !== "string") return "";
			let v = s.replace(/\r\n/g, "\n");
			v = v.split("\n")[0];
			v = v.trim();
			if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
				v = v.slice(1, -1).trim();
			}
			return v;
		}

		// Try to extract a string value from an upstream node's widgets
		function extractStringFromNode(node) {
			if (!node || !node.widgets || !Array.isArray(node.widgets)) return null;
			for (const w of node.widgets) {
				const t = (w?.type || "").toLowerCase();
				if ((t === "text" || t === "string") && typeof w.value === "string") {
					return normalizeName(w.value);
				}
			}
			// fallback: if there is a widget with a string value regardless of type
			for (const w of node.widgets) {
				if (typeof w?.value === "string") return normalizeName(w.value);
			}
			return null;
		}

		class SetNode extends LGraphNode {
			constructor(title) {
				super(title);
				// properties
				if (!this.properties) this.properties = {};
				// persist widget values in workflow JSON
				this.serialize_widgets = true;
				// widgets
				this.addWidget(
					"text",
					"Name",
					"",
					() => {
						const oldName = this._prevName || "";
						this.resolveConflictsPreferCurrent();
						this.ensureUniqueName();
						this.updateTitle();
						this.updateGetters();
						const newName = this.getCurrentName();
						if (oldName && newName !== undefined && oldName !== newName) {
							if (newName === "") {
								this.propagateNameRemoval(oldName);
							} else {
								this.propagateNameChange(oldName, newName);
							}
						}
						this._prevName = newName;
					}
				);
				this._prevName = this.getCurrentName();
				// io
				this.addInput("*", "*");
				this.addOutput("*", "*");
				// virtual node (not serialized into prompt)
				this.isVirtualNode = true;
				this.updateTitle();
			}

			// Ensure unique name when the node is added (e.g. after copy/paste)
			onAdded(graph) {
				const oldName = this.getCurrentName();
				this.ensureUniqueName();
				const newName = this.getCurrentName();
				// Do not propagate name changes on add (e.g. after copy/paste)
				this._prevName = newName;
				this.updateTitle();
				this.updateGetters();
			}

			onConfigure() {
				// refresh title and propagate types after load
				const oldName = this.getCurrentName();
				this.ensureUniqueName();
				this.updateTitle();
				this.updateGetters();
				const newName = this.getCurrentName();
				if (oldName && newName !== undefined && oldName !== newName) {
					if (newName === "") this.propagateNameRemoval(oldName);
					else this.propagateNameChange(oldName, newName);
				}
				this._prevName = newName;
			}

			updateTitle() {
				const name = this.widgets?.[0]?.value || "";
				this.title = name ? `Set_${name}` : "Set";
			}

			onRemoved() {
				const name = this.getCurrentName();
				if (name) this.propagateNameRemoval(name);
			}

			getCurrentName() {
				return this.widgets?.[0]?.value || "";
			}

			ensureUniqueName() {
				if (!this.graph) return;
				const widget = this.widgets?.[0];
				if (!widget) return;
				let name = widget.value || "";
				if (!name) return;
				const others = [];
				for (const n of this.graph._nodes) {
					if (n !== this && n instanceof SetNode) {
						const val = n.widgets?.[0]?.value;
						if (val) others.push(String(val));
					}
				}
				if (!others.includes(name)) return;
				// New copy naming policy: first duplicate -> _copy, then _copy_2, _copy_3, ...
				const base = String(name);
				const copyBase = `${base}_copy`;
				const escapedCopyBase = copyBase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
				let hasPlainCopy = false;
				const used = new Set();
				for (const v of others) {
					if (v === copyBase) {
						hasPlainCopy = true;
						continue;
					}
					const mm = v.match(new RegExp(`^${escapedCopyBase}_(\\d+)$`));
					if (mm) used.add(parseInt(mm[1], 10));
				}
				if (!hasPlainCopy) {
					widget.value = copyBase;
					return;
				}
				let idx = 2; // numbering starts from 2
				while (used.has(idx)) idx++;
				widget.value = `${copyBase}_${idx}`;
			}

			resolveConflictsPreferCurrent() {
				if (!this.graph) return;
				const widget = this.widgets?.[0];
				if (!widget) return;
				const name = widget.value || "";
				if (!name) return;
				// Build a set of used names reserving current name
				const used = new Set();
				for (const n of this.graph._nodes) {
					if (n instanceof SetNode) {
						const val = n.widgets?.[0]?.value;
						if (val) used.add(String(val));
					}
				}
				// For every conflicting peer, rename it using `_copy` policy, keeping current unchanged
				for (const n of this.graph._nodes) {
					if (n !== this && n instanceof SetNode) {
						const w = n.widgets?.[0];
						if (!w) continue;
						if (String(w.value || "") === name) {
							const oldVal = String(w.value || "");
							const copyBase = `${name}_copy`;
							let newVal = "";
							if (!used.has(copyBase)) {
								newVal = copyBase;
							} else {
								let idx = 2; // numbering starts from 2
								while (used.has(`${copyBase}_${idx}`)) idx++;
								newVal = `${copyBase}_${idx}`;
							}
							w.value = newVal;
							used.add(newVal);
							n.updateTitle?.();
							n.updateGetters?.();
							n.propagateNameChange?.(oldVal, newVal);
						}
					}
				}
			}

			propagateNameChange(oldName, newName) {
				if (!this.graph || !oldName || !newName) return;
				for (const n of this.graph._nodes) {
					if (n instanceof GetNode) {
						const w = n.widgets?.[0];
						if (!w) continue;
						if (String(w.value || "") === String(oldName)) {
							w.value = String(newName);
							n.onNameChanged();
						}
					}
				}
			}

			propagateNameRemoval(oldName) {
				if (!this.graph || !oldName) return;
				for (const n of this.graph._nodes) {
					if (n instanceof GetNode) {
						const w = n.widgets?.[0];
						if (!w) continue;
						if (String(w.value || "") === String(oldName)) {
							w.value = "";
							n.onNameChanged();
						}
					}
				}
			}

			// propagate current input type to all matching Get nodes
			updateGetters() {
				if (!this.graph) return;
				const name = this.widgets?.[0]?.value || "";
				const type = this.inputs?.[0]?.type || "*";
				// Always color Set by its current resolved type, even if name is empty
				applyNodeColors(this, type);
				if (!name) return;
				for (const n of this.graph._nodes) {
					if (n instanceof GetNode) {
						const getName = n.widgets?.[0]?.value || "";
						if (getName === name) {
							// Delegate to node's own logic so it can check target-compatibility
							if (typeof n.onNameChanged === "function") n.onNameChanged();
							else {
								n.setOutputType?.(type);
								n.updateTitle?.();
							}
						}
					}
				}
			}

			onConnectionsChange(slotType, slot, isChangeConnect, link_info) {
				// slotType: 1=input, 2=output in Comfy's wrapper (LiteGraph uses 1=input, 2=output)
				if (!this.graph) return;
				// When input gets connected, adopt the upstream type and mirror to output
				if (slotType === 1 && isChangeConnect && link_info) {
					const origin = this.graph._nodes.find(n => n.id === link_info.origin_id);
					if (origin && origin.outputs && origin.outputs[link_info.origin_slot]) {
						const t = origin.outputs[link_info.origin_slot].type || "*";
						this.inputs[0].type = t;
						this.inputs[0].name = t;
						this.outputs[0].type = t;
						this.outputs[0].name = t;
						this.updateGetters();
					}
				}
				// When output gets connected to a typed input, adopt that input type
				if (slotType === 2 && isChangeConnect && link_info) {
					const toNode = this.graph._nodes.find(n => n.id === link_info.target_id);
					if (toNode && toNode.inputs && toNode.inputs[link_info.target_slot]) {
						const t = toNode.inputs[link_info.target_slot].type || "*";
						this.outputs[0].type = t;
						this.outputs[0].name = t;
						// Do not force input type here; Set may have no upstream
						this.updateGetters();
					}
				}
				// If input link removed, reset io types to wildcard
				if (slotType === 1 && !isChangeConnect) {
					if (this.inputs && this.inputs[slot]) {
						this.inputs[slot].type = "*";
						this.inputs[slot].name = "*";
					}
					if (this.outputs && this.outputs[0]) {
						this.outputs[0].type = "*";
						this.outputs[0].name = "*";
					}
					this.updateGetters();
				}
				// If output link removed and there is no input typing, keep wildcard on output
				if (slotType === 2 && !isChangeConnect) {
					if (!this.inputs || !this.inputs[0] || (this.inputs[0].type === "*")) {
						if (this.outputs && this.outputs[0]) {
							this.outputs[0].type = "*";
							this.outputs[0].name = "*";
						}
						this.updateGetters();
					}
				}
			}
		}

		SetNode.title = "💀Prepack Set Any";
		SetNode.category = "💀Prepack";
		LiteGraph.registerNodeType("💀Prepack/💀Prepack Set Any", SetNode);

		class GetNode extends LGraphNode {
			constructor(title) {
				super(title);
				if (!this.properties) this.properties = {};
				// persist widget values in workflow JSON
				this.serialize_widgets = true;
				this.addWidget(
					"combo",
					"Name",
					"",
					() => this.onNameChanged(),
					{
						values: () => this.collectSetterNames(),
					}
				);
				this.addOutput("*", "*");
				this.isVirtualNode = true;
				this.updateTitle();
			}

			onAdded() {
				// Inherit color based on resolved type after paste/creation
				const setter = this.findSetter?.();
				const t = setter?.inputs?.[0]?.type || "*";
				this.setOutputType?.(t);
			}

			onConfigure() {
				// ensure output type/title reflects saved selection after load
				this.onNameChanged();
			}

			collectSetterNames() {
				if (!this.graph) return [];
				// Determine required type from the first connected target input (if any)
				const requiredType = this.getRequiredTargetType();
				const isCompatible = (setType, reqType) => {
					if (!reqType || reqType === "*") return true;
					if (!setType || setType === "*") return true;
					const reqs = String(reqType).split(",").map(s => s.trim()).filter(Boolean);
					const sets = String(setType).split(",").map(s => s.trim()).filter(Boolean);
					return sets.some(t => reqs.includes(t));
				};
				// Group by full base name (without copy suffix). Order: base first, then copies by index
				const groups = new Map(); // base -> { base: string|null, copies: Array<{name:string,index:number}> }
				for (const n of this.graph._nodes) {
					if (!(n instanceof SetNode)) continue;
					const val = n.widgets?.[0]?.value;
					if (!val) continue;
					const setType = n.inputs?.[0]?.type || "*";
					if (!isCompatible(setType, requiredType)) continue;
					const cp = String(val).match(/^(.*)_copy(?:_(\d+))?$/);
					if (cp) {
						const base = cp[1];
						const idx = cp[2] ? parseInt(cp[2], 10) : 1;
						let bucket = groups.get(base);
						if (!bucket) { bucket = { base: null, copies: [] }; groups.set(base, bucket); }
						bucket.copies.push({ name: val, index: idx });
					} else {
						let bucket = groups.get(val);
						if (!bucket) { bucket = { base: null, copies: [] }; groups.set(val, bucket); }
						bucket.base = val;
					}
				}
				const orderedBaseKeys = Array.from(groups.keys()).sort();
				const result = [];
				for (const base of orderedBaseKeys) {
					const bucket = groups.get(base);
					if (bucket.base) result.push(bucket.base);
					bucket.copies.sort((a, b) => a.index - b.index);
					for (const c of bucket.copies) result.push(c.name);
				}
				return result;
			}

			// Determine type expected by the first target connected to this Get's output
			getRequiredTargetType() {
				if (!this.graph) return null;
				const out = this.outputs?.[0];
				if (!out || !out.links || out.links.length === 0) return null;
				const linkId = out.links[0];
				const link = this.graph.links[linkId];
				if (!link) return null;
				const toNode = this.graph._nodes.find(n => n.id === link.target_id);
				if (!toNode || !toNode.inputs || !toNode.inputs[link.target_slot]) return null;
				return toNode.inputs[link.target_slot].type || "*";
			}

			findSetter() {
				if (!this.graph) return null;
				const name = this.widgets?.[0]?.value || "";
				if (!name) return null;
				return this.graph._nodes.find(n => (n instanceof SetNode) && n.widgets?.[0]?.value === name) || null;
			}

			onNameChanged() {
				const setter = this.findSetter();
				if (setter) {
					const t = setter.inputs?.[0]?.type || "*";
					this.setOutputType(t);
				} else {
					this.setOutputType("*");
				}
				this.updateTitle();
			}

			setOutputType(t) {
				this.outputs[0].type = t;
				this.outputs[0].name = t;
				this.removeIncompatibleLinks();
				// apply color to Get based on chosen type
				applyNodeColors(this, t);
			}

			// Map Get's output to the Set's input link for prompt building
			getInputLink(slot) {
				const setter = this.findSetter();
				if (!setter) return null;
				const slotInfo = setter.inputs?.[slot];
				if (!slotInfo) return null;
				return this.graph?.links?.[slotInfo.link] || null;
			}

			removeIncompatibleLinks() {
				if (!this.graph) return;
				const out = this.outputs?.[0];
				if (!out || !out.links || out.type === "*") return;
				for (const linkId of [...out.links]) {
					const link = this.graph.links[linkId];
					if (!link) continue;
					const linkType = link.type;
					if (linkType !== "*" && !String(linkType).split(",").includes(out.type)) {
						this.graph.removeLink(linkId);
					}
				}
			}

			updateTitle() {
				const name = this.widgets?.[0]?.value || "";
				this.title = name ? `Get_${name}` : "Get";
			}
		}

		GetNode.title = "💀Prepack Get Any";
		GetNode.category = "💀Prepack";
		LiteGraph.registerNodeType("💀Prepack/💀Prepack Get Any", GetNode);

	},
});

