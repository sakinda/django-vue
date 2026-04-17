# 计划：更新 Wix 订位人数 (Party Size)

## 需求
根据 Wix API 文档 (`update-reservation`)，将指定 ID (`c240ba90-2cc0-4dc4-8f73-97ddfac6baa7`) 的订位人数 (`partySize`) 修改为 3。

## API 分析
根据提供的 Wix Velo 文档，`updateReservation` 接受以下参数：
- `reservationId`: 订位 ID。
- `reservation`: 包含需要更新的字段的对象。
- `options`: 可选参数（如忽略冲突）。

在 REST API 中，这通常对应 `PATCH` 请求。
**Endpoint**: `PATCH /reservations/{reservationId}`
**Body**:
```json
{
  "reservation": {
    "details": {
      "partySize": 3
    },
    "revision": "<current_revision_number>" 
  }
}
```
*注意*：Wix 更新通常需要提供 `revision` 字段以进行乐观锁控制。如果未提供，API 可能会拒绝更新。我们需要先获取当前的 `revision`，或者尝试不带 revision 发送（取决于 API 的严格程度）。为保险起见，建议先获取详情拿到 revision 再更新。

## 实施步骤

1.  **实现 `patch` 方法**：在 `WixReservationDetailView` 中添加 `patch` 方法。
2.  **获取当前 Revision**：在更新前，先调用 `GET` 获取该订位的最新 `revision` 号。
3.  **构造更新请求**：
    -   URL: `f"{WIX_BASE_URL}/reservations/{pk}"`
    -   Method: `PATCH`
    -   Headers: 包含 `Authorization` 和 `wix-site-id`。
    -   Body:
        ```json
        {
          "reservation": {
            "details": {
              "partySize": 3
            },
            "revision": current_revision
          }
        }
        ```
    *注：为了通用性，`patch` 方法将接收前端传递的 `partySize`，默认为 3 (针对此任务)。*

## 临时验证脚本 (针对特定 ID)
由于这是一个一次性任务（"把这个id...改为3"），我将编写一个临时的 Python 脚本来执行此操作，而不是硬编码到视图中。或者，更合理的方式是完善 `WixReservationDetailView.patch` 方法，然后通过 `curl` 调用它。

**方案选择**：完善 `WixReservationDetailView` 的 `patch` 功能，使其支持通用的更新操作，然后指导用户使用 `curl` 发送请求。

### 修改 `restaurant_beta_02/views.py`

```python
    def patch(self, request, pk):
        url = f"{WIX_BASE_URL}/reservations/{pk}"
        headers = {
            "Authorization": WIX_API_KEY,
            "wix-site-id": WIX_SITE_ID,
            "Content-Type": "application/json"
        }
        
        # 1. Get current reservation to get the revision
        try:
            get_response = requests.get(url, headers=headers)
            get_response.raise_for_status()
            current_data = get_response.json()
            # Handle different response structures (root object vs nested 'reservation')
            reservation_data = current_data.get('reservation', current_data) 
            current_revision = reservation_data.get('revision')
        except Exception as e:
            return Response({"error": f"Failed to fetch current revision: {str(e)}"}, status=500)

        # 2. Prepare update body
        # Allow updating other fields from request.data, but merge with partySize=3 requirement
        update_payload = {
            "reservation": {
                "revision": current_revision,
                "details": {}
            }
        }
        
        if 'partySize' in request.data:
             update_payload['reservation']['details']['partySize'] = request.data['partySize']
        
        # For this specific task, if no body provided, force partySize=3? 
        # Better to just support standard PATCH and let user send {"partySize": 3}
        
        # 3. Send PATCH request
        try:
            response = requests.patch(url, headers=headers, json=update_payload)
            response.raise_for_status()
            return Response(response.json())
        except requests.exceptions.RequestException as e:
            # ... error handling ...
```

**执行计划**:
1.  完善 `WixReservationDetailView` 的 `patch` 方法。
2.  使用 `curl` 命令发送 PATCH 请求，将 ID `c240ba90-2cc0-4dc4-8f73-97ddfac6baa7` 的 `partySize` 改为 3。
