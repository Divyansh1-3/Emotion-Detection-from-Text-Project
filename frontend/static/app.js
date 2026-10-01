/**
 * P_098 Emotion Detection — Frontend Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const textInput = document.getElementById("textInput");
  const charCounter = document.getElementById("charCounter");
  const sampleSelect = document.getElementById("sampleSelect");
  const analyzeBtn = document.getElementById("analyzeBtn");

  const emptyState = document.getElementById("emptyState");
  const loadingState = document.getElementById("loadingState");
  const resultContent = document.getElementById("resultContent");
  const batchResultsContent = document.getElementById("batchResultsContent");

  const verdictEmoji = document.getElementById("verdictEmoji");
  const verdictEmotion = document.getElementById("verdictEmotion");
  const confidenceValue = document.getElementById("confidenceValue");
  const uncertainBadge = document.getElementById("uncertainBadge");
  const sarcasmBadge = document.getElementById("sarcasmBadge");

  const rationaleText = document.getElementById("rationaleText");
  const rationaleSourceBadge = document.getElementById("rationaleSourceBadge");
  const sourcesList = document.getElementById("sourcesList");
  const routePills = document.getElementById("routePills");
  const latencyTrace = document.getElementById("latencyTrace");
  const requestIdTrace = document.getElementById("requestIdTrace");
  const inspectLink = document.getElementById("inspectLink");
  const warningsBox = document.getElementById("warningsBox");
  const warningsList = document.getElementById("warningsList");
  const copyJsonBtn = document.getElementById("copyJsonBtn");

  // Batch elements
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");
  const dropZone = document.getElementById("dropZone");
  const csvFileInput = document.getElementById("csvFileInput");
  const browseFileBtn = document.getElementById("browseFileBtn");
  const fileInfo = document.getElementById("fileInfo");
  const fileName = document.getElementById("fileName");
  const processBatchBtn = document.getElementById("processBatchBtn");
  const batchTableBody = document.getElementById("batchTableBody");
  const batchCountBadge = document.getElementById("batchCountBadge");

  let lastResultData = null;
  let chartInstance = null;
  let selectedFile = null;

  const EMOTION_COLORS = {
    joy: "rgba(22, 163, 74, 0.8)",
    anger: "rgba(220, 38, 38, 0.8)",
    fear: "rgba(147, 51, 234, 0.8)",
    sadness: "rgba(2, 132, 199, 0.8)",
    surprise: "rgba(217, 119, 6, 0.8)",
    disgust: "rgba(5, 150, 105, 0.8)",
    neutral: "rgba(71, 85, 105, 0.8)",
  };

  const EMOTION_EMOJIS = {
    joy: "😄",
    anger: "😠",
    fear: "😨",
    sadness: "😢",
    surprise: "😮",
    disgust: "🤢",
    neutral: "😐",
  };

  // Tab switching
  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabBtns.forEach((b) => b.classList.remove("active"));
      tabPanes.forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      const targetPane = document.getElementById(btn.dataset.tab);
      if (targetPane) targetPane.classList.add("active");
    });
  });

  // Character counter
  textInput.addEventListener("input", () => {
    const len = textInput.value.length;
    charCounter.textContent = `${len} / 4000 characters`;
    if (len > 4000) {
      charCounter.style.color = "var(--anger-color)";
    } else {
      charCounter.style.color = "var(--text-muted)";
    }
  });

  // Demo sample loader
  sampleSelect.addEventListener("change", () => {
    if (sampleSelect.value) {
      textInput.value = sampleSelect.value;
      textInput.dispatchEvent(new Event("input"));
      submitSingleAnalysis();
    }
  });

  // Single analysis submit
  analyzeBtn.addEventListener("click", submitSingleAnalysis);
  textInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      submitSingleAnalysis();
    }
  });

  async function submitSingleAnalysis() {
    const text = textInput.value.trim();
    if (!text) {
      alert("Please enter some text to analyze.");
      return;
    }

    // UI State: Loading
    emptyState.classList.add("hidden");
    resultContent.classList.add("hidden");
    batchResultsContent.classList.add("hidden");
    loadingState.classList.remove("hidden");
    analyzeBtn.disabled = true;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 20000);

    try {
      const response = await fetch("/api/v1/emotion/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: text }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.error || "Analysis failed");
      }

      lastResultData = data;
      renderSingleResult(data);
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === "AbortError") {
        alert("Error: Analysis request timed out after 20 seconds. Please verify the backend server status.");
      } else {
        alert(`Error: ${err.message}`);
      }
      emptyState.classList.remove("hidden");
    } finally {
      loadingState.classList.add("hidden");
      analyzeBtn.disabled = false;
    }
  }

  function renderSingleResult(payload) {
    const res = payload.result;
    resultContent.classList.remove("hidden");
    copyJsonBtn.classList.remove("hidden");

    // Primary verdict
    const emotion = res.primary_emotion || "neutral";
    verdictEmotion.textContent = emotion;
    verdictEmotion.style.color = `var(--${emotion}-color)`;
    verdictEmoji.textContent = EMOTION_EMOJIS[emotion] || "😐";

    // Confidence
    const confPct = (res.confidence * 100).toFixed(1);
    confidenceValue.textContent = `${confPct}%`;

    // Flags
    if (res.uncertain) {
      uncertainBadge.classList.remove("hidden");
    } else {
      uncertainBadge.classList.add("hidden");
    }

    if (res.sarcasm) {
      sarcasmBadge.classList.remove("hidden");
      sarcasmBadge.innerHTML = `<i class="fa-solid fa-masks-theater"></i> Sarcasm (${(res.sarcasm_score * 100).toFixed(0)}%)`;
    } else {
      sarcasmBadge.classList.add("hidden");
    }

    // Rationale
    rationaleText.textContent = res.rationale || "No explanation generated.";
    rationaleSourceBadge.textContent = res.llm_used ? "OpenAI API" : "Offline Template";

    // Render Chart
    renderChart(res.emotion_scores || []);

    // Sources list
    sourcesList.innerHTML = "";
    if (res.sources && res.sources.length > 0) {
      res.sources.forEach((src) => {
        const li = document.createElement("li");
        li.className = "source-item";
        li.innerHTML = `
          <div class="source-tag">[${src.source} &bull; ${src.label} &bull; ${(src.similarity * 100).toFixed(0)}% sim]</div>
          <div class="source-text">${escapeHtml(src.text)}</div>
        `;
        sourcesList.appendChild(li);
      });
    } else {
      sourcesList.innerHTML = `<li class="text-muted text-sm">No specific RAG sources needed.</li>`;
    }

    // Route Trace
    routePills.innerHTML = "";
    if (res.route && res.route.length > 0) {
      res.route.forEach((r) => {
        const pill = document.createElement("span");
        pill.className = "route-pill";
        pill.textContent = r;
        routePills.appendChild(pill);
      });
    }

    // Trace Meta
    latencyTrace.innerHTML = `<i class="fa-solid fa-clock"></i> Latency: ${res.latency_ms.toFixed(1)} ms`;
    requestIdTrace.innerHTML = `<i class="fa-solid fa-fingerprint"></i> ID: ${res.request_id || "req"}`;
    if (res.id) {
      inspectLink.href = `/inspect/${res.id}`;
      inspectLink.classList.remove("hidden");
    } else {
      inspectLink.href = `/inspect`;
    }

    // Warnings
    warningsList.innerHTML = "";
    if (res.warnings && res.warnings.length > 0) {
      warningsBox.classList.remove("hidden");
      res.warnings.forEach((w) => {
        const li = document.createElement("li");
        li.textContent = w;
        warningsList.appendChild(li);
      });
    } else {
      warningsBox.classList.add("hidden");
    }
  }

  function renderChart(scores) {
    const ctx = document.getElementById("emotionChart").getContext("2d");
    const labels = scores.map((s) => s.label.charAt(0).toUpperCase() + s.label.slice(1));
    const values = scores.map((s) => (s.score * 100).toFixed(1));
    const colors = scores.map((s) => EMOTION_COLORS[s.label] || "rgba(71, 85, 105, 0.8)");

    if (chartInstance) {
      chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Probability (%)",
            data: values,
            backgroundColor: colors,
            borderRadius: 6,
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
              label: (item) => ` ${item.raw}%`,
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: {
              callback: (val) => `${val}%`,
            },
            grid: {
              color: "#f1f5f9",
            },
          },
          x: {
            grid: { display: false },
          },
        },
      },
    });
  }

  // Copy JSON
  copyJsonBtn.addEventListener("click", () => {
    if (lastResultData) {
      navigator.clipboard.writeText(JSON.stringify(lastResultData, null, 2));
      const originalText = copyJsonBtn.innerHTML;
      copyJsonBtn.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
      setTimeout(() => {
        copyJsonBtn.innerHTML = originalText;
      }, 2000);
    }
  });

  // Batch CSV Drag & Drop
  browseFileBtn.addEventListener("click", () => csvFileInput.click());
  dropZone.addEventListener("click", (e) => {
    if (e.target !== browseFileBtn) csvFileInput.click();
  });

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "var(--primary-color)";
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.style.borderColor = "#cbd5e1";
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "#cbd5e1";
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleSelectedFile(e.dataTransfer.files[0]);
    }
  });

  csvFileInput.addEventListener("change", () => {
    if (csvFileInput.files && csvFileInput.files.length > 0) {
      handleSelectedFile(csvFileInput.files[0]);
    }
  });

  function handleSelectedFile(file) {
    if (!file.name.endsWith(".csv")) {
      alert("Please select a valid CSV file.");
      return;
    }
    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.classList.remove("hidden");
  }

  processBatchBtn.addEventListener("click", async () => {
    if (!selectedFile) return;

    emptyState.classList.add("hidden");
    resultContent.classList.add("hidden");
    batchResultsContent.classList.add("hidden");
    loadingState.classList.remove("hidden");
    processBatchBtn.disabled = true;

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("/api/v1/emotion/batch", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.error || "Batch processing failed");
      }

      renderBatchResults(data);
    } catch (err) {
      alert(`Batch Error: ${err.message}`);
      emptyState.classList.remove("hidden");
    } finally {
      loadingState.classList.add("hidden");
      processBatchBtn.disabled = false;
    }
  });

  function renderBatchResults(data) {
    batchResultsContent.classList.remove("hidden");
    batchCountBadge.textContent = `${data.total_processed} items processed`;

    batchTableBody.innerHTML = "";
    data.results.forEach((row, idx) => {
      const tr = document.createElement("tr");
      const emotion = row.primary_emotion || "neutral";
      const conf = ((row.confidence || 0) * 100).toFixed(0);
      const isSarcastic = row.sarcasm ? "Yes" : "No";
      const statusClass = row.uncertain ? "warning" : "success";
      const statusText = row.uncertain ? "Uncertain" : "Clear";

      tr.innerHTML = `
        <td class="font-mono">${idx + 1}</td>
        <td class="text-truncate" title="${escapeHtml(row.input_text)}">${escapeHtml(row.input_text)}</td>
        <td><span class="emotion-pill ${emotion}">${EMOTION_EMOJIS[emotion] || ""} ${emotion}</span></td>
        <td class="font-mono">${conf}%</td>
        <td>${isSarcastic}</td>
        <td><span class="status-tag ${statusClass}">${statusText}</span></td>
      `;
      batchTableBody.appendChild(tr);
    });
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
