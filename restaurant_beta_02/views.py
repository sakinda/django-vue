# -*- coding: utf-8 -*-
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

import requests

from .models import *
from django.views import View
from rest_framework import serializers, status
from rest_framework.generics import ListAPIView, GenericAPIView, UpdateAPIView, CreateAPIView, DestroyAPIView, \
    RetrieveAPIView

tId = '1624561370'  # 关机后每15分钟更新一次
phpId = '97gbuipcup949jc9png2t02nl7'  # 每周更新一次


class DataTicketSerializer(serializers.ModelSerializer):
    orderList = serializers.SerializerMethodField()
    sortedOrderList = serializers.SerializerMethodField()
    sortedOrderListNoDrink = serializers.SerializerMethodField()
    sortedOrderListGroupBy = serializers.SerializerMethodField()

    class Meta:
        model = DataTicket
        fields = "__all__"
        # depth = 1

    def get_orderList(self, obj):
        orders_list2 = DataOrder.objects.prefetch_related('code').filter(tid__ticket_id=obj.ticket_id).values('order_id',
        'order_time', 'quantity', 'o_note', 'prepare_status', 'discount_type', 'extra_discount', 'emergency', 'is_served',
        'tid_id', 'person', 'finish_time', 'code__dname', 'code__dfrname', 'code__dprice', 'code__dcategory', 'code__dsubcategory',
        'code__dingredients', 'code__dtax', 'code__dprice', 'code__drecipe', 'tid__ticket_pickup_time')
        # print(orders_list2)
        orders_list = DataDish.objects.select_related('DataOrder').filter(orders__tid__ticket_id=obj.ticket_id) # 这里的orders是在DataDish中定义的related_name外键字段
        return orders_list2

    def get_sortedOrderList(self, obj):
        orders_list = DataOrder.objects.prefetch_related('code').filter(tid__ticket_id=obj.ticket_id).values('order_id',
        'order_time', 'quantity', 'o_note', 'prepare_status', 'discount_type', 'extra_discount', 'emergency', 'is_served',
        'tid_id', 'person', 'finish_time', 'code__dname', 'code__dfrname', 'code__dprice', 'code__dcategory', 'code__dsubcategory',
        'code__dingredients', 'code__dtax', 'code__dprice', 'code__drecipe', 'tid__ticket_pickup_time').order_by('code__dsubcategory', 'code__dcode')
        # print(orders_list)
        return orders_list

    def get_sortedOrderListNoDrink(self, obj):
        orders_list = DataOrder.objects.prefetch_related('code').filter(Q(tid__ticket_id=obj.ticket_id) &
                                                                        ~Q(code__dcategory=10) &
                                                                        ~Q(code__dcategory=11) &
                                                                        ~Q(code__dcategory=12) &
                                                                        ~Q(code__dcategory=13) &
                                                                        ~Q(code__dcategory=14) &
                                                                        ~Q(code__dcategory=15)).values('order_id',
        'order_time', 'quantity', 'o_note', 'prepare_status', 'discount_type', 'extra_discount', 'emergency', 'is_served',
        'tid_id', 'person', 'finish_time', 'code__dname', 'code__dfrname', 'code__dprice', 'code__dcategory', 'code__dsubcategory',
        'code__dingredients', 'code__dtax', 'code__dprice', 'code__drecipe', 'tid__ticket_pickup_time').order_by('code__dsubcategory', 'code__dcode')
        # print(orders_list)
        return orders_list

    def get_sortedOrderListGroupBy(self, obj):
        orders_list = DataOrder.objects.prefetch_related('code')\
            .filter(tid__ticket_id=obj.ticket_id).values('code__dname',
                                                         'code__dfrname', 'code__dprice', 'code__dcategory',
                                                         'code__dsubcategory', 'code__dingredients', 'code__dtax',
                                                         'code__dprice', 'code__drecipe', 'tid__ticket_pickup_time').order_by(
            'code__dsubcategory', 'code__dcode').annotate(total_quantity=Sum('quantity'))
        print(orders_list)
        return orders_list
        # print('obj：', obj) # obj是传进来的实例(instance)，由__str__决定显示的内容，但实际是一个完整的实例，包含了所有字段
        # total_q = DataDish.objects.filter(Q(orders__tid__table_num=self.context['tNum']) & Q(dname=obj.dname) & Q(
        #     orders__finish_time__isnull=True)).values_list('dname').annotate(total_quantity=Sum('orders__quantity'))
        # # print('total_q:       ', total_q)
        # return total_q.values_list('total_quantity', flat=True)


class DataPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataDeliveryPlatform
        fields = "__all__"


class DataDeliveryManSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataDeliveryMan
        fields = "__all__"


class DataOrderSerializer(serializers.ModelSerializer):
    ticket = DataTicketSerializer(read_only=True, many=True)
    # tid = DataTicketSerializer(read_only=True, many=True)
    ticket_emergency = serializers.SerializerMethodField()
    ticket_status = serializers.SerializerMethodField()

    class Meta:
        model = DataOrder
        # fields = "__all__"
        fields = ["order_id", "order_time", "quantity", "prepare_status", 'is_served', "discount_type", "extra_discount",
                  "emergency", "person", "finish_time", "code", "tid", "o_note", "ticket_status", "ticket_emergency", "ticket"]

    def get_ticket_emergency(self, obj):
        print(obj.tid.ticket_id)
        print(DataTicket.objects.filter(ticket_id=obj.tid.ticket_id))
        ticket_emergency = DataTicket.objects.filter(ticket_id=obj.tid.ticket_id).values_list(
            'ticket_emergency', flat=True)
        # ticket_emergency = DataTicket.objects.get(ticket_id=obj.tid.ticket_id)
        # ticket_emergency = obj.tid
        return ticket_emergency

    def get_ticket_status(self, obj):
        ticket_status = DataTicket.objects.filter(ticket_id=obj.tid.ticket_id).values_list(
            'ticket_status', flat=True)
        return ticket_status


class DataDishSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataDish
        fields = '__all__'


class TestOrderSerializer(serializers.ModelSerializer):
    dname = serializers.CharField(source='code.dname')
    dfrdname = serializers.CharField(source='code.dfrname')
    dprice = serializers.CharField(source='code.dprice')
    dingredients = serializers.CharField(source='code.dingredients')
    dcategory = serializers.CharField(source='code.dcategory')  # 2023-02添加，为了给Cuisine单排序
    dsubcategory = serializers.CharField(source='code.dsubcategory.subcategory_id')  # 2023-02添加，为了给Cuisine单排序
    table_num = serializers.CharField(source='tid.table_num')
    ticket_note = serializers.CharField(source='tid.ticket_note')
    ticket_emergency = serializers.CharField(source='tid.ticket_emergency')
    ticket_personquantity = serializers.CharField(source='tid.person_quantity')
    ticket_price = serializers.CharField(source='tid.ticket_price')
    ticket_platform = serializers.CharField(source='tid.delivery_platform.platform')
    ticket_payment_status = serializers.CharField(source='tid.payment_status')  # 2023-03添加
    # note = serializers.CharField(source='o_note.note')
    note = serializers.CharField(source='o_note')

    class Meta:
        model = DataOrder
        # fields = ['order_id', 'prepare_status', 'quantity', 'finish_time', 'dname', 'table_num', 'ticket_note', 'ticket_emergency',
        #           'note']
        fields = ['order_id', 'prepare_status', 'quantity', 'finish_time', 'dname','dfrdname', 'dprice', 'table_num',
                  'ticket_note',
                  'ticket_emergency', 'note', 'ticket_personquantity', 'dingredients', 'dcategory', 'dsubcategory',
                  'ticket_price', 'ticket_platform', 'ticket_payment_status']
        read_only_fields = ['prepare_status', 'finish_time', 'dname', 'dfrdname', 'dprice', 'ticket_note', 'table_num',
                            'ticket_emergency', 'note', 'ticket_price', 'ticket_platform', 'ticket_payment_status']


class AxiosSerializer(serializers.ModelSerializer):
    res = serializers.SerializerMethodField()

    def get_res(self, obj):
        url = "http://www.xinweiyun.com/weixin/index.php/auser/orderlist.html"
        headers = {
            "cookie": "Hm_lvt_ff8c31aa33cfd42f791daf61788c0167=%(tid)s;PHPSESSID=%(phpId)s;Hm_lpvt_ff8c31aa33cfd42f791daf61788c0167=%(tid)s;cookieshopid=23311" % {
                "tid": tId, "phpId": phpId}
        }
        print(headers)
        response = requests.post(url, headers=headers)
        # print(response.text)
        return response.text

    class Meta:
        model = DataOrder
        fields = ['res']


