# 计划：将菜品详情查询字段改为 dcode

## 现状分析
当前 `DataDishDetailView` 使用 Django REST Framework 的默认配置，默认的 `lookup_field` 是 `pk`。
在 `DataDish` 模型中：
- `did` 是主键 (`primary_key=True`)。
- `dcode` 是唯一键 (`unique=True`)。

因此，**当前接口使用的是 `did` (数据库自增 ID)，而不是 `dcode`**。

## 目标
将菜品详情接口 (`/dishdetail/...`) 的查询字段从 `did` 改为 `dcode` (菜品代码)，以便前端可以通过菜品代码直接进行增删改查，这在业务上通常更直观。

## 实施步骤

1.  **修改视图 (`views.py`)**
    - 在 `DataDishDetailView` 类中设置 `lookup_field = 'dcode'`。

2.  **修改路由 (`urls.py`)**
    - 将路由规则从 `^dishdetail/(?P<pk>.+)/$` 修改为 `^dishdetail/(?P<dcode>.+)/$`。

3.  **更新文档 (`dish_management_api_reference.md`)**
    - 更新 API 文档中的 URL 参数说明，将 `id` / `did` 替换为 `dcode`。
    - 更新请求示例中的 URL。

## 验证
- 确认可以通过 `/dishdetail/A001/` 这样的 URL 访问到菜品详情。
