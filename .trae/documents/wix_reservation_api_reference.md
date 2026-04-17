# Wix 订位 API 参考文档

本文档详细描述了 Wix 订位功能的后端 API 接口，供前端开发人员调取数据使用。

## 1. 基础信息

*   **基础 URL**: `/` (相对于服务器根路径)
*   **数据格式**: JSON
*   **字符编码**: UTF-8

## 2. 接口详情

### 2.1 获取订位列表 (List)

获取 Wix 平台上的订位列表。支持按日期过滤，默认返回当日（巴黎时间）的所有订位。

*   **URL**: `/wixreservations/`
*   **Method**: `GET`
*   **参数**:
    *   `date` (可选): 查询日期，格式 `YYYY-MM-DD`。如果不传，默认为巴黎时间的“今天”。

**请求示例**:

```http
GET /wixreservations/?date=2026-03-11 HTTP/1.1
```

**响应示例 (200 OK)**:

```json
{
    "reservations": [
        {
            "id": "4096d70d-880b-487f-988f-b185d28a7d6e",
            "status": "RESERVED",
            "source": "ONLINE",
            "details": {
                "reservationLocationId": "38853019-1e11-47bb-af81-7f292682f271",
                "locationId": "38853019-1e11-47bb-af81-7f292682f271",
                "tableIds": [
                    "892fbde2-ce44-49c6-874e-6785f612e384"
                ],
                "tables": {
                    "ids": [
                        "892fbde2-ce44-49c6-874e-6785f612e384"
                    ]
                },
                "startDate": "2026-03-11T11:30:00Z",
                "endDate": "2026-03-11T13:00:00Z",
                "partySize": 2,
                "manualApproval": false
            },
            "reservee": {
                "firstName": "Maité (Nièce de Daniel Florentiny)",
                "lastName": "Leon",
                "email": "mleon1@bbox.fr",
                "phone": "+33666927008",
                "marketingConsent": false,
                "customFields": {
                    "a29b8947-6651-4887-835b-11978291010f": ""
                },
                "contactId": "3f90d1fc-967d-4c96-8901-3a5ab6005def"
            },
            "reservedBy": {
                "contactId": "3f90d1fc-967d-4c96-8901-3a5ab6005def"
            },
            "createdDate": "2026-03-05T13:45:11.805Z",
            "updatedDate": "2026-03-05T13:46:19.697Z",
            "revision": "2",
            "migrationNotes": [],
            "tablesWithReservationConflicts": [],
            "paymentStatus": "FREE"
        },
        {
            "id": "ecdeaa0f-ccfe-4b01-a3a5-ceb62ebcbd3c",
            "status": "RESERVED",
            "source": "ONLINE",
            "details": {
                "reservationLocationId": "38853019-1e11-47bb-af81-7f292682f271",
                "locationId": "38853019-1e11-47bb-af81-7f292682f271",
                "tableIds": [
                    "f195dc4f-0804-4d49-9258-0a9b16f59e1a"
                ],
                "tables": {
                    "ids": [
                        "f195dc4f-0804-4d49-9258-0a9b16f59e1a"
                    ]
                },
                "startDate": "2026-03-11T17:30:00Z",
                "endDate": "2026-03-11T19:00:00Z",
                "partySize": 2,
                "manualApproval": false
            },
            "reservee": {
                "firstName": "Sarah",
                "lastName": "Chabb",
                "email": "sarahchabb@hotmail.fr",
                "phone": "+33609263250",
                "marketingConsent": false,
                "customFields": {
                    "a29b8947-6651-4887-835b-11978291010f": ""
                },
                "contactId": "2a2f09ca-540f-4fff-a793-c05df0fed237"
            },
            "reservedBy": {
                "contactId": "2a2f09ca-540f-4fff-a793-c05df0fed237"
            },
            "createdDate": "2026-03-09T17:10:41.494Z",
            "updatedDate": "2026-03-09T17:10:57.904Z",
            "revision": "2",
            "migrationNotes": [],
            "tablesWithReservationConflicts": [],
            "paymentStatus": "FREE"
        }
    ]
}
```

### 2.2 获取单条订位详情 (Detail)

根据 ID 获取单个订位的详细信息。

*   **URL**: `/wixreservations/{id}/`
*   **Method**: `GET`
*   **参数**: `id` (订位 ID)

**请求示例**:

```http
GET /wixreservations/c240ba90-2cc0-4dc4-8f73-97ddfac6baa7/ HTTP/1.1
```

**响应示例 (200 OK)**:

