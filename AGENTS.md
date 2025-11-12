# 會員制內容發布系統 — Phase 1 後台 MVP（AGENTS.md）

## 一、專案簡介
本階段為「會員制內容發布系統」的後台 MVP（Minimum Viable Product）。
目標：建立能管理會員與內容的後台系統，具備登入驗證、分類、內容編輯與基礎稽核；採用 Docker Compose 一鍵啟動。

---

## 二、開發目標
- 後台登入與帳號管理（會員 CRUD）。
- 內容管理模組（含分類管理與所見即所得編輯器）。
- 單一裝置登入限制（同帳號不得同時於多裝置登入）。
- 行為稽核（登入、登出、裝置切換、閱讀行為、後台操作）。
- Docker Compose 架構，支援本地/測試/正式環境配置。

---

## 三、系統架構
```
[Frontend Admin (Vue3)] → [FastAPI Backend] → [PostgreSQL]
                                 ↑
                         [SQLAlchemy + Alembic]
```
### Docker Compose（摘要）
```yaml
version: "3.9"
services:
  backend:
    build: ./backend
    container_name: content_backend
    restart: always
    env_file: .env
    ports: ["8000:8000"]
    depends_on: [db]
    volumes: ["./backend:/app"]

  frontend:
    build: ./frontend
    container_name: content_frontend
    restart: always
    ports: ["5173:5173"]
    depends_on: [backend]
    volumes: ["./frontend:/app"]

  db:
    image: postgres:15
    container_name: content_db
    restart: always
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
      POSTGRES_DB: content_db
    volumes: ["./postgres_data:/var/lib/postgresql/data"]
    ports: ["5432:5432"]
```

---

## 四、功能模組與 API

### 4.1 會員管理（Member Management）
**功能**
- 登入/登出（JWT）。
- 列表、搜尋、分頁、排序。
- 新增/編輯/刪除（軟刪除）。
- 權限：`admin` 可登入後台；`member` 僅限前台。

**API**
```
POST   /api/auth/login
POST   /api/auth/logout           # 使目前 token 失效（加入黑名單/版本遞增）
GET    /api/members
POST   /api/members
PUT    /api/members/{id}
DELETE /api/members/{id}
```

---

### 4.2 登入與行為稽核（Login & Behavior Audit）
#### 4.2.1 單一裝置登入限制
- 規則：同帳號僅允許同時一個有效會話。
- 流程：
  1. 用戶於新裝置登入 → 簽發新 JWT 與 `session_version`；
  2. 伺服器將舊會話標記為失效（強制登出）；
  3. 更新 `last_device_id`、`last_login_at`；
  4. 若 5 分鐘內多次不同裝置切換 → 建立高風險稽核紀錄。
- 即時登出機制：在保留無狀態 JWT 的同時，於伺服器端維護 `token_version` 或 session store。
  - 選項 A（建議）：在 `users.token_version` + JWT 內置 `token_version`，版本不一致即失效。
  - 選項 B：維護 `active_sessions` 表，登入時撤銷舊 session（將其列入黑名單）。

#### 4.2.2 使用者行為紀錄
- 登入、登出、裝置切換。
- 閱讀行為：內容 ID、進入時間、停留秒數（前端定時回報）。
- 後台操作：新增/編輯/刪除會員與內容。
- 內容瀏覽統計（依分類、標籤匯總）。

**API（事件上報）**
```
POST /api/audit/track   # body: { action, target_id, meta }
```

#### 4.2.3 後台監控頁
- 最近登入列表（IP、裝置、地區）。
- 單用戶軌跡查詢（登入、閱讀）。
- 強制某帳號立即登出（遞增 token_version 或撤銷 session）。

---

### 4.3 內容管理（Content Management）
**功能**
- 列表/搜尋（分類、標題、狀態）。
- 新增/編輯：標題、封面、分類、標籤、內容（TipTap/Quill）、狀態（草稿/已發佈/下架）。
- 預覽渲染。
- 軟刪除。

**API**
```
GET    /api/contents
POST   /api/contents
PUT    /api/contents/{id}
DELETE /api/contents/{id}
```

---

### 4.4 分類管理（Category Management）
**功能**
- 列表、排序。
- 新增/編輯/刪除（若有內容則禁止刪除）。

**API**
```
GET    /api/categories
POST   /api/categories
PUT    /api/categories/{id}
DELETE /api/categories/{id}
```

---

