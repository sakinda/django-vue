# 计划：增强 Wix 订位更新功能

## 需求
扩展 `WixReservationDetailView` 的 `patch` 方法，使其支持更新更多字段，而不仅仅是 `partySize`。
支持的字段包括：
- `partySize` (人数)
- `startDate` (订位开始时间)
- `firstName`, `lastName`, `email`, `phone` (预订人信息)
- `teamMessage` (团队留言/内部备注)

## 数据结构映射
根据用户提供的 JSON 模板，各字段在请求体中的位置如下：

1.  **顶层字段**:
    -   `teamMessage` -> `reservation.teamMessage`

2.  **Details 对象**:
    -   `partySize` -> `reservation.details.partySize`
    -   `startDate` -> `reservation.details.startDate`
    -   `endDate` -> `reservation.details.endDate` (通常随 startDate 自动调整或需要同时传递)

3.  **Reservee 对象**:
    -   `firstName` -> `reservation.reservee.firstName`
    -   `lastName` -> `reservation.reservee.lastName`
    -   `email` -> `reservation.reservee.email`
    -   `phone` -> `reservation.reservee.phone`

## 实施步骤

1.  **修改 `restaurant_beta_02/views.py`**
    -   在 `patch` 方法中，保留获取 `revision` 的逻辑。
    -   初始化 `update_payload` 结构，确保包含 `details` 和 `reservee` 的空字典。
    -   遍历 `request.data`，根据字段名将值填充到 `update_payload` 的正确位置。
        -   如果是 `startDate`，可能需要同时处理 `endDate`（或者假设 Wix 会自动处理时长，如果只传 startDate）。为安全起见，我们暂时只透传用户给定的字段。
    -   发送 PATCH 请求。

2.  **验证**
    -   通过 `curl` 测试更新不同字段，例如同时更新 `firstName` 和 `partySize`。

## 代码逻辑预览
```python
        # Initialize structure
        update_payload = {
            "reservation": {
                "revision": current_revision,
                "details": {},
                "reservee": {}
            }
        }
        
        # Map request fields to Wix structure
        # Details
        if 'partySize' in request.data:
             update_payload['reservation']['details']['partySize'] = request.data['partySize']
        if 'startDate' in request.data:
             update_payload['reservation']['details']['startDate'] = request.data['startDate']
        if 'endDate' in request.data:
             update_payload['reservation']['details']['endDate'] = request.data['endDate']
             
        # Reservee
        if 'firstName' in request.data:
             update_payload['reservation']['reservee']['firstName'] = request.data['firstName']
        if 'lastName' in request.data:
             update_payload['reservation']['reservee']['lastName'] = request.data['lastName']
        if 'email' in request.data:
             update_payload['reservation']['reservee']['email'] = request.data['email']
        if 'phone' in request.data:
             update_payload['reservation']['reservee']['phone'] = request.data['phone']

        # Top level
        if 'teamMessage' in request.data:
             update_payload['reservation']['teamMessage'] = request.data['teamMessage']

        # Cleanup empty objects to avoid sending empty patches which might be rejected or ignored
        if not update_payload['reservation']['details']:
            del update_payload['reservation']['details']
        if not update_payload['reservation']['reservee']:
            del update_payload['reservation']['reservee']
```
