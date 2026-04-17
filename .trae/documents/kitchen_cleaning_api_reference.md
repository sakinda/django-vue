# 厨房清洁管理系统 API 接口文档

本文档详细描述了厨房清洁管理系统的前端 API 接口，供前端开发人员参考使用。

## 1. 基础信息

*   **基础 URL**: `/` (相对于服务器根路径)
*   **数据格式**: JSON
*   **字符编码**: UTF-8

## 2. 数据模型 (DataKitchenCleaningTask)

该模型对应数据库表 `data_kitchen_cleaning_task`。

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `task_id` | Integer | - | - | **主键**，任务 ID，自动生成 |
| `task_name` | String | 是 | - | 任务名称 (最大长度 100) |
| `task_manager` | String | 是 | - | 任务负责人 (最大长度 50) |
| `task_duration` | Integer | 否 | 0 | 任务时长，单位：分钟 |
| `task_frequency` | Integer | 否 | 1 | 任务频率，单位：天。例如：`1` 代表每天，`7` 代表每周 |
| `last_completed_time` | String | 否 | null | 最近完成时间 (格式建议: YYYY-MM-DD HH:mm:ss) |
| `completion_history` | String | 否 | null | 完成历史记录 (建议存储 JSON 字符串或逗号分隔的时间戳) |
| `task_description` | String | 否 | null | 任务详细描述 |
| `task_status` | Integer | 否 | 0 | 任务状态：`0` (待完成), `1` (已完成) |
| `area` | String | 否 | null | 任务所属区域 (最大长度 50) |

## 3. 接口详情

### 3.1 获取任务列表

获取所有厨房清洁任务的列表。

*   **URL**: `/kitchencleaningtasklist/`
*   **Method**: `GET`
*   **参数**: 无

**请求示例**:

```http
GET /kitchencleaningtasklist/ HTTP/1.1
```

**响应示例 (200 OK)**:

```json
[
    {
        "task_id": 1,
        "task_name": "清洁灶台",
        "task_manager": "张三",
        "task_duration": 30,
        "task_frequency": 1,
        "last_completed_time": "2023-10-27 10:00:00",
        "completion_history": "...",
        "task_description": "清洁所有灶台表面及油污",
        "task_status": 0,
        "area": "热厨区"
    },
    {
        "task_id": 2,
        "task_name": "清洁冰箱",
        "task_manager": "李四",
        "task_duration": 45,
        "task_frequency": 7,
        "last_completed_time": null,
        "completion_history": null,
        "task_description": "清理过期食物，擦拭隔板",
        "task_status": 0,
        "area": "冷厨区"
    }
]
```

### 3.2 创建新任务

创建一个新的清洁任务。

*   **URL**: `/kitchencleaningtasklist/`
*   **Method**: `POST`
*   **Content-Type**: `application/json`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `task_name` | String | 是 | 任务名称 |
| `task_manager` | String | 是 | 任务负责人 |
| `task_duration` | Integer | 否 | 任务时长(分钟) |
| `task_frequency` | Integer | 否 | 任务频率(天) |
| `task_description` | String | 否 | 任务描述 |
| `area` | String | 否 | 区域 |

**请求示例**:

```json
{
    "task_name": "深度清洁烤箱",
    "task_manager": "王五",
    "task_duration": 60,
    "task_frequency": 7,
    "task_description": "使用专用清洁剂清洁烤箱内部",
    "area": "烘焙区"
}
```

**响应示例 (201 Created)**:

```json
{
    "task_id": 3,
    "task_name": "深度清洁烤箱",
    "task_manager": "王五",
    "task_duration": 60,
    "task_frequency": 7,
    "last_completed_time": null,
    "completion_history": null,
    "task_description": "使用专用清洁剂清洁烤箱内部",
    "task_status": 0,
    "area": "烘焙区"
}
```

### 3.3 获取任务详情

根据 ID 获取单个任务的详细信息。

*   **URL**: `/kitchencleaningtaskdetail/{id}/`
*   **Method**: `GET`
*   **参数**: `id` (任务 ID)

**请求示例**:

```http
GET /kitchencleaningtaskdetail/1/ HTTP/1.1
```

**响应示例 (200 OK)**:

```json
{
    "task_id": 1,
    "task_name": "清洁灶台",
    "task_manager": "张三",
    ...
}
```

### 3.4 更新任务

更新指定任务的信息（支持全量更新 PUT 或部分更新 PATCH）。

*   **URL**: `/kitchencleaningtaskdetail/{id}/`
*   **Method**: `PUT` 或 `PATCH`
*   **Content-Type**: `application/json`
*   **参数**: `id` (任务 ID)

**场景示例：标记任务为已完成**

```json
{
    "task_status": 1,
    "last_completed_time": "2023-10-28 14:00:00"
}
```

**响应示例 (200 OK)**:

返回更新后的完整对象。

### 3.5 删除任务

删除指定的任务。

*   **URL**: `/kitchencleaningtaskdetail/{id}/`
*   **Method**: `DELETE`
*   **参数**: `id` (任务 ID)

**请求示例**:

```http
DELETE /kitchencleaningtaskdetail/1/ HTTP/1.1
```

**响应示例 (204 No Content)**:

无响应体。