class AxiosTicketDetailSerializer(serializers.ModelSerializer):
    res = serializers.SerializerMethodField()

    class Meta:
        model = DataOrder
        fields = ['res']

    def get_res(self, obj):
        url = "http://www.xinweiyun.com/weixin/index.php/auser/orderdetails/act/change/id/" + self.context[
            'ticketNum'] + '/from/aHR0cDovL3d3dy54aW53ZWl5dW4uY29tL3dlaXhpbi9pbmRleC5waHAvYXVzZXIvb3JkZXJsaXN0Lmh0bWw%3D.jtml/'
        headers = {
            "cookie": "Hm_lvt_ff8c31aa33cfd42f791daf61788c0167=%(tid)s;PHPSESSID=%(phpId)s;Hm_lpvt_ff8c31aa33cfd42f791daf61788c0167=%(tid)s;cookieshopid=23311" % {
                "tid": tId, "phpId": phpId}
        }
        print(url)
        response = requests.get(url, headers=headers)
        # print(response.text)
        return response.text


class TestCategorySerializer(serializers.ModelSerializer):
    foods = serializers.SerializerMethodField()

    class Meta:
        model = DataDishCategory
        fields = ['category_id', 'category', 'foods']

    def get_foods(self, obj):
        return []


class TestSubCategorySerializer(serializers.ModelSerializer):
    foods = serializers.SerializerMethodField()

    class Meta:
        model = DataDishCategory
        fields = ['subcategory_id', 'subcategory', 'foods']

    def get_foods(self, obj):
        return []


class TestOrderGroupbySerializer(serializers.ModelSerializer):
    orders = DataOrderSerializer(read_only=True, many=True)
    total_quantity = serializers.SerializerMethodField()
    total_quantity_salle = serializers.SerializerMethodField()

    class Meta:
        model = DataDish
        fields = ['did', 'dname', 'dcode', 'dcategory', 'dsubcategory', 'dingredients', 'orders', 'total_quantity', 'total_quantity_salle']

    def get_total_quantity(self, obj):
        # print('目标：', obj.dname)
        # print(DataDish.objects.filter(Q(dname=obj.dname) & Q(orders__finish_time__isnull=True)).values_list())
        # print(obj.dname)
        total_q = DataDish.objects.filter(Q(dname=obj.dname) & Q(orders__finish_time__isnull=True) & Q(
                    orders__tid__ticket_status=1) & ~Q(
                    orders__prepare_status=0) & ~Q(
                    orders__prepare_status=3)).values_list(
            'dname').annotate(total_quantity=Sum('orders__quantity'))
        # print('total_q:       ', total_q)
        q = DataDish.objects.filter(Q(dname=obj.dname) & Q(orders__finish_time__isnull=True)).filter(
            orders__tid__table_num=31)
        # print('q:    ', q)
        return total_q.values_list('total_quantity', flat=True)

    def get_total_quantity_salle(self, obj):
        total_q = DataDish.objects.filter(Q(dname=obj.dname) & Q(orders__finish_time__isnull=True) & Q(
                    orders__is_served=0) & Q(orders__tid__ticket_is_served=0)).values_list(
            'dname').annotate(total_quantity=Sum('orders__quantity'))
        # print('total_q:       ', total_q)
        q = DataDish.objects.filter(Q(dname=obj.dname) & Q(orders__finish_time__isnull=True)).filter(
            orders__tid__table_num=31)
        # print('q:    ', q)
        return total_q.values_list('total_quantity', flat=True)


class TestTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataTicket
        fields = "__all__"


class TestTicketOrderGroupbySerializer(serializers.ModelSerializer):
    orders = DataOrderSerializer(read_only=True, many=True)
    total_quantity = serializers.SerializerMethodField()
    tableNumber = serializers.SerializerMethodField()
    tableid = serializers.SerializerMethodField()

    def get_tableid(self, obj):
        tid = DataTicket.objects.filter(Q(table_num=self.context['tNum']) & Q(ticket_status__lte=2)).values_list(
            'ticket_id', flat=True)
        return tid

    def get_tableNumber(self, obj):
        # print('OOOOOObbhJ', self.context['tNum'])
        return self.context['tNum']

    class Meta:
        model = DataDish
        fields = ['tableNumber', 'tableid', 'did', 'dname', 'dprice', 'dtax', 'dsubcategory', 'orders',
                  'total_quantity']

    def get_total_quantity(self, obj):
        # print('obj：', obj) # obj是传进来的实例(instance)，由__str__决定显示的内容，但实际是一个完整的实例，包含了所有字段
        total_q = DataDish.objects.filter(Q(orders__tid__table_num=self.context['tNum']) & Q(dname=obj.dname) & Q(
            orders__finish_time__isnull=True)).values_list('dname').annotate(total_quantity=Sum('orders__quantity'))
        # print('total_q:       ', total_q)
        return total_q.values_list('total_quantity', flat=True)


