# 备注增删改查 API 文档

## 基本信息
- 基础路径: `http://<host>:<port>/`
- 接口前缀: 无
- 数据格式: `Content-Type: application/json`

## 数据模型
- 字段
  - `id` (integer, 主键)
  - `note_category_id` (integer)
  - `note_category` (string, max 20)
  - `note_content` (string, max 250)
  - `max` (integer, 默认 0)
- 说明
  - 当前模型使用手动指定 `id` 作为主键，创建时需提供未占用的 `id`

## 接口列表

### 1. 获取备注列表
- 方法: GET  
- 路径: `/testbasenote/`
- 响应: 200 OK
- 响应示例:
```json
[
  {
    "id": 1,
    "note_category_id": 1,
    "note_category": "无",
    "note_content": "无备注",
    "max": 0
  }
]
```

### 2. 新增备注
- 方法: POST  
- 路径: `/testbasenote/`
- 请求体:
```json
{
  "id": 999001,
  "note_category_id": 1,
  "note_category": "口味",
  "note_content": "微辣",
  "max": 0
}
```
- 响应: 201 Created 或 200 OK（按 DRF 配置返回）
- 响应示例:
```json
{
  "id": 999001,
  "note_category_id": 1,
  "note_category": "口味",
  "note_content": "微辣",
  "max": 0
}
```

### 3. 获取备注详情
- 方法: GET  
- 路径: `/testbasenote/{id}/`
- 路径参数:
  - `id`: integer
- 响应: 200 OK
- 响应示例:
```json
{
  "id": 999001,
  "note_category_id": 1,
  "note_category": "口味",
  "note_content": "微辣",
  "max": 0
}
```

### 4. 更新备注
- 方法: PATCH  
- 路径: `/testbasenote/{id}/`
- 路径参数:
  - `id`: integer
- 请求体（部分字段可选，支持局部更新）:
```json
{
  "note_content": "微辣（少油少盐）"
}
```
- 响应: 200 OK
- 响应示例:
```json
{
  "id": 999001,
  "note_category_id": 1,
  "note_category": "口味",
  "note_content": "微辣（少油少盐）",
  "max": 0
}
```

### 5. 删除备注
- 方法: DELETE  
- 路径: `/testbasenote/{id}/`
- 路径参数:
  - `id`: integer
- 响应: 204 No Content

## 错误码
- 400 Bad Request: 请求体校验失败
- 404 Not Found: `id` 不存在
- 500 Internal Server Error: 服务器内部错误

## Curl 示例

获取列表:
```bash
curl -s http://127.0.0.1:8000/testbasenote/
```

新增备注:
```bash
curl -X POST http://127.0.0.1:8000/testbasenote/ \
  -H "Content-Type: application/json" \
  -d '{"id":999001,"note_category_id":1,"note_category":"口味","note_content":"微辣","max":0}'
```

查询详情:
```bash
curl -s http://127.0.0.1:8000/testbasenote/999001/
```

更新备注:
```bash
curl -X PATCH http://127.0.0.1:8000/testbasenote/999001/ \
  -H "Content-Type: application/json" \
  -d '{"note_content":"微辣（少油少盐）"}'
```

删除备注:
```bash
curl -X DELETE http://127.0.0.1:8000/testbasenote/999001/
```
