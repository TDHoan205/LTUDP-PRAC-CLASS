let latestScanId = null;
let currentEntries = [];
let selectedEntry = null;
let pieChart = null;
let barChart = null;
let timelineChart = null;
let plagiarismPairs = [];
let activeRowMssv = '';
let plagLoadedScanId = null;
const compareCache = new Map();
const aiCache = new Map();

const els = {
  sheetUrl: document.getElementById('sheetUrlInput'),
  section: document.getElementById('sectionInput'),
  deadline: document.getElementById('deadlineInput'),
  refresh: document.getElementById('refreshInput'),
  search: document.getElementById('searchInput'),
  filter: document.getElementById('filterSelect'),
  scanBtn: document.getElementById('scanBtn'),
  themeBtn: document.getElementById('themeBtn'),
  notifyBtn: document.getElementById('notifyBtn'),
  cardTotal: document.getElementById('cardTotal'),
  cardSubmitted: document.getElementById('cardSubmitted'),
  cardMissing: document.getElementById('cardMissing'),
  cardLate: document.getElementById('cardLate'),
  tableBody: document.querySelector('#studentTable tbody'),
  tableCount: document.getElementById('tableCount'),
  detailBox: document.getElementById('detailBox'),
  logBox: document.getElementById('logBox'),
  viewBtn: document.getElementById('viewBtn'),
  aiBtn: document.getElementById('aiBtn'),
  plagBtn: document.getElementById('plagBtn'),
  toastBody: document.getElementById('toastBody'),
  loading: document.getElementById('loadingOverlay'),
  studentModalBody: document.getElementById('studentModalBody'),
  plagTableBody: document.querySelector('#plagTable tbody'),
  similarityRange: document.getElementById('similarityRange'),
  similarityLabel: document.getElementById('similarityLabel'),
  plagCount: document.getElementById('plagCount'),
  compareMeta: document.getElementById('compareMeta'),
  aiQuestion: document.getElementById('aiQuestionInput'),
  aiAskBtn: document.getElementById('aiAskBtn'),
  aiQuickLate: document.getElementById('aiQuickLate'),
  aiQuickMissing: document.getElementById('aiQuickMissing'),
  aiQuickTop: document.getElementById('aiQuickTop'),
  aiQuickWeak: document.getElementById('aiQuickWeak'),
  aiAnswerBox: document.getElementById('aiAnswerBox'),
  codeA: document.getElementById('codeA'),
  codeB: document.getElementById('codeB'),
};

const toast = new bootstrap.Toast(document.getElementById('quickToast'));
const studentModal = new bootstrap.Modal(document.getElementById('studentModal'));
const plagModal = new bootstrap.Modal(document.getElementById('plagModal'));

function logLine(msg) {
  const now = new Date().toLocaleTimeString();
  els.logBox.textContent += `\n[${now}] ${msg}`;
  els.logBox.scrollTop = els.logBox.scrollHeight;
}

function setLoading(on) {
  els.loading.classList.toggle('d-none', !on);
}

function statusBadge(status, deadlineStatus) {
  if (status === 'DA_NOP' && deadlineStatus === 'TRE_HAN') {
    return '<span class="status-pill status-late">Trễ</span>';
  }
  if (status === 'DA_NOP') {
    return '<span class="status-pill status-submitted">Đã nộp</span>';
  }
  return '<span class="status-pill status-missing">Chưa nộp</span>';
}

function safe(v) {
  if (v === null || v === undefined) return '';
  return String(v)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');
}

function getGradeBadge(entry) {
  const score = Number(entry?.score_10 || 0);
  const submitted = entry?.submitted_status === 'DA_NOP';
  const late = entry?.deadline_status === 'TRE_HAN';
  const risk = Number(entry?.plagiarism_high_risk || 0) === 1;

  if (!submitted) return 'CHUA_NOP';
  if (risk) return 'CANH_BAO_DAO_CODE';
  if (score >= 8.5 && !late) return 'XUAT_SAC';
  if (score >= 7) return 'TOT';
  if (score >= 5) return 'DAT';
  return 'CAN_CAI_THIEN';
}

