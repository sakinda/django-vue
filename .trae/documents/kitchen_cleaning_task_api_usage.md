# Plan: 清洁任务 API 使用指南与验证

## 目标

说明如何通过 URL 对 `DataKitchenCleaningTask`（清洁任务）进行增删改查操作，并提供简单的验证步骤。

## 步骤

### 1. 确认 API 路由与字段

* **确认路由文件**: [restaurant\_beta\_02/urls.py](file:///Users/user/Documents/Django-project/django-vue/restaurant_beta_02/urls.py)

  * 列表/创建接口: `/kitchencleaningtasklist/`

  * 详情/更新/删除接口: `/kitchencleaningtaskdetail/<pk>/`

* **确认模型字段**: [restaurant\_beta\_02/models.py](file:///Users/user/Documents/Django-project/django-vue/restaurant_beta_02/models.py)

  * 关键字段: `task_name`, `task_manager`, `task_duration`, `task_frequency`, `area` 等。

### 2. API 使用说明

#### 2.1 获取任务列表 (Read List)

* **URL**: `http://<your-domain>/kitchencleaningtasklist/`

* **Method**: `GET`

* **说明**: 获取所有清洁任务的列表。

#### 2.2 创建新任务 (Create)

* **URL**: `http://<your-domain>/kitchencleaningtasklist/`

* **Method**: `POST`

* **Header**: `Content-Type: application/json`

* **Body (示例)**:

  ```json
  {
      "task_name": "清洗排烟罩",
      "task_manager": "张三",
      "task_duration": 60,
      "task_frequency": 7,
      "area": "热厨",
      "task_description": "使用专用清洁剂清洗排烟罩内部油污",
      "task_status": 0
  }
  ```

#### 2.3 获取单个任务详情 (Read Detail)

* **URL**: `http://<your-domain>/kitchencleaningtaskdetail/<task_id>/`

  * 例如: `http://<your-domain>/kitchencleaningtaskdetail/1/`

* **Method**: `GET`

* **说明**: 获取 ID 为 `1` 的任务详情。

#### 2.4 更新任务 (Update)

* **URL**: `http://<your-domain>/kitchencleaningtaskdetail/<task_id>/`

* **Method**: `PUT` (全量更新) 或 `PATCH` (部分更新)

* **Header**: `Content-Type: application/json`

* **Body (示例 - PATCH)**:

  ```json
  {
      "task_status": 1,
      "last_completed_time": "2023-10-27 14:00:00"
  }
  ```

#### 2.5 删除任务 (Delete)

* **URL**: `http://<your-domain>/kitchencleaningtaskdetail/<task_id>/`

* **Method**: `DELETE`

* **说明**: 删除指定 ID 的任务。

### 3. 验证计划 (可选)

* 使用 `curl` 或 Postman 等工具按上述顺序测试接口。

* 检查数据库确认数据变更。

## 下一步

* 用户确认该计划/说明无误后，无需额外代码开发，直接参考上述文档使用即可。

