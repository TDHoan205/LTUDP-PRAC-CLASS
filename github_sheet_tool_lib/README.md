# GitHub Sheet Tool (Nang cao)

## Smart GitHub Assignment Checker with AI

Da bo sung he thong mo rong theo huong backend API + UI:

- Quan ly sinh vien (CRUD)
- Scan bai tu Google Sheet
- Kiem tra GitHub repo + diem AI + canh bao tuong dong
- Kiem tra deadline (dua tren commit cuoi)
- Dashboard tong quan theo nhom
- Chatbot hoi dap cho giang vien
- Auto scan dinh ky
- Export CSV + HTML report

## UI chuyen nghiep (web) - FastAPI + HTML + CSS + JS

Da chuyen sang kieu UI web 1 man hinh theo huong chuyen nghiep:

- Topbar: search, thong bao, settings deadline/refresh
- Card thong ke nhanh: Tong SV / Da nop / Chua nop / Tre
- Bieu do: pie (nop/chua nop) + bar (theo nhom)
- Bang sinh vien + action View/AI/Check dao code
- Panel chi tiet ben phai
- Popup dao code + so sanh code chia doi man hinh
- AJAX fetch (khong reload trang)
- Dark mode + loading overlay

### Kien truc trong thu muc nay (da toi uu de de quan ly)

- `core.py`: Engine phan tich/cham diem
- `ui_app.py`: Wrapper tuong thich, goi desktop UI legacy
- `smart_system.py`: Lop he thong tong hop + luu sqlite
- `smart_api.py`: FastAPI endpoints
- `run_smart_api.py`: Launcher API server

Web structure (gom vao 1 folder):

- `web/app.py`: FastAPI web route `/` + static mount
- `web/legacy/ui_app.py`: Desktop UI cu
- `web/templates/dashboard.html`: giao dien dashboard
- `web/static/css/style.css`: style chinh
- `web/static/js/app.js`: logic AJAX + chart + modal
- `web/services/github.py`: helper dich vu GitHub
- `web/services/ai.py`: helper AI summary/risk
- `web/services/sheet.py`: helper Google Sheet

Tool nay kiem tra:
- Link GitHub trong Google Sheet co truy cap duoc hay khong
- Dong gop code theo contributors (%)
- Kiem tra bai tap theo section + danh sach file + mo ta de bai
- Rule rieng cho bai1..bai5 khi kiem tra section 2.3
- Phat hien code tuong dong giua cac repo
- Xuat CSV tong hop de xem nhanh ket qua

## Chay bang UI (dan link va bam chay)

```bash
python baitapclass/github_sheet_tool_lib/ui_app.py
```

Sau khi mo UI:
- Dan Google Sheet URL
- Chinh section/bai-range neu can
- Neu co token thi dan vao o GitHub Token
- Bam "Chay Phan Tich"
- Co nut chuyen che do giao dien: Light / Dark Navy

## Chay backend API (Smart System)

### 1) Cai thu vien

```bash
pip install fastapi uvicorn jinja2
```

### 2) Chay server

```bash
python baitapclass/github_sheet_tool_lib/run_smart_api.py
```

Mac dinh server chay tai: `http://127.0.0.1:8088`

### 3) Mo dashboard web

- Dashboard: `http://127.0.0.1:8088/`

### 4) Mo tai lieu API

- Swagger UI: `http://127.0.0.1:8088/docs`

## Endpoint chinh

- `GET /api/students`: Danh sach sinh vien
- `POST /api/students`: Them sinh vien
- `PUT /api/students/{id}`: Sua sinh vien
- `DELETE /api/students/{id}`: Xoa sinh vien (admin)
- `POST /api/scans/from-sheet`: Chay scan tu Google Sheet
- `GET /api/scans`: Danh sach lan scan
- `GET /api/scans/latest`: Lay lan scan moi nhat
- `GET /api/scans/{scan_id}/entries`: Chi tiet bai nop
- `GET /api/scans/{scan_id}/dashboard`: Tong quan thong ke
- `GET /api/scans/{scan_id}/plagiarism`: Cac cap nghi dao code
- `GET /api/code-compare`: Lay noi dung 2 file code de so sanh
- `POST /api/scans/{scan_id}/chat`: Chatbot hoi dap
- `POST /api/auto-scan/start`: Bat auto scan
- `POST /api/auto-scan/stop`: Dung auto scan

## Ghi chu quan trong

- De ket qua day du va chinh xac, nen dat bien `GITHUB_TOKEN`.
- Neu khong co token, GitHub API de bi rate-limit (403/429).
- File DB sqlite duoc luu tai: `baitapclass/smart_checker_data/smart_checker.db`.

## Cach chay co ban

```bash
python baitapclass/github_sheet_tool_lib/github_sheet_tool.py --sheet-url "https://docs.google.com/spreadsheets/d/<ID>/edit#gid=0"
```

## Kiem tra bai tap section 2.3

```bash
python baitapclass/github_sheet_tool_lib/github_sheet_tool.py \
  --sheet-url "https://docs.google.com/spreadsheets/d/<ID>/edit#gid=0" \
  --section "2.3" \
  --bai-range "1-5" \
  --assignment "Kiem tra bai 2.3, dung logic theo de bai" \
  --similarity-threshold 0.9 \
  --output "baitapclass/github_sheet_report_advanced.json"

```

## Xuat CSV tong hop

```bash
python baitapclass/github_sheet_tool_lib/github_sheet_tool.py \
  --sheet-url "https://docs.google.com/spreadsheets/d/<ID>/edit#gid=0" \
  --section "2.3" \
  --bai-range "1-5" \
  --assignment "Kiem tra bai 2.3" \
  --summary-csv "baitapclass/github_sheet_report_advanced_summary.csv"
```

## Dung token de ket qua chinh xac hon

```bash
set GITHUB_TOKEN=ghp_xxx
python baitapclass/github_sheet_tool_lib/github_sheet_tool.py --sheet-url "..."
```

## Dau ra

- JSON report mac dinh: `baitapclass/github_sheet_report.json`
- Bao gom:
  - Thong ke link truy cap
  - % dong gop contributors
  - Bao cao cham bai theo repo (PASS/WARN/FAIL)
  - Bao cao tuong dong code (exact + near duplicate)
- CSV summary (neu bat kiem tra bai):
  - Trang thai PASS/WARN/FAIL theo repo
  - Diem va duong dan tung bai