function drawPie(submitted, missing) {
  const ctx = document.getElementById('pieChart').getContext('2d');
  if (pieChart) pieChart.destroy();
  pieChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Đã nộp', 'Chưa nộp'],
      datasets: [{
        data: [submitted, missing],
        backgroundColor: ['#1a7f37', '#b42318'],
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
}

function drawBar(groups) {
  const topGroups = [...groups]
    .sort((a, b) => Number(b.total || 0) - Number(a.total || 0))
    .slice(0, 8);
  const labels = topGroups.map((x) => {
    const raw = String(x.group || 'NA');
    return raw.length > 8 ? `${raw.slice(0, 8)}...` : raw;
  });
  const values = topGroups.map(x => x.total || 0);
  const maxValue = Math.max(0, ...values);
  const chartMax = Math.max(10, Math.ceil(maxValue * 1.1));
  const tickStep = (() => {
    if (chartMax <= 10) return 1;
    const rough = chartMax / 5;
    const base = Math.pow(10, Math.floor(Math.log10(rough)));
    if (rough / base >= 5) return 5 * base;
    if (rough / base >= 2) return 2 * base;
    return base;
  })();
  const ctx = document.getElementById('barChart').getContext('2d');
  if (barChart) barChart.destroy();
  barChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Số SV',
        data: values,
        backgroundColor: '#2f86d6',
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          suggestedMax: chartMax,
          ticks: {
            stepSize: tickStep,
            maxTicksLimit: 6,
          }
        },
        x: {
          ticks: {
            maxRotation: 0,
            minRotation: 0,
            autoSkip: true,
            maxTicksLimit: 8,
          }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            footer: () => groups.length > topGroups.length ? `Dang hien thi top ${topGroups.length}/${groups.length} nhom` : ''
          }
        }
      }
    }
  });
}

function drawTimeline(entry) {
  const files = entry?.details?.files || [];
  const compact = files.slice(0, 6);
  const labels = compact.map((f) => {
    const raw = String(f.required_name || 'bai');
    return raw.length > 10 ? `${raw.slice(0, 10)}...` : raw;
  });
  const scores = compact.map(f => Number(f.score || 0));

  const ctx = document.getElementById('timelineChart').getContext('2d');
  if (timelineChart) timelineChart.destroy();
  timelineChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Điểm theo bài',
        data: scores,
        borderColor: '#2f86d6',
        pointBackgroundColor: '#2f86d6',
        fill: false,
        tension: 0.25,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 10,
        },
        x: {
          ticks: {
            maxRotation: 0,
            minRotation: 0,
            autoSkip: true,
            maxTicksLimit: 6,
          }
        }
      }
    }
  });
}

function renderDetail(entry) {
  if (!entry) {
    els.detailBox.textContent = 'Chọn một sinh viên để xem chi tiết.';
    els.viewBtn.disabled = true;
    els.aiBtn.disabled = true;
    return;
  }
  els.viewBtn.disabled = false;
  els.aiBtn.disabled = false;

  const comments = safe(entry.comments || '');
  const gradeBadge = getGradeBadge(entry);
  const text = [
    `MSSV: ${safe(entry.mssv || '')}`,
    `Tên: ${safe(entry.full_name || '')}`,
    `Repo: ${safe(entry.repo_full_name || '')}`,
    `Nộp: ${safe(entry.submitted_status || '')}`,
    `Deadline: ${safe(entry.deadline_status || '')}`,
    `Commit cuối: ${safe(entry.last_commit_at || '')}`,
    `Điểm: ${Number(entry.score_10 || 0).toFixed(2)}/10`,
    `Đánh giá: ${gradeBadge}`,
    '',
    'Nhận xét AI:',
    comments || 'Chưa có nhận xét'
  ].join('\n');

  els.detailBox.textContent = text;
  drawTimeline(entry);
}

