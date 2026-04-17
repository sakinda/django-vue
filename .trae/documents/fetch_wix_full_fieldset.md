# 计划：获取 Wix 订位详细信息 (Full Fieldset)

## 需求分析
用户希望 `WixReservationDetailView` (以及列表视图) 返回的字段中包含 `firstName`, `lastName` 等预订人信息。
目前这些字段未返回，原因可能是 Wix API 默认只返回部分字段 (BASIC fieldset)。
根据 Wix 文档（搜索结果 #1, #2, #5），获取 `FULL` 字段集（包含 PII 个人身份信息）需要：
1.  **权限**：调用者需要具有 `MANAGE_RESERVATIONS (MEDIUM)` 或 `MANAGE_RESERVATIONS (FULL)` 权限。
2.  **参数**：在请求中明确指定 `fieldsets` 为 `FULL`。

## 实施步骤

1.  **修改 `WixReservationListView.get`**
    -   在 POST `/reservations/query` 的请求体中，添加 `fieldsets: ["FULL"]` 参数。
    -   *注：Query 接口的参数可能略有不同，需尝试 `fieldsets` 或 `fields`。*

2.  **修改 `WixReservationDetailView.get`**
    -   在 GET `/reservations/{id}` 的请求 URL 中，添加查询参数 `?fieldsets=FULL`。

3.  **验证**
    -   调用接口，检查返回的 JSON 中是否包含 `reservee` 对象（其中包含 `firstName`, `lastName`, `phone`, `email`）。

## 代码变更预览

**views.py - List View**
```python
        body = {
            "query": { ... },
            "fieldsets": ["FULL"]  # 尝试添加此字段
        }
```

**views.py - Detail View**
```python
        url = f"{WIX_BASE_URL}/reservations/{pk}?fieldsets=FULL"
```

*注意：如果 API Key 权限不足，可能会返回 403 错误。如果发生这种情况，用户需要去 Wix 开发者中心为该 API Key 增加权限。我们将先假设权限已足够。*
