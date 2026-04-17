# 计划：关于 Wix Table Reservations API Endpoint 的来源说明

## 来源分析
您询问的 Wix API endpoint 地址 (`https://www.wixapis.com/table-reservations/reservations/v1/reservations/query`) 主要基于以下几个方面确定：

1.  **Wix 官方文档结构**:
    *   Wix 的 REST API 通常遵循 `https://www.wixapis.com/{namespace}/{version}/{resource}` 的模式。
    *   在之前的搜索结果中（如搜索结果 #4 和 #5），虽然文档标题可能是 "Query Reservations" 或 "Introduction"，但其对应的 REST API 路径通常会在文档的 "Endpoint" 部分明确列出。
    *   例如，搜索结果 #4 显示 `POST https://www.wixapis.com/table-reservations/reservations/v1/reservations/query`。

2.  **API 命名空间**:
    *   `table-reservations` 是 Wix Table Reservations 应用的命名空间。
    *   `reservations` 是资源名称。
    *   `v1` 是版本号。

3.  **实际验证与推断**:
    *   在之前的任务中，我们通过 `WIX_BASE_URL` 的配置和实际请求的测试（尽管遇到了 404 和 INVALID_FILTER 等错误），逐步验证了该路径的有效性。
    *   404 错误提示 "meta-site not found" 确认了我们已经到达了 Wix 的服务器，只是 Site ID 或应用安装状态有问题，而不是 Endpoint 本身不存在。
    *   随后的 `INVALID_FILTER` 和 `INVALID_SORT` 错误更是直接证明了 Endpoint 是正确的，因为服务器解析了请求体并返回了具体的业务逻辑错误。

## 结论
该 Endpoint 地址来源于 Wix 官方开发者文档（Wix Developers Documentation - Table Reservations API）中的 REST API 参考部分，并经过了实际请求的错误反馈验证。

## 下一步
无需修改代码，此计划仅作为对您问题的回答。