```json
{
    "reservation": {
        "id": "c240ba90-2cc0-4dc4-8f73-97ddfac6baa7",
        "status": "RESERVED",
        "source": "ONLINE",
        "details": {
            "reservationLocationId": "38853019-1e11-47bb-af81-7f292682f271",
            "locationId": "38853019-1e11-47bb-af81-7f292682f271",
            "tableIds": [
                "892fbde2-ce44-49c6-874e-6785f612e384"
            ],
            "tables": {
                "ids": [
                    "892fbde2-ce44-49c6-874e-6785f612e384"
                ]
            },
            "startDate": "2026-03-11T21:00:00Z",
            "endDate": "2026-03-11T22:30:00Z",
            "partySize": 3,
            "manualApproval": false
        },
        "reservee": {
            "firstName": "测试ZHANG JUN",
            "lastName": "Test",
            "email": "sekinda@hotmail.com",
            "phone": "+33624646090",
            "marketingConsent": false,
            "customFields": {
                "a29b8947-6651-4887-835b-11978291010f": "备注测试"
            },
            "contactId": "b284df9d-697c-458a-91f0-1d5b9fb715ae"
        },
        "reservedBy": {
            "contactId": "b284df9d-697c-458a-91f0-1d5b9fb715ae"
        },
        "teamMessage": "",
        "createdDate": "2026-03-11T00:39:33.721Z",
        "updatedDate": "2026-03-11T01:01:30.410Z",
        "revision": "6",
        "migrationNotes": [],
        "tablesWithReservationConflicts": [],
        "paymentStatus": "FREE"
    }
}
```

### 2.3 更新订位信息 (Update)

更新指定订位的信息。

*   **URL**: `/wixreservations/{id}/`
*   **Method**: `PATCH`
*   **Content-Type**: `application/json`
*   **参数**: `id` (订位 ID)

**支持更新的字段**:

*   `partySize`: 人数
*   `startDate`: 开始时间
*   `endDate`: 结束时间
*   `firstName`: 预订人名
*   `lastName`: 预订人姓
*   `email`: 邮箱
*   `phone`: 电话
*   `teamMessage`: 团队留言/内部备注

**请求示例**:

```json
{
    "partySize": 4,
    "firstName": "张",
    "lastName": "三",
    "teamMessage": "VIP 客户，请安排靠窗位置"
}
```

**响应示例 (200 OK)**:

返回更新后的完整订位对象（结构同 Detail 接口）。

### 2.4 新建订位信息 (Create)

创建一条新的订位记录。该接口会调用 Wix Table Reservations v2 的 create-reservation 能力。

*   **URL**: `/wixreservations/`
*   **Method**: `POST`
*   **Content-Type**: `application/json`

**必填字段**:

*   `partySize`: 人数（正整数）
*   `startDate`: 开始时间（ISO8601，UTC，如 `2026-03-11T19:00:00Z`）
*   `firstName`: 预订人名
*   `phone`: 联系电话

**可选字段**:

*   `lastName`: 预订人姓
*   `email`: 邮箱
*   `teamMessage`: 团队留言/内部备注
*   `status`: 订位状态（不建议在创建时传入，默认由系统设置为 RESERVED 或按 Wix 流程生成）

**请求示例**:

```json
{
  "partySize": 2,
  "startDate": "2026-03-11T19:00:00Z",
  "firstName": "Li",
  "lastName": "Hua",
  "email": "li.hua@example.com",
  "phone": "+33600000000",
  "teamMessage": "周年纪念，尽量靠窗",
  "status": "RESERVED"
}
```

**响应示例 (201 Created)**:

```json
{
  "reservation": {
    "id": "7c3f1d6e-1b2c-4e6a-9a11-2b3c4d5e6f70",
    "status": "RESERVED",
    "source": "ONLINE",
    "details": {
      "reservationLocationId": "38853019-1e11-47bb-af81-7f292682f271",
      "locationId": "38853019-1e11-47bb-af81-7f292682f271",
      "tableIds": [],
      "tables": {
        "ids": []
      },
      "startDate": "2026-03-11T19:00:00Z",
      "endDate": "2026-03-11T20:30:00Z",
      "partySize": 2,
      "manualApproval": false
    },
    "reservee": {
      "firstName": "Li",
      "lastName": "Hua",
      "email": "li.hua@example.com",
      "phone": "+33600000000",
      "marketingConsent": false,
      "customFields": {}
    },
    "reservedBy": {},
    "teamMessage": "周年纪念，尽量靠窗",
    "createdDate": "2026-03-10T18:25:43.511Z",
    "updatedDate": "2026-03-10T18:25:43.511Z",
    "revision": "1",
    "migrationNotes": [],
    "tablesWithReservationConflicts": [],
    "paymentStatus": "FREE"
  }
}
```

**说明**:

* `startDate` 采用 UTC 时间；若以本地（巴黎）时间构建，请先转换为 UTC。
* 若请求未传 `reservationLocationId` / `locationId`，后端会使用站点默认值 `38853019-1e11-47bb-af81-7f292682f271`。
* Wix 可能基于门店配置自动计算 `endDate`（例如 90 分钟时长），无需前端传入。
* 若未指定分配桌台，Wix 可能在后续排台流程中分配或保持为空。