function passesFilter(entry) {
  const kw = els.search.value.trim().toLowerCase();
  const mode = els.filter.value;

  const hay = `${entry.mssv || ''} ${entry.full_name || ''} ${entry.repo_full_name || ''}`.toLowerCase();
  if (kw && !hay.includes(kw)) return false;

  if (mode === 'CHUA_NOP') {
    return entry.submitted_status !== 'DA_NOP';
  }
  if (mode === 'TRE_HAN') {
    return entry.deadline_status === 'TRE_HAN';
  }
  if (mode === 'LOW_SCORE') {
    return Number(entry.score_10 || 0) < 5;
  }
  return true;
}

function renderTable() {
  const rows = currentEntries.filter(passesFilter);
  els.tableCount.textContent = `${rows.length} dòng`;
  els.tableBody.innerHTML = rows.map((e, idx) => {
    const score = Number(e.score_10 || 0).toFixed(1);
    const isRisk = Number(e.plagiarism_high_risk || 0) === 1;
    const riskBadge = isRisk ? '<span class="badge text-bg-danger">Risk</span>' : '';
    return `
      <tr data-index="${idx}">
        <td>${safe(e.mssv || '')}</td>
        <td>${safe(e.full_name || '')}</td>
        <td class="text-break">${safe(e.repo_full_name || '')}</td>
        <td>${statusBadge(e.submitted_status, e.deadline_status)}</td>
        <td>${score} ${riskBadge}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary act-view">👁️</button>
          <button class="btn btn-sm btn-outline-success act-ai">🤖</button>
          <button class="btn btn-sm btn-outline-danger act-plag">🔍</button>
        </td>
      </tr>
    `;
  }).join('');

  const filtered = rows;
  els.tableBody.querySelectorAll('tr').forEach((tr, index) => {
    const entry = filtered[index];
    if ((entry.mssv || '') === activeRowMssv) {
      tr.classList.add('active-row');
    }

    tr.addEventListener('click', () => {
      selectedEntry = entry;
      activeRowMssv = String(entry.mssv || '');
      renderTable();
      renderDetail(selectedEntry);
    });
    tr.querySelector('.act-view').addEventListener('click', (ev) => {
      ev.stopPropagation();
      selectedEntry = entry;
      activeRowMssv = String(entry.mssv || '');
      renderTable();
      openStudentModal(selectedEntry);
    });
    tr.querySelector('.act-ai').addEventListener('click', (ev) => {
      ev.stopPropagation();
      selectedEntry = entry;
      activeRowMssv = String(entry.mssv || '');
      renderTable();
      showAISummary(selectedEntry);
    });
    tr.querySelector('.act-plag').addEventListener('click', (ev) => {
      ev.stopPropagation();
      openPlagiarismModal();
    });
  });
}

function openStudentModal(entry) {
  if (!entry) return;
  const files = entry.details?.files || [];
  const fileHtml = files.slice(0, 8).map(f => `
    <li><b>${safe(f.required_name || '')}</b>: ${safe(f.verdict || '')} (${Number(f.score || 0).toFixed(1)})</li>
  `).join('');

  els.studentModalBody.innerHTML = `
    <div><b>MSSV:</b> ${safe(entry.mssv || '')}</div>
    <div><b>Tên:</b> ${safe(entry.full_name || '')}</div>
    <div><b>Repo:</b> ${safe(entry.repo_full_name || '')}</div>
    <div><b>Trạng thái:</b> ${safe(entry.submitted_status || '')} / ${safe(entry.deadline_status || '')}</div>
    <div><b>Điểm:</b> ${Number(entry.score_10 || 0).toFixed(2)}/10</div>
    <hr />
    <div><b>File checks:</b></div>
    <ul>${fileHtml || '<li>Không có dữ liệu file.</li>'}</ul>
    <div><b>Nhận xét:</b> ${safe(entry.comments || 'N/A')}</div>
  `;
  studentModal.show();
}

