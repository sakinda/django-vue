# 菜品管理 API 参考文档

本文档详细描述了菜品管理系统的前端 API 接口，供前端开发人员参考使用。

## 1. 基础信息

*   **基础 URL**: `/` (相对于服务器根路径)
*   **数据格式**: JSON
*   **字符编码**: UTF-8

## 2. 数据模型 (DataDish)

该模型对应数据库表 `data_dish`。

| 字段名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `did` | Integer | - | **主键**，菜品 ID，自动生成 |
| `dname` | String | 是 | 菜品名称 |
| `dcode` | String | 是 | 菜品代码 (唯一) |
| `dprice` | Decimal | 是 | 价格 |
| `dtax` | Decimal | 是 | 税率 |
| `dcategory` | String | 是 | 类别 |
| `dsubcategory` | Integer | 是 | 子类别 ID (关联 DataDishCategory) |
| `dingredients` | String | 否 | 配料 |
| `drecipe` | String | 否 | 食谱 |
| `dfrname` | String | 否 | 法语名称 |
| `dondelete` | Integer | 否 | 软删除标记 (0: 正常, 1: 删除) |

## 3. 接口详情

### 3.1 获取菜品列表

获取所有菜品的列表。

*   **URL**: `/dishlist/`
*   **Method**: `GET`
*   **参数**: 无

**请求示例**:

```http
GET /dishlist/ HTTP/1.1
```

**响应示例 (200 OK)**:

```json
[
    {
        "did": 1,
        "dname": "宫保鸡丁",
        "dcode": "A001",
        "dprice": "38.00",
        "dtax": "6.00",
        "dcategory": "热菜",
        "dsubcategory": 101,
        "dingredients": "鸡肉, 花生",
        "drecipe": "...",
        "dfrname": "Poulet Kung Pao",
        "dondelete": 0
    },
    ...
]
```

### 3.2 创建新菜品

创建一个新的菜品。

*   **URL**: `/dishlist/`
*   **Method**: `POST`
*   **Content-Type**: `application/json`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `dname` | String | 是 | 菜品名称 |
| `dcode` | String | 是 | 菜品代码 |
| `dprice` | Decimal | 是 | 价格 |
| `dtax` | Decimal | 是 | 税率 |
| `dcategory` | String | 是 | 类别 |
| `dsubcategory` | Integer | 是 | 子类别 ID |
| ... | ... | ... | 其他可选字段 |

**请求示例**:

```json
{
    "dname": "麻婆豆腐",
    "dcode": "A002",
    "dprice": 28.00,
    "dtax": 6.00,
    "dcategory": "热菜",
    "dsubcategory": 101,
    "dfrname": "Mapo Tofu"
}
```

**响应示例 (201 Created)**:

返回创建成功的菜品对象。

### 3.3 获取菜品详情

根据菜品代码获取单个菜品的详细信息。

*   **URL**: `/dishdetail/{dcode}/`
*   **Method**: `GET`
*   **参数**: `dcode` (菜品代码)

**请求示例**:

```http
GET /dishdetail/A001/ HTTP/1.1
```

**响应示例 (200 OK)**:

```json
{
    "did": 1,
    "dname": "宫保鸡丁",
    "dcode": "A001",
    ...
}
```

### 3.4 更新菜品

更新指定菜品的信息。

*   **URL**: `/dishdetail/{dcode}/`
*   **Method**: `PUT` 或 `PATCH`
*   **Content-Type**: `application/json`
*   **参数**: `dcode` (菜品代码)

**请求示例**:

```json
{
    "dprice": 40.00
}
```

**响应示例 (200 OK)**:

返回更新后的完整对象。

### 3.5 删除菜品

删除指定的菜品。

*   **URL**: `/dishdetail/{dcode}/`
*   **Method**: `DELETE`
*   **参数**: `dcode` (菜品代码)

**请求示例**:

```http
DELETE /dishdetail/A001/ HTTP/1.1
```

**响应示例 (204 No Content)**:

无响应体。
