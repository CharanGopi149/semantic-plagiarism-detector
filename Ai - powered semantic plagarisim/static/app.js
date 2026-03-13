const form = document.getElementById("analysis-form");
const loadDemoButton = document.getElementById("load-demo-button");
const downloadButton = document.getElementById("download-report-button");
const statusNode = document.getElementById("form-status");
const enginePill = document.getElementById("engine-pill");
const emptyState = document.getElementById("empty-state");
const resultsShell = document.getElementById("results-shell");
const summaryCards = document.getElementById("summary-cards");
const sectionsList = document.getElementById("sections-list");
const sourcesList = document.getElementById("sources-list");
const matchesList = document.getElementById("matches-list");
const summaryTimestamp = document.getElementById("summary-timestamp");
const flaggedCount = document.getElementById("flagged-count");
const analyzeButton = document.getElementById("analyze-button");

let latestReport = null;

const formatPercent = (value) => `${Number(value || 0).toFixed(1)}%`;
const escapeHtml = (value) =>
    String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

function setStatus(message, tone = "neutral") {
    statusNode.textContent = message;
    statusNode.className = `form-note ${tone === "error" ? "error" : tone === "success" ? "success" : ""}`.trim();
}

function buildSummaryCards(summary) {
    const cards = [
        ["Overall Similarity", formatPercent(summary.overall_similarity_percentage)],
        ["Direct Match", formatPercent(summary.direct_match_percentage)],
        ["Semantic Match", formatPercent(summary.semantic_match_percentage)],
        ["Flagged Sentences", `${summary.flagged_sentences} / ${summary.total_sentences}`],
    ];

    summaryCards.innerHTML = cards
        .map(
            ([label, value]) => `
                <article class="summary-card">
                    <span>${escapeHtml(label)}</span>
                    <strong>${escapeHtml(value)}</strong>
                </article>
            `,
        )
        .join("");
}

function buildSections(sections) {
    sectionsList.innerHTML = sections
        .map(
            (section) => `
                <article class="section-card">
                    <h4>${escapeHtml(section.name)}</h4>
                    <div class="section-meta">
                        <span class="meta-chip">${section.flagged_count} flagged</span>
                        <span class="meta-chip">${section.direct_count} direct</span>
                        <span class="meta-chip">${section.semantic_count} semantic</span>
                        <span class="meta-chip">${section.suspicious_count} suspicious</span>
                    </div>
                    <div class="meter"><span style="width: ${Math.min(section.similarity_percentage, 100)}%"></span></div>
                    <div class="section-meta">
                        <span>${formatPercent(section.similarity_percentage)} similarity</span>
                        <span>${section.sentence_count} sentences</span>
                    </div>
                </article>
            `,
        )
        .join("");
}

function buildSources(sources) {
    if (!sources.length) {
        sourcesList.innerHTML = `<div class="empty-state"><p>No flagged source contributions were found.</p></div>`;
        return;
    }

    sourcesList.innerHTML = sources
        .map(
            (source) => `
                <article class="source-card">
                    <h4>${escapeHtml(source.source_name)}</h4>
                    <div class="source-meta">
                        <span class="meta-chip">${formatPercent(source.contribution_percentage)} contribution</span>
                        <span class="meta-chip">${source.matched_sentences} matched sentences</span>
                        <span class="meta-chip">${escapeHtml(source.origin)}</span>
                    </div>
                    ${source.top_section ? `<div class="source-meta"><span>Most matched section: ${escapeHtml(source.top_section)}</span></div>` : ""}
                </article>
            `,
        )
        .join("");
}