class TestTicketOrderGroupby2Serializer(serializers.ModelSerializer):
    orders = DataOrderSerializer(read_only=True, many=True)
    total_quantity = serializers.SerializerMethodField()

    class Meta:
        model = DataDish
        fields = ['did', 'dcode', 'dname', 'dprice', 'dtax', 'dsubcategory', 'orders', 'total_quantity']

    def get_total_quantity(self, obj):
        # print('::::::::::::::::::::::::::::::::', obj)
        # print('obj：', obj) # obj是传进来的实例(instance)，由__str__决定显示的内容，但实际是一个完整的实例，包含了所有字段
        total_q = DataDish.objects.filter(Q(orders__tid=self.context['tid']) & Q(dname=obj.dname)).values_list(
            'dname').annotate(total_quantity=Sum('orders__quantity'))
        # print('total_q:       ', total_q)
        return total_q.values_list('total_quantity', flat=True)


class TestBaseNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataNoteBase
        fields = "__all__"


# Create your views here.
class OrderListView(View):
    pass


class OrderDetailView(View):
    pass


class TableListView(View):
    pass


class TableDetailView(View):
    pass


class TestView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'test.html'

    def get(self, request):
        return Response()


class TestXHRView(ListAPIView, CreateAPIView):
    queryset = DataOrder.objects.all()
    serializer_class = TestOrderSerializer

    def get(self, request, *args, **kwargs):
        res = super().get(self, request, *args, **kwargs)
        # table_list = []
        table_list = list(DataOrder.objects.values('tid__table_num', 'tid__ticket_price',
                                                   'tid__delivery_platform__platform',
                                                   'tid__payment_status', 'tid__type').distinct())

        table_quantity = DataOrder.objects.values('tid__table_num').distinct().count()

        return Response({'table_quantity': table_quantity, 'table_list': table_list, 'data': res.data})


class TestXHR2View(ListAPIView):
    queryset = DataDish.objects.filter(
        Q(orders__finish_time__isnull=True) & Q(orders__isnull=False) & Q(orders__tid__ticket_status=1)).order_by(
        'dsubcategory').distinct()
    serializer_class = TestOrderGroupbySerializer

    # # 以下代码可以用来测试 get() 方法
    # def get(self, request, *args, **kwargs):
    #     res = super().get(self, request, *args, **kwargs)
    #
    #     for r in res.data:
    #         print(r)
    #
    #     return Response({'data': res.data})


class TestSalleView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'salle.html'

    def get(self, request):
        return Response()


class TestServiceView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'testService.html'

    def get(self, request, pk):
        return Response()


class TestCategoryView(ListAPIView):
    queryset = DataDishCategory.objects.values('category_id', 'category').distinct()
    serializer_class = TestCategorySerializer


class TestDishView(ListAPIView):
    # queryset = DataDish.objects.filter(dsubcategory__category_id=3)
    serializer_class = DataDishSerializer

    def get_queryset(self):
        categoryName = DataDish.objects.filter(dsubcategory__category_id=self.kwargs['pk'])
        # ###############测试##########################
        # print(self.kwargs['pk'])
        # print(categoryName)
        # ###############测试##########################
        return categoryName


class TestTicketView(ListAPIView):
    serializer_class = TestOrderSerializer

    def get_queryset(self):
        ticket_detail = DataOrder.objects.filter(Q(tid__table_num=self.kwargs['pk']) & Q(tid__ticket_status=1))
        # print(ticket_detail)
        return ticket_detail


class TestTicket2View(ListAPIView):
    serializer_class = TestOrderSerializer

    def get_queryset(self):
        # print('test::::::::', self.kwargs['pk'])
        ticket_detail = DataOrder.objects.filter(Q(tid=self.kwargs['pk']) & Q(tid__ticket_status=1))
        # print('test::::::::', ticket_detail)
        return ticket_detail


