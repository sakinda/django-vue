# -*- coding: utf-8 -*-
from django.db.models import Count, Q, Sum, F
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal

import requests
import json
import re
import os

from .models import *
from django.views import View
from rest_framework import serializers, status
from rest_framework.generics import ListAPIView, GenericAPIView, UpdateAPIView, CreateAPIView, DestroyAPIView, \
    RetrieveAPIView
from django.core.cache import cache
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

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

    def _orders(self, obj):
        ctx = self.context.get('orders_by_ticket')
        if ctx is not None:
            return ctx.get(obj.ticket_id, [])
        return list(DataOrder.objects.select_related('code').filter(tid__ticket_id=obj.ticket_id))

    def get_orderList(self, obj):
        orders = self._orders(obj)
        return [{
            'order_id': o.order_id,
            'order_time': o.order_time,
            'quantity': o.quantity,
            'o_note': o.o_note,
            'prepare_status': o.prepare_status,
            'discount_type': o.discount_type,
            'extra_discount': o.extra_discount,
            'emergency': o.emergency,
            'is_served': o.is_served,
            'tid_id': o.tid_id,
            'person': o.person,
            'finish_time': o.finish_time,
            'code': o.code.dcode,
            'code__dname': o.code.dname,
            'code__dfrname': o.code.dfrname,
            'code__dmininame': o.code.dmininame,
            'code__dprice': o.code.dprice,
            'code__dcategory': o.code.dcategory,
            'code__dsubcategory': o.code.dsubcategory_id,
            'code__dingredients': o.code.dingredients,
            'code__dtax': o.code.dtax,
            'code__dprice': o.code.dprice,
            'code__drecipe': o.code.drecipe,
            'tid__ticket_pickup_time': obj.ticket_pickup_time
        } for o in orders]

    def get_sortedOrderList(self, obj):
        orders = sorted(self._orders(obj), key=lambda o: (o.code.dsubcategory_id, o.code.dcode))
        return [{
            'order_id': o.order_id,
            'order_time': o.order_time,
            'quantity': o.quantity,
            'o_note': o.o_note,
            'prepare_status': o.prepare_status,
            'discount_type': o.discount_type,
            'extra_discount': o.extra_discount,
            'emergency': o.emergency,
            'is_served': o.is_served,
            'tid_id': o.tid_id,
            'person': o.person,
            'finish_time': o.finish_time,
            'code': o.code.dcode,
            'code__dname': o.code.dname,
            'code__dfrname': o.code.dfrname,
            'code__dmininame': o.code.dmininame,
            'code__dprice': o.code.dprice,
            'code__dcategory': o.code.dcategory,
            'code__dsubcategory': o.code.dsubcategory_id,
            'code__dingredients': o.code.dingredients,
            'code__dtax': o.code.dtax,
            'code__dprice': o.code.dprice,
            'code__drecipe': o.code.drecipe,
            'tid__ticket_pickup_time': obj.ticket_pickup_time
        } for o in orders]

    def get_sortedOrderListNoDrink(self, obj):
        excludes = {'10', '11', '12', '13', '14', '15'}
        orders = [o for o in self._orders(obj) if str(o.code.dcategory) not in excludes]
        orders = sorted(orders, key=lambda o: (o.code.dsubcategory_id, o.code.dcode))
        return [{
            'order_id': o.order_id,
            'order_time': o.order_time,
            'quantity': o.quantity,
            'o_note': o.o_note,
            'prepare_status': o.prepare_status,
            'discount_type': o.discount_type,
            'extra_discount': o.extra_discount,
            'emergency': o.emergency,
            'is_served': o.is_served,
            'tid_id': o.tid_id,
            'person': o.person,
            'finish_time': o.finish_time,
            'code': o.code.dcode,
            'code__dname': o.code.dname,
            'code__dfrname': o.code.dfrname,
            'code__dmininame': o.code.dmininame,
            'code__dprice': o.code.dprice,
            'code__dcategory': o.code.dcategory,
            'code__dsubcategory': o.code.dsubcategory_id,
            'code__dingredients': o.code.dingredients,
            'code__dtax': o.code.dtax,
            'code__dprice': o.code.dprice,
            'code__drecipe': o.code.drecipe,
            'tid__ticket_pickup_time': obj.ticket_pickup_time
        } for o in orders]

    def get_sortedOrderListGroupBy(self, obj):
        orders = self._orders(obj)
        totals = {}
        for o in orders:
            k = o.code.dcode
            totals[k] = totals.get(k, 0) + o.quantity
        unique_codes = {}
        for o in orders:
            k = o.code.dcode
            if k not in unique_codes:
                unique_codes[k] = o
        rows = [{
            'code': k,
            'code__dname': v.code.dname,
            'code__dfrname': v.code.dfrname,
            'code__dmininame': v.code.dmininame,
            'code__dprice': v.code.dprice,
            'code__dcategory': v.code.dcategory,
            'code__dsubcategory': v.code.dsubcategory_id,
            'code__dingredients': v.code.dingredients,
            'code__dtax': v.code.dtax,
            'code__dprice': v.code.dprice,
            'code__drecipe': v.code.drecipe,
            'tid__ticket_pickup_time': obj.ticket_pickup_time,
            'total_quantity': totals[k]
        } for k, v in unique_codes.items()]
        rows.sort(key=lambda r: (r['code__dsubcategory'], r['code']))
        return rows
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
        return [obj.tid.ticket_emergency]

    def get_ticket_status(self, obj):
        return [obj.tid.ticket_status]


class DataDishSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataDish
        fields = '__all__'