function showAISummary(entry) {
  if (!entry || !latestScanId) return;
  const question = `Hay danh gia nhanh sinh vien ${entry.full_name || ''} (${entry.mssv || ''}) theo diem, tre han va nguy co dao code.`;
  askChatbot(question, { fallbackEntry: entry }).catch((err) => {
    alert(`Lỗi AI: ${err.message}`);
  });
}

function buildFallbackAi(entry) {
  const score = Number(entry?.score_10 || 0).toFixed(2);
  const grade = getGradeBadge(entry);
  const comment = entry?.comments || 'Chưa có nhận xét.';
  return `Đánh giá nhanh\n- Điểm: ${score}/10\n- Nhóm đánh giá: ${grade}\n- Trạng thái nộp: ${entry?.submitted_status || 'N/A'}\n- Deadline: ${entry?.deadline_status || 'N/A'}\n\nNhận xét:\n${comment}`;
}

async function askChatbot(question, options = {}) {
  if (!latestScanId) {
    throw new Error('Chưa có scan để hỏi AI.');
  }

  const q = (question || '').trim();
  if (!q) {
    throw new Error('Bạn chưa nhập câu hỏi.');
  }

  const cacheKey = `${latestScanId}|${q}`;
  if (aiCache.has(cacheKey)) {
    const cached = aiCache.get(cacheKey);
    els.aiAnswerBox.textContent = cached;
    return cached;
  }

  els.aiAnswerBox.textContent = 'AI đang phân tích...';
  const payload = { question: q };

  try {
    const data = await fetchJSON(`/api/scans/${latestScanId}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const answer = (data.answer || '').trim() || buildFallbackAi(options.fallbackEntry);
    aiCache.set(cacheKey, answer);
    els.aiAnswerBox.textContent = answer;
    return answer;
  } catch (err) {
    if (options.fallbackEntry) {
      const fallback = buildFallbackAi(options.fallbackEntry);
      els.aiAnswerBox.textContent = `${fallback}\n\n(Loi goi AI API: ${err.message})`;
      return fallback;
    }
    throw err;
  }
}

async function fetchJSON(url, options = {}) {
  const r = await fetch(url, options);
  if (!r.ok) {
    const txt = await r.text();
    throw new Error(`${r.status} ${txt}`);
  }
  return r.json();
}

async function loadLatestScan() {
  const latest = await fetchJSON('/api/scans/latest');
  if (!latest?.scan_id) {
    logLine('Chưa có scan nào. Hãy bấm Scan GitHub.');
    return;
  }

  latestScanId = latest.scan_id;
  const [dashboard, entries] = await Promise.all([
    fetchJSON(`/api/scans/${latestScanId}/dashboard`),
    fetchJSON(`/api/scans/${latestScanId}/entries`),
  ]);

  currentEntries = entries.items || [];
  plagiarismPairs = [];
  plagLoadedScanId = null;
  compareCache.clear();
  aiCache.clear();

  const total = Number(dashboard.total || 0);
  const submitted = Math.round(total * Number(dashboard.submitted_percent || 0) / 100);
  const missing = Math.max(0, total - submitted);
  const late = Math.round(total * Number(dashboard.late_percent || 0) / 100);

  els.cardTotal.textContent = String(total);
  els.cardSubmitted.textContent = String(submitted);
  els.cardMissing.textContent = String(missing);
  els.cardLate.textContent = String(late);

  drawPie(submitted, missing);
  drawBar(dashboard.by_group || []);
  renderTable();

  const highRisk = currentEntries.filter(x => Number(x.plagiarism_high_risk || 0) === 1).length;
  const notice = `${missing} sinh viên chưa nộp, ${highRisk} trường hợp nghi đạo code`;
  els.toastBody.textContent = notice;
  toast.show();
  logLine(`Đã tải scan #${latestScanId}.`);
}

async function runScan() {
  const sheetUrl = els.sheetUrl.value.trim();
  const section = els.section.value.trim() || '2.3';
  if (!sheetUrl) {
    alert('Bạn cần nhập Google Sheet URL');
    return;
  }

  setLoading(true);
  try {
    const payload = {
      sheet_url: sheetUrl,
      section,
      bai_range: '1-5',
      assignment: `kiem tra bai trong folder ${section}`,
      similarity_threshold: 0.9,
      deadline_iso: els.deadline.value.trim(),
      token: '',
    };

    const result = await fetchJSON('/api/scans/from-sheet', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    latestScanId = result.scan_id;
    logLine(`Scan thành công: #${latestScanId}`);
    await loadLatestScan();
  } catch (err) {
    logLine(`Lỗi scan: ${err.message}`);
    alert(`Lỗi scan: ${err.message}`);
  } finally {
    setLoading(false);
  }
}

function getPlagiarismThreshold() {
  return Number(els.similarityRange?.value || 80) / 100;
}

function renderPlagiarismRows() {
  const threshold = getPlagiarismThreshold();
  const filtered = plagiarismPairs.filter((p) => Number(p.similarity || 0) >= threshold);
  els.plagCount.textContent = `${filtered.length} cặp`;

  els.plagTableBody.innerHTML = filtered.map((p, idx) => `
    <tr>
      <td>${safe(p.repo_a || '')}</td>
      <td>${safe(p.repo_b || '')}</td>
      <td>${(Number(p.similarity || 0) * 100).toFixed(1)}%</td>
      <td>${safe(p.required_name || '')}</td>
      <td><button class="btn btn-sm btn-outline-primary" data-idx="${idx}">Mở</button></td>
    </tr>
  `).join('');

  return filtered;
}

function overlapStats(codeA, codeB) {
  const linesA = codeA.split('\n').map((x) => x.trim()).filter(Boolean);
  const linesBSet = new Set(codeB.split('\n').map((x) => x.trim()).filter(Boolean));
  if (!linesA.length) return { matched: 0, total: 0, ratio: 0 };
  let matched = 0;
  for (const line of linesA) {
    if (linesBSet.has(line)) matched += 1;
  }
  return { matched, total: linesA.length, ratio: matched / linesA.length };
}

async function loadPlagiarismIfNeeded() {
  if (!latestScanId) return;
  if (plagLoadedScanId === latestScanId && plagiarismPairs.length) return;
  const data = await fetchJSON(`/api/scans/${latestScanId}/plagiarism`);
  plagiarismPairs = data.items || [];
  plagLoadedScanId = latestScanId;
}

async function openPlagiarismModal() {
  if (!latestScanId) {
    alert('Chưa có scan để kiểm tra đạo code.');
    return;
  }

  setLoading(true);
  try {
    await loadPlagiarismIfNeeded();
  } catch (err) {
    setLoading(false);
    alert(`Lỗi tải dữ liệu đạo code: ${err.message}`);
    return;
  }
  setLoading(false);

  const filtered = renderPlagiarismRows();

  els.codeA.textContent = 'Chọn một dòng để xem code.';
  els.codeB.textContent = 'Chọn một dòng để xem code.';
  els.compareMeta.textContent = 'Chọn một cặp để xem chi tiết so sánh.';

  els.plagTableBody.querySelectorAll('button[data-idx]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const pair = filtered[Number(btn.dataset.idx)];
      const key = `${pair.repo_a}|${pair.path_a}|${pair.repo_b}|${pair.path_b}`;
      try {
        let data = compareCache.get(key);
        if (!data) {
          data = await fetchJSON(`/api/code-compare?repo_a=${encodeURIComponent(pair.repo_a)}&path_a=${encodeURIComponent(pair.path_a)}&repo_b=${encodeURIComponent(pair.repo_b)}&path_b=${encodeURIComponent(pair.path_b)}`);
          compareCache.set(key, data);
        }
        els.codeA.innerHTML = highlightOverlap(data.code_a || '', data.code_b || '');
        els.codeB.innerHTML = highlightOverlap(data.code_b || '', data.code_a || '');
        const aStats = overlapStats(data.code_a || '', data.code_b || '');
        els.compareMeta.textContent = `Overlap: ${(aStats.ratio * 100).toFixed(1)}% (${aStats.matched}/${aStats.total} dòng trùng theo repo A)`;
      } catch (err) {
        alert(`Lỗi tải code: ${err.message}`);
      }
    });
  });

  plagModal.show();
}

