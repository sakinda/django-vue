# 计划：整理并交付后端订位接口文档

## 目标
根据您的要求，我将整理一份完整的后端订位信息接口 API 文档，供前端开发人员调取数据使用。
为了提供更规范的接口，我将先把当前的测试路由 `/testwixreservations/` 重命名为正式路由 `/wixreservations/`。

## 现状
1.  **路由**: 目前在 `urls.py` 中定义为 `/testwixreservations/`。
2.  **功能**:
    -   **列表 (List)**: 支持按日期查询 (`?date=YYYY-MM-DD`)，默认返回巴黎时间“今天”的订位。已包含完整字段（如 `firstName`）。
    -   **详情 (Detail)**: 支持获取单个订位详情。
    -   **更新 (Update)**: 支持更新 `partySize`, `startDate`, `firstName`, `lastName`, `email`, `phone`, `teamMessage` 等字段。

## 实施步骤

1.  **优化路由 (`restaurant_beta_02/urls.py`)**
    -   将 `^testwixreservations/$` 修改为 `^wixreservations/$`。
    -   将 `^testwixreservations/(?P<pk>.+)/$` 修改为 `^wixreservations/(?P<pk>.+)/$`。

2.  **生成接口文档 (`.trae/documents/wix_reservation_api_reference.md`)**
    -   **接口 1: 获取订位列表**
        -   URL: `/wixreservations/`
        -   Method: `GET`
        -   参数: `date` (可选, 默认今日)
        -   响应示例: 使用用户提供的 **订单列表示例**。
    -   **接口 2: 获取单条订位**
        -   URL: `/wixreservations/{id}/`
        -   Method: `GET`
        -   响应示例: 使用用户提供的 **订单详情示例**。
    -   **接口 3: 更新订位信息**
        -   URL: `/wixreservations/{id}/`
        -   Method: `PATCH`
        -   Body 参数说明: `partySize`, `firstName`, `lastName`, `teamMessage` 等。

## 交付物
-   更新后的 `urls.py` 代码。
-   `wix_reservation_api_reference.md` 文档文件（包含详细的 JSON 示例）。
