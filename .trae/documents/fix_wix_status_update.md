# 计划：修复 Wix 订位状态更新问题

## 问题分析
用户反馈 `status` 字段无法通过 `patch` 更新，而 `partySize` 等其他字段可以。
根据 Wix API 文档（搜索结果 #1, #2, #4）：
1.  **状态流转限制**：Wix 对状态变更（Lifecycle）有严格控制。例如，不能通过 `Update Reservation` 将状态从 `HELD` 更改为其他状态（需要调用 `Reserve Reservation`）。
2.  **权限要求**：更新 `status` 可能需要更高的权限（如 `MANAGE_RESERVATIONS (FULL)`），而普通更新可能只需要 `MEDIUM` 权限。
3.  **代码遗漏**：当前的 `WixReservationDetailView.patch` 方法中，根本**没有处理 `status` 字段的映射逻辑**。即使前端传了 `status`，后端也没有将其放入 `update_payload` 中。

## 解决方案
我们需要在 `patch` 方法中显式添加对 `status` 字段的处理。

## 实施步骤

1.  **修改 `restaurant_beta_02/views.py`**
    -   在 `WixReservationDetailView.patch` 方法中，检查 `request.data` 是否包含 `status`。
    -   如果包含，将其添加到 `update_payload['reservation']['status']`。
    -   *注意*：虽然 Wix 有状态流转限制，但如果是合法的状态变更（如 `RESERVED` -> `SEATED` 或 `CANCELED`），API 应该允许。

2.  **验证**
    -   通过 `curl` 尝试更新状态（例如从 `RESERVED` 更新为 `SEATED` 或 `CANCELED`）。

## 代码变更预览
```python
        # Top level
        if 'teamMessage' in request.data:
             update_payload['reservation']['teamMessage'] = request.data['teamMessage']
        if 'status' in request.data:
             update_payload['reservation']['status'] = request.data['status']
```
