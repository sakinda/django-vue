# 计划：Wix 订位排序修正

## 问题分析
根据 Wix API 返回的错误 `INVALID_SORT: Sorting by an object value is not supported`，说明 `details.startDate` 虽然支持过滤（如搜索结果 #1 和 #3 所示），但可能不支持直接作为排序字段，或者该字段被视为复杂对象而非标量值。

搜索结果 #1 的表格中显示 `details.startDate` 是支持 Filter 和 Sort 的。这表明理论上应该是支持的，但可能存在 API 版本的差异，或者特定的 API 端点 (`query`) 对排序有更严格的限制。

另一种可能性是，我们需要使用一级字段进行排序。搜索结果 #1 中列出了 `createdDate` 和 `updatedDate` 是支持排序的。虽然它们不是预订开始时间，但在某些场景下可以作为替代。

**然而，最可能的解决方案是：** Wix V2 API 可能有变动，或者我们在使用 V1 API 时遇到了未记录的限制。
尝试移除排序字段，或者改用其他字段排序。

考虑到用户希望获取“今日起”的数据，过滤条件是必须的。排序虽然重要，但如果导致报错，可以先在应用层（Python 代码）中进行排序。

## 目标
1.  **保留过滤条件**：`details.startDate` 的过滤是核心需求。
2.  **移除 API 排序**：暂时从 Wix API 请求中移除 `sort` 字段，避免报错。
3.  **应用层排序**：在获取到 Wix 数据后，使用 Python 对结果列表按 `details.startDate` 进行排序。

## 实施步骤

1.  **修改 `restaurant_beta_02/views.py`**
    -   在 `WixReservationListView` 中，从 `body` 中移除 `sort` 字段。
    -   在获取到 `response.json()` 后，解析出预订列表。
    -   使用 Python 的 `sort` 或 `sorted` 函数，根据 `reservation['details']['startDate']` 对列表进行排序。
    -   返回排序后的数据。

    ```python
    # 移除 sort
    body = {
        "query": {
            "filter": {
                "details.startDate": {"$gte": formatted_date}
            }
        }
    }
    
    # ... 请求 Wix API ...
    
    data = response.json()
    if 'reservations' in data:
        data['reservations'].sort(key=lambda x: x.get('details', {}).get('startDate', ''))
    
    return Response(data)
    ```

2.  **验证**
    -   确认不再返回 `INVALID_SORT` 错误。
    -   确认返回的数据已按时间顺序排列。
