/**
 * static/app.js
 * Frontend controller for Lex Detective — Autonomous Contract Conflict & Loophole Engine.
 * Manages case selection, interactive evidence board, SVG proof tree rendering,
 * and settlement audit reporting.
 */

(function () {
  'use strict';

  // --- Application State ---
  const state = {
    presets: [],
    currentPresetId: 'ai-charter-clash',
    currentContract: null,
    auditResult: null,
    activeMode: 'conflict', // 'conflict' | 'breach'
    selectedPipelineClauseId: null,
    theme: localStorage.getItem('theme') || 'light',
    graph: {
      panX: 40,
      panY: 30,
      scale: 1.0,
      isDragging: false,
      startX: 0,
      startY: 0
    }
  };

  // --- DOM Elements ---
  const el = {
    presetSelector: document.getElementById('preset-selector'),
    btnRunAudit: document.getElementById('btn-run-audit'),
    btnExportReport: document.getElementById('btn-export-report'),
    btnThemeToggle: document.getElementById('btn-theme-toggle'),
    themeIcon: document.getElementById('theme-icon'),
    navTabs: document.querySelectorAll('.nav-tab'),
    viewPanels: document.querySelectorAll('.view-panel'),
    heroTitle: document.getElementById('hero-title'),
    heroStakes: document.getElementById('hero-stakes'),
    heroDesc: document.getElementById('hero-desc'),
    heroBadges: document.getElementById('hero-badges'),
    clauseListContainer: document.getElementById('clause-list-container'),
    axiomListContainer: document.getElementById('axiom-list-container'),
    factsListContainer: document.getElementById('facts-list-container'),
    pipelineClauseSelect: document.getElementById('pipeline-clause-select'),
    pipelineStepsContainer: document.getElementById('pipeline-steps-container'),
    btnModeConflict: document.getElementById('btn-mode-conflict'),
    btnModeBreach: document.getElementById('btn-mode-breach'),
    proverStatusBadge: document.getElementById('prover-status-badge'),
    graphContainer: document.getElementById('graph-container'),
    proofDagSvg: document.getElementById('proof-dag-svg'),
    dagViewport: document.getElementById('dag-viewport'),
    btnZoomIn: document.getElementById('btn-zoom-in'),
    btnZoomOut: document.getElementById('btn-zoom-out'),
    btnZoomReset: document.getElementById('btn-zoom-reset'),
    resolutionTableBody: document.getElementById('resolution-table-body'),
    riskScoreNum: document.getElementById('risk-score-num'),
    riskScoreCircle: document.getElementById('risk-score-circle'),
    riskHeadline: document.getElementById('risk-headline'),
    riskSummary: document.getElementById('risk-summary'),
    reportMarkdownPreview: document.getElementById('report-markdown-preview'),
    btnCopyMarkdown: document.getElementById('btn-copy-markdown'),
    btnPrintReport: document.getElementById('btn-print-report'),
    // Modal
    btnAddClauseModal: document.getElementById('btn-add-clause-modal'),
    addClauseModal: document.getElementById('add-clause-modal'),
    btnCloseModal: document.getElementById('btn-close-modal'),
    btnCancelClause: document.getElementById('btn-cancel-clause'),
    btnSaveClause: document.getElementById('btn-save-clause'),
    btnAutoTranslate: document.getElementById('btn-auto-translate'),
    inputClauseTitle: document.getElementById('input-clause-title'),
    inputClauseText: document.getElementById('input-clause-text'),
    inputClauseFopl: document.getElementById('input-clause-fopl'),
  };

  // --- Initialization ---
  async function init() {
    setupTheme();
    setupEventListeners();
    await loadPresets();
    await loadAndAuditCurrentPreset();
  }

  // --- Theme Management ---
  function setupTheme() {
    document.documentElement.setAttribute('data-theme', state.theme);
    updateThemeIcon();
  }

  function toggleTheme() {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', state.theme);
    document.documentElement.setAttribute('data-theme', state.theme);
    updateThemeIcon();
    renderProofGraph();
  }

  function updateThemeIcon() {
    if (state.theme === 'dark') {
      el.themeIcon.innerHTML = `<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>`;
    } else {
      el.themeIcon.innerHTML = `<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>`;
    }
  }

  // --- API Calls ---
  async function loadPresets() {
    try {
      const res = await fetch('/api/presets');
      state.presets = await res.json();
      el.presetSelector.innerHTML = state.presets
        .map(p => `<option value="${p.id}">${p.title} (${p.stakes || 'Dispute'})</option>`)
        .join('');
      if (state.presets.length > 0) {
        state.currentPresetId = state.presets[0].id;
        el.presetSelector.value = state.currentPresetId;
      }
    } catch (err) {
      console.error('Failed to load presets:', err);
    }
  }

  async function loadAndAuditCurrentPreset() {
    try {
      el.heroTitle.textContent = "Executing First-Order Logic Deduction...";
      const res = await fetch(`/api/audit-preset/${state.currentPresetId}`, { method: 'POST' });
      state.auditResult = await res.json();
      state.currentContract = state.presets.find(p => p.id === state.currentPresetId);

      renderHeroMeta();
      renderContractStudio();
      renderPipelineSelector();
      renderPipelineSteps();
      renderResolutionView();
      renderReportView();
    } catch (err) {
      console.error('Failed to audit case:', err);
      el.heroTitle.textContent = "Deduction Error";
      el.heroDesc.textContent = String(err);
    }
  }

  // --- UI Renderers ---

  function renderHeroMeta() {
    const p = state.currentContract;
    if (!p) return;
    el.heroTitle.textContent = p.title;
    el.heroDesc.textContent = p.description;
    el.heroStakes.textContent = p.stakes || "High Stakes Dispute";

    const res = state.auditResult;
    el.heroBadges.innerHTML = `
      <span class="badge badge-blue">${escapeHtml(p.category)}</span>
      <span class="badge ${res.risk_score >= 80 ? 'badge-red' : 'badge-amber'}">
        Legal Risk Index: ${res.risk_score}/100 [${res.risk_level}]
      </span>
      <span class="badge badge-amber">⚡ Deduction: ${res.elapsed_ms} ms</span>
      <span class="badge badge-green">Clauses in KB: ${res.kb_clauses_total}</span>
    `;
  }

  function renderContractStudio() {
    const res = state.auditResult;
    if (!res) return;

    // 1. Clauses
    el.clauseListContainer.innerHTML = res.clause_conversions.map(c => `
      <div class="clause-item">
        <div class="clause-item-head">
          <span class="clause-title">${escapeHtml(c.clause_num)}: ${escapeHtml(c.title)}</span>
          <span class="badge badge-blue">Formally Mapped</span>
        </div>
        <p class="clause-quote">"${escapeHtml(c.natural_text)}"</p>
        <div class="fopl-box">${escapeHtml(c.fopl)}</div>
        <div class="cnf-chips">
          ${c.clauses.map(cl => `<span class="cnf-chip" title="Clause ID: ${cl.clause_id}">${escapeHtml(cl.text)}</span>`).join('')}
        </div>
      </div>
    `).join('');

    // 2. Axioms
    const axioms = state.currentContract.domain_axioms || [];
    if (axioms.length === 0) {
      el.axiomListContainer.innerHTML = `<p style="font-size:0.85rem; color:var(--text-muted); font-style:italic;">No external legal axioms needed for this contract.</p>`;
    } else {
      el.axiomListContainer.innerHTML = axioms.map(ax => `
        <div class="clause-item" style="padding:0.75rem;">
          <div class="clause-item-head">
            <span class="clause-title" style="font-size:0.82rem;">${escapeHtml(ax.id)}: Legal Axiom</span>
          </div>
          <p style="font-size:0.82rem; color:var(--text-secondary); margin-bottom:0.4rem;">${escapeHtml(ax.natural_text)}</p>
          <div class="fopl-box" style="font-size:0.78rem;">${escapeHtml(ax.fopl)}</div>
        </div>
      `).join('');
    }

    // 3. Facts
    const demo = state.activeMode === 'conflict' ? state.currentContract.conflict_demo : state.currentContract.breach_demo;
    const facts = (demo && demo.facts) || [];
    el.factsListContainer.innerHTML = `
      <div style="margin-bottom:0.65rem; font-size:0.85rem; font-weight:600; color:var(--text-primary);">
        Active Scenario: ${escapeHtml(demo.title || 'Dispute Incident Log')}
      </div>
      <div style="display:flex; flex-direction:column; gap:0.45rem;">
        ${facts.map(f => `
          <div style="display:flex; align-items:center; justify-content:space-between; font-family:var(--font-mono); font-size:0.8rem; background-color:var(--bg-tertiary); padding:0.45rem 0.75rem; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
            <span>${escapeHtml(f)}</span>
            <span class="badge badge-green" style="font-size:0.7rem; padding: 0.1rem 0.4rem;">ACTIVE FACT</span>
          </div>
        `).join('')}
      </div>
    `;
  }

  function renderPipelineSelector() {
    const res = state.auditResult;
    if (!res || !res.clause_conversions) return;

    el.pipelineClauseSelect.innerHTML = res.clause_conversions.map(c => `
      <option value="${c.clause_id}">${c.clause_num}: ${c.title}</option>
    `).join('');

    if (!state.selectedPipelineClauseId && res.clause_conversions.length > 0) {
      state.selectedPipelineClauseId = res.clause_conversions[0].clause_id;
    }
    el.pipelineClauseSelect.value = state.selectedPipelineClauseId;
  }

  function renderPipelineSteps() {
    const res = state.auditResult;
    if (!res || !res.clause_conversions) return;

    const clauseConv = res.clause_conversions.find(c => c.clause_id === state.selectedPipelineClauseId) || res.clause_conversions[0];
    if (!clauseConv) return;

    el.pipelineStepsContainer.innerHTML = clauseConv.steps.map(s => `
      <div class="pipeline-card">
        <div class="pipeline-header" onclick="this.nextElementSibling.classList.toggle('hidden');">
          <div style="display:flex; align-items:center;">
            <span class="pipeline-step-badge">Stage ${s.step_num}</span>
            <span style="font-weight:600; font-size:0.9rem;">${escapeHtml(s.name)}</span>
          </div>
          <span style="color:var(--text-muted); font-size:0.8rem;">Click to toggle</span>
        </div>
        <div class="pipeline-body">
          <p class="pipeline-desc">${escapeHtml(s.description)}</p>
          <div class="fopl-box">${escapeHtml(s.formula_str)}</div>
          ${s.clauses && s.clauses.length > 0 ? `
            <div class="cnf-chips" style="margin-top:0.6rem;">
              ${s.clauses.map(cl => `<span class="cnf-chip"><b>${cl.clause_id || 'C'}:</b> [ ${escapeHtml(cl.text)} ]</span>`).join('')}
            </div>
          ` : ''}
        </div>
      </div>
    `).join('');
  }

  function renderResolutionView() {
    const res = state.auditResult;
    if (!res) return;

    const auditDemo = state.activeMode === 'conflict' ? res.conflict_audit : res.breach_audit;
    if (!auditDemo) return;

    const proof = auditDemo.proof;
    const isSuccess = proof.success;

    // Status Badge
    if (state.activeMode === 'conflict') {
      el.proverStatusBadge.innerHTML = isSuccess ? `
        <span class="badge badge-red" style="font-size:0.85rem; padding:0.4rem 0.85rem;">
          🚨 FATAL LOOPHOLE: Contradiction [${proof.empty_clause_id}] Derived (${proof.steps.length} Steps)
        </span>
      ` : `
        <span class="badge badge-green" style="font-size:0.85rem; padding:0.4rem 0.85rem;">
          ✅ Terms Harmonious (No Contradiction)
        </span>
      `;
    } else {
      el.proverStatusBadge.innerHTML = isSuccess ? `
        <span class="badge badge-red" style="font-size:0.85rem; padding:0.4rem 0.85rem;">
          ⚖️ VERDICT: Liability Breach Proven (${proof.steps.length} Steps)
        </span>
      ` : `
        <span class="badge badge-green" style="font-size:0.85rem; padding:0.4rem 0.85rem;">
          🛡️ VERDICT: Dismissed (No Breach)
        </span>
      `;
    }

    // Render Proof Graph
    renderProofGraph();

    // Render Step Table
    el.resolutionTableBody.innerHTML = proof.steps.map(s => `
      <tr>
        <td><span class="badge badge-blue" style="font-family:var(--font-mono);">${s.step_id}</span></td>
        <td>
          <span style="font-family:var(--font-mono); font-size:0.8rem; color:var(--text-secondary);">
            ${escapeHtml(s.parent1_id)} &amp; ${escapeHtml(s.parent2_id)}
          </span>
        </td>
        <td>
          <div style="font-family:var(--font-mono); font-size:0.8rem;">
            <span style="color:var(--brand-primary);">${escapeHtml(s.literal1)}</span> &bull; 
            <span style="color:var(--danger-accent);">${escapeHtml(s.literal2)}</span>
          </div>
          <div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">
            Substitution θ: <code>${escapeHtml(s.mgu)}</code>
          </div>
        </td>
        <td>
          <span style="font-family:var(--font-mono); font-weight:600; font-size:0.82rem; ${s.resolvent.is_empty ? 'color:var(--danger-accent);' : ''}">
            ${escapeHtml(s.resolvent.text)}
          </span>
        </td>
        <td style="font-size:0.82rem; color:var(--text-secondary); line-height:1.4;">
          ${escapeHtml(s.explanation)}
        </td>
      </tr>
    `).join('');
  }

  // --- SVG Proof Graph Layout & Interactive Rendering ---
  function renderProofGraph() {
    const res = state.auditResult;
    if (!res) return;

    const auditDemo = state.activeMode === 'conflict' ? res.conflict_audit : res.breach_audit;
    if (!auditDemo || !auditDemo.proof || !auditDemo.proof.graph) return;

    const graph = auditDemo.proof.graph;
    const nodes = graph.nodes;
    const edges = graph.edges;

    if (!nodes || nodes.length === 0) {
      el.dagViewport.innerHTML = `<text x="50" y="50" fill="var(--text-muted)">No graph elements to display</text>`;
      return;
    }

    const nodeById = {};
    nodes.forEach(n => { nodeById[n.id] = n; n.layer = 0; });

    let maxLayer = 0;
    function computeLayer(id, currentDepth) {
      if (currentDepth > 20) return;
      const n = nodeById[id];
      if (!n) return;
      if (n.layer < currentDepth) {
        n.layer = currentDepth;
        if (currentDepth > maxLayer) maxLayer = currentDepth;
      }
      edges.filter(e => e.from === id).forEach(e => {
        computeLayer(e.to, currentDepth + 1);
      });
    }

    nodes.filter(n => n.type === 'axiom' || n.type === 'query').forEach(n => {
      computeLayer(n.id, 0);
    });

    const contraNode = nodes.find(n => n.type === 'contradiction');
    if (contraNode) {
      contraNode.layer = maxLayer + 1;
      maxLayer = contraNode.layer;
    }

    const layers = [];
    for (let i = 0; i <= maxLayer; i++) layers.push([]);
    nodes.forEach(n => {
      const l = Math.min(n.layer, maxLayer);
      layers[l].push(n);
    });

    const layerHeight = 110;
    const nodeWidth = 240;
    const nodeHeight = 52;
    const horizSpacing = 260;

    layers.forEach((layerNodes, lIdx) => {
      const startX = 60;
      layerNodes.forEach((node, nIdx) => {
        node.x = startX + nIdx * horizSpacing;
        node.y = 50 + lIdx * layerHeight;
      });
    });

    let svgHtml = '';

    // Edges
    edges.forEach(e => {
      const src = nodeById[e.from];
      const dst = nodeById[e.to];
      if (!src || !dst) return;

      const x1 = src.x + nodeWidth / 2;
      const y1 = src.y + nodeHeight;
      const x2 = dst.x + nodeWidth / 2;
      const y2 = dst.y;
      const cy1 = y1 + (y2 - y1) / 2;
      const cy2 = y1 + (y2 - y1) / 2;

      const isContraEdge = dst.type === 'contradiction';
      const strokeColor = isContraEdge ? 'var(--danger-accent)' : 'var(--border-focus)';
      const markerId = isContraEdge ? 'url(#arrow-contradiction)' : 'url(#arrow)';

      svgHtml += `
        <path d="M ${x1} ${y1} C ${x1} ${cy1}, ${x2} ${cy2}, ${x2} ${y2}"
              fill="none"
              stroke="${strokeColor}"
              stroke-width="${isContraEdge ? 2.5 : 1.5}"
              marker-end="${markerId}" />
      `;
    });

    // Nodes
    nodes.forEach(node => {
      const isContra = node.type === 'contradiction';
      const isAxiom = node.type === 'axiom';
      const isQuery = node.type === 'query';

      let bgColor = 'var(--bg-card)';
      let borderColor = 'var(--border-subtle)';
      let textColor = 'var(--text-primary)';
      let strokeWidth = '1';

      if (isContra) {
        bgColor = 'var(--danger-bg)';
        borderColor = 'var(--danger-accent)';
        textColor = 'var(--danger-text)';
        strokeWidth = '2.5';
      } else if (isQuery) {
        bgColor = 'var(--warning-bg)';
        borderColor = 'var(--warning-border)';
      } else if (isAxiom) {
        borderColor = 'var(--border-focus)';
      }

      svgHtml += `
        <g class="dag-node" transform="translate(${node.x}, ${node.y})" style="cursor:pointer;" onclick="alert('Clause ID: ${node.id}\\nFormula: ${escapeQuotes(node.label)}\\nSource: ${escapeQuotes(node.source)}')">
          <rect width="${nodeWidth}" height="${nodeHeight}" rx="8"
                fill="${bgColor}"
                stroke="${borderColor}"
                stroke-width="${strokeWidth}"
                filter="drop-shadow(0 2px 4px rgba(0,0,0,0.06))" />
          <text x="12" y="20" font-size="11" font-weight="700" fill="${isContra ? 'var(--danger-accent)' : 'var(--brand-primary)'}" font-family="var(--font-mono)">
            ${node.id} [${node.type.toUpperCase()}]
          </text>
          <text x="12" y="38" font-size="11" font-weight="500" fill="${textColor}" font-family="var(--font-mono)">
            ${escapeHtml(truncate(node.label, 26))}
          </text>
        </g>
      `;
    });

    el.dagViewport.innerHTML = svgHtml;
    updateDagTransform();
  }

  function updateDagTransform() {
    el.dagViewport.setAttribute('transform', `translate(${state.graph.panX}, ${state.graph.panY}) scale(${state.graph.scale})`);
  }

  function renderReportView() {
    const res = state.auditResult;
    if (!res) return;

    el.riskScoreNum.textContent = res.risk_score;
    if (res.risk_score >= 80) {
      el.riskScoreCircle.style.borderColor = 'var(--danger-accent)';
      el.riskScoreCircle.style.color = 'var(--danger-accent)';
      el.riskHeadline.textContent = "Fatal Contract Contradiction & Liability";
      el.riskSummary.textContent = "First-order resolution refutation derived the empty clause [], confirming that the contract contains an irreconcilable conflict or active liability breach.";
    } else {
      el.riskScoreCircle.style.borderColor = 'var(--success-accent)';
      el.riskScoreCircle.style.color = 'var(--success-accent)';
      el.riskHeadline.textContent = "Low Legal Risk / Terms Consistent";
      el.riskSummary.textContent = "The contract terms are logically sound and no violations were derived under current facts.";
    }

    el.reportMarkdownPreview.textContent = res.markdown_report || "No report generated.";
  }

  // --- Event Listeners ---
  function setupEventListeners() {
    // Preset Selector
    el.presetSelector.addEventListener('change', async (e) => {
      state.currentPresetId = e.target.value;
      await loadAndAuditCurrentPreset();
    });

    // Run Trial Button
    el.btnRunAudit.addEventListener('click', async () => {
      await loadAndAuditCurrentPreset();
    });

    // Theme Toggle
    el.btnThemeToggle.addEventListener('click', toggleTheme);

    // Nav Tabs
    el.navTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        el.navTabs.forEach(t => t.classList.remove('active'));
        el.viewPanels.forEach(p => p.classList.remove('active'));

        tab.classList.add('active');
        const targetPanel = document.getElementById(tab.dataset.tab);
        if (targetPanel) targetPanel.classList.add('active');

        if (tab.dataset.tab === 'tab-prover') {
          setTimeout(renderProofGraph, 50);
        }
      });
    });

    // Pipeline Clause Select
    el.pipelineClauseSelect.addEventListener('change', (e) => {
      state.selectedPipelineClauseId = e.target.value;
      renderPipelineSteps();
    });

    // Prover Modes
    el.btnModeConflict.addEventListener('click', () => {
      state.activeMode = 'conflict';
      el.btnModeConflict.classList.remove('btn-outline');
      el.btnModeConflict.classList.add('btn-primary');
      el.btnModeBreach.classList.remove('btn-primary');
      el.btnModeBreach.classList.add('btn-outline');
      renderResolutionView();
      renderContractStudio();
    });

    el.btnModeBreach.addEventListener('click', () => {
      state.activeMode = 'breach';
      el.btnModeBreach.classList.remove('btn-outline');
      el.btnModeBreach.classList.add('btn-primary');
      el.btnModeConflict.classList.remove('btn-primary');
      el.btnModeConflict.classList.add('btn-outline');
      renderResolutionView();
      renderContractStudio();
    });

    // SVG Zoom & Pan
    el.btnZoomIn.addEventListener('click', () => {
      state.graph.scale = Math.min(state.graph.scale + 0.15, 2.5);
      updateDagTransform();
    });

    el.btnZoomOut.addEventListener('click', () => {
      state.graph.scale = Math.max(state.graph.scale - 0.15, 0.4);
      updateDagTransform();
    });

    el.btnZoomReset.addEventListener('click', () => {
      state.graph.scale = 1.0;
      state.graph.panX = 40;
      state.graph.panY = 30;
      updateDagTransform();
    });

    // Drag Pan
    el.proofDagSvg.addEventListener('mousedown', (e) => {
      state.graph.isDragging = true;
      state.graph.startX = e.clientX - state.graph.panX;
      state.graph.startY = e.clientY - state.graph.panY;
    });

    window.addEventListener('mousemove', (e) => {
      if (!state.graph.isDragging) return;
      state.graph.panX = e.clientX - state.graph.startX;
      state.graph.panY = e.clientY - state.graph.startY;
      updateDagTransform();
    });

    window.addEventListener('mouseup', () => {
      state.graph.isDragging = false;
    });

    // Modal
    el.btnAddClauseModal.addEventListener('click', () => {
      el.addClauseModal.classList.add('open');
    });

    const closeModal = () => el.addClauseModal.classList.remove('open');
    el.btnCloseModal.addEventListener('click', closeModal);
    el.btnCancelClause.addEventListener('click', closeModal);

    // Auto-Translate
    el.btnAutoTranslate.addEventListener('click', async () => {
      const text = el.inputClauseText.value.trim();
      if (!text) {
        alert('Please enter natural legal clause text first.');
        return;
      }
      try {
        const res = await fetch('/api/parse-clause', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ natural_text: text })
        });
        const data = await res.json();
        el.inputClauseFopl.value = data.fopl;
      } catch (err) {
        alert('Translation failed: ' + err);
      }
    });

    // Save Custom Clause
    el.btnSaveClause.addEventListener('click', async () => {
      const title = el.inputClauseTitle.value.trim();
      const text = el.inputClauseText.value.trim();
      const fopl = el.inputClauseFopl.value.trim();

      if (!title || !text || !fopl) {
        alert('Please fill out all fields.');
        return;
      }

      const newClause = {
        id: `C${state.currentContract.clauses.length + 1}`,
        clause_num: `Custom Sec`,
        title: title,
        natural_text: text,
        fopl: fopl,
        modality: "Custom"
      };

      state.currentContract.clauses.push(newClause);
      closeModal();

      try {
        const res = await fetch('/api/audit-custom', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ contract_data: state.currentContract })
        });
        state.auditResult = await res.json();
        renderHeroMeta();
        renderContractStudio();
        renderPipelineSelector();
        renderPipelineSteps();
        renderResolutionView();
        renderReportView();
      } catch (err) {
        alert('Trial failed: ' + err);
      }
    });

    // Report Actions
    el.btnCopyMarkdown.addEventListener('click', () => {
      const md = state.auditResult?.markdown_report || '';
      navigator.clipboard.writeText(md).then(() => {
        alert('Settlement & Audit Report copied to clipboard!');
      });
    });

    el.btnExportReport.addEventListener('click', () => {
      document.querySelector('[data-tab="tab-report"]').click();
      setTimeout(() => window.print(), 300);
    });

    el.btnPrintReport.addEventListener('click', () => {
      window.print();
    });
  }

  // --- Utilities ---
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function escapeQuotes(str) {
    if (!str) return '';
    return String(str).replace(/'/g, "\\'").replace(/"/g, '\\"');
  }

  function truncate(str, maxLen) {
    if (!str) return '';
    return str.length > maxLen ? str.substring(0, maxLen - 2) + '..' : str;
  }

  window.addEventListener('DOMContentLoaded', init);

})();
