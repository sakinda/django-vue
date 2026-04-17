# 菜品管理 API 设计方案

## 背景
目前系统缺少专门用于管理（增、删、改、查）菜品数据 (`DataDish`) 的 API 接口。需要新增一个页面用于此目的，因此后端需要提供相应的接口支持。

## 变更内容

### 后端
- **视图 (Views)**:
  - `DataDishListView`: 支持获取所有菜品列表 (`GET`) 和创建新菜品 (`POST`)。
  - `DataDishDetailView`: 支持获取 (`GET`)、更新 (`PUT`/`PATCH`) 和删除 (`DELETE`) 指定菜品。
- **路由 (URLs)**:
  - 添加 `/dishlist/` 对应 `DataDishListView`。
  - 添加 `/dishdetail/(?P<pk>.+)/` 对应 `DataDishDetailView`。

### 前端设计建议 (参考)
- **菜品列表页**:
  - 显示菜品表格，包含名称、代码、价格、类别等列。
  - "新增菜品" 按钮跳转到创建表单。
  - 每行提供 "编辑" 和 "删除" 操作按钮。
- **菜品表单页**:
  - 字段: 菜名 (`dname`)、代码 (`dcode`)、价格 (`dprice`)、税率 (`dtax`)、类别 (`dcategory`)、子类别 (`dsubcategory`)、配料 (`dingredients`)、食谱 (`drecipe`)、法语名 (`dfrname`)。
  - 验证: `dcode` 必须唯一。

## 影响范围
- **受影响文件**:
  - `restaurant_beta_02/views.py`
  - `restaurant_beta_02/urls.py`

## 需求详情

### 需求: 获取菜品列表
- **接口**: `GET /dishlist/`
- **响应**: 所有菜品对象的 JSON 数组。

### 需求: 创建菜品
- **接口**: `POST /dishlist/`
- **请求体**: 包含菜品字段的 JSON 对象。
- **行为**: 创建一条新的 `DataDish` 记录。

### 需求: 获取菜品详情
- **接口**: `GET /dishdetail/{pk}/`
- **响应**: 指定菜品的 JSON 对象。

### 需求: 更新菜品
- **接口**: `PUT /dishdetail/{pk}/` 或 `PATCH /dishdetail/{pk}/`
- **请求体**: 包含更新字段的 JSON 对象。
- **行为**: 更新指定的 `DataDish` 记录。

### 需求: 删除菜品
- **接口**: `DELETE /dishdetail/{pk}/`
- **行为**: 删除指定的 `DataDish` 记录。
