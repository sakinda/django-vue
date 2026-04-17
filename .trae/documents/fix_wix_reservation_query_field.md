# 计划：修正 Wix 订位查询过滤字段

## 问题分析
之前的查询使用了 `startDate` 作为过滤字段，但 Wix API 返回了 `INVALID_FILTER` 错误，提示 `startDate` 是未知字段。
根据 Wix Velo 文档和 API 参考（特别是搜索结果 #3 和 #4），`startDate` 实际上嵌套在 `details` 对象中。

**错误的字段路径**: `startDate`
**正确的字段路径**: `details.startDate`

## 目标
修改 `WixReservationListView` 中的查询构造逻辑，将过滤字段从 `startDate` 更改为 `details.startDate`。

## 实施步骤

1.  **修改 `restaurant_beta_02/views.py`**
    -   定位到 `WixReservationListView` 类。
    -   在构造查询 `body` 时，将 `filter` 和 `sort` 中的 `startDate` 键修改为 `details.startDate`。

    ```python
    body = {
        "query": {
            "filter": {
                "details.startDate": {"$gte": formatted_date}  # 修改此处
            },
            "sort": [{"details.startDate": "ASC"}]  # 修改此处
        }
    }
    ```

2.  **验证**
    -   再次调用接口，确认不再返回 `INVALID_FILTER` 错误。
    -   确认返回的数据已按日期正确过滤和排序。
