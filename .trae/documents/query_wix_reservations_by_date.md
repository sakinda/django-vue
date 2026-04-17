# 计划：Wix 订位精确日期查询

## 需求变更
用户希望从“获取今日起”改为“获取指定日期”的订位列表。
例如：查询 `2026-03-11` 当天的所有订位。

## 现状分析
当前的 `WixReservationListView` 使用 `details.startDate` 大于等于 (`$gte`) 今日零点作为过滤条件。
为了查询特定的一天，我们需要构造一个时间范围：
- **开始时间**: 该日期的 00:00:00
- **结束时间**: 该日期的 23:59:59 (或次日 00:00:00)

## 实施步骤

1.  **修改 `restaurant_beta_02/views.py`**
    -   在 `WixReservationListView.get` 方法中，接收前端传递的查询参数 `date` (格式 YYYY-MM-DD)。
    -   如果前端未提供 `date`，则默认为当天。
    -   根据 `date` 计算出 `start_of_day` 和 `end_of_day`。
    -   更新 Wix Query 的 `filter`，使用 `$gte` (大于等于开始时间) 和 `$lt` (小于次日零点) 组合条件。

    ```python
    # 获取日期参数
    target_date_str = request.query_params.get('date')
    if target_date_str:
        target_date = datetime.datetime.strptime(target_date_str, '%Y-%m-%d').date()
    else:
        target_date = timezone.now().date()

    # 构造时间范围
    start_of_day = datetime.datetime.combine(target_date, datetime.time.min).isoformat() + "Z"
    # 次日零点作为结束界限
    end_of_day = datetime.datetime.combine(target_date + datetime.timedelta(days=1), datetime.time.min).isoformat() + "Z"

    # 构造 Query Body
    body = {
        "query": {
            "filter": {
                "$and": [
                    {"details.startDate": {"$gte": start_of_day}},
                    {"details.startDate": {"$lt": end_of_day}}
                ]
            }
        }
    }
    ```

2.  **验证**
    -   调用 `/wixreservations/?date=2026-03-11`，确认只返回该日期的订位。
    -   不传参数调用，确认返回当天的订位。