class TestEmptyTicketView(ListAPIView):
    serializer_class = TestTicketSerializer

    def get_queryset(self):
        # print(self.kwargs['pk'])
        ticket_detail = DataTicket.objects.filter(Q(table_num=self.kwargs['pk']) & Q(ticket_status=1)).order_by(
            '-ticket_time')
        # print(ticket_detail[0])
        return ticket_detail


class TestTicketView2(ListAPIView):
    serializer_class = TestTicketOrderGroupbySerializer

    def get_serializer_context(self):
        return {
            'tNum': self.kwargs['pk']
        }
        # tNum = self.kwargs['pk']
        # print('TNum', tNum )
        # return TestTicketOrderGroupbySerializer

    def get_queryset(self):
        # print(DataDish.objects.filter(orders__tid__table_num=self.kwargs['pk']))
        ticket_datail_order_groupby = DataDish.objects.filter(
            Q(orders__tid__table_num=self.kwargs['pk']) & Q(orders__finish_time__isnull=True) & Q(
                orders__isnull=False) & Q(orders__tid__payment_status='0')).distinct()
        # print(ticket_datail_order_groupby)
        return ticket_datail_order_groupby


class TestBaseNoteView(ListAPIView):
    queryset = DataNoteBase.objects.all()
    serializer_class = TestBaseNoteSerializer


# 作用：修改 或 删除 order
class TestPatchView(UpdateAPIView, DestroyAPIView):
    queryset = DataOrder.objects.all()
    serializer_class = DataOrderSerializer


class TestCreatView(CreateAPIView):
    queryset = DataOrder.objects.all()
    serializer_class = DataOrderSerializer


class TestCreatTableView(CreateAPIView):
    queryset = DataTicket.objects.all()
    serializer_class = DataTicketSerializer


class TestPatchTableView(UpdateAPIView, DestroyAPIView, ListAPIView):
    queryset = DataTicket.objects.all()
    serializer_class = DataTicketSerializer


class TestTicketsView(ListAPIView):
    serializer_class = DataTicketSerializer

    def get_queryset(self):
        ticket_using = DataTicket.objects.filter(Q(payment_status=0)).order_by('-ticket_time')
        print(ticket_using)
        return ticket_using


class TestTicketDetailView(ListAPIView):
    serializer_class = DataTicketSerializer

    def get_queryset(self):
        # ticket_status=1：排除已结完账的桌
        ticket_detail = DataTicket.objects.filter(Q(table_num=self.kwargs['pk']) & Q(ticket_status=1))
        return ticket_detail


class TestPatchTicketView(ListAPIView, UpdateAPIView, DestroyAPIView):
    serializer_class = DataTicketSerializer

    def get_queryset(self):
        # ticket_status=1：排除已结完账的桌
        # ticket_detail = DataTicket.objects.filter(Q(ticket_id=self.kwargs['pk']) & Q(ticket_status=1))
        ticket_detail = DataTicket.objects.filter(Q(ticket_id=self.kwargs['pk']))
        print(ticket_detail)
        return ticket_detail


class TestTicketListPaiedView(ListAPIView):
    serializer_class = DataTicketSerializer

    def get_queryset(self):
        tickets = DataTicket.objects.filter(payment_status=2)
        return tickets


class TestTicketDetailPaiedView(RetrieveAPIView, DestroyAPIView, UpdateAPIView):
    serializer_class = DataTicketSerializer

    def get_queryset(self):
        # ticket_status=1：排除已结完账的桌
        ticket_detail = DataTicket.objects.filter(ticket_id=self.kwargs['pk'])
        return ticket_detail


class TestTicketGroupbyView(ListAPIView):
    serializer_class = TestTicketOrderGroupby2Serializer

    def get_serializer_context(self):
        return {
            'tid': self.kwargs['pk']
        }

    def get_queryset(self):
        # print(DataDish.objects.filter(orders__tid__table_num=self.kwargs['pk']))
        ticket_datail_order_groupby = DataDish.objects.filter(orders__tid=self.kwargs['pk']).distinct()
        # print(ticket_datail_order_groupby)
        return ticket_datail_order_groupby


# 获取所有未付款的ticketList
class TestTicketListNoPaiedView(ListAPIView):
    serializer_class = DataTicketSerializer

    class Meta:
        depth: 1

    def get_queryset(self):
        tickets = DataTicket.objects.filter(Q(payment_status=0) | Q(payment_status=1) | Q(payment_status=2))
        return tickets


