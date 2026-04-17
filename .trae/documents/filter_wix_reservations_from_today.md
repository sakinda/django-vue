# 计划：Wix 订位数据过滤（仅获取今日起）

## 现状分析
当前 `WixReservationListView` 使用空的查询对象 (`"query": {}`)，因此 Wix API 返回所有历史和未来的预订记录。

## 目标
修改 `WixReservationListView` 的查询逻辑，使其只返回 `startDate` 大于或等于当前时间（或今日零点）的预订数据。

## 实施步骤

1.  **修改 `restaurant_beta_02/views.py`**
    -   在 `WixReservationListView.get` 方法中，动态生成当前日期的 ISO 格式字符串。
    -   构造 Wix Query 对象的 `filter` 字段。
    -   根据 Wix API 文档（通常遵循 Google AIP 过滤标准或 Wix 自定义查询语法），设置 `startDate` 的过滤条件。

    *注：假设 Wix Query API 支持如下结构（需根据标准 Wix Data Query 适配）：*
    ```json
    {
      "query": {
        "filter": {
          "startDate": { "$gte": "2023-10-27T00:00:00.000Z" }
        },
        "sort": [ { "startDate": "ASC" } ]
      }
    }
    ```

2.  **验证**
    -   确保生成的日期格式符合 Wix 要求（ISO 8601 UTC）。
    -   确保接口返回的数据不再包含过去日期的预订。

## 关键代码逻辑
```python
from django.utils import timezone
import datetime

# 获取今日零点（UTC）
now = timezone.now()
today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
formatted_date = today_start.isoformat()

# 构造 Query Body
body = {
    "query": {
        "filter": {
            "startDate": { "$gte": formatted_date }
        },
        "sort": [{"startDate": "ASC"}]
    }
}
```
