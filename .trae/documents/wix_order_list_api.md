# WixOrderList（Wix 在线订单）接口文档

## 基础信息
- Base URL：按部署域名/端口为准
- 接口前缀：`/testwixonlineorders/`
- 数据格式：`application/json`
- 说明：
  - 后端会通过 Wix API `POST https://www.wixapis.com/ecom/v1/orders/search` 拉取订单并进行清洗。
  - 接口支持两类返回：清洗后的订单列表（默认）与原始调试视图（`debug=1`）。

## 路由
- 标准模式（保持现有行为）：`GET /testwixonlineorders/`
- 调试模式（开启日期过滤能力）：`GET /testwixonlineorders/1/`

## Query 参数
通用参数（两个路由都支持）：
- `limit`：integer，可选。单次返回数量上限（后端会限制最大 100）。不传默认 100。
- `cursor`：string，可选。用于 Wix cursor paging（透传给 Wix 搜索接口的 `cursorPaging.cursor`）。
- `debug`：`1|true|True`，可选。开启调试返回结构（返回 rawOrders）。
- `kind`：`order|reserve`，可选。默认 `order`。
  - `order`：普通订单
  - `reserve`：订位类订单（通过 lineItems 名称中是否包含 reservation/订位等关键词判断）

仅在调试路由 `/testwixonlineorders/1/` 下启用：
- `date`：`YYYY-MM-DD`，可选。按 `createdDate` 前缀过滤指定日期的订单。
  - 不传 `date`：不做日期过滤（只多了“可过滤”的能力，默认行为不变）

## 1) 获取清洗后的订单列表（默认）
- Method：GET
- Path：`/testwixonlineorders/`
- Query：
  - `kind`（可选，默认 `order`）
  - `limit`（可选）
  - `cursor`（可选）

### Response 200
返回结构：
- `total`：integer，清洗后订单数量
- `orders`：array，清洗后订单列表

清洗后单条订单字段：
- `id`：string，Wix order id
- `orderNumber`：string|number，Wix order number
- `createdDate`：string，Wix createdDate（ISO 字符串）
- `customerName`：string，从 billingInfo.contactDetails 拼接
- `totalPrice`：string|null，来源 `priceSummary.total.formattedAmount`
- `paymentStatus`：string|null，来源 `paymentStatus`（例：`NOT_PAID` / `PAID`）
- `paidAmount`：string|null，来源 `balanceSummary.paid.amount`（纯数字字符串）
- `balanceAmount`：string|null，来源 `balanceSummary.balance.amount`（纯数字字符串）
- `shippingMethod`：string|null，来源 `shippingInfo.title`
- `items`：array，清洗后的商品项列表

items 字段说明：
- `name`：string，商品名或展开后的 modifier/description 文本
- `quantity`：number
- `code`：string，若文本包含 `[xxx]` 则提取方括号内作为 code，否则为空字符串

示例响应：
```json
{
  "orders": [
    {
      "id": "xxxxxxxx",
      "orderNumber": 10001,
      "createdDate": "2026-03-25T12:34:56.000Z",
      "customerName": "John Doe",
      "totalPrice": "€27.50",
      "paymentStatus": "NOT_PAID",
      "paidAmount": "0",
      "balanceAmount": "27.50",
      "shippingMethod": "Delivery",
      "items": [
        {"name": "NOUILLES [A12]", "quantity": 1, "code": "A12"},
        {"name": "Extra spicy", "quantity": 1, "code": ""}
      ]
    }
  ],
  "total": 1
}
```

### 示例
获取默认（order）清洗列表：
```bash
curl -s "http://127.0.0.1:8000/testwixonlineorders/"
```

获取 reserve（订位类）清洗列表：
```bash
curl -s "http://127.0.0.1:8000/testwixonlineorders/?kind=reserve"
```

指定 limit：
```bash
curl -s "http://127.0.0.1:8000/testwixonlineorders/?limit=50"
```

## 2) 获取原始调试视图（debug=1）
- Method：GET
- Path：`/testwixonlineorders/`
- Query：
  - `debug=1`
  - 可叠加 `kind`、`limit`、`cursor`

### Response 200
返回结构：
- `rawTotal`：integer，从 Wix 拉到的 orders 数量（未清洗前）
- `rawHasShippingInfoCount`：integer，rawOrders 中包含 shippingInfo 的数量（用于观察外卖/配送相关订单比例）
- `rawOrders`：array，调试订单列表（会按 limit 截断）

rawOrders 单条字段（调试用）：
- `id`
- `orderNumber`
- `createdDate`
- `status`
- `paymentStatus`
- `fulfillmentStatus`
- `channelType`
- `kind`：`order|reserve`
- `hasShippingInfo`：boolean
- `hasRecipientInfo`：boolean
- `billingName`
- `recipientName`
- `lineItemNames`：array（最多 5 个）
- `lineItems`：array（最多 10 个；包含 name/quantity/code/modifierLabels/descriptionLines）
- `keyHints`：array（从原始 order keys 中筛出包含 ship/deliver/pickup/fulfill/method 字样的 key）

示例：
```bash
curl -s "http://127.0.0.1:8000/testwixonlineorders/?debug=1&limit=20"
```

## 3) 调试路由：按日期过滤（/1/ + date）
- Method：GET
- Path：`/testwixonlineorders/1/`
- Query：
  - `date=YYYY-MM-DD`（可选）
  - 其他参数同上（`debug`、`kind`、`limit`、`cursor`）

说明：
- 当 `date` 存在时：仅返回 `createdDate` 以该日期开头的订单（字符串前缀匹配）。
- 未传 `date`：与普通路由行为一致（只是在该路由下允许启用日期过滤）。

示例（清洗后结果按日期过滤）：
```bash
curl -s "http://127.0.0.1:8000/testwixonlineorders/1/?date=2026-03-10"
```

示例（调试视图按日期过滤）：
```bash
curl -s "http://127.0.0.1:8000/testwixonlineorders/1/?debug=1&date=2026-03-10&limit=50"
```

## 错误码
- 400 Bad Request
  - `limit` 非整数或 <= 0：
    - `{"error": "Invalid limit. Must be an integer."}`
    - `{"error": "Invalid limit. Must be a positive integer."}`
- 500 Internal Server Error
  - Wix 请求失败或网络异常：`{"error": <details>}`