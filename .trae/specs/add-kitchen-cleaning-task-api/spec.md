# Add Kitchen Cleaning Task API Spec

## Why
为了实现前端对厨房清洁任务数据的增删改查操作，需要提供相应的后端API接口。

## What Changes
1.  在 `restaurant_beta_02/views.py` 中新增 `DataKitchenCleaningTaskSerializer`。
2.  在 `restaurant_beta_02/views.py` 中新增 `DataKitchenCleaningTaskListView` (用于列表和创建)。
3.  在 `restaurant_beta_02/views.py` 中新增 `DataKitchenCleaningTaskDetailView` (用于获取详情、更新和删除)。
4.  在 `restaurant_beta_02/urls.py` 中注册路由。

## Impact
- Affected specs: None
- Affected code: `restaurant_beta_02/views.py`, `restaurant_beta_02/urls.py`

## ADDED Requirements
### Requirement: DataKitchenCleaningTask API
The system SHALL provide RESTful APIs for `DataKitchenCleaningTask`.

#### Scenario: List Tasks
- **WHEN** user sends GET request to `/kitchencleaningtasklist/`
- **THEN** return list of all cleaning tasks.

#### Scenario: Create Task
- **WHEN** user sends POST request to `/kitchencleaningtasklist/` with valid data
- **THEN** create a new task and return it.

#### Scenario: Retrieve Task
- **WHEN** user sends GET request to `/kitchencleaningtaskdetail/<pk>/`
- **THEN** return the task details.

#### Scenario: Update Task
- **WHEN** user sends PUT/PATCH request to `/kitchencleaningtaskdetail/<pk>/`
- **THEN** update the task and return updated data.

#### Scenario: Delete Task
- **WHEN** user sends DELETE request to `/kitchencleaningtaskdetail/<pk>/`
- **THEN** delete the task and return 204.