class TestOrderSerializer(serializers.ModelSerializer):
    dname = serializers.CharField(source='code.dname')
    dfrdname = serializers.CharField(source='code.dfrname')
    dmininame = serializers.CharField(source='code.dmininame')
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
        fields = ['order_id', 'prepare_status', 'quantity', 'finish_time', 'dname', 'dfrdname', 'dmininame', 'dprice', 'table_num',
                  'ticket_note',
                  'ticket_emergency', 'note', 'ticket_personquantity', 'dingredients', 'dcategory', 'dsubcategory',
                  'ticket_price', 'ticket_platform', 'ticket_payment_status']
        read_only_fields = ['prepare_status', 'finish_time', 'dname', 'dfrdname', 'dmininame', 'dprice', 'ticket_note', 'table_num',
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


class TestOrderGroupbyAllSerializer(serializers.ModelSerializer):
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
        total_q = DataDish.objects.filter(Q(dname=obj.dname)).values_list(
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


class TestBaseNoteView(ListAPIView, CreateAPIView):
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

    def get_serializer_context(self):
        qs = self.get_queryset()
        tickets = list(qs.values_list('ticket_id', flat=True))
        orders = DataOrder.objects.select_related('code').filter(tid__ticket_id__in=tickets)
        orders_by_ticket = {}
        for o in orders:
            orders_by_ticket.setdefault(o.tid.ticket_id, []).append(o)
        return {'orders_by_ticket': orders_by_ticket}



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


# 获取所有出菜的ticketList
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


class TestDishGroupby2View(APIView):
    def get(self, request, pk):
        page = int(request.GET.get('page', '1'))
        size = int(request.GET.get('size', '200'))
        qs = DataOrder.objects.select_related('code')
        if pk == '2':
            qs = qs.filter(
                (Q(finish_time__isnull=True) | Q(finish_time='')) &
                Q(tid__payment_status=0) &
                Q(tid__ticket_status=1) &
                Q(tid__zrapport_condition=0) &
                Q(prepare_status=1)
            )
        elif pk == '0':
            qs = qs.filter(
                Q(tid__ticket_status=1) &
                ~Q(prepare_status=0) &
                ~Q(prepare_status=3) &
                Q(tid__zrapport_condition=0) &
                ~Q(tid__ticket_emergency=2)
            )
        elif pk == '1':
            qs = qs.filter(
                (Q(finish_time__isnull=True) | Q(finish_time='')) &
                Q(tid__payment_status=0) &
                Q(tid__ticket_status=1) &
                Q(tid__zrapport_condition=0) &
                Q(tid__ticket_emergency=2) &
                Q(prepare_status=1)
            )
        elif pk == '3':
            qs = qs.filter(
                Q(finish_time__isnull=True) &
                Q(tid__zrapport_condition=0)
            )
        agg = qs.annotate(
            did=F('code__did'),
            dname=F('code__dname'),
            dmininame=F('code__dmininame'),
            dcode=F('code'),
            dcategory=F('code__dcategory'),
            dsubcategory=F('code__dsubcategory_id'),
            dingredients=F('code__dingredients'),
        ).values('did', 'dname', 'dmininame', 'dcode', 'dcategory', 'dsubcategory', 'dingredients')\
         .annotate(total_quantity=Sum('quantity')).order_by('dsubcategory', 'dcode')
        start = (page - 1) * size
        end = start + size
        orders_rows = list(qs.values(
            'order_id', 'order_time', 'quantity', 'prepare_status', 'is_served',
            'discount_type', 'extra_discount', 'emergency', 'person', 'finish_time',
            'code', 'tid_id', 'o_note', 'tid__ticket_status', 'tid__ticket_emergency'
        ))
        orders_by_code = {}
        for o in orders_rows:
            od = {
                'order_id': o['order_id'],
                'order_time': o['order_time'],
                'quantity': o['quantity'],
                'prepare_status': o['prepare_status'],
                'is_served': o['is_served'],
                'discount_type': o['discount_type'],
                'extra_discount': float(o['extra_discount']) if o['extra_discount'] is not None else None,
                'emergency': o['emergency'],
                'person': o['person'],
                'finish_time': o['finish_time'],
                'code': o['code'],
                'tid': o['tid_id'],
                'o_note': o['o_note'],
                'ticket_status': [o['tid__ticket_status']] if o['tid__ticket_status'] is not None else [],
                'ticket_emergency': [o['tid__ticket_emergency']] if o['tid__ticket_emergency'] is not None else []
            }
            orders_by_code.setdefault(o['code'], []).append(od)
        rows = list(agg[start:end])
        for r in rows:
            tq = r.get('total_quantity')
            if tq is not None:
                r['total_quantity_salle'] = [tq]
                r['total_quantity'] = [tq]
            r['orders'] = orders_by_code.get(r['dcode'], [])
        payload = json.dumps({'page': page, 'size': size, 'count': agg.count(), 'rows': rows}, separators=(',', ':'))
        return HttpResponse(payload, content_type='application/json')


# 无论是否完成结账或者是否zrapport，菜品都可以获取（原来的那个直接复制过来的）
# 用于前厅调度系统
class TestDishGroupby3View(APIView):
    def get(self, request, pk):
        page = int(request.GET.get('page', '1'))
        size = int(request.GET.get('size', '200'))
        qs = DataOrder.objects.select_related('code')
        if pk == '2':
            qs = qs.filter(
                Q(tid__ticket_is_served=0) &
                ~Q(is_served=1) &
                Q(tid__zrapport_condition=0)
            )
        elif pk == '0':
            qs = qs.filter(
                (Q(finish_time__isnull=True) | Q(finish_time='')) &
                Q(tid__payment_status=0) &
                (Q(tid__ticket_emergency=0) | Q(tid__ticket_emergency=1))
            )
        elif pk == '1':
            qs = qs.filter(
                (Q(finish_time__isnull=True) | Q(finish_time='')) &
                Q(tid__payment_status=0) &
                Q(tid__ticket_emergency=2)
            )
        agg = qs.annotate(
            did=F('code__did'),
            dname=F('code__dname'),
            dmininame=F('code__dmininame'),
            dcode=F('code'),
            dcategory=F('code__dcategory'),
            dsubcategory=F('code__dsubcategory_id'),
            dingredients=F('code__dingredients'),
        ).values('did', 'dname', 'dmininame', 'dcode', 'dcategory', 'dsubcategory', 'dingredients') \
         .annotate(total_quantity=Sum('quantity')).order_by('dsubcategory', 'dcode')
        start = (page - 1) * size
        end = start + size
        orders_rows = list(qs.values(
            'order_id', 'order_time', 'quantity', 'prepare_status', 'is_served',
            'discount_type', 'extra_discount', 'emergency', 'person', 'finish_time',
            'code', 'tid_id', 'o_note', 'tid__ticket_status', 'tid__ticket_emergency'
        ))
        orders_by_code = {}
        for o in orders_rows:
            od = {
                'order_id': o['order_id'],
                'order_time': o['order_time'],
                'quantity': o['quantity'],
                'prepare_status': o['prepare_status'],
                'is_served': o['is_served'],
                'discount_type': o['discount_type'],
                'extra_discount': float(o['extra_discount']) if o['extra_discount'] is not None else None,
                'emergency': o['emergency'],
                'person': o['person'],
                'finish_time': o['finish_time'],
                'code': o['code'],
                'tid': o['tid_id'],
                'o_note': o['o_note'],
                'ticket_status': [o['tid__ticket_status']] if o['tid__ticket_status'] is not None else [],
                'ticket_emergency': [o['tid__ticket_emergency']] if o['tid__ticket_emergency'] is not None else []
            }
            orders_by_code.setdefault(o['code'], []).append(od)
        rows = list(agg[start:end])
        for r in rows:
            tq = r.get('total_quantity')
            if tq is not None:
                r['total_quantity_salle'] = [tq]
                r['total_quantity'] = [tq]
            r['orders'] = orders_by_code.get(r['dcode'], [])
        payload = json.dumps({'page': page, 'size': size, 'count': agg.count(), 'rows': rows}, separators=(',', ':'))
        return HttpResponse(payload, content_type='application/json')


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

def EmptyDataPrintView(self):
    DataPrint.objects.all().delete()
    return HttpResponse('删除所有打印队列数据')


class DataKitchenCleaningTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataKitchenCleaningTask
        fields = '__all__'


class DataKitchenCleaningTaskListView(ListAPIView, CreateAPIView):
    queryset = DataKitchenCleaningTask.objects.all()
    serializer_class = DataKitchenCleaningTaskSerializer


class DataKitchenCleaningTaskDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    queryset = DataKitchenCleaningTask.objects.all()
    serializer_class = DataKitchenCleaningTaskSerializer


class DataDishListView(ListAPIView, CreateAPIView):
    queryset = DataDish.objects.all()
    serializer_class = DataDishSerializer


class DataDishDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    queryset = DataDish.objects.all()
    serializer_class = DataDishSerializer
    lookup_field = 'dcode'

class DataNoteBaseDetailView(APIView):
    def get(self, request, pk):
        obj = DataNoteBase.objects.filter(id=pk).first()
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(TestBaseNoteSerializer(obj).data)

    def patch(self, request, pk):
        obj = DataNoteBase.objects.filter(id=pk).first()
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TestBaseNoteSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = DataNoteBase.objects.filter(id=pk).first()
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Wix API Configuration
WIX_API_KEY = 'IST.eyJraWQiOiJQb3pIX2FDMiIsImFsZyI6IlJTMjU2In0.eyJkYXRhIjoie1wiaWRcIjpcIjM1YzFlZTViLTIwZGItNGFmYS04MmEzLTgxNzkzZTQ1MTk4NlwiLFwiaWRlbnRpdHlcIjp7XCJ0eXBlXCI6XCJhcHBsaWNhdGlvblwiLFwiaWRcIjpcIjZjOGRiOGM1LTA4NjItNDQyYS1iNmY3LTk3MjcwNGIzM2FkZVwifSxcInRlbmFudFwiOntcInR5cGVcIjpcImFjY291bnRcIixcImlkXCI6XCI2MWRlMDZlMS05NzgwLTRjMDYtOTE3Yi1mNjE3OWQ3YzMxY2VcIn19IiwiaWF0IjoxNzczMTAxMzQ4fQ.Ucs_BJxlZPF22GHguycKqCWtCzM_BApT6aK_zE65CIo6ECXZzyoDYBdIiiJp3gGygCOVDB80NzaBKfCS3F3VZnb7J0SQhEtwXOGGmyxl3d2G_FIAi8rp0vAkOk-xmeqPPzU88byXq5bldpckHxEVOelkZqRFJbZrSII2uCnuD0KBT_1xLoRjcR5oCT-4kMcebKkh3ccOU-mQltvMVY3dChBIJinLg7Ns-pZ06WScgwr7DdIBm1aBi_1cpsR2X71jaemd12sqcN3OX5esz5EDJznHA5cPTkJ2133bSe_Y1SQS8Jg4ra9uGnFA6dyS4j5yWaP2bbsoHqtz8oQjmfFuPg'
WIX_SITE_ID = 'cdf00b53-5571-49f9-8fa9-e9fb08f6515c'
# Correct Base URL based on verification: https://www.wixapis.com/table-reservations/reservations/v1
WIX_BASE_URL = 'https://www.wixapis.com/table-reservations/reservations/v1'
WIX_RESERVATION_LOCATIONS_URL = 'https://www.wixapis.com/table-reservations/reservation-locations/v1/reservation-locations'
WIX_ECOM_ORDERS_SEARCH_URL = 'https://www.wixapis.com/ecom/v1/orders/search'
WIX_DEFAULT_LOCATION_ID = '38853019-1e11-47bb-af81-7f292682f271'

WIX_VALID_RESERVATION_STATUSES = {
    'UNKNOWN',
    'HELD',
    'RESERVED',
    'CANCELED',
    'FINISHED',
    'NO_SHOW',
    'SEATED',
    'REQUESTED',
    'DECLINED',
    'PAYMENT_PENDING',
    'PAYMENT_INFORMATION_PENDING',
}


def normalize_wix_reservation_status(raw_status, default=None):
    """
    Convert user-facing or upstream reservation statuses into Wix-supported enums.
    """
    if raw_status is None:
        return default

    normalized = str(raw_status).strip()
    if not normalized:
        return default

    upper_value = normalized.upper().replace('-', '_').replace(' ', '_')
    alias_map = {
        'CONFIRMED': 'RESERVED',
        'BOOKED': 'RESERVED',
        'RECORDED': 'RESERVED',
        'ARRIVED': 'SEATED',
        'SEATED': 'SEATED',
        'CANCELLED': 'CANCELED',
        'CANCELED': 'CANCELED',
        'CANCLED': 'CANCELED',
        'NO_SHOW': 'NO_SHOW',
        'NOSHOW': 'NO_SHOW',
        'DECLINED': 'DECLINED',
        'REQUESTED': 'REQUESTED',
        'HELD': 'HELD',
        'FINISHED': 'FINISHED',
        'COMPLETED': 'FINISHED',
        'PAYMENT_PENDING': 'PAYMENT_PENDING',
        'PAYMENT_INFORMATION_PENDING': 'PAYMENT_INFORMATION_PENDING',
    }

    mapped = alias_map.get(upper_value, upper_value)
    if mapped in WIX_VALID_RESERVATION_STATUSES:
        return mapped
    return default


class WixReservationListView(APIView):
    def get(self, request):
        # Wix Query endpoint requires POST
        url = f"{WIX_BASE_URL}/reservations/query"
        headers = {
            "Authorization": WIX_API_KEY,
            "wix-site-id": WIX_SITE_ID,
            "Content-Type": "application/json"
        }

        # Calculate today's start date (UTC)
        from django.utils import timezone
        import datetime
        import pytz
        
        # Get target date from query parameters or default to today (in Paris time)
        target_date_str = request.query_params.get('date')
        if target_date_str:
            try:
                target_date = datetime.datetime.strptime(target_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
        else:
            # Use Paris timezone for default date
            paris_tz = pytz.timezone('Europe/Paris')
            target_date = timezone.now().astimezone(paris_tz).date()
        
        # Construct time range for the target date (Paris Time -> UTC)
        paris_tz = pytz.timezone('Europe/Paris')
        
        # Start of day in Paris
        start_naive = datetime.datetime.combine(target_date, datetime.time.min)
        start_paris = paris_tz.localize(start_naive)
        start_utc = start_paris.astimezone(pytz.UTC)
        
        # End of day in Paris (Start of next day)
        end_naive = datetime.datetime.combine(target_date + datetime.timedelta(days=1), datetime.time.min)
        end_paris = paris_tz.localize(end_naive)
        end_utc = end_paris.astimezone(pytz.UTC)
        
        start_of_day = start_utc.isoformat().replace('+00:00', 'Z')
        end_of_day = end_utc.isoformat().replace('+00:00', 'Z')

        limit = request.query_params.get('limit')
        if limit is not None:
            try:
                parsed_limit = int(limit)
            except ValueError:
                return Response({"error": "Invalid limit. Must be an integer."}, status=400)
            if parsed_limit <= 0:
                return Response({"error": "Invalid limit. Must be a positive integer."}, status=400)
            page_limit = min(parsed_limit, 100)
        else:
            page_limit = 100

        query = {
            "filter": {
                "$and": [
                    {"details.startDate": {"$gte": start_of_day}},
                    {"details.startDate": {"$lt": end_of_day}}
                ]
            }
        }

        try:
            cursor = None
            all_reservations = []
            seen_ids = set()
            data = None
            page_count = 0

            while True:
                page_count += 1
                page_query = dict(query)
                page_query["cursorPaging"] = {"limit": page_limit}
                if cursor:
                    page_query["cursorPaging"]["cursor"] = cursor

                body = {
                    "query": page_query,
                    "fieldsets": ["FULL"]
                }

                response = requests.post(url, headers=headers, json=body)
                if response.status_code == 404 and page_count == 1:
                    try:
                        error_detail = response.json()
                        if "meta-site" in str(error_detail):
                            return Response(
                                {"error": "Wix Site ID not found or app not installed", "details": error_detail},
                                status=404
                            )
                    except Exception:
                        pass

                response.raise_for_status()

                page_data = response.json()
                if data is None:
                    data = page_data

                for r in (page_data.get('reservations') or []):
                    rid = r.get('id')
                    if rid and rid in seen_ids:
                        continue
                    if rid:
                        seen_ids.add(rid)
                    all_reservations.append(r)

                paging = page_data.get('pagingMetadata') or {}
                cursor = ((paging.get('cursors') or {}).get('next'))
                if not paging.get('hasNext') or not cursor:
                    break
                if page_count >= 30:
                    break

            data = data or {}
            data['reservations'] = all_reservations
            data['pagingMetadata'] = {"count": len(all_reservations), "hasNext": False, "cursors": {}}
            data['reservations'].sort(key=lambda x: x.get('details', {}).get('startDate', ''))

            if request.query_params.get('debugPaging') in ('1', 'true', 'True'):
                data['pagingDebug'] = {
                    'pageCount': page_count,
                    'pageLimit': page_limit,
                    'totalReservations': len(all_reservations)
                }

            locations_headers = {
                "Authorization": WIX_API_KEY,
                "wix-site-id": WIX_SITE_ID
            }
            try:
                locations_response = requests.get(WIX_RESERVATION_LOCATIONS_URL, headers=locations_headers)
                locations_response.raise_for_status()
                data['reservationLocations'] = locations_response.json()
            except requests.exceptions.RequestException as e:
                status_code = 500
                details = str(e)
                if e.response is not None:
                    status_code = e.response.status_code
                    try:
                        details = e.response.json()
                    except:
                        details = e.response.text
                data['reservationLocationsError'] = {"status": status_code, "error": details}

            return Response(data)
        except requests.exceptions.RequestException as e:
            status_code = 500
            details = str(e)
            if e.response is not None:
                status_code = e.response.status_code
                try:
                    details = e.response.json()
                except:
                    details = e.response.text
            return Response({"error": details}, status=status_code)

    def post(self, request):
        url = f"{WIX_BASE_URL}/reservations"
        headers = {
            "Authorization": WIX_API_KEY,
            "wix-site-id": WIX_SITE_ID,
            "Content-Type": "application/json"
        }
        required_fields = ["partySize", "startDate", "firstName", "phone"]
        missing = [f for f in required_fields if f not in request.data]
        location_id = request.data.get("reservationLocationId") or request.data.get("locationId") or WIX_DEFAULT_LOCATION_ID
        if missing:
            return Response({"error": "Missing required fields", "missing": missing}, status=400)
        payload = {
            "reservation": {
                "details": {
                    "partySize": request.data.get("partySize"),
                    "startDate": request.data.get("startDate"),
                    "reservationLocationId": location_id,
                    "locationId": location_id
                },
                "reservee": {
                    "firstName": request.data.get("firstName"),
                    "lastName": request.data.get("lastName"),
                    "email": request.data.get("email"),
                    "phone": request.data.get("phone")
                }
            }
        }
        if request.data.get("endDate") is not None:
            payload["reservation"]["details"]["endDate"] = request.data.get("endDate")
        if request.data.get("teamMessage") is not None:
            payload["reservation"]["teamMessage"] = request.data.get("teamMessage")
        if request.data.get("status") is not None:
            normalized_status = normalize_wix_reservation_status(request.data.get("status"))
            if normalized_status is None:
                return Response(
                    {
                        "error": "Invalid reservation status",
                        "received": request.data.get("status"),
                        "allowed": sorted(WIX_VALID_RESERVATION_STATUSES),
                    },
                    status=400
                )
            payload["reservation"]["status"] = normalized_status
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            status_code = 500
            details = str(e)
            if e.response is not None:
                status_code = e.response.status_code
                try:
                    details = e.response.json()
                except:
                    details = e.response.text
            return Response({"error": details}, status=status_code)


class TestTheForkSyncView(APIView):
    def post(self, request):
        import datetime
        import re
        import requests as wix_requests
        from django.utils import timezone as dj_timezone

        try:
            from zoneinfo import ZoneInfo
            paris_tz = ZoneInfo('Europe/Paris')
        except Exception:
            try:
                import pytz
                paris_tz = pytz.timezone('Europe/Paris')
            except Exception:
                return Response({'error': 'timezone unavailable'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        source_marker_re = re.compile(r'THEFORK_SOURCE_ID\s*=\s*([A-Za-z0-9_\-]+)', re.IGNORECASE)
        canceled_re = re.compile(r'cancel(l)?(ed)?|已取消|取消', re.IGNORECASE)
        NAME_PREFIX = '(叉子订位)'

        def parse_iso_to_paris(value):
            if not value:
                return None
            s = str(value).strip()
            if not s:
                return None
            if s.endswith('Z'):
                s = s[:-1] + '+00:00'
            try:
                dt = datetime.datetime.fromisoformat(s)
            except Exception:
                return None
            try:
                if dt.tzinfo is None:
                    if hasattr(paris_tz, 'localize'):
                        dt = paris_tz.localize(dt)
                    else:
                        dt = dt.replace(tzinfo=paris_tz)
                return dt.astimezone(paris_tz)
            except Exception:
                return None

        def to_paris_date_str(dt):
            return dt.strftime('%Y-%m-%d')

        def minute_key(dt):
            return dt.strftime('%Y-%m-%d %H:%M')

        def strip_none(value):
            if value is None:
                return ''
            return str(value).strip()

        def eq_blank(a, b):
            return strip_none(a) == strip_none(b)

        def extract_source_id(team_message):
            if not team_message:
                return None
            m = source_marker_re.search(str(team_message))
            if not m:
                return None
            return (m.group(1) or '').strip() or None

        def is_canceled_status(raw_status):
            if not raw_status:
                return False
            return bool(canceled_re.search(str(raw_status).strip()))

        def strip_name_prefix(prefixed):
            v = strip_none(prefixed)
            if v.startswith(NAME_PREFIX):
                v = v[len(NAME_PREFIX):]
            return v.strip()

        def prefix_full_name_first_name(raw_first_name):
            raw = strip_name_prefix(raw_first_name)
            return f"{NAME_PREFIX} {raw}" if raw else NAME_PREFIX

        def build_team_message(source_id, customer_note, restaurant_note, raw_status, extra=None):
            parts = [f"[THEFORK_SYNC] THEFORK_SOURCE_ID={source_id}"]
            if raw_status:
                parts.append(f"theForkStatus={raw_status}")
            if isinstance(extra, dict):
                for k, v in extra.items():
                    if v is None:
                        continue
                    parts.append(f"{k}={v}")
            notes = []
            for n in (customer_note, restaurant_note):
                if n and str(n).strip():
                    notes.append(str(n).strip())
            if notes:
                parts.append("note=" + " | ".join(notes))
            return " ".join(parts)

        def wix_headers():
            return {
                "Authorization": WIX_API_KEY,
                "wix-site-id": WIX_SITE_ID,
                "Content-Type": "application/json"
            }

        def fetch_wix_reservations_for_date(paris_date_str):
            try:
                target_date = datetime.datetime.strptime(paris_date_str, '%Y-%m-%d').date()
            except Exception:
                raise ValueError('invalid paris_date_str')
            start_naive = datetime.datetime.combine(target_date, datetime.time.min)
            end_naive = datetime.datetime.combine(target_date + datetime.timedelta(days=1), datetime.time.min)
            try:
                if hasattr(paris_tz, 'localize'):
                    start_paris = paris_tz.localize(start_naive)
                    end_paris = paris_tz.localize(end_naive)
                else:
                    start_paris = start_naive.replace(tzinfo=paris_tz)
                    end_paris = end_naive.replace(tzinfo=paris_tz)
                utc_tz = datetime.timezone.utc
                start_utc = start_paris.astimezone(utc_tz)
                end_utc = end_paris.astimezone(utc_tz)
            except Exception as e:
                raise ValueError(f"date tz conversion failed: {e}")

            start_of_day = start_utc.isoformat().replace('+00:00', 'Z')
            end_of_day = end_utc.isoformat().replace('+00:00', 'Z')

            url = f"{WIX_BASE_URL}/reservations/query"
            reservations = []
            cursor = None
            page_count = 0
            while True:
                page_count += 1
                if page_count > 30:
                    break
                query = {
                    "filter": {
                        "$and": [
                            {"details.startDate": {"$gte": start_of_day}},
                            {"details.startDate": {"$lt": end_of_day}}
                        ]
                    }
                }
                payload_q = {"query": query}
                if cursor:
                    payload_q["query"]["cursorPaging"] = {"cursor": cursor}
                page_resp = wix_requests.post(url, headers=wix_headers(), json=payload_q, timeout=25)
                page_resp.raise_for_status()
                page_data = page_resp.json()
                for r in (page_data.get('reservations') or []):
                    reservations.append(r)
                paging = page_data.get('pagingMetadata') or {}
                nxt = ((paging.get('cursors') or {}).get('next'))
                if not paging.get('hasNext') or not nxt:
                    break
                cursor = nxt
            seen = set()
            uniq = []
            for r in reservations:
                rid = r.get('id')
                if rid and rid in seen:
                    continue
                if rid:
                    seen.add(rid)
                uniq.append(r)
            return uniq

        def wix_create_reservation(normalized):
            location_id = normalized.get('reservationLocationId') or WIX_DEFAULT_LOCATION_ID
            reservee = {
                "firstName": normalized.get('firstName') or '',
                "lastName": normalized.get('lastName') or '',
            }
            email_val = normalized.get('email')
            phone_val = normalized.get('phone')
            if email_val is None:
                reservee['email'] = ''
            else:
                reservee['email'] = email_val
            if phone_val is None:
                reservee['phone'] = ''
            else:
                reservee['phone'] = phone_val

            payload = {
                "reservation": {
                    "details": {
                        "partySize": normalized['partySize'],
                        "startDate": normalized['startDate'],
                        "reservationLocationId": location_id,
                        "locationId": location_id,
                    },
                    "reservee": reservee,
                    "teamMessage": normalized.get('teamMessage'),
                    "status": normalize_wix_reservation_status(normalized.get('status'), default='RESERVED'),
                }
            }
            if normalized.get('endDate'):
                payload['reservation']['details']['endDate'] = normalized['endDate']
            url = f"{WIX_BASE_URL}/reservations"
            resp = wix_requests.post(url, headers=wix_headers(), json=payload, timeout=25)
            resp.raise_for_status()
            return resp.status_code, resp.json()

        def wix_patch_reservation(wix_id, *, start_date=None, end_date=None, status=None, team_message=None, party_size=None, reservee_first=None, reservee_last_raw=None, email=None, phone=None):
            kwargs = {k: v for k, v in locals().items() if k not in ('wix_id', 'kwargs')}
            if all(v is None for k, v in kwargs.items() if k != 'wix_id'):
                return None, None
            get_url = f"{WIX_BASE_URL}/reservations/{wix_id}"
            get_resp = wix_requests.get(get_url, headers={k: v for k, v in wix_headers().items() if k != 'Content-Type'}, timeout=25)
            get_resp.raise_for_status()
            current = get_resp.json()
            reservation_data = current.get('reservation', current)
            revision = reservation_data.get('revision')
            update_payload = {"reservation": {"revision": revision}}

            need_details = (start_date is not None) or (end_date is not None) or (party_size is not None)
            if need_details:
                details = {}
                if start_date is not None:
                    details['startDate'] = start_date
                if end_date is not None:
                    details['endDate'] = end_date
                if party_size is not None:
                    details['partySize'] = int(party_size)
                update_payload['reservation']['details'] = details

            need_reservee = any(v is not None for v in (reservee_first, reservee_last_raw, email, phone))
            if need_reservee:
                old_reservee = reservation_data.get('reservee') or {}
                reservee = dict(old_reservee)
                if reservee_first is not None:
                    reservee['firstName'] = prefix_full_name_first_name(reservee_first)
                if reservee_last_raw is not None:
                    reservee['lastName'] = strip_name_prefix(reservee_last_raw)
                if email is not None:
                    reservee['email'] = '' if email is None else email
                if phone is not None:
                    reservee['phone'] = '' if phone is None else phone
                update_payload['reservation']['reservee'] = reservee

            if status is not None:
                update_payload['reservation']['status'] = status
            if team_message is not None:
                update_payload['reservation']['teamMessage'] = team_message

            patch_url = f"{WIX_BASE_URL}/reservations/{wix_id}"
            patch_resp = wix_requests.patch(patch_url, headers=wix_headers(), json=update_payload, timeout=25)
            patch_resp.raise_for_status()
            return patch_resp.status_code, patch_resp.json()

        payload = request.data
        if payload is None or payload == '':
            return Response({'error': 'Empty body'}, status=status.HTTP_400_BAD_REQUEST)

        raw_items = None
        if isinstance(payload, dict):
            if isinstance(payload.get('reservations'), list):
                raw_items = payload['reservations']
            elif isinstance(payload.get('data'), dict) and isinstance((payload.get('data') or {}).get('dayReservations'), list):
                raw_items = payload['data']['dayReservations']
            elif 'id' in payload or 'mealDate' in payload:
                raw_items = [payload]
        elif isinstance(payload, list):
            raw_items = payload

        if not isinstance(raw_items, list):
            return Response({'error': 'payload must include reservations[] or raw TheFork dayReservations or single reservation object'}, status=status.HTTP_400_BAD_REQUEST)

        normalized_items = []
        validation_errors = []
        for idx, r in enumerate(raw_items):
            if not isinstance(r, dict):
                validation_errors.append({'index': idx, 'error': 'item must be object'})
                continue
            customer = r.get('customer') if isinstance(r.get('customer'), dict) else {}
            source_id = (r.get('id') or '').strip() if isinstance(r.get('id'), str) else ''
            if not source_id:
                validation_errors.append({'index': idx, 'error': 'missing source id (id)'})
                continue

            meal_date_raw = r.get('mealDate')
            start_dt = parse_iso_to_paris(meal_date_raw)
            if start_dt is None:
                validation_errors.append({'index': idx, 'sourceId': source_id, 'error': 'invalid mealDate/startDate'})
                continue

            end_date_raw = r.get('mealEndAt')
            end_dt = parse_iso_to_paris(end_date_raw) if end_date_raw else None

            try:
                party_size = int(r.get('partySize') or 0)
            except Exception:
                party_size = 0
            if party_size <= 0:
                validation_errors.append({'index': idx, 'sourceId': source_id, 'error': 'invalid partySize'})
                continue

            first_name_raw = strip_name_prefix(customer.get('firstName') or r.get('firstName') or '')
            last_name_raw = strip_name_prefix(customer.get('lastName') or r.get('lastName') or '')
            first_name_prefixed = prefix_full_name_first_name(first_name_raw)
            email_raw = (customer.get('email') or r.get('email'))
            phone_raw = (customer.get('phone') or r.get('phone'))

            raw_status = r.get('status')
            canceled_flag = is_canceled_status(raw_status)
            target_status = normalize_wix_reservation_status(raw_status, default='RESERVED')
            if canceled_flag:
                target_status = 'CANCELED'

            customer_note = customer.get('notes') if isinstance(customer, dict) else None
            if customer_note is None:
                customer_note = r.get('customerNote')
            restaurant_note = r.get('restaurantNote')

            cancellation_ts = None
            if isinstance(r.get('cancellation'), dict):
                cancellation_ts = (r['cancellation'].get('timestamp') or '').strip() or None

            normalized_items.append({
                'index': idx,
                'sourceId': source_id,
                'startDate': (meal_date_raw if isinstance(meal_date_raw, str) else start_dt.isoformat()),
                'endDate': (end_date_raw if isinstance(end_date_raw, str) else (end_dt.isoformat() if end_dt else None)),
                'startDt': start_dt,
                'endDt': end_dt,
                'partySize': party_size,
                'firstName': first_name_raw,
                'firstNamePrefixed': first_name_prefixed,
                'lastNameRaw': last_name_raw,
                'email': email_raw,
                'phone': phone_raw,
                'status': target_status,
                'isCanceled': canceled_flag,
                'rawStatus': raw_status,
                'cancellationTs': cancellation_ts,
                'reservationLocationId': r.get('reservationLocationId') or r.get('locationId') or WIX_DEFAULT_LOCATION_ID,
                'customerNote': customer_note,
                'restaurantNote': restaurant_note,
            })

        if validation_errors:
            return Response({'error': 'invalid reservations', 'validationErrors': validation_errors}, status=status.HTTP_400_BAD_REQUEST)

        date_to_wix_cache = {}
        results = []
        summary = {
            'total': len(normalized_items),
            'created': 0,
            'patched': 0,
            'status_patched': 0,
            'info_patched': 0,
            'skipped': 0,
            'failed': 0,
            'ambiguous': 0
        }

        for item in normalized_items:
            idx = item['index']
            source_id = item['sourceId']
            try:
                date_str = to_paris_date_str(item['startDt'])
                wix_list = date_to_wix_cache.get(date_str)
                if wix_list is None:
                    wix_list = fetch_wix_reservations_for_date(date_str)
                    date_to_wix_cache[date_str] = wix_list

                matched = []
                for wr in wix_list:
                    wr_res = wr.get('reservation', wr)
                    wr_team = wr_res.get('teamMessage')
                    wr_id = extract_source_id(wr_team)
                    if wr_id and wr_id == source_id:
                        matched.append(wr)

                if len(matched) > 1:
                    summary['ambiguous'] += 1
                    results.append({
                        'index': idx,
                        'sourceId': source_id,
                        'action': 'ambiguous',
                        'matchedWixIds': [w.get('id') or (w.get('reservation') or {}).get('id') for w in matched]
                    })
                    continue

                if len(matched) == 0:
                    if item['isCanceled']:
                        summary['skipped'] += 1
                        results.append({
                            'index': idx,
                            'sourceId': source_id,
                            'action': 'skipped_canceled',
                            'message': 'TheFork reservation already canceled; skipped creation on Wix'
                        })
                        continue
                    team_msg = build_team_message(
                        source_id,
                        item['customerNote'],
                        item['restaurantNote'],
                        item['rawStatus']
                    )
                    create_item = dict(item)
                    create_item['teamMessage'] = team_msg
                    create_item['firstName'] = item['firstNamePrefixed']
                    create_item['lastName'] = item['lastNameRaw']
                    try:
                        status_code, resp_data = wix_create_reservation(create_item)
                        created_res = resp_data.get('reservation', resp_data) if isinstance(resp_data, dict) else {}
                        wix_id = resp_data.get('id') or created_res.get('id')
                        summary['created'] += 1
                        results.append({
                            'index': idx,
                            'sourceId': source_id,
                            'action': 'created',
                            'wixReservationId': wix_id,
                            'startDate': item['startDate'],
                            'endDate': item['endDate'],
                            'partySize': item['partySize'],
                            'firstName': item['firstNamePrefixed'],
                            'lastName': item['lastNameRaw'],
                            'email': item['email'],
                            'phone': item['phone'],
                            'statusWrittenToWix': item['status'],
                        })
                    except wix_requests.exceptions.HTTPError as e:
                        summary['failed'] += 1
                        detail = str(e)
                        try:
                            if e.response is not None:
                                detail = f"HTTP {e.response.status_code} {e.response.text[:800]}"
                        except Exception:
                            pass
                        results.append({'index': idx, 'sourceId': source_id, 'action': 'failed', 'error': f'create failed: {detail}'})
                    except Exception as e:
                        summary['failed'] += 1
                        results.append({'index': idx, 'sourceId': source_id, 'action': 'failed', 'error': f'create failed: {e}'})
                    continue

                wix_res = matched[0]
                wix_res_data = wix_res.get('reservation', wix_res)
                wix_id = wix_res.get('id') or wix_res_data.get('id')
                wix_details = wix_res_data.get('details') or {}
                wix_reservee = wix_res_data.get('reservee') or {}
                wix_start_dt = parse_iso_to_paris(wix_details.get('startDate'))
                wix_end_dt = parse_iso_to_paris(wix_details.get('endDate'))
                wix_current_status = wix_res_data.get('status')
                wix_current_team = wix_res_data.get('teamMessage')

                try:
                    wix_party_size = int(wix_details.get('partySize') or 0)
                except Exception:
                    wix_party_size = None

                wix_first = wix_reservee.get('firstName')
                wix_last = wix_reservee.get('lastName')
                wix_first_raw = strip_name_prefix(wix_first)
                wix_last_raw = strip_name_prefix(wix_last)
                wix_email = wix_reservee.get('email')
                wix_phone = wix_reservee.get('phone')

                same_start = (wix_start_dt is not None and minute_key(wix_start_dt) == minute_key(item['startDt']))
                if item['endDt'] is None:
                    # TheFork did not provide an end time, so ignore Wix endDate drift.
                    need_time_patch = not same_start
                else:
                    if wix_end_dt is not None and minute_key(item['endDt']) == minute_key(wix_end_dt):
                        same_end = True
                    else:
                        same_end = False
                    need_time_patch = not (same_start and same_end)

                if item['isCanceled']:
                    desired_status = 'CANCELED'
                else:
                    desired_status = normalize_wix_reservation_status(item['rawStatus'], default='RESERVED')
                need_status_patch = (str(wix_current_status).strip().upper() != str(desired_status).strip().upper())

                desired_team_msg = build_team_message(
                    source_id,
                    item['customerNote'],
                    item['restaurantNote'],
                    item['rawStatus'],
                    extra={"cancellationAt": item['cancellationTs']} if item['isCanceled'] and item['cancellationTs'] else None
                )
                need_team_patch = (str(wix_current_team or '') != str(desired_team_msg or ''))

                patch_party_size = None
                patch_first = None
                patch_last_raw = None
                patch_email = None
                patch_phone = None
                info_changed = False

                if wix_party_size is None or wix_party_size != int(item['partySize']):
                    patch_party_size = int(item['partySize'])
                    info_changed = True
                if not eq_blank(wix_first, item['firstNamePrefixed']):
                    patch_first = (item['firstName'] or '')
                    info_changed = True
                if not eq_blank(wix_last, item['lastNameRaw']):
                    patch_last_raw = item['lastNameRaw']
                    info_changed = True
                if not eq_blank(wix_email, item['email']):
                    patch_email = item['email']
                    info_changed = True
                if not eq_blank(wix_phone, item['phone']):
                    patch_phone = item['phone']
                    info_changed = True

                if not (need_time_patch or need_status_patch or need_team_patch or info_changed):
                    summary['skipped'] += 1
                    results.append({
                        'index': idx,
                        'sourceId': source_id,
                        'action': 'skipped',
                        'wixReservationId': wix_id,
                        'startDate': item['startDate'],
                        'endDate': item['endDate'],
                        'wixStatus': wix_current_status,
                        'desiredStatus': desired_status,
                    })
                    continue

                try:
                    status_code, patch_resp = wix_patch_reservation(
                        wix_id,
                        start_date=item['startDate'] if need_time_patch else None,
                        end_date=item['endDate'] if need_time_patch and item['endDate'] else None,
                        status=desired_status if need_status_patch else None,
                        team_message=desired_team_msg if need_team_patch else None,
                        party_size=patch_party_size,
                        reservee_first=patch_first,
                        reservee_last_raw=patch_last_raw,
                        email=patch_email,
                        phone=patch_phone,
                    )
                    actions = []
                    if need_time_patch:
                        actions.append('time')
                        summary['patched'] += 1
                    if need_status_patch:
                        actions.append('status')
                        summary['status_patched'] += 1
                    if info_changed:
                        if patch_party_size is not None:
                            actions.append('partySize')
                        if patch_first is not None:
                            actions.append('firstName')
                        if patch_last_raw is not None:
                            actions.append('lastName')
                        if patch_email is not None:
                            actions.append('email')
                        if patch_phone is not None:
                            actions.append('phone')
                        summary['info_patched'] += 1
                    if need_team_patch:
                        actions.append('teamMessage')
                    results.append({
                        'index': idx,
                        'sourceId': source_id,
                        'action': 'patched',
                        'patchedFields': actions,
                        'wixReservationId': wix_id,
                        'oldStartDate': (wix_start_dt.isoformat() if wix_start_dt else None),
                        'oldEndDate': (wix_end_dt.isoformat() if wix_end_dt else None),
                        'oldStatus': wix_current_status,
                        'oldPartySize': wix_party_size,
                        'oldFirstName': wix_first,
                        'oldLastName': wix_last,
                        'oldFirstNameRaw': wix_first_raw,
                        'oldLastNameRaw': wix_last_raw,
                        'oldEmail': wix_email,
                        'oldPhone': wix_phone,
                        'newStartDate': item['startDate'],
                        'newEndDate': item['endDate'],
                        'newStatus': desired_status,
                        'newPartySize': item['partySize'],
                        'newFirstName': item['firstNamePrefixed'],
                        'newLastName': item['lastNameRaw'],
                        'newFirstNameRaw': item['firstName'],
                        'newLastNameRaw': item['lastNameRaw'],
                        'newEmail': item['email'],
                        'newPhone': item['phone'],
                    })
                except wix_requests.exceptions.HTTPError as e:
                    summary['failed'] += 1
                    detail = str(e)
                    try:
                        if e.response is not None:
                            detail = f"HTTP {e.response.status_code} {e.response.text[:800]}"
                    except Exception:
                        pass
                    results.append({'index': idx, 'sourceId': source_id, 'action': 'failed', 'error': f'patch failed: {detail}'})
                except Exception as e:
                    summary['failed'] += 1
                    results.append({'index': idx, 'sourceId': source_id, 'action': 'failed', 'error': f'patch failed: {e}'})
            except wix_requests.exceptions.HTTPError as e:
                summary['failed'] += 1
                detail = str(e)
                try:
                    if e.response is not None:
                        detail = f"HTTP {e.response.status_code} {e.response.text[:800]}"
                except Exception:
                    pass
                results.append({'index': idx, 'sourceId': item.get('sourceId'), 'action': 'failed', 'error': detail})
            except Exception as e:
                summary['failed'] += 1
                results.append({'index': idx, 'sourceId': item.get('sourceId'), 'action': 'failed', 'error': str(e)})

        return Response({
            'processedAt': (dj_timezone.now().astimezone(paris_tz).isoformat() if paris_tz else dj_timezone.now().isoformat()),
            'summary': summary,
            'results': results
        }, status=status.HTTP_200_OK)


class TestUberInView(APIView):
    def post(self, request):
        payload = request.data
        if payload is None or payload == '':
            return Response({"error": "Empty body"}, status=400)

        orders = payload if isinstance(payload, list) else [payload]
        results = []
        created_count = 0
        skipped_count = 0

        def parse_price(formatted):
            s = str(formatted or '')
            chars = []
            for ch in s:
                if ch.isdigit() or ch in ('.', ','):
                    chars.append(ch)
            num = ''.join(chars)
            if not num:
                return Decimal('0')
            if num.count(',') == 1 and num.count('.') == 0:
                num = num.replace(',', '.')
            elif num.count(',') >= 1 and num.count('.') >= 1:
                num = num.replace(',', '')
            try:
                return Decimal(num)
            except Exception:
                return Decimal('0')

        import datetime
        import random
        from django.db import transaction
        try:
            from zoneinfo import ZoneInfo
            paris_tz = ZoneInfo('Europe/Paris')
        except Exception:
            import pytz
            paris_tz = pytz.timezone('Europe/Paris')

        def parse_iso_dt_to_paris(value):
            if not value:
                return None
            s = str(value).strip()
            if not s:
                return None
            if s.endswith('Z'):
                s = s[:-1] + '+00:00'
            try:
                dt = datetime.datetime.fromisoformat(s)
            except Exception:
                return None
            try:
                if dt.tzinfo is None:
                    dt = paris_tz.localize(dt) if hasattr(paris_tz, 'localize') else dt.replace(tzinfo=paris_tz)
                dt_paris = dt.astimezone(paris_tz)
            except Exception:
                return None
            return dt_paris

        def enqueue_print(ticket_id, order_number_str, base_print_id):
            try:
                print_id = str(base_print_id)
                try:
                    n = int(print_id)
                except Exception:
                    n = int(datetime.datetime.now().timestamp() * 1000)
                    print_id = str(n)

                while DataPrint.objects.filter(print_id=print_id).exists():
                    n += 1
                    print_id = str(n)

                ticket_obj = DataTicket.objects.get(ticket_id=ticket_id)
                ticket_data = DataTicketSerializer(ticket_obj).data
                DataPrint.objects.create(
                    print_id=print_id,
                    print_type=5,
                    print_content=json.dumps(ticket_data, ensure_ascii=False, separators=(',', ':'), cls=DjangoJSONEncoder)
                )
            except Exception as e:
                print(f"[UBER_IN] enqueue_print failed ticket={ticket_id} orderNumber={order_number_str}: {e}")

        for o in orders:
            if not isinstance(o, dict):
                results.append({"status": "error", "error": "Invalid payload item. Must be an object."})
                continue

            order_number = o.get('orderNumber')
            if order_number is None or str(order_number).strip() == '':
                results.append({"status": "error", "error": "Missing orderNumber"})
                continue

            order_number_str = str(order_number)
            dup_q = Q(client_name__endswith=order_number_str) | Q(client_name__contains=f"- {order_number_str} - ")
            if DataTicket.objects.filter(dup_q).exists():
                skipped_count += 1
                results.append({"status": "skipped", "orderNumber": order_number_str, "reason": "duplicate"})
                continue

            customer_name = str(o.get('customerName') or '').strip()
            client_name = f"{customer_name} - {order_number_str}" if customer_name else f"- {order_number_str}"

            needs_cutlery = o.get('needsCutlery')
            if needs_cutlery is True:
                client_name = f"{client_name} - √"
            elif needs_cutlery is False:
                client_name = f"{client_name} - X"

            created_dt = parse_iso_dt_to_paris(o.get('createdDate'))
            if created_dt is None and o.get('createdDate'):
                print(f"[UBER_IN] invalid createdDate={o.get('createdDate')}, fallback to now for orderNumber={order_number_str}")

            now_utc = datetime.datetime.now(datetime.timezone.utc)
            ms = int(now_utc.timestamp() * 1000)
            ticket_id = 'T' + str(ms)
            while DataTicket.objects.filter(ticket_id=ticket_id).exists():
                ms += 1
                ticket_id = 'T' + str(ms)

            pickup_dt_source = created_dt if created_dt is not None else datetime.datetime.fromtimestamp(ms / 1000, paris_tz)
            ticket_time_source = datetime.datetime.fromtimestamp(ms / 1000, paris_tz)
            ticket_time = ticket_time_source.strftime('%Y%m%d%H%M%S')
            pickup_time_str = f"{pickup_dt_source.year}{pickup_dt_source.month:02d}{pickup_dt_source.day:02d}{pickup_dt_source.hour:02d}{pickup_dt_source.minute:02d}{pickup_dt_source.second:02d}"

            items = o.get('items') or []
            if not isinstance(items, list):
                items = []

            with transaction.atomic():
                dup_q = Q(client_name__endswith=order_number_str) | Q(client_name__contains=f"- {order_number_str} - ")
                if DataTicket.objects.filter(dup_q).exists():
                    skipped_count += 1
                    results.append({"status": "skipped", "orderNumber": order_number_str, "reason": "duplicate"})
                    continue

                next_delivery_n = DataTicket.objects.filter(type=2).count() + 1
                table_num = f"L{next_delivery_n}"

                ticket_price = parse_price(o.get('totalPrice'))
                ticket_note = o.get('orderNotes')
                if ticket_note is not None:
                    ticket_note = str(ticket_note).strip()
                ticket = DataTicket.objects.create(
                    ticket_id=ticket_id,
                    ticket_time=ticket_time,
                    ticket_pickup_time=pickup_time_str,
                    delivery_time=str(ms),
                    type=2,
                    table_num=table_num,
                    client_name=client_name,
                    ticket_note=ticket_note or None,
                    delivery_platform_id=3,
                    ticket_price=ticket_price,
                )

                db_total = Decimal('0')

                for it in items:
                    if not isinstance(it, dict):
                        continue
                    code = str(it.get('code') or '').strip()
                    if not code:
                        continue

                    qty = it.get('quantity') or 1
                    try:
                        qty = int(qty)
                    except Exception:
                        qty = 1

                    dish_price = DataDish.objects.filter(dcode=code).values_list('dprice', flat=True).first()
                    if dish_price is None:
                        continue

                    db_total += (dish_price or Decimal('0')) * qty

                    now2 = datetime.datetime.now()
                    ms2 = int(now2.timestamp() * 1000)
                    order_id = 'D' + str(ms2) + str(random.randint(100, 999))
                    order_time = now2.strftime('%Y%m%d%H%M%S')

                    DataOrder.objects.create(
                        order_id=order_id,
                        order_time=order_time,
                        code_id=code,
                        quantity=qty,
                        o_note='无备注',
                        tid=ticket,
                    )

                ticket.ticket_reduction = db_total - ticket_price
                ticket.save(update_fields=['ticket_reduction'])

                base_print_id = str(ms)
                transaction.on_commit(
                    lambda tid=ticket.ticket_id, on=order_number_str, bp=base_print_id: enqueue_print(tid, on, bp)
                )

            created_count += 1
            results.append({
                "status": "created",
                "orderNumber": order_number_str,
                "ticket_id": ticket_id,
                "table_num": table_num,
            })

        status_code = 201 if created_count else 200
        return Response({
            "created": created_count,
            "skipped": skipped_count,
            "results": results
        }, status=status_code)


class TestWixAutoSyncSwitchView(APIView):
    def _flag_path(self):
        return getattr(
            settings,
            'WIX_APSCHEDULER_FLAG_FILE',
            '/tmp/restaurant_beta_02_wix_sync.enabled'
        )

    def _read(self):
        default_enabled = bool(getattr(settings, 'WIX_APSCHEDULER_ENABLED', True))
        path = self._flag_path()
        if not os.path.exists(path):
            return default_enabled, 'settings'
        try:
            raw = (open(path).read() or '').strip().lower()
        except Exception:
            return default_enabled, 'settings'
        if raw in ('1', 'true', 'on', 'yes'):
            return True, 'file'
        if raw in ('0', 'false', 'off', 'no'):
            return False, 'file'
        return default_enabled, 'settings'

    def get(self, request):
        enabled, source = self._read()
        return Response({
            'enabled': enabled,
            'source': source,
            'flagFile': self._flag_path()
        })

    def post(self, request):
        enabled_val = None
        if isinstance(request.data, dict):
            enabled_val = request.data.get('enabled')
        if enabled_val is None:
            enabled_val = request.query_params.get('enabled')

        enabled = None
        if isinstance(enabled_val, bool):
            enabled = enabled_val
        elif isinstance(enabled_val, int):
            enabled = bool(enabled_val)
        elif enabled_val is not None:
            s = str(enabled_val).strip().lower()
            if s in ('1', 'true', 'on', 'yes'):
                enabled = True
            elif s in ('0', 'false', 'off', 'no'):
                enabled = False

        if enabled is None:
            return Response(
                {'error': 'enabled must be true/false or 1/0'},
                status=status.HTTP_400_BAD_REQUEST
            )

        path = self._flag_path()
        try:
            open(path, 'w').write('1' if enabled else '0')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        print(f"[WIX_SYNC] api set enabled={enabled} flagFile={path}")
        return Response({
            'enabled': enabled,
            'source': 'file',
            'flagFile': path
        })

    def patch(self, request):
        return self.post(request)


class TestPatchPickupTimeView(APIView):
    def post(self, request):
        import datetime
        from django.db.models import Q
        from django.db import transaction

        try:
            from zoneinfo import ZoneInfo
            paris_tz = ZoneInfo('Europe/Paris')
        except Exception:
            try:
                import pytz
                paris_tz = pytz.timezone('Europe/Paris')
            except Exception:
                return Response({'error': 'timezone unavailable'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        payload = request.data
        if payload is None or payload == '':
            return Response({'error': 'Empty body'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(payload, dict):
            return Response({'error': 'payload must be an object'}, status=status.HTTP_400_BAD_REQUEST)

        order_number = payload.get('orderNumber')
        if order_number is None or str(order_number).strip() == '':
            return Response({'error': 'Missing orderNumber'}, status=status.HTTP_400_BAD_REQUEST)
        order_number_str = str(order_number)

        pick_up_time_raw = payload.get('pickUpTime')
        if not pick_up_time_raw:
            return Response({'error': 'Missing pickUpTime'}, status=status.HTTP_400_BAD_REQUEST)

        s = str(pick_up_time_raw).strip()
        if s.endswith('Z'):
            s = s[:-1] + '+00:00'
        try:
            pick_up_dt = datetime.datetime.fromisoformat(s)
        except Exception as e:
            return Response({'error': f'Invalid pickUpTime: {e}'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if pick_up_dt.tzinfo is None:
                pick_up_dt = paris_tz.localize(pick_up_dt) if hasattr(paris_tz, 'localize') else pick_up_dt.replace(tzinfo=paris_tz)
            pick_up_paris = pick_up_dt.astimezone(paris_tz)
        except Exception as e:
            return Response({'error': f'pickUpTime timezone conversion failed: {e}'}, status=status.HTTP_400_BAD_REQUEST)

        pickup_time_str = (
            f"{pick_up_paris.year}"
            f"{pick_up_paris.month:02d}"
            f"{pick_up_paris.day:02d}"
            f"{pick_up_paris.hour:02d}"
            f"{pick_up_paris.minute:02d}"
            f"{pick_up_paris.second:02d}"
        )

        dup_q = Q(client_name__endswith=order_number_str) | Q(client_name__contains=f"- {order_number_str} - ")

        try:
            with transaction.atomic():
                tickets = list(DataTicket.objects.filter(dup_q).order_by('-ticket_time'))
                if not tickets:
                    return Response(
                        {'error': f'ticket not found for orderNumber={order_number_str}',
                         'orderNumber': order_number_str},
                        status=status.HTTP_404_NOT_FOUND
                    )
                if len(tickets) > 1:
                    ticket_ids = [t.ticket_id for t in tickets]
                    return Response(
                        {'error': f'multiple tickets matched orderNumber={order_number_str}',
                         'orderNumber': order_number_str,
                         'matchedTicketIds': ticket_ids},
                        status=status.HTTP_409_CONFLICT
                    )
                ticket = tickets[0]
                old_value = ticket.ticket_pickup_time
                ticket.ticket_pickup_time = pickup_time_str
                ticket.save(update_fields=['ticket_pickup_time'])
        except Exception as e:
            return Response(
                {'error': f'update failed: {e}', 'orderNumber': order_number_str},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'status': 'updated',
            'orderNumber': order_number_str,
            'ticket_id': ticket.ticket_id,
            'client_name': ticket.client_name,
            'old_ticket_pickup_time': old_value,
            'new_ticket_pickup_time': pickup_time_str,
        }, status=status.HTTP_200_OK)


class WixReservationDetailView(APIView):
    def get(self, request, pk):
        url = f"{WIX_BASE_URL}/reservations/{pk}?fieldsets=FULL"
        headers = {
            "Authorization": WIX_API_KEY,
            "wix-site-id": WIX_SITE_ID
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return Response(response.json())
        except requests.exceptions.RequestException as e:
            status_code = 500
            details = str(e)
            if e.response is not None:
                status_code = e.response.status_code
                try:
                    details = e.response.json()
                except:
                    details = e.response.text
            return Response({"error": details}, status=status_code)

    def patch(self, request, pk):
        url = f"{WIX_BASE_URL}/reservations/{pk}"
        headers = {
            "Authorization": WIX_API_KEY,
            "wix-site-id": WIX_SITE_ID,
            "Content-Type": "application/json"
        }
        try:
            get_resp = requests.get(url, headers=headers)
            get_resp.raise_for_status()
            current = get_resp.json()
            reservation_data = current.get('reservation', current)
            current_revision = reservation_data.get('revision')
        except Exception as e:
            return Response({"error": f"Failed to fetch current revision: {str(e)}"}, status=500)

        update_payload = {"reservation": {"revision": current_revision, "details": {}, "reservee": {}}}

        if 'partySize' in request.data:
            update_payload['reservation']['details']['partySize'] = request.data['partySize']
        if 'startDate' in request.data:
            update_payload['reservation']['details']['startDate'] = request.data['startDate']
        if 'endDate' in request.data:
            update_payload['reservation']['details']['endDate'] = request.data['endDate']

        table_ids = None
        if 'tableIds' in request.data:
            table_ids = request.data['tableIds']
        elif 'tablesIds' in request.data:
            table_ids = request.data['tablesIds']
        elif 'tables' in request.data and isinstance(request.data['tables'], dict) and 'ids' in request.data['tables']:
            table_ids = request.data['tables']['ids']
        if table_ids is not None:
            if isinstance(table_ids, str):
                table_ids = [table_ids]
            update_payload['reservation']['details']['tableIds'] = table_ids
            update_payload['reservation']['details']['tables'] = {"ids": table_ids}

        if 'firstName' in request.data:
            update_payload['reservation']['reservee']['firstName'] = request.data['firstName']
        if 'lastName' in request.data:
            update_payload['reservation']['reservee']['lastName'] = request.data['lastName']
        if 'email' in request.data:
            update_payload['reservation']['reservee']['email'] = request.data['email']
        if 'phone' in request.data:
            update_payload['reservation']['reservee']['phone'] = request.data['phone']

        if 'teamMessage' in request.data:
            update_payload['reservation']['teamMessage'] = request.data['teamMessage']
        if 'status' in request.data:
            normalized_status = normalize_wix_reservation_status(request.data['status'])
            if normalized_status is None:
                return Response(
                    {
                        "error": "Invalid reservation status",
                        "received": request.data['status'],
                        "allowed": sorted(WIX_VALID_RESERVATION_STATUSES),
                    },
                    status=400
                )
            update_payload['reservation']['status'] = normalized_status

        if not update_payload['reservation']['details']:
            del update_payload['reservation']['details']
        if not update_payload['reservation']['reservee']:
            del update_payload['reservation']['reservee']

        try:
            resp = requests.patch(url, headers=headers, json=update_payload)
            resp.raise_for_status()
            return Response(resp.json())
        except requests.exceptions.RequestException as e:
            status_code = 500
            details = str(e)
            if e.response is not None:
                status_code = e.response.status_code
                try:
                    details = e.response.json()
                except:
                    details = e.response.text
            return Response({"error": details}, status=status_code)



class WixOnlineOrdersView(APIView):
    def get(self, request, mode=None):
        url = WIX_ECOM_ORDERS_SEARCH_URL
        api_key = getattr(settings, 'WIX_API_KEY', None) or WIX_API_KEY
        site_id = getattr(settings, 'WIX_SITE_ID', None) or WIX_SITE_ID
        headers = {
            "Authorization": api_key,
            "wix-site-id": site_id,
            "Content-Type": "application/json"
        }

        body = {
            "sort": [{"fieldName": "createdDate", "order": "DESC"}],
            "cursorPaging": {}
        }

        limit = request.query_params.get('limit')
        cursor = request.query_params.get('cursor')

        if limit is not None:
            try:
                parsed_limit = int(limit)
            except ValueError:
                return Response({"error": "Invalid limit. Must be an integer."}, status=400)
            if parsed_limit <= 0:
                return Response({"error": "Invalid limit. Must be a positive integer."}, status=400)
            body['cursorPaging']['limit'] = min(parsed_limit, 100)
        else:
            body['cursorPaging']['limit'] = 100

        if cursor:
            body['cursorPaging']['cursor'] = cursor

        try:
            debug_mode = request.query_params.get('debug') in ('1', 'true', 'True')
            target_limit = (body.get('cursorPaging') or {}).get('limit') or 100

            date_filter = request.query_params.get('date') if str(mode) == '1' else None

            kind_param = request.query_params.get('kind')
            if kind_param is None:
                kind_param = 'order'

            def extract_code(text):
                if not text:
                    return ''
                match = re.search(r'\[([^\[\]]+)\]', str(text))
                return match.group(1).strip() if match else ''

            response = requests.post(url, headers=headers, json={"search": body})
            response.raise_for_status()

            raw = response.json()
            orders = raw.get('orders') or []

            if debug_mode:
                raw_orders = []
                for o in orders:
                    channel_type = ((o.get('channelInfo') or {}).get('type'))
                    billing_contact = ((o.get('billingInfo') or {}).get('contactDetails') or {})
                    recipient_contact = ((o.get('recipientInfo') or {}).get('contactDetails') or {})
                    line_items = o.get('lineItems') or []
                    line_item_names = []
                    line_item_details = []
                    for li in line_items:
                        pn = li.get('productName')
                        if isinstance(pn, dict):
                            name = pn.get('original') or pn.get('translated')
                        else:
                            name = pn
                        if name:
                            line_item_names.append(name)

                        modifier_labels = []
                        seen_modifier_labels = set()
                        modifier_groups = li.get('modifierGroups') or []
                        for mg in modifier_groups:
                            modifiers = (mg or {}).get('modifiers') or []
                            for m in modifiers:
                                label = (m or {}).get('label')
                                if isinstance(label, dict):
                                    label_name = label.get('original') or label.get('translated')
                                else:
                                    label_name = label
                                if label_name and label_name not in seen_modifier_labels:
                                    seen_modifier_labels.add(label_name)
                                    modifier_labels.append(label_name)

                        description_lines = []
                        seen_description_lines = set()
                        for dl in (li.get('descriptionLines') or []):
                            text_val = None
                            if isinstance(dl, dict):
                                text_val = dl.get('plainText') or dl.get('text') or dl.get('value') or dl.get('line')
                            else:
                                text_val = dl

                            if isinstance(text_val, dict):
                                text = text_val.get('original') or text_val.get('translated')
                            else:
                                text = text_val

                            if text is not None:
                                text = str(text).strip()
                            if text and text not in seen_description_lines:
                                seen_description_lines.add(text)
                                description_lines.append(text)

                        line_item_details.append({
                            'name': name,
                            'quantity': li.get('quantity') or 1,
                            'code': extract_code(name) or '',
                            'modifierLabels': modifier_labels,
                            'descriptionLines': description_lines
                        })

                    normalized_line_item_names = [str(n).strip().casefold() for n in line_item_names]
                    is_reservation = any(
                        n in ('réservation', 'reservation', '订位', '预订', '預訂')
                        for n in normalized_line_item_names
                    )
                    kind = 'reserve' if is_reservation else 'order'

                    if date_filter:
                        created_date_str = str(o.get('createdDate') or '')
                        if not created_date_str.startswith(date_filter):
                            continue

                    raw_orders.append({
                        'id': o.get('id'),
                        'orderNumber': o.get('number'),
                        'createdDate': o.get('createdDate'),
                        'status': o.get('status'),
                        'paymentStatus': o.get('paymentStatus'),
                        'fulfillmentStatus': o.get('fulfillmentStatus'),
                        'channelType': channel_type,
                        'kind': kind,
                        'hasShippingInfo': 'shippingInfo' in o,
                        'hasRecipientInfo': 'recipientInfo' in o,
                        'billingName': ((billing_contact.get('firstName') or '') + ' ' + (billing_contact.get('lastName') or '')).strip(),
                        'recipientName': ((recipient_contact.get('firstName') or '') + ' ' + (recipient_contact.get('lastName') or '')).strip(),
                        'lineItemNames': line_item_names[:5],
                        'lineItems': line_item_details[:10],
                        'keyHints': [k for k in o.keys() if any(x in k.lower() for x in ('ship', 'deliver', 'pickup', 'fulfill', 'method'))]
                    })

                return Response({
                    'rawTotal': len(orders),
                    'rawHasShippingInfoCount': sum(1 for r in raw_orders if r.get('hasShippingInfo')),
                    'rawOrders': raw_orders[:target_limit]
                })

            cleaned = []
            for o in orders:
                if date_filter:
                    cds = str(o.get('createdDate') or '')
                    if not cds.startswith(date_filter):
                        continue
                line_items = o.get('lineItems') or []
                line_item_names = []
                for li in line_items:
                    pn = li.get('productName')
                    if isinstance(pn, dict):
                        name = pn.get('original') or pn.get('translated')
                    else:
                        name = pn
                    if name:
                        line_item_names.append(name)

                normalized_line_item_names = [str(n).strip().casefold() for n in line_item_names]
                is_reservation = any(
                    n in ('réservation', 'reservation', '订位', '预订', '預訂')
                    for n in normalized_line_item_names
                )
                kind = 'reserve' if is_reservation else 'order'

                if kind_param in ('order', 'reserve') and kind != kind_param:
                    continue

                shipping_info = o.get('shippingInfo')
                shipping_method = shipping_info.get('title') if isinstance(shipping_info, dict) else None

                contact = (o.get('billingInfo') or {}).get('contactDetails') or {}
                first_name = contact.get('firstName') or ''
                last_name = contact.get('lastName') or ''
                customer_name = (first_name + ' ' + last_name).strip()

                items = []
                for li in line_items:
                    product_name = li.get('productName')
                    if isinstance(product_name, dict):
                        name = product_name.get('original') or product_name.get('translated')
                    else:
                        name = product_name

                    modifier_labels = []
                    seen_modifier_labels = set()
                    modifier_groups = li.get('modifierGroups') or []
                    for mg in modifier_groups:
                        modifiers = (mg or {}).get('modifiers') or []
                        for m in modifiers:
                            label = (m or {}).get('label')
                            if isinstance(label, dict):
                                label_name = label.get('original') or label.get('translated')
                            else:
                                label_name = label
                            if label_name and label_name not in seen_modifier_labels:
                                seen_modifier_labels.add(label_name)
                                modifier_labels.append(label_name)

                    description_lines = []
                    seen_description_lines = set()
                    for dl in (li.get('descriptionLines') or []):
                        text_val = None
                        if isinstance(dl, dict):
                            text_val = dl.get('plainText') or dl.get('text') or dl.get('value') or dl.get('line')
                        else:
                            text_val = dl

                        if isinstance(text_val, dict):
                            text = text_val.get('original') or text_val.get('translated')
                        else:
                            text = text_val

                        if text is not None:
                            text = str(text).strip()
                        if text and text not in seen_description_lines:
                            seen_description_lines.add(text)
                            description_lines.append(text)

                    quantity = li.get('quantity') or 1
                    code = extract_code(name) or ''
                    if code:
                        items.append({
                            'name': name,
                            'quantity': quantity,
                            'code': code
                        })
                    else:
                        expanded = []
                        for entry in (modifier_labels or []) + (description_lines or []):
                            expanded.append({
                                'name': entry,
                                'quantity': 1,
                                'code': extract_code(entry) or ''
                            })
                        if expanded:
                            items.extend(expanded)
                        else:
                            items.append({
                                'name': name,
                                'quantity': quantity,
                                'code': ''
                            })

                cleaned.append({
                    'id': o.get('id'),
                    'orderNumber': o.get('number'),
                    'createdDate': o.get('createdDate'),
                    'customerName': customer_name,
                    'totalPrice': ((o.get('priceSummary') or {}).get('total') or {}).get('formattedAmount'),
                    'paymentStatus': o.get('paymentStatus'),
                    'paidAmount': ((o.get('balanceSummary') or {}).get('paid') or {}).get('amount'),
                    'balanceAmount': ((o.get('balanceSummary') or {}).get('balance') or {}).get('amount'),
                    'shippingMethod': shipping_method,
                    'items': items
                })

            return Response({
                'orders': cleaned,
                'total': len(cleaned)
            })
        except requests.exceptions.RequestException as e:
            status_code = 500
            details = str(e)
            if e.response is not None:
                status_code = e.response.status_code
                try:
                    details = e.response.json()
                except:
                    details = e.response.text
            return Response({"error": details}, status=status_code)
