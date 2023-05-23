from django.conf.urls import url
from django.views.generic import TemplateView

from restaurant_beta_02 import views

urlpatterns = [
    url('^index/$', TemplateView.as_view(template_name="index.html")),
    url('^test/$', views.TestView.as_view()),  # cuisine页面
    url('^testxhr/$', views.TestXHRView.as_view()),  # DRF页面：遍历所有 状态为 '准备中' 的 order、桌数、桌号
    url('^testxhr2/$', views.TestXHR2View.as_view()),  # DRF页面：菜品汇总()

    # url('^salle/$', views.TestSalleView.as_view()),  # 大厅页面
    url('^testservice/(?P<pk>.+)$', views.TestServiceView.as_view()),  # 点菜详情页面 order页面
    url('^testcategory/$', views.TestCategoryView.as_view()),  # 点菜页面左侧 类别栏
    url('^testdish/(?P<pk>.+)/$', views.TestDishView.as_view()),  # 点菜页面右侧 菜品栏
    url('^testsubcategory/$', views.TestSubCategoryView.as_view()),  # 点菜页面左侧 子类别栏subCategory
    url('^testalldish/$', views.TestAllDishView.as_view()),  # 获取所有菜品
    url('^testtickets/$', views.TestTicketsView.as_view()),  # 点菜页面右侧 菜品栏
    url('^testticket/(?P<pk>.+)/$', views.TestTicketView.as_view()),  # 根据Table_num从DataOrder反向查询单个ticket
    url('^testticket2/(?P<pk>.+)/$', views.TestTicket2View.as_view()),  # 根据Ticket_id从DataOrder反向查询单个ticket，2023年增加了dsubcategory
    url('^testticket/(?P<pk>.+)/$', views.TestTicketView.as_view()),  # 根据Dataorder反向查询单个ticket
    url('^testticketdetail/(?P<pk>.+)/$', views.TestTicketDetailView.as_view()),  # 根据桌号从Dataticket中查询单个ticket：入单用
    url('^testticketlistpaiedandnopaied/$', views.TestTicketListPaiedNoPaiedView.as_view()),
    # 从Dataticket中查询所有的ticketList （无论是否已经结账，都可以被查询到）
    url('^testticketlistpaied/$', views.TestTicketListPaiedView.as_view()),  # 从Dataticket中查询所有已结账的ticketList
    url('^testticketdetailpaied/(?P<pk>.+)/$', views.TestTicketDetailPaiedView.as_view()),  # 从Dataticket中查询、修改、删除单个ticket，无论是否结账皆可查询
    url('^testticketlistnopaied/$', views.TestTicketListNoPaiedView.as_view()),  # 从Dataticket中查询所有的ticketList （无论是否已经结账，都可以被查询到）
    url('^testticketlistlivraison/$', views.TestTicketListLivraisonView.as_view()),  # 从Dataticket中查询所有的外送的ticketList （无论是否已经结账，都可以被查询到）
    url('^testticketlistemporter/$', views.TestTicketListEmporterView.as_view()),  # 从Dataticket中查询所有的外送的ticketList （无论是否已经结账，都可以被查询到）
    url('^testemptyticket/(?P<pk>.+)/$', views.TestEmptyTicketView.as_view()),  # 点菜页面右侧 菜品栏
    url('^testticketordergroupby/(?P<pk>.+)/$', views.TestTicketView2.as_view()),  # 将已选菜品goupe_by，留给cuisine页面
    url('^testticketordergroupby2/(?P<pk>.+)/$', views.TestTicketGroupbyView.as_view()),  # 根据ticket_id查询goupe_by菜品，供management里的detail.vue使用
    url('^testdishordergroupby/(?P<pk>.+)/$', views.TestDishGroupbyView.as_view()),  # 汇总查询所有订单的goupe_by菜品，供厨房贴单用，参数0：未结账，参数1：已结账，参数2：未结账和已结账
    url('^testdishordergroupby2/(?P<pk>.+)/$', views.TestDishGroupby2View.as_view()),  # 汇总查询（未付款、未zrapport、未完成的）订单的goupe_by菜品，供厨房贴单用，参数0：普通&优先，参数1：延后，参数2：所有
    url('^testdishordergroupby3/(?P<pk>.+)/$', views.TestDishGroupby3View.as_view()),  # 汇总查询所有订单的goupe_by菜品，供前厅贴单用，参数0：普通&优先，参数1：延后，参数2：所有
    url('^testallplatform/$', views.TestAllPlatformView.as_view()),  # 获取所有外送平台
    url('^testalllivreur/$', views.TestAllLivreurView.as_view()),  # 获取所有送餐员
    url('^testemptydataticket/$', views.EmptyDataTicketView),  # 清空DataTicket表 - 用于删除所有订单
    url('^testemptydatatableticket/$', views.EmptyDataTableTicketView),  # 部分清空DataTicket表 - 用于删除所有未结账堂食订单

    url('^testAxios/$', views.TestAxiosTicketListView.as_view()),  # 测试后端发送携带cookie的请求，小程序调单用
    url('^testAxios2/$', views.TestAxiosTicketListView2),  # 测试后端发送携带cookie的请求(测试简化版)，小程序调单用
    url('^testAxios/(?P<pk>.+)/$', views.TestAxiosTicketDetailView.as_view()),  # 测试后端发送携带cookie的请求，小程序调单用
    url('^testAxios2/(?P<pk>.+)/$', views.TestAxiosTicketDetailView2),  # 测试后端发送携带cookie的请求(测试简化版)，小程序调单用

    url('^testprintlist/$', views.TestPrintListView.as_view()),  # 获取打印队列 或者 新添加内容进打印队列
    url('^testprintlist/(?P<pk>.+)/$', views.TestPrintDetailListView.as_view()),  # 获取打印队列 或者 新添加内容进打印队列

    url('^testbasenote/$', views.TestBaseNoteView.as_view()),  # DRF页面：获取base_note

    url('^testpatch/(?P<pk>.+)/$', views.TestPatchView.as_view()),  # 测试put请求用
    url('^testpatchtable/(?P<pk>.+)/$', views.TestPatchTableView.as_view()),  # 测试put请求用
    url('^testpatchticket/(?P<pk>.+)/$', views.TestPatchTicketView.as_view()),  # patch Ticket内容，例如付款信息、结账状态
    url('^testcreate/', views.TestCreatView.as_view()),  # 测试create_order请求用
    url('^testcreatetable/', views.TestCreatTableView.as_view()),  # 测试create_table请求用

    url('^orderlist/$', views.OrderListView.as_view()),
    url('^orderlist/(?P<pk>\w+)$', views.OrderDetailView.as_view()),
    url('^tablelist/$', views.TableListView.as_view()),
    url('^tablelist/(?P<pk>\w+)$', views.TableDetailView.as_view()),
]