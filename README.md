# 會員制內容發布系統 — Phase 1 後台 MVP

快速搭建 Vue3 後台 + FastAPI + PostgreSQL 的會員／內容管理系統，符合 `AGENTS.md` 規格並支援 Docker Compose 一鍵啟動。

## 目錄結構

```
.
├── AGENTS.md                # PRD
├── backend/                 # FastAPI 專案
│   ├── app/
│   │   ├── core/            # 設定
│   │   ├── models/          # SQLAlchemy models (users, contents, ...)
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routers/         # Auth / Members / Contents / Categories / Audit / Dashboard
│   │   └── utils/           # JWT、密碼
│   ├── alembic/             # 資料庫 migration
│   └── requirements.txt
├── frontend/                # Vue 3 + Element Plus 後台
│   └── src/
│       ├── components/      # 共用版面
│       ├── pages/           # Login / Dashboard / CRUD 頁面
│       └── store/           # Pinia (登入狀態)
├── docker-compose.yml       # backend + frontend + postgres
├── .env.example             # 環境變數樣板
└── README.md
```

## 環境變數

複製 `.env.example` 為 `.env` 並依需要調整：

```
cp .env.example .env
```

| 變數 | 說明 |
| ---- | ---- |
| `APP_ENV` | `development` / `staging` / `production` |
| `SECRET_KEY` | JWT 簽章金鑰 |
| `DATABASE_URL` | PostgreSQL 連線字串，預設對應 docker db 服務 |
| `JWT_EXPIRE_MINUTES` | Token 時效（分鐘） |
| `RATE_LIMIT_*` | 登入節流設定 |
| `VITE_API_BASE` | 前端呼叫後端的 base URL |

## Docker Compose 一鍵啟動

```bash
docker compose up --build
```

- Backend：`http://localhost:8000` (FastAPI + Swagger)
- Frontend：`http://localhost:5173`
- DB：`localhost:5432`，帳密 `admin/password`

> Alembic 初始 migration (`backend/alembic/versions/0001_initial.py`) 已定義所有資料表，可透過 `alembic upgrade head` 套用至資料庫。

## 本地開發（可選）

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## 功能摘要

- **登入 / 單裝置限制**：登入即遞增 `token_version`，舊 token 立即失效，並記錄行為稽核。
- **會員管理**：列表搜尋、建立/編輯、軟刪除（停用），密碼更新會重置 token。
- **內容管理**：分類、狀態（草稿/發佈/下架）、TipTap 後續可整合；目前提供基本 CRUD 與軟刪除。
- **分類管理**：排序、描述、刪除時檢查是否有內容。
- **行為稽核**：任意事件可透過 `/api/audit/track` 上報，後台有簡易紀錄清單與 Dashboard 摘要。
- **Dashboard**：顯示總計、最近登入/閱讀紀錄，預留圖表空間。

## 後續建議

1. 依照實際部署需求補齊 CI/CD（測試、格式化、自動 migration）。
2. 在 Frontend 整合 TipTap / 上傳模組，並完善表單驗證與錯誤顯示。
3. 增加測試（pytest + httpx）覆蓋核心 API 與權限情境。
會員制內容管理系統