function highlightOverlap(primary, other) {
  const linesOther = new Set(other.split('\n').map(x => x.trim()).filter(Boolean));
  return primary.split('\n').map(line => {
    const esc = safe(line);
    if (line.trim() && linesOther.has(line.trim())) {
      return `<span class="hl">${esc}</span>`;
    }
    return esc;
  }).join('\n');
}

function toggleTheme() {
  const html = document.documentElement;
  const next = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
  html.setAttribute('data-theme', next);
  els.themeBtn.textContent = next === 'dark' ? 'Light' : 'Dark';
}

function wireEvents() {
  els.scanBtn.addEventListener('click', runScan);
  els.themeBtn.addEventListener('click', toggleTheme);
  els.notifyBtn.addEventListener('click', () => toast.show());
  els.search.addEventListener('input', renderTable);
  els.filter.addEventListener('change', renderTable);

  els.viewBtn.addEventListener('click', () => openStudentModal(selectedEntry));
  els.aiBtn.addEventListener('click', () => showAISummary(selectedEntry));
  els.plagBtn.addEventListener('click', openPlagiarismModal);
  els.aiAskBtn.addEventListener('click', () => {
    askChatbot(els.aiQuestion.value).catch((err) => {
      alert(`Lỗi AI: ${err.message}`);
    });
  });
  els.aiQuestion.addEventListener('keydown', (ev) => {
    if (ev.key === 'Enter') {
      ev.preventDefault();
      askChatbot(els.aiQuestion.value).catch((err) => {
        alert(`Lỗi AI: ${err.message}`);
      });
    }
  });
  els.aiQuickMissing.addEventListener('click', () => {
    els.aiQuestion.value = 'Ai chưa nộp bài?';
    askChatbot(els.aiQuestion.value).catch(() => {});
  });
  els.aiQuickLate.addEventListener('click', () => {
    els.aiQuestion.value = 'Ai nộp trễ hạn?';
    askChatbot(els.aiQuestion.value).catch(() => {});
  });
  els.aiQuickTop.addEventListener('click', () => {
    els.aiQuestion.value = 'Top sinh viên tốt nhất?';
    askChatbot(els.aiQuestion.value).catch(() => {});
  });
  els.aiQuickWeak.addEventListener('click', () => {
    els.aiQuestion.value = 'Top sinh viên yếu cần xử lý sớm?';
    askChatbot(els.aiQuestion.value).catch(() => {});
  });
  els.similarityRange.addEventListener('input', () => {
    const value = Number(els.similarityRange.value || 80);
    els.similarityLabel.textContent = `${value}%`;
    renderPlagiarismRows();
  });

  let timer = null;
  els.refresh.addEventListener('change', () => {
    if (timer) clearInterval(timer);
    const m = Number(els.refresh.value || 0);
    if (m > 0) {
      timer = setInterval(() => {
        loadLatestScan().catch(() => {});
      }, m * 60 * 1000);
      logLine(`Auto refresh mỗi ${m} phút`);
    }
  });
}

async function boot() {
  wireEvents();
  els.similarityLabel.textContent = `${Number(els.similarityRange.value || 80)}%`;
  try {
    await loadLatestScan();
  } catch (err) {
    logLine(`Boot warning: ${err.message}`);
  }
}

boot();