function buildMatches(matches) {
    const filtered = matches.filter((item) => item.classification !== "original");
    flaggedCount.textContent = `${filtered.length} flagged`;

    if (!filtered.length) {
        matchesList.innerHTML = `<div class="empty-state"><p>No suspicious sentences were found for the provided sources.</p></div>`;
        return;
    }

    matchesList.innerHTML = filtered
        .map(
            (match) => `
                <article class="match-card ${escapeHtml(match.classification)}">
                    <div class="match-meta">
                        <span class="tag ${escapeHtml(match.classification)}">${escapeHtml(match.classification)}</span>
                        <span class="meta-chip">${formatPercent(match.similarity_score)}</span>
                        <span class="meta-chip">${escapeHtml(match.student_section)}</span>
                        <span class="meta-chip">${escapeHtml(match.source_name)}</span>
                    </div>
                    <div class="match-snippet">
                        <strong>Student Sentence</strong>
                        <div>${escapeHtml(match.student_sentence)}</div>
                    </div>
                    <div class="match-snippet">
                        <strong>Matched Source Sentence</strong>
                        <div>${escapeHtml(match.source_sentence)}</div>
                    </div>
                    <div class="match-meta">
                        <span>Semantic: ${formatPercent(match.semantic_score)}</span>
                        <span>Lexical: ${formatPercent(match.lexical_score)}</span>
                        <span>TF-IDF: ${formatPercent(match.tfidf_score)}</span>
                    </div>
                </article>
            `,
        )
        .join("");
}

function renderReport(report) {
    latestReport = report;
    emptyState.classList.add("hidden");
    resultsShell.classList.remove("hidden");
    downloadButton.disabled = false;

    enginePill.textContent = report.model_info.analyzer_name;
    buildSummaryCards(report.summary);
    buildSections(report.sections);
    buildSources(report.source_contributions);
    buildMatches(report.matches);

    const generatedAt = new Date(report.generated_at);
    summaryTimestamp.textContent = Number.isNaN(generatedAt.getTime())
        ? ""
        : `Generated ${generatedAt.toLocaleString()}`;
}

async function loadDemoData() {
    setStatus("Loading demo data...");
    const response = await fetch("/api/sources/library");
    if (!response.ok) {
        throw new Error("Could not load demo data.");
    }
    const payload = await response.json();
    document.getElementById("title").value = "Demo Assignment";
    document.getElementById("assignment-text").value = payload.demo_assignment || "";
    document.getElementById("use-sample-sources").checked = true;
    document.getElementById("source-urls").value = "";
    document.getElementById("assignment-file").value = "";
    document.getElementById("source-files").value = "";
    setStatus("Demo content loaded. Run the analysis to view the report.", "success");
}

async function submitAnalysis(event) {
    event.preventDefault();
    analyzeButton.disabled = true;
    downloadButton.disabled = true;
    enginePill.textContent = "Analyzing...";
    setStatus("Analyzing assignment and matching source sentences...");

    const formData = new FormData(form);
    const assignmentFileInput = document.getElementById("assignment-file");
    const sourceFilesInput = document.getElementById("source-files");

    if (!assignmentFileInput.files.length) {
        formData.delete("assignment_file");
    }

    if (!sourceFilesInput.files.length) {
        formData.delete("source_files");
    }

    if (!document.getElementById("use-sample-sources").checked) {
        formData.delete("use_sample_sources");
    }

    try {
        const response = await fetch("/api/analyze-upload", {
            method: "POST",
            body: formData,
        });

        const payload = await response.json();
        if (!response.ok) {
            throw new Error(payload.detail || "Analysis failed.");
        }

        renderReport(payload);
        setStatus("Analysis completed successfully.", "success");
    } catch (error) {
        enginePill.textContent = "Analysis failed";
        setStatus(error.message || "Unexpected error while analyzing.", "error");
    } finally {
        analyzeButton.disabled = false;
    }
}

function downloadReport() {
    if (!latestReport) {
        return;
    }

    const blob = new Blob([JSON.stringify(latestReport, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "plagiarism-report.json";
    anchor.click();
    URL.revokeObjectURL(url);
}

form.addEventListener("submit", submitAnalysis);
loadDemoButton.addEventListener("click", () => {
    loadDemoData().catch((error) => setStatus(error.message || "Unable to load demo content.", "error"));
});
downloadButton.addEventListener("click", downloadReport);
