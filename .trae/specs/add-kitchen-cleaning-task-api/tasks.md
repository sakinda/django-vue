# Tasks

- [x] Task 1: Create Serializer for DataKitchenCleaningTask
  - [x] SubTask 1.1: In `restaurant_beta_02/views.py`, define `DataKitchenCleaningTaskSerializer` inheriting from `serializers.ModelSerializer`.
  - [x] SubTask 1.2: Include all fields (`__all__`).

- [x] Task 2: Create Views for DataKitchenCleaningTask
  - [x] SubTask 2.1: In `restaurant_beta_02/views.py`, define `DataKitchenCleaningTaskListView` inheriting from `ListAPIView` and `CreateAPIView`.
  - [x] SubTask 2.2: Define `DataKitchenCleaningTaskDetailView` inheriting from `RetrieveAPIView`, `UpdateAPIView`, and `DestroyAPIView`.
  - [x] SubTask 2.3: Set `queryset` and `serializer_class` for both views.

- [x] Task 3: Add URLs for DataKitchenCleaningTask
  - [x] SubTask 3.1: In `restaurant_beta_02/urls.py`, import the new views.
  - [x] SubTask 3.2: Add URL pattern `^kitchencleaningtasklist/$` for `DataKitchenCleaningTaskListView`.
  - [x] SubTask 3.3: Add URL pattern `^kitchencleaningtaskdetail/(?P<pk>.+)/$` for `DataKitchenCleaningTaskDetailView`.
