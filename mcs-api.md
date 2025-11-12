# MCS API 一覽

## Auth
| Method | Path | 說明 |
| --- | --- | --- |
| `POST` | `/api/auth/login` | 使用 email/password 登入，回傳 JWT 與會話資訊 |
| `POST` | `/api/auth/logout` | 使目前 token 失效（遞增 token_version 或加入黑名單） |

## Members
| Method | Path | 說明 |
| --- | --- | --- |
| `GET` | `/api/members` | 會員列表／搜尋／分頁／排序 |
| `POST` | `/api/members` | 新增會員 |
| `PUT` | `/api/members/{id}` | 編輯會員 |
| `DELETE` | `/api/members/{id}` | 軟刪除會員 |

## Contents
| Method | Path | 說明 |
| --- | --- | --- |
| `GET` | `/api/contents` | 內容列表／搜尋（分類、標題、狀態） |
| `POST` | `/api/contents` | 新增內容（含分類、標籤、TipTap/富文字內容、狀態） |
| `PUT` | `/api/contents/{id}` | 編輯內容 |
| `DELETE` | `/api/contents/{id}` | 軟刪除內容 |

## Categories
| Method | Path | 說明 |
| --- | --- | --- |
| `GET` | `/api/categories` | 取得分類列表與排序 |
| `POST` | `/api/categories` | 新增分類 |
| `PUT` | `/api/categories/{id}` | 編輯分類 |
| `DELETE` | `/api/categories/{id}` | 刪除分類（若仍被內容引用則禁止） |

## Audit & Tracking
| Method | Path | 說明 |
| --- | --- | --- |
| `POST` | `/api/audit/track` | 上報行為事件（登入、閱讀、後台操作等），`body: { action, target_id, meta }` |

## Media / Upload
| Method | Path | 說明 |
| --- | --- | --- |
| `POST` | `/api/uploads` | 圖片／媒體上傳，限制 500 KB，成功回傳 `{ id, url, ... }` |
| `GET` | `/api/media` | 媒體檔案列表（檔名、大小、引用次數） |
| `DELETE` | `/api/media/{id}` | 刪除媒體；若仍被內容引用則回傳 400 |
