# 计划：修正默认日期的时区问题（Wix 订位）

## 问题分析
用户反馈当不传 `date` 参数时，默认的 `target_date = timezone.now().date()` 获取的日期可能与用户所在的 **巴黎时区 (CET/CEST)** 不一致。
Django 的 `timezone.now()` 默认返回 UTC 时间。如果服务器运行在 UTC 时间（如 2026-03-11 23:00 UTC），而巴黎已经是 2026-03-12 00:00，那么获取到的“今天”就是错误的。

## 目标
修改 `WixReservationListView` 中的默认日期逻辑，强制使用 **巴黎时区 (Europe/Paris)** 来计算“今天”的日期。

## 实施步骤

1.  **修改 `restaurant_beta_02/views.py`**
    -   引入 `pytz` 库（如果项目中没有，可能需要使用 `datetime.timezone` 或 Django 的 `timezone` 配合时区字符串）。
    -   将 `target_date` 的获取逻辑修改为：
        ```python
        import pytz
        
        # ...
        
        else:
            # Use Paris timezone for default date
            paris_tz = pytz.timezone('Europe/Paris')
            target_date = timezone.now().astimezone(paris_tz).date()
        ```
    -   确保 `start_of_day` 和 `end_of_day` 的计算仍然生成正确的 UTC ISO 字符串，以便 Wix API 能够正确过滤。
        *注意*：Wix API 需要 UTC 时间。如果我们在巴黎时间 `2026-03-11` 查询，我们需要：
        -   巴黎 `2026-03-11 00:00:00` -> 转换为 UTC
        -   巴黎 `2026-03-12 00:00:00` -> 转换为 UTC

2.  **验证**
    -   再次不传参数调用接口，确认返回的是巴黎时间“今天”的订位数据。

## 关键代码逻辑变更
```python
        else:
            # Set default to Paris time
            paris_tz = pytz.timezone('Europe/Paris')
            now_paris = timezone.now().astimezone(paris_tz)
            target_date = now_paris.date()
        
        # Construct time range (Paris Time -> UTC)
        paris_tz = pytz.timezone('Europe/Paris')
        
        # Start of day in Paris
        start_naive = datetime.datetime.combine(target_date, datetime.time.min)
        start_paris = paris_tz.localize(start_naive)
        start_utc = start_paris.astimezone(pytz.UTC)
        
        # End of day in Paris (Start of next day)
        end_naive = datetime.datetime.combine(target_date + datetime.timedelta(days=1), datetime.time.min)
        end_paris = paris_tz.localize(end_naive)
        end_utc = end_paris.astimezone(pytz.UTC)
        
        start_of_day = start_utc.isoformat().replace('+00:00', 'Z')
        end_of_day = end_utc.isoformat().replace('+00:00', 'Z')
```
