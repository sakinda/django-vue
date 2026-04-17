# Wix 订位功能后端接口方案

## 背景
用户需要通过 Django 后端与 Wix 平台进行 API 连接，获取订位数据，并以 RESTful 接口的形式暴露给前端（Vue2）。

## 变更内容

### 后端
1.  **新增视图 (`restaurant_beta_02/views.py`)**:
    *   在视图中直接集成 Wix API 调用逻辑（使用 `requests` 库）。
    *   配置 Wix API Key 和 Site ID（建议作为常量或配置项）。
    *   **`WixReservationListView`**:
        *   `GET /wix/reservations/`: 获取 Wix 预订列表。
        *   `POST /wix/reservations/`: 创建新的 Wix 预订。
    *   **`WixReservationDetailView`**:
        *   `GET /wix/reservations/{id}/`: 获取单条预订详情。
        *   `PATCH /wix/reservations/{id}/`: 更新预订信息。
        *   `DELETE /wix/reservations/{id}/`: 取消预订。

2.  **新增路由 (`restaurant_beta_02/urls.py`)**:
    *   `/wix/reservations/` -> `WixReservationListView`
    *   `/wix/reservations/(?P<reservation_id>.+)/` -> `WixReservationDetailView`

## 影响范围
*   修改文件: `restaurant_beta_02/views.py`, `restaurant_beta_02/urls.py`

## 需求详情

### 需求: 获取预订列表 (List)
*   **接口**: `GET /wix/reservations/`
*   **行为**: 后端向 Wix API 发起 GET 请求，获取预订列表，并将结果以 JSON 格式返回给前端。

### 需求: 创建预订 (Create)
*   **接口**: `POST /wix/reservations/`
*   **行为**: 后端接收前端 JSON 数据，透传给 Wix API 创建预订，并返回 Wix 的响应。

### 需求: 获取预订详情 (Retrieve)
*   **接口**: `GET /wix/reservations/{reservation_id}/`
*   **行为**: 后端向 Wix API 发起 GET 请求，获取指定 ID 的预订详情。

### 需求: 更新预订 (Update)
*   **接口**: `PATCH /wix/reservations/{reservation_id}/`
*   **行为**: 后端接收前端更新数据，调用 Wix API 更新预订状态或详情。

### 需求: 取消预订 (Delete)
*   **接口**: `DELETE /wix/reservations/{reservation_id}/`
*   **行为**: 后端调用 Wix API 取消该预订。

## API 配置
*   **Base URL**: `https://www.wixapis.com/table-reservations/v1` (暂定)
*   **Headers**:
    *   `Authorization`: `<API-KEY>`
    *   `wix-site-id`: `<SITE-ID>`