# 获取所有SubCategoryList - 用于DeliveryOrder.vue中的左侧category区域
class TestSubCategoryView(ListAPIView):
    queryset = DataDishCategory.objects.values('subcategory_id', 'subcategory').distinct().order_by('subcategory_id')
    serializer_class = TestSubCategorySerializer


# 获取DataDish中所有dishList - 用于DeliveryOrder.vue中
class TestAllDishView(ListAPIView):
    queryset = DataDish.objects.all().order_by('dsubcategory_id')
    serializer_class = DataDishSerializer


# 获取所有未做zrapport的ticketList(仅Livraison) - 用于Delivery.vue中
class TestTicketListLivraisonView(ListAPIView):
    serializer_class = DataTicketSerializer

    def get_queryset(self):
        tickets = DataTicket.objects.filter(Q(zrapport_condition=0) & Q(type=2))
        return tickets


# 获取所有未做zrapport的ticketList(仅Emporter) - 用于Delivery.vue中
class TestTicketListEmporterView(ListAPIView):
    serializer_class = DataTicketSerializer

    def get_queryset(self):
        tickets = DataTicket.objects.filter(Q(zrapport_condition=0) & Q(type=1))
        return tickets


class TestAxiosTicketListView(ListAPIView):
    queryset = DataDish.objects.filter(dcode='gjf')
    serializer_class = AxiosSerializer


class TestAxiosTicketDetailView(ListAPIView):
    serializer_class = AxiosTicketDetailSerializer
    queryset = DataDish.objects.filter(dcode='gjf')

    def get_serializer_context(self):
        print(self.kwargs['pk'])
        return {
            'ticketNum': self.kwargs['pk']
        }


def TestAxiosTicketListView2(request):
    url = "http://www.xinweiyun.com/weixin/index.php/auser/orderlist.html"
    headers = {
        "cookie": "Hm_lvt_ff8c31aa33cfd42f791daf61788c0167=%(tid)s;PHPSESSID=%(phpId)s;"
                  "Hm_lpvt_ff8c31aa33cfd42f791daf61788c0167=%(tid)s;cookieshopid=23311" % {"tid": tId, "phpId": phpId}
    }
    # print(headers)
    response = requests.post(url, headers=headers)
    # print(response.text)
    return HttpResponse(response.content)


def TestAxiosTicketDetailView2(request, pk):
    url = "http://www.xinweiyun.com/weixin/index.php/auser/orderdetails/act/change/id/" + pk + \
          '/from/aHR0cDovL3d3dy54aW53ZWl5dW4uY29tL3dlaXhpbi9pbmRleC5waHAvYXVzZXIvb3JkZXJsaXN0Lmh0bWw%3D.jtml/'
    headers = {
        "cookie": "Hm_lvt_ff8c31aa33cfd42f791daf61788c0167=%(tid)s;PHPSESSID=%(phpId)s;"
                  "Hm_lpvt_ff8c31aa33cfd42f791daf61788c0167=%(tid)s;cookieshopid=23311" % {"tid": tId, "phpId": phpId}
    }
    print(url)
    response = requests.get(url, headers=headers)
    print(response.text)
    return HttpResponse(response.text)


class DataPrintModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataPrint
        fields = "__all__"


class TestPrintListView(ListAPIView, CreateAPIView):
    queryset = DataPrint.objects.all()
    serializer_class = DataPrintModelSerializer


class TestPrintDetailListView(DestroyAPIView, UpdateAPIView):
    queryset = DataPrint.objects.all()
    serializer_class = DataPrintModelSerializer


class TestDishGroupbyView(ListAPIView):
    serializer_class = TestOrderGroupbySerializer

    def get_queryset(self):
        if self.kwargs['pk'] == '2':
            # print('进入方法2')
            dishes = DataDish.objects.filter(
                Q(orders__finish_time__isnull=True) & Q(orders__isnull=False) & Q(orders__tid__ticket_status=1)).order_by(
                'dsubcategory').distinct()
            print(dishes)
            return dishes
        elif self.kwargs['pk'] == '0':
            # print('进入方法0')
            dishes = DataDish.objects.filter(
                Q(orders__finish_time__isnull=True) & Q(orders__isnull=False) & Q(
                    orders__tid__payment_status=0)).order_by(
                'dsubcategory').distinct()
            return dishes
        elif self.kwargs['pk'] == '1':
            # print('进入方法1')
            dishes = DataDish.objects.filter(
                Q(orders__finish_time__isnull=True) & Q(orders__isnull=False) & Q(
                    orders__tid__payment_status=2)).order_by(
                'dsubcategory').distinct()
            return dishes


