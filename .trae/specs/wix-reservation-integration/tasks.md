# 任务列表

- [x] Task 1: 实现 Wix 预订视图
  - [x] 在 `restaurant_beta_02/views.py` 中定义 Wix API 配置（API Key, Site ID, Base URL）。
  - [x] 实现 `WixReservationListView` (继承 `APIView`)：
    - [x] `get`: 调用 Wix List API，返回 JSON。
    - [x] `post`: 调用 Wix Create API，返回 JSON。
  - [x] 实现 `WixReservationDetailView` (继承 `APIView`)：
    - [x] `get`: 调用 Wix Get API，返回 JSON。
    - [x] `patch`: 调用 Wix Update API，返回 JSON。
    - [x] `delete`: 调用 Wix Cancel API，返回 JSON。

- [x] Task 2: 注册 Wix 路由
  - [x] 在 `restaurant_beta_02/urls.py` 中添加 `/wix/reservations/` 和 `/wix/reservations/(?P<reservation_id>.+)/` 路由。

- [x] Task 3: 创建 API 文档
  - [x] 在 `.trae/documents/` 下创建 `wix_reservation_api_reference.md`，记录 RESTful 接口使用方法。
