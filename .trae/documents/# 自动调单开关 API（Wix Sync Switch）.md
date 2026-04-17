# 自动调单开关 API（Wix Sync Switch）

## 基础信息
- Base URL：按部署域名/端口为准
- 接口前缀：`/testwixautosyncswitch/`
- 默认 flag 文件：`/tmp/restaurant_beta_02_wix_sync.enabled`
- 可选配置：`settings.WIX_APSCHEDULER_FLAG_FILE` 可覆盖 flag 文件路径
- 说明：接口会写入/读取 flag 文件；后端 scheduler 每分钟执行前读取开关，从而实现动态开关。

## 1) 查询当前开关状态
- Method：GET
- Path：`/testwixautosyncswitch/`
- Response 200：
  - `enabled`：boolean，当前是否开启自动调单
  - `source`：`file` 或 `settings`，表示本次状态来源（flag 文件优先生效）
  - `flagFile`：flag 文件路径（后端返回便于排查）

示例：
```bash
curl -s http://127.0.0.1:8000/testwixautosyncswitch/
```

## 2) 设置开关状态（开启/关闭）
- Method：POST 或 PATCH（二者等价）
- Path：`/testwixautosyncswitch/`

### 方式 A：JSON Body
- Body：
  - `enabled`: `true` / `false`

示例：
```bash
curl -s -X POST http://127.0.0.1:8000/testwixautosyncswitch/ \
  -H 'Content-Type: application/json' \
  -d '{"enabled": true}'
```

### 方式 B：Query 参数
- Query：
  - `enabled=1` 开启
  - `enabled=0` 关闭

示例：
```bash
curl -s -X POST "http://127.0.0.1:8000/testwixautosyncswitch/?enabled=0"
```

- Response 200：
  - `enabled`：boolean
  - `source`：固定为 `file`
  - `flagFile`：flag 文件路径

- Response 400：
  - `{"error": "enabled must be true/false or 1/0"}`

## 开关优先级规则
- 若 flag 文件存在且内容可识别：以 flag 文件为准（`source=file`）
- 否则：回退到 `settings.WIX_APSCHEDULER_ENABLED`（`source=settings`）