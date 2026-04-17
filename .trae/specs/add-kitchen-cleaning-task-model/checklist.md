# Checklist

- [x] DataKitchenCleaningTask class exists in `restaurant_beta_02/models.py`
- [x] Field `task_id` is defined as AutoField
- [x] Field `task_name` is defined as CharField
- [x] Field `task_manager` is defined as CharField
- [x] Field `task_duration` is defined as IntegerField
- [x] Field `task_frequency` is defined as IntegerField with default=1
- [x] Field `last_completed_time` is defined as CharField
- [x] Field `completion_history` is defined as TextField
- [x] Field `task_description` is defined as TextField (if implemented)
- [x] Field `task_status` is defined as IntegerField (if implemented)
- [x] Field `area` is defined as CharField (if implemented)
- [x] Meta class is defined with `db_table='data_kitchen_cleaning_task'` and `verbose_name='厨房清洁任务'`
- [x] `__str__` method returns a string representation of the task (e.g., name or id)