class TestDishGroupby2View(ListAPIView):
    serializer_class = TestOrderGroupbySerializer

    def get_queryset(self):
        if self.kwargs['pk'] == '2':
            # print('进入方法2')
            dishes = DataDish.objects.filter(
                Q(orders__finish_time__isnull=True) & Q(orders__isnull=False) & Q(
                    orders__tid__payment_status=0) & Q(
                    orders__tid__ticket_status=1) & Q(
                    orders__tid__zrapport_condition=0) & Q(
                    orders__prepare_status=1)).order_by(
                'dsubcategory').distinct()
            print(dishes)
            return dishes
        elif self.kwargs['pk'] == '0':
            # print('进入方法0')
            dishes = DataDish.objects.filter(
                Q(
                    orders__tid__ticket_status=1) & ~Q(
                    orders__prepare_status=0) & ~Q(
                    orders__prepare_status=3) & Q(
                    orders__tid__zrapport_condition=0) & ~Q(
                    orders__tid__ticket_emergency=2)).order_by(
                'dsubcategory', 'dcode').distinct()
            return dishes
        elif self.kwargs['pk'] == '1':
            # print('进入方法1')
            dishes = DataDish.objects.filter(
                Q(orders__finish_time__isnull=True) & Q(orders__isnull=False) & Q(
                    orders__tid__payment_status=0) & Q(
                    orders__tid__ticket_status=1) & Q(
                    orders__tid__zrapport_condition=0) & Q(
                    orders__tid__ticket_emergency=2) & Q(
                    orders__prepare_status=1)).order_by(
                'dsubcategory').distinct()
            return dishes


# 无论是否完成结账或者是否zrapport，菜品都可以获取（原来的那个直接复制过来的）
# 用于前厅调度系统
class TestDishGroupby3View(ListAPIView):
    serializer_class = TestOrderGroupbySerializer

    def get_queryset(self):
        if self.kwargs['pk'] == '2':
            print('进入接口testdishordergroupby3/2，调取salleGroupBy数据')
            # 无论优先级，一律调取
            dishes = DataDish.objects.filter(
                Q(orders__tid__ticket_is_served=0) & ~Q(
                    orders__is_served=1) & Q(
                    orders__tid__zrapport_condition=0)).order_by(
                'dsubcategory').distinct()
            # print(dishes)
            return dishes
        elif self.kwargs['pk'] == '0':
            # print('进入方法0')
            dishes = DataDish.objects.filter(
                Q(orders__finish_time__isnull=True) & Q(orders__isnull=False) & Q(
                    orders__tid__payment_status=0) & Q(
                    orders__tid__ticket_emergency=0) | Q(
                    orders__tid__ticket_emergency=1)).order_by(
                'dsubcategory').distinct()
            return dishes
        elif self.kwargs['pk'] == '1':
            # print('进入方法1')
            dishes = DataDish.objects.filter(
                Q(orders__finish_time__isnull=True) & Q(orders__isnull=False) & Q(
                    orders__tid__payment_status=0) & Q(
                    orders__tid__ticket_emergency=2)).order_by(
                'dsubcategory').distinct()
            return dishes


class TestAllPlatformView(ListAPIView):
    queryset = DataDeliveryPlatform.objects.all()
    serializer_class = DataPlatformSerializer


class TestAllLivreurView(ListAPIView):
    queryset = DataDeliveryMan.objects.all()
    serializer_class = DataDeliveryManSerializer


class TestTicketListPaiedNoPaiedView(ListAPIView):
    serializer_class = DataTicketSerializer
    queryset = DataTicket.objects.all()


def EmptyDataTicketView(self):
    DataTicket.objects.all().delete()
    DataOrder.objects.all().delete()
    return HttpResponse('删除所有数据')


def EmptyDataTableTicketView(self):
    # print(DataTicket.objects.filter(type=0))
    # print(DataOrder.objects.filter(tid__type=0))
    DataOrder.objects.filter(Q(tid__payment_status=0) & Q(tid__type=0)).delete()
    DataTicket.objects.filter(Q(payment_status=0) & Q(type=0)).delete()
    return HttpResponse('删除所有堂食数据')