# 修复 Wix 在线订单只调取到一条数据的问题计划

## 问题分析
当前 `WixOnlineOrdersView` 接口在向 Wix API (`/ecom/v1/orders/search`) 发起 POST 请求时，没有显式指定**排序方式 (Sort)** 和**单次获取的最大数量 (Limit)**。
Wix API 默认可能会按照最早的时间正序返回，且默认限制通常为 50 条。由于店铺有大量的“订位订单”与“在线订单”混合在一起，如果不按照最新时间倒序拉取，很可能拉取到的前 50 条数据中只有 1 条是包含 `shippingInfo` 的早期在线订单（或者只包含了某一次测试订单），而后续的新在线订单都被分页截断了。

## 解决步骤
1. **增加时间倒序排序 (Sort)**：
   修改 `WixOnlineOrdersView` 中的请求体 (body)，加入按 `createdDate` 降序排列的参数，确保每次拉取到的都是**最新**的订单。
   ```json
   {
       "sort": [{"fieldName": "createdDate", "order": "DESC"}]
   }
   ```
2. **增大默认拉取数量 (Limit)**：
   如果前端没有传入 `limit` 参数，后端默认将 `limit` 设置为 100（Wix 允许的最大单页限制），尽可能多地在一次请求中覆盖更多的订单。
3. **优化 Payload 结构**：
   调整代码中的 `body` 构建逻辑，整合 `sort` 和 `paging` 参数：
   ```python
   body = {
       "sort": [{"fieldName": "createdDate", "order": "DESC"}],
       "paging": {
           "limit": int(limit) if limit else 100,
           "offset": int(offset) if offset else 0
       }
   }
   ```
4. **验证结果**：
   应用代码修改后，通过后端 `curl` 或在前端页面刷新，确认是否能成功拉取到多条最新的在线外卖/自提订单。

## 预期结果
修改后，接口将首先获取最新的 100 条订单，经过 `shippingInfo` 字段过滤后，能够正确返回所有近期的真实在线订单（排除订位订单）。