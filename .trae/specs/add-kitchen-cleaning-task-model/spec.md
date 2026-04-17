# Add Kitchen Cleaning Task Model Spec

## Why
为了管理和记录厨房清洁任务，确保厨房卫生符合标准，需要新增一个数据模型来存储清洁任务的相关信息。

## What Changes
在 `restaurant_beta_02/models.py` 中新增 `DataKitchenCleaningTask` 类。

### DataKitchenCleaningTask 字段设计
- **task_id**: 任务ID (AutoField, Primary Key)
- **task_name**: 任务名称 (CharField, max_length=100)
- **task_manager**: 任务负责人 (CharField, max_length=50) - *新增*
- **task_duration**: 任务时长 (IntegerField, 单位: 分钟)
- **task_frequency**: 任务频率 (IntegerField, 单位: 天, default=1)
- **last_completed_time**: 任务完成时间 (CharField, max_length=32, 允许为空)
- **completion_history**: 任务历史 (TextField, 允许为空, 用于记录最近30次完成时间)

### 补充字段 (Recommended)
为了增强功能，建议增加以下字段：
- **task_description**: 任务描述/步骤 (TextField, 允许为空) - 用于详细说明清洁步骤
- **task_status**: 任务状态 (IntegerField, choices=((0, '待完成'), (1, '已完成')), default=0)
- **area**: 区域 (CharField, max_length=50, 允许为空) - 例如：热厨、冷厨、洗碗间

## Impact
- Affected specs: None
- Affected code: `restaurant_beta_02/models.py`

## ADDED Requirements
### Requirement: DataKitchenCleaningTask Model
The system SHALL provide a `DataKitchenCleaningTask` model with the specified fields.
