/**
 * Comparative Analysis — load companies, compare metrics, draw overlay chart.
 */

(function () {
    const API_BASE = "http://127.0.0.1:8000";
    const COMPANIES_URL = `${API_BASE}/compare/companies`;
    const COMPARE_URL = `${API_BASE}/compare`;

    let profitChart = null;
    let companies = [];

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
        const el = document.getElementById("compare-status");
        if (!el) return;
        el.classList.remove("hidden", "success", "error", "info");
        el.textContent = message;
        if (type) el.classList.add(type);
    }

    function formatValue(value, format) {
        if (value == null || value === "") return "—";
        const num = Number(value);
        if (Number.isNaN(num)) return "—";

        if (format === "percent") {
            return `${num.toLocaleString(undefined, { maximumFractionDigits: 2 })}%`;
        }

        const abs = Math.abs(num);
        if (abs >= 1_000_000_000) {
            return `NPR ${(num / 1_000_000_000).toFixed(2)}B`;
        }
        if (abs >= 1_000_000) {
            return `NPR ${(num / 1_000_000).toFixed(2)}M`;
        }
        return `NPR ${num.toLocaleString()}`;
    }

    function deltaHtml(row) {
        if (row.delta_pct == null && row.direction === "none") {
            return `<span class="text-on-surface-variant">—</span>`;
        }

        if (row.winner === "tie" || row.direction === "flat") {
            return `<span class="inline-flex items-center gap-xs text-on-surface-variant font-bold">
                <span class="material-symbols-outlined text-sm">remove</span> ~0%
            </span>`;
        }

        const favoursA = row.winner === "a";
        const color = favoursA ? "text-green-600" : "text-red-600";
        const icon = favoursA ? "trending_up" : "trending_down";
        const label = favoursA ? "A higher" : "B higher";
        const pct =
            row.delta_pct != null
                ? `${Number(row.delta_pct).toLocaleString(undefined, { maximumFractionDigits: 1 })}%`
                : "";

        return `<span class="inline-flex items-center gap-xs ${color} font-bold" title="${escapeHtml(label)}">
            <span class="material-symbols-outlined text-sm">${icon}</span>
            ${escapeHtml(pct)}
        </span>`;
    }

    function fillSelect(selectEl, items, selected) {
        if (!selectEl) return;
        const previous = selected ?? selectEl.value;
        selectEl.innerHTML = '<option value="">Select company…</option>';
        items.forEach((c) => {
            const opt = document.createElement("option");
            opt.value = c.company_symbol;
            opt.textContent = `${c.company_name} (${c.company_symbol})`;
            selectEl.appendChild(opt);
        });
        if (previous && [...selectEl.options].some((o) => o.value === previous)) {
            selectEl.value = previous;
        }
    }

    function updateAvatars() {
        const a = document.getElementById("company-a")?.value || "";
        const b = document.getElementById("company-b")?.value || "";
        const avA = document.getElementById("avatar-a");
        const avB = document.getElementById("avatar-b");
        if (avA) avA.textContent = a ? a.charAt(0) : "A";
        if (avB) avB.textContent = b ? b.charAt(0) : "B";
    }

    async function loadCompanies() {
        try {
            const res = await fetch(COMPANIES_URL, { cache: "no-store" });
            if (!res.ok) throw new Error(`Companies failed (${res.status})`);
            companies = await res.json();

            const selectA = document.getElementById("company-a");
            const selectB = document.getElementById("company-b");
            fillSelect(selectA, companies);
            fillSelect(selectB, companies);

            if (companies.length >= 2) {
                selectA.value = companies[0].company_symbol;
                selectB.value = companies[1].company_symbol;
            } else if (companies.length === 1) {
                selectA.value = companies[0].company_symbol;
            }

            updateAvatars();

            if (companies.length < 2) {
                showStatus(
                    "Need at least two companies with extracted reports. Upload more on Report Upload.",
                    "info"
                );
                return false;
            }
            return true;
        } catch (err) {
            console.warn(err);
            showStatus(
                "API offline. Run: uvicorn backend.app:app --reload --port 8000",
                "error"
            );
            return false;
        }
    }

    function renderTable(data) {
        const tbody = document.getElementById("compare-tbody");
        const thA = document.getElementById("th-a");
        const thB = document.getElementById("th-b");
        const badge = document.getElementById("period-badge");
        const legendA = document.getElementById("legend-a");
        const legendB = document.getElementById("legend-b");

        if (thA) thA.textContent = data.company_a.symbol;
        if (thB) thB.textContent = data.company_b.symbol;
        if (legendA) legendA.textContent = data.company_a.symbol;
        if (legendB) legendB.textContent = data.company_b.symbol;
        if (badge) badge.textContent = data.period_label || "—";

        if (!tbody) return;

        if (!data.rows || !data.rows.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="px-lg py-xl text-center text-on-surface-variant">
                        No comparable metrics found.
                    </td>
                </tr>`;
            return;
        }

        tbody.innerHTML = data.rows
            .map((row) => {
                const winnerClass =
                    row.winner === "a"
                        ? "row-winner-a"
                        : row.winner === "b"
                          ? "row-winner-b"
                          : "";
                return `
                <tr class="hover:bg-surface-container-low ${winnerClass}">
                    <td class="px-lg py-md font-medium">${escapeHtml(row.label)}</td>
                    <td class="px-lg py-md font-data-mono text-data-mono ${row.winner === "a" ? "font-bold text-primary" : ""}">
                        ${escapeHtml(formatValue(row.a, row.format))}
                    </td>
                    <td class="px-lg py-md font-data-mono text-data-mono ${row.winner === "b" ? "font-bold text-primary" : ""}">
                        ${escapeHtml(formatValue(row.b, row.format))}
                    </td>
                    <td class="px-lg py-md">${deltaHtml(row)}</td>
                </tr>`;
            })
            .join("");
    }

    function buildAlignedTrend(companyA, companyB) {
        const mapA = {};
        const mapB = {};
        (companyA.trend || []).forEach((p) => {
            mapA[p.period] = p.net_profit;
        });
        (companyB.trend || []).forEach((p) => {
            mapB[p.period] = p.net_profit;
        });

        const labels = [
            ...new Set([
                ...(companyA.trend || []).map((p) => p.period),
                ...(companyB.trend || []).map((p) => p.period),
            ]),
        ];

        // Sort by fiscal year then quarter
        labels.sort((x, y) => {
            const [fyA, qA] = x.split(" ");
            const [fyB, qB] = y.split(" ");
            const qOrder = { Q1: 1, Q2: 2, Q3: 3, Q4: 4 };
            if (fyA !== fyB) return String(fyA).localeCompare(String(fyB));
            return (qOrder[qA] || 0) - (qOrder[qB] || 0);
        });

        return {
            labels,
            seriesA: labels.map((l) =>
                mapA[l] != null ? Number(mapA[l]) : null
            ),
            seriesB: labels.map((l) =>
                mapB[l] != null ? Number(mapB[l]) : null
            ),
        };
    }

    function drawProfitChart(data) {
        const canvas = document.getElementById("profitCompareChart");
        const empty = document.getElementById("chart-empty");
        if (!canvas) return;

        const aligned = buildAlignedTrend(data.company_a, data.company_b);

        if (!aligned.labels.length) {
            canvas.classList.add("hidden");
            empty?.classList.remove("hidden");
            if (profitChart) {
                profitChart.destroy();
                profitChart = null;
            }
            return;
        }

        canvas.classList.remove("hidden");
        empty?.classList.add("hidden");

        if (profitChart) profitChart.destroy();

        profitChart = new Chart(canvas, {
            type: "line",
            data: {
                labels: aligned.labels,
                datasets: [
                    {
                        label: data.company_a.symbol,
                        data: aligned.seriesA,
                        borderColor: "#051125",
                        backgroundColor: "rgba(5, 17, 37, 0.08)",
                        tension: 0.25,
                        spanGaps: true,
                        pointRadius: 3,
                    },
                    {
                        label: data.company_b.symbol,
                        data: aligned.seriesB,
                        borderColor: "#47607e",
                        backgroundColor: "rgba(71, 96, 126, 0.08)",
                        tension: 0.25,
                        spanGaps: true,
                        pointRadius: 3,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label(ctx) {
                                const v = ctx.parsed.y;
                                if (v == null) return `${ctx.dataset.label}: —`;
                                return `${ctx.dataset.label}: NPR ${Number(v).toLocaleString()}`;
                            },
                        },
                    },
                },
                scales: {
                    y: {
                        ticks: {
                            callback(value) {
                                const n = Number(value);
                                if (Math.abs(n) >= 1_000_000) {
                                    return (n / 1_000_000).toFixed(1) + "M";
                                }
                                return n.toLocaleString();
                            },
                        },
                        grid: { color: "rgba(197, 198, 205, 0.35)" },
                    },
                    x: {
                        grid: { display: false },
                    },
                },
            },
        });
    }

    async function runCompare() {
        const symbolA = document.getElementById("company-a")?.value;
        const symbolB = document.getElementById("company-b")?.value;
        const btn = document.getElementById("run-compare-btn");

        if (!symbolA || !symbolB) {
            showStatus("Select both Company A and Company B.", "error");
            return;
        }
        if (symbolA === symbolB) {
            showStatus("Select two different companies.", "error");
            return;
        }

        if (btn) {
            btn.disabled = true;
            btn.classList.add("opacity-70");
        }

        showStatus("Loading comparison…", "info");

        try {
            const url = `${COMPARE_URL}?symbol_a=${encodeURIComponent(symbolA)}&symbol_b=${encodeURIComponent(symbolB)}`;
            const res = await fetch(url, { cache: "no-store" });
            let data = null;
            try {
                data = await res.json();
            } catch {
                data = null;
            }

            if (!res.ok) {
                const detail =
                    (data && (data.detail || data.message)) ||
                    `Compare failed (${res.status})`;
                throw new Error(
                    typeof detail === "string" ? detail : JSON.stringify(detail)
                );
            }

            renderTable(data);
            drawProfitChart(data);
            showStatus(data.note || "Comparison ready.", "success");
        } catch (err) {
            console.error(err);
            showStatus(err.message || "Comparison failed.", "error");
            const tbody = document.getElementById("compare-tbody");
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4" class="px-lg py-xl text-center text-red-700">
                            ${escapeHtml(err.message || "Comparison failed.")}
                        </td>
                    </tr>`;
            }
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.classList.remove("opacity-70");
            }
        }
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

        document.getElementById("company-a")?.addEventListener("change", updateAvatars);
        document.getElementById("company-b")?.addEventListener("change", updateAvatars);
        document.getElementById("run-compare-btn")?.addEventListener("click", runCompare);

        document.addEventListener("keydown", (e) => {
            if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) {
                return;
            }
            if (e.key === "u" && !e.ctrlKey) window.location.href = "upload_file.html";
            if (e.key === "d" && !e.ctrlKey) window.location.href = "dashboard.html";
            if (e.key === "c" && !e.ctrlKey) window.location.href = "comparative_analysis.html";
            if (e.key === "t" && !e.ctrlKey) toggleTheme();
        });

        // Prefer query params ?a=SYM&b=SYM
        const params = new URLSearchParams(window.location.search);
        const presetA = params.get("a");
        const presetB = params.get("b");

        loadCompanies().then((ready) => {
            if (!ready) return;

            if (presetA && document.getElementById("company-a")) {
                const a = presetA.toUpperCase();
                if ([...document.getElementById("company-a").options].some((o) => o.value === a)) {
                    document.getElementById("company-a").value = a;
                }
            }
            if (presetB && document.getElementById("company-b")) {
                const b = presetB.toUpperCase();
                if ([...document.getElementById("company-b").options].some((o) => o.value === b)) {
                    document.getElementById("company-b").value = b;
                }
            }
            updateAvatars();
            runCompare();
        });
    });
})();
