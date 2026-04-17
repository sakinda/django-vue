# 任务列表

- [x] 任务 1: 实现菜品管理视图
  - [x] 在 `restaurant_beta_02/views.py` 中创建 `DataDishListView` (继承 ListAPIView, CreateAPIView)
  - [x] 在 `restaurant_beta_02/views.py` 中创建 `DataDishDetailView` (继承 RetrieveAPIView, UpdateAPIView, DestroyAPIView)
- [x] 任务 2: 注册菜品管理路由
  - [x] 在 `restaurant_beta_02/urls.py` 中添加 `url('^dishlist/$', ...)`
  - [x] 在 `restaurant_beta_02/urls.py` 中添加 `url('^dishdetail/(?P<pk>.+)/$', ...)`
- [x] 任务 3: 创建 API 文档
  - [x] 在 `.trae/documents/` 中编写 `dish_management_api_reference.md`，描述新增的接口。
