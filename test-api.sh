#!/bin/bash

# API 測試腳本
# 使用方法: ./test-api.sh

API_BASE="http://localhost:8000"
EMAIL="admin@test.com"
PASSWORD="admin123"

echo "=========================================="
echo "  會員制內容管理系統 - API 測試"
echo "=========================================="
echo ""

# 1. 登入獲取 Token
echo "📝 步驟 1: 登入獲取 Token"
echo "----------------------------------------"
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"device_id\":\"test-script\"}")

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ 登入失敗"
    echo "回應: $LOGIN_RESPONSE"
    exit 1
fi

echo "✅ 登入成功！"
echo "Token: ${TOKEN:0:50}..."
echo ""

# 2. 獲取當前用戶信息
echo "📝 步驟 2: 獲取當前用戶信息"
echo "----------------------------------------"
curl -s "$API_BASE/api/auth/me" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 3. 獲取會員列表
echo "📝 步驟 3: 獲取會員列表"
echo "----------------------------------------"
curl -s "$API_BASE/api/members" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 4. 獲取分類列表
echo "📝 步驟 4: 獲取分類列表"
echo "----------------------------------------"
curl -s "$API_BASE/api/categories" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 5. 獲取內容列表
echo "📝 步驟 5: 獲取內容列表"
echo "----------------------------------------"
curl -s "$API_BASE/api/contents" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 6. 獲取儀表板數據
echo "📝 步驟 6: 獲取儀表板數據"
echo "----------------------------------------"
curl -s "$API_BASE/api/dashboard" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=========================================="
echo "  ✅ 所有 API 測試完成！"
echo "=========================================="
echo ""
echo "💡 提示："
echo "  - 登入帳號: $EMAIL"
echo "  - 登入密碼: $PASSWORD"
echo "  - API 文檔: $API_BASE/docs"
echo "  - 前端地址: http://localhost:5173"
echo ""