### 4.5 後台首頁（Dashboard）
- 概覽：會員數、內容數、發佈趨勢。
- 快速操作：新增內容、檢視最新會員。
- 系統公告：版本紀錄。
- 行為稽核：最近登入與閱讀活動摘要。

---

## 五、資料庫設計（初版）

### 5.1 users
| 欄位 | 型態 | 說明 |
|---|---|---|
| id | UUID | 主鍵 |
| email | VARCHAR(255) | 登入帳號（唯一） |
| name | VARCHAR(255) | 顯示名稱 |
| password_hash | TEXT | 雜湊密碼 |
| role | ENUM('admin','member') | 權限角色 |
| is_active | BOOLEAN | 啟用狀態 |
| last_device_id | VARCHAR(255) | 最近登入裝置 |
| last_login_at | TIMESTAMP | 最近登入時間 |
| token_version | INT | 會話版本（單一裝置控制） |
| force_logout_flag | BOOLEAN | 是否被強制登出 |
| created_at | TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP | 更新時間 |

### 5.2 categories
| 欄位 | 型態 | 說明 |
|---|---|---|
| id | SERIAL | 主鍵 |
| name | VARCHAR(100) | 分類名稱 |
| description | TEXT | 描述 |
| order_index | INT | 排序 |
| created_at | TIMESTAMP | 建立時間 |

### 5.3 contents
| 欄位 | 型態 | 說明 |
|---|---|---|
| id | SERIAL | 主鍵 |
| title | VARCHAR(255) | 標題 |
| slug | VARCHAR(255) | URL slug |
| category_id | INT | 關聯分類 |
| body | TEXT | 內容（HTML/Markdown） |
| status | ENUM('draft','published','archived') | 狀態 |
| author_id | UUID | 作者 |
| created_at | TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP | 更新時間 |

### 5.4 audit_logs
| 欄位 | 型態 | 說明 |
|---|---|---|
| id | SERIAL | 主鍵 |
| user_id | UUID | 觸發者 |
| action | VARCHAR(100) | 行為類型（login/logout/read_content/update_member/...） |
| target_id | VARCHAR(100) | 影響對象（內容 ID、會員 ID） |
| device_info | TEXT | 裝置資訊（UA/硬體指紋） |
| ip_address | VARCHAR(45) | IP |
| created_at | TIMESTAMP | 時間戳 |

### 5.5 active_sessions（選配）
> 若不採 token_version，可採此表維護有效會話與撤銷清單。

| 欄位 | 型態 | 說明 |
|---|---|---|
| id | SERIAL | 主鍵 |
| user_id | UUID | 使用者 |
| device_id | VARCHAR(255) | 裝置指紋 |
| jwt_id | VARCHAR(64) | JWT jti |
| issued_at | TIMESTAMP | 簽發時間 |
| revoked | BOOLEAN | 是否撤銷 |
| revoked_at | TIMESTAMP | 撤銷時間 |

---

## 六、安全設計
- 密碼：`bcrypt` 雜湊；登入暴力嘗試限制（例如 5 分鐘 5 次）。
- JWT：設定 `exp`、`iat`、`jti`；支援 `token_version` 比對或黑名單機制。
- CORS：限制管理後台來源。
- 日誌：後端統一結構化日誌（含 request_id）。
- PII：email/name 僅後台可見；導出報表前需遮罩。

---

## 七、環境變數（.env 範例）
```
APP_ENV=development
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql+psycopg2://admin:password@db:5432/content_db
JWT_EXPIRE_MINUTES=1440
RATE_LIMIT_WINDOW=300
RATE_LIMIT_MAX=5
VITE_API_BASE=http://localhost:8000
```

---

## 八、開發時程（估）
| 週次 | 交付 |
|---|---|
| W1 | Docker 架構、FastAPI skeleton、DB/ORM/Alembic |
| W2 | Auth + Member CRUD、token_version/或 active_sessions |
| W3 | Content/Category CRUD、TipTap 整合、Preview |
| W4 | Audit logs、Dashboard 稽核卡、風險規則 |

---

## 九、交付清單
- `/backend`：FastAPI（models/routers/schemas/auth/migrations）。
- `/frontend`：Vue 3 管理介面（Element Plus）。
- `docker-compose.yml`、`.env.example`。
- 初版 ERD 與 API 文件（OpenAPI 自動生成）。
- 稽核查詢頁（最近 7 天登入/閱讀）。

---

## 十、未來擴充（Phase 2）
- 訂閱與金流、內容權限分層、前台閱讀端、報表分析、通知中心（Email/LINE/Discord）。
