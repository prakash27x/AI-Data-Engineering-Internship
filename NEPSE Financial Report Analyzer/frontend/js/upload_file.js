/**
 * Upload page — extraction modal, duplicate overwrite, recent activity view-all.
 */

(function () {
    const API_BASE = "http://127.0.0.1:8000";
    const UPLOAD_URL = `${API_BASE}/upload/report`;
    const RECENT_URL = `${API_BASE}/upload/recent`;
    const FORM_OPTIONS_URL = `${API_BASE}/upload/form-options`;
    const CHECK_DUP_URL = `${API_BASE}/upload/check-duplicate`;
    const MAX_BYTES = 25 * 1024 * 1024;
    const PREVIEW_LIMIT = 5;

    let selectedFile = null;
    let isUploading = false;
    let allActivityRows = [];
    let activityExpanded = false;
    let pendingOverwrite = false;

    function escapeHtml(text) {
        return String(text ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    function toggleTheme() {
        document.documentElement.classList.toggle("dark");
        localStorage.setItem(
            "theme",
            document.documentElement.classList.contains("dark") ? "dark" : "light"
        );
    }

    function toggleSidebar() {
        const sidebar = document.getElementById("sidebar");
        if (!sidebar) return;
        sidebar.classList.toggle("hidden");
        sidebar.classList.toggle("flex");
    }

    function showStatus(message, type) {
        const el = document.getElementById("upload-status");
        if (!el) return;
        el.classList.remove("hidden", "success", "error", "info");
        el.textContent = message;
        if (type) el.classList.add(type);
    }

    function setEngineState(label, message, progressPct) {
        const status = document.getElementById("engine-status");
        const msg = document.getElementById("engine-message");
        const bar = document.getElementById("engine-progress");
        if (status) {
            status.innerHTML =
                '<span class="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span> ' +
                escapeHtml(label);
        }
        if (msg) msg.textContent = message;
        if (bar) bar.style.width = `${progressPct}%`;
    }

    function openModal(id) {
        const el = document.getElementById(id);
        if (!el) return;
        el.classList.remove("hidden");
        el.setAttribute("aria-hidden", "false");
        
        if (id === "extract-modal") {
            setTimeout(() => {
                const card = document.getElementById("extract-popup-card");
                if (card) {
                    card.classList.remove("translate-y-10", "opacity-0");
                    card.classList.add("translate-y-0", "opacity-100");
                }
            }, 10);
        } else {
            document.body.classList.add("modal-open");
        }
    }

    function closeModal(id) {
        const el = document.getElementById(id);
        if (!el) return;

        if (id === "extract-modal") {
            const card = document.getElementById("extract-popup-card");
            if (card) {
                card.classList.remove("translate-y-0", "opacity-100");
                card.classList.add("translate-y-10", "opacity-0");
                setTimeout(() => {
                    el.classList.add("hidden");
                    el.setAttribute("aria-hidden", "true");
                    checkModalOpenClass();
                }, 300);
            } else {
                el.classList.add("hidden");
                el.setAttribute("aria-hidden", "true");
                checkModalOpenClass();
            }
        } else {
            el.classList.add("hidden");
            el.setAttribute("aria-hidden", "true");
            checkModalOpenClass();
        }
    }

    function checkModalOpenClass() {
        if (
            document.getElementById("extract-modal")?.classList.contains("hidden") &&
            document.getElementById("duplicate-modal")?.classList.contains("hidden")
        ) {
            document.body.classList.remove("modal-open");
        }
    }

    function showExtractLoading() {
        document.getElementById("extract-modal-loading")?.classList.remove("hidden");
        document.getElementById("extract-modal-result")?.classList.add("hidden");
        openModal("extract-modal");
    }

    function showExtractResult(ok, title, message, dashboardUrl) {
        document.getElementById("extract-modal-loading")?.classList.add("hidden");
        const result = document.getElementById("extract-modal-result");
        result?.classList.remove("hidden");

        const icon = document.getElementById("extract-modal-icon");
        const titleEl = document.getElementById("extract-modal-result-title");
        const msgEl = document.getElementById("extract-modal-result-msg");
        const dash = document.getElementById("extract-modal-dashboard");

        if (icon) {
            icon.innerHTML = ok
                ? '<span class="material-symbols-outlined text-green-600 text-3xl">check_circle</span>'
                : '<span class="material-symbols-outlined text-red-600 text-3xl">error</span>';
        }
        if (titleEl) titleEl.textContent = title;
        if (msgEl) msgEl.textContent = message;

        if (dash) {
            if (ok && dashboardUrl) {
                dash.href = dashboardUrl;
                dash.classList.remove("hidden");
            } else {
                dash.classList.add("hidden");
            }
        }

        openModal("extract-modal");
    }

    function askOverwrite(message) {
        return new Promise((resolve) => {
            const msgEl = document.getElementById("duplicate-modal-msg");
            if (msgEl) msgEl.textContent = message || "This report already exists.";

            const yes = document.getElementById("duplicate-yes");
            const no = document.getElementById("duplicate-no");

            const cleanup = () => {
                yes?.removeEventListener("click", onYes);
                no?.removeEventListener("click", onNo);
                closeModal("duplicate-modal");
            };

            const onYes = () => {
                cleanup();
                resolve(true);
            };
            const onNo = () => {
                cleanup();
                resolve(false);
            };

            yes?.addEventListener("click", onYes);
            no?.addEventListener("click", onNo);
            openModal("duplicate-modal");
        });
    }

    function assignFileToInput(file) {
        const input = document.getElementById("file-input");
        if (!input || !file) return;
        try {
            const dt = new DataTransfer();
            dt.items.add(file);
            input.files = dt.files;
        } catch (e) {
            console.warn("Could not sync file to input", e);
        }
    }

    function setSelectedFile(file) {
        const title = document.getElementById("dropzone-title");
        const subtitle = document.getElementById("dropzone-subtitle");

        if (!file) {
            selectedFile = null;
            const input = document.getElementById("file-input");
            if (input) input.value = "";
            if (title) title.textContent = "Drop PDF report here";
            if (subtitle) subtitle.textContent = "or click to browse from your computer";
            return;
        }

        if (!file.name.toLowerCase().endsWith(".pdf")) {
            showStatus("Only PDF files are allowed.", "error");
            return;
        }
        if (file.size > MAX_BYTES) {
            showStatus("PDF exceeds the 25MB size limit.", "error");
            return;
        }

        selectedFile = file;
        assignFileToInput(file);

        const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
        if (title) title.textContent = file.name;
        if (subtitle) subtitle.textContent = `${sizeMb} MB selected`;
        showStatus(`Selected: ${file.name}`, "info");
    }

    function resetForm() {
        selectedFile = null;
        isUploading = false;
        pendingOverwrite = false;
        document.getElementById("company-symbol").value = "";
        document.getElementById("company-name").value = "";
        document.getElementById("existing-company").value = "";
        document.getElementById("sector").value = "hydropower";
        document.getElementById("report-type").value = "quarterly";
        setSelectedFile(null);
        setEngineState("READY", "Waiting for PDF", 0);
        document.getElementById("upload-status")?.classList.add("hidden");
        loadFormOptions();
    }

    function fillSelect(selectEl, items, getValue, getLabel, selectedValue) {
        if (!selectEl) return;
        const previous = selectedValue ?? selectEl.value;
        selectEl.innerHTML = "";
        items.forEach((item) => {
            const opt = document.createElement("option");
            opt.value = getValue(item);
            opt.textContent = getLabel(item);
            selectEl.appendChild(opt);
        });
        if (previous && [...selectEl.options].some((o) => o.value === previous)) {
            selectEl.value = previous;
        }
    }

    async function loadFormOptions() {
        try {
            const res = await fetch(FORM_OPTIONS_URL, { cache: "no-store" });
            if (!res.ok) throw new Error(`Form options failed (${res.status})`);
            const data = await res.json();

            const companySelect = document.getElementById("existing-company");
            if (companySelect) {
                companySelect.innerHTML =
                    '<option value="">— New company or select —</option>';
                (data.companies || []).forEach((c) => {
                    const opt = document.createElement("option");
                    opt.value = c.company_symbol;
                    opt.textContent = `${c.company_name} (${c.company_symbol})`;
                    opt.dataset.name = c.company_name || "";
                    opt.dataset.sector = c.sector || "hydropower";
                    companySelect.appendChild(opt);
                });
            }

            fillSelect(
                document.getElementById("fiscal-year"),
                data.fiscal_years || [],
                (y) => y,
                (y) => y,
                "2081/82"
            );
            fillSelect(
                document.getElementById("quarter"),
                data.quarters || [],
                (q) => q.value || q,
                (q) => q.label || q,
                "Q3"
            );
            fillSelect(
                document.getElementById("report-type"),
                data.report_types || [],
                (r) => r.value || r,
                (r) => r.label || r,
                "quarterly"
            );

            const sectorSelect = document.getElementById("sector");
            if (sectorSelect && data.sectors) {
                sectorSelect.innerHTML = "";
                data.sectors.forEach((s) => {
                    const opt = document.createElement("option");
                    opt.value = s.value;
                    opt.textContent = s.label;
                    opt.disabled = s.enabled === false;
                    if (s.value === "hydropower") opt.selected = true;
                    sectorSelect.appendChild(opt);
                });
            }

            const engine = data.engine || {};
            setEngineState(
                engine.status === "ready" ? "READY" : "OFFLINE",
                engine.message || "API status unknown",
                0
            );
        } catch (err) {
            console.warn(err);
            setEngineState("OFFLINE", "Cannot reach API on :8000", 0);
            showStatus(
                "API offline. Run: uvicorn backend.app:app --reload --port 8000",
                "error"
            );
        }
    }

    function statusBadge(status) {
        const s = (status || "").toLowerCase();
        if (s === "extracted" || s === "success") {
            return `<span class="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-bold">Success</span>`;
        }
        if (s === "extracting" || s === "uploaded" || s === "pending") {
            return `<span class="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-bold">${escapeHtml(status)}</span>`;
        }
        return `<span class="inline-flex items-center gap-1 px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-bold">${escapeHtml(status || "Failed")}</span>`;
    }

    function renderActivityRows() {
        const tbody = document.getElementById("activity-tbody");
        const viewWrap = document.getElementById("view-all-wrap");
        const viewBtn = document.getElementById("view-all-btn");
        if (!tbody) return;

        if (!allActivityRows.length) {
            tbody.innerHTML =
                '<tr><td colspan="5" class="px-lg py-xl text-center text-on-surface-variant">No reports in the database yet.</td></tr>';
            viewWrap?.classList.add("hidden");
            return;
        }

        const visible = activityExpanded
            ? allActivityRows
            : allActivityRows.slice(0, PREVIEW_LIMIT);

        tbody.innerHTML = visible
            .map((row) => {
                const typeRaw = row.report_type || "quarterly";
                const typeLabel = typeRaw.charAt(0).toUpperCase() + typeRaw.slice(1);
                const symbol = escapeHtml(row.company_symbol || "");
                const company = escapeHtml(row.company_name || symbol);
                const reportName = escapeHtml(row.report_name || `${symbol}.pdf`);
                const period = escapeHtml(
                    `${row.report_quarter || ""} ${row.fiscal_year || ""}`.trim()
                );
                const uploaded = escapeHtml(row.uploaded_at || "—");

                return `
                <tr class="hover:bg-surface-container-low">
                    <td class="px-lg py-md">
                        <div class="flex items-center gap-md">
                            <span class="material-symbols-outlined text-primary">picture_as_pdf</span>
                            <div>
                                <p class="font-semibold text-primary text-sm">${company}</p>
                                <p class="text-xs text-on-surface-variant">${symbol} · ${period} · ${reportName}</p>
                            </div>
                        </div>
                    </td>
                    <td class="px-lg py-md text-on-surface whitespace-nowrap text-sm">${uploaded}</td>
                    <td class="px-lg py-md"><span class="px-2 py-1 bg-surface-container-high rounded text-xs font-bold">${escapeHtml(typeLabel)}</span></td>
                    <td class="px-lg py-md text-center">${statusBadge(row.extraction_status)}</td>
                    <td class="px-lg py-md text-right">
                        <a href="dashboard.html?symbol=${encodeURIComponent(row.company_symbol || "")}"
                           class="material-symbols-outlined text-on-surface-variant hover:text-primary"
                           title="Open dashboard">visibility</a>
                    </td>
                </tr>`;
            })
            .join("");

        if (allActivityRows.length > PREVIEW_LIMIT) {
            viewWrap?.classList.remove("hidden");
            if (viewBtn) {
                viewBtn.textContent = activityExpanded
                    ? "Show less"
                    : `View all uploads (${allActivityRows.length})`;
            }
        } else {
            viewWrap?.classList.add("hidden");
        }
    }

    async function loadRecentActivity() {
        const tbody = document.getElementById("activity-tbody");
        if (!tbody) return;

        tbody.innerHTML =
            '<tr><td colspan="5" class="px-lg py-xl text-center text-on-surface-variant">Loading from database…</td></tr>';

        try {
            const res = await fetch(`${RECENT_URL}?limit=50&_=${Date.now()}`, {
                cache: "no-store",
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const rows = await res.json();

            allActivityRows = Array.isArray(rows) ? rows : [];
            activityExpanded = false;
            renderActivityRows();
        } catch (err) {
            console.warn(err);
            allActivityRows = [];
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="px-lg py-xl text-center text-red-700">
                        Could not load activity from the API. Is uvicorn running on port 8000?
                    </td>
                </tr>`;
            document.getElementById("view-all-wrap")?.classList.add("hidden");
        }
    }

    async function checkDuplicateBeforeUpload(meta) {
        const params = new URLSearchParams({
            company_symbol: meta.symbol,
            report_type: meta.reportType,
            fiscal_year: meta.fiscalYear,
            quarter: meta.quarter,
        });
        if (selectedFile?.name) params.set("filename", selectedFile.name);

        try {
            const res = await fetch(`${CHECK_DUP_URL}?${params}`, { cache: "no-store" });
            if (!res.ok) return { exists: false };
            return await res.json();
        } catch {
            return { exists: false };
        }
    }

    function parseErrorDetail(data, status) {
        if (!data) return `Upload failed (${status})`;
        const detail = data.detail ?? data.message;
        if (typeof detail === "string") return detail;
        if (detail && typeof detail === "object") {
            return detail.message || JSON.stringify(detail);
        }
        return JSON.stringify(data);
    }

    async function runUpload({ overwrite }) {
        const symbol = document.getElementById("company-symbol").value.trim().toUpperCase();
        const name = document.getElementById("company-name").value.trim();
        const sector = document.getElementById("sector").value;
        const reportType = document.getElementById("report-type").value;
        const fiscalYear = document.getElementById("fiscal-year").value;
        const quarter = document.getElementById("quarter").value;

        const formData = new FormData();
        formData.append("file", selectedFile, selectedFile.name);
        formData.append("company_symbol", symbol);
        formData.append("company_name", name);
        formData.append("sector", sector);
        formData.append("report_type", reportType);
        formData.append("fiscal_year", fiscalYear);
        formData.append("quarter", quarter);
        formData.append("overwrite", overwrite ? "true" : "false");

        const btn = document.getElementById("extract-btn");
        const btnLabel = document.getElementById("extract-btn-label");
        isUploading = true;
        if (btn) btn.disabled = true;
        if (btnLabel) btnLabel.textContent = "Extracting…";

        setEngineState("EXTRACTING", "Uploading & extracting with pdfplumber…", 45);
        showExtractLoading();

        try {
            const res = await fetch(UPLOAD_URL, {
                method: "POST",
                body: formData,
            });

            let data = null;
            try {
                data = await res.json();
            } catch {
                data = null;
            }

            if (res.status === 409) {
                closeModal("extract-modal");
                const msg = parseErrorDetail(data, 409);
                const confirmed = await askOverwrite(msg);
                if (!confirmed) {
                    setEngineState("READY", "Overwrite cancelled", 0);
                    showStatus("Upload cancelled — existing report kept.", "info");
                    return;
                }
                // Nested call manages its own button/modal state
                isUploading = false;
                if (btn) btn.disabled = false;
                if (btnLabel) btnLabel.textContent = "Start Extraction";
                await runUpload({ overwrite: true });
                return;
            }

            if (!res.ok) {
                throw new Error(parseErrorDetail(data, res.status));
            }

            setEngineState(
                "DONE",
                `Saved ${data.metrics_count} metrics · ${(data.periods || []).join(", ")}`,
                100
            );

            const dash =
                data.dashboard_url ||
                `dashboard.html?symbol=${encodeURIComponent(data.company_symbol)}`;

            showExtractResult(
                true,
                "Extraction complete",
                `${data.company_symbol} saved (${data.metrics_count} metrics, ${(data.periods || []).length} periods).`,
                dash
            );
            showStatus(`Success: ${data.company_symbol} saved to MySQL.`, "success");

            await loadRecentActivity();
            await loadFormOptions();
            pendingOverwrite = false;
        } catch (err) {
            console.error(err);
            setEngineState("FAILED", "Extraction failed", 0);
            showExtractResult(
                false,
                "Extraction failed",
                err.message || "Upload failed. Please try again."
            );
            showStatus(err.message || "Upload failed.", "error");
        } finally {
            isUploading = false;
            if (btn) btn.disabled = false;
            if (btnLabel) btnLabel.textContent = "Start Extraction";
        }
    }

    async function startExtraction() {
        if (isUploading) return;

        if (!selectedFile) {
            showStatus("Select a PDF first (drop or click the upload area).", "error");
            return;
        }

        const symbol = document.getElementById("company-symbol").value.trim().toUpperCase();
        const name = document.getElementById("company-name").value.trim();
        const reportType = document.getElementById("report-type").value;
        const fiscalYear = document.getElementById("fiscal-year").value;
        const quarter = document.getElementById("quarter").value;

        if (!symbol || !name) {
            showStatus("Company symbol and name are required.", "error");
            return;
        }

        const dup = await checkDuplicateBeforeUpload({
            symbol,
            reportType,
            fiscalYear,
            quarter,
        });

        if (dup.exists) {
            const confirmed = await askOverwrite(
                dup.message ||
                    `A report for ${symbol} (${quarter} ${fiscalYear}) already exists.`
            );
            if (!confirmed) {
                showStatus("Upload cancelled — existing report kept.", "info");
                return;
            }
            pendingOverwrite = true;
            return runUpload({ overwrite: true });
        }

        return runUpload({ overwrite: pendingOverwrite });
    }

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll(".theme-toggle-btn").forEach((btn) => {
            btn.addEventListener("click", toggleTheme);
        });
        document.getElementById("sidebar-toggle")?.addEventListener("click", toggleSidebar);
        document.getElementById("shortcuts-btn")?.addEventListener("click", () => {
            alert("U Upload · D Dashboard · C Comparison · T Theme");
        });

        if ((localStorage.getItem("theme") || "light") === "dark") {
            document.documentElement.classList.add("dark");
        }

        const sidebar = document.getElementById("sidebar");
        if (sidebar && window.innerWidth < 768) sidebar.classList.add("hidden");

        const dropzone = document.getElementById("dropzone");
        const fileInput = document.getElementById("file-input");

        dropzone?.addEventListener("click", () => fileInput?.click());
        dropzone?.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                fileInput?.click();
            }
        });

        dropzone?.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropzone.classList.add("drag-over");
        });
        dropzone?.addEventListener("dragleave", () => dropzone.classList.remove("drag-over"));
        dropzone?.addEventListener("drop", (e) => {
            e.preventDefault();
            dropzone.classList.remove("drag-over");
            const file = e.dataTransfer?.files?.[0];
            if (file) setSelectedFile(file);
        });

        fileInput?.addEventListener("change", () => {
            const file = fileInput.files?.[0];
            if (file) setSelectedFile(file);
        });

        document.getElementById("existing-company")?.addEventListener("change", (e) => {
            const opt = e.target.selectedOptions?.[0];
            if (!opt || !opt.value) return;
            document.getElementById("company-symbol").value = opt.value;
            document.getElementById("company-name").value = opt.dataset.name || "";
            if (opt.dataset.sector) {
                document.getElementById("sector").value = opt.dataset.sector;
            }
        });

        document.getElementById("report-type")?.addEventListener("change", (e) => {
            if (e.target.value === "annual") {
                document.getElementById("quarter").value = "Q4";
            }
        });

        document.getElementById("extract-btn")?.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            startExtraction();
        });

        document.getElementById("upload-form")?.addEventListener("submit", (e) => {
            e.preventDefault();
            e.stopPropagation();
            startExtraction();
            return false;
        });

        document.getElementById("discard-btn")?.addEventListener("click", resetForm);
        document.getElementById("refresh-activity")?.addEventListener("click", () => {
            loadRecentActivity();
            loadFormOptions();
        });

        document.getElementById("view-all-btn")?.addEventListener("click", () => {
            activityExpanded = !activityExpanded;
            renderActivityRows();
        });

        document.getElementById("extract-modal-close")?.addEventListener("click", () => {
            closeModal("extract-modal");
        });

        document.getElementById("extract-modal")?.addEventListener("click", (e) => {
            if (e.target.id === "extract-modal" && !isUploading) {
                closeModal("extract-modal");
            }
        });

        loadFormOptions();
        loadRecentActivity();
    });
})();
