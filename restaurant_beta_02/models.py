# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class DataDishCategory(models.Model):
    class Meta:
        managed = True
        db_table = 'data_dish_category'
        verbose_name = '菜品类别'

    def __str__(self):
        return 'id：%s | category_id：%s | subcategory_id：%s | category：%s | subcategory：%s ' % (
            self.id, self.category_id, self.subcategory_id, self.category, self.subcategory)

    id = models.AutoField(primary_key=True)
    category_id = models.IntegerField()
    subcategory_id = models.IntegerField(unique=True)
    category = models.CharField(verbose_name='类别名', max_length=10)
    subcategory = models.CharField(verbose_name='子类别名', max_length=10)


class DataDish(models.Model):
    did = models.AutoField(primary_key=True)
    dcategory = models.CharField(max_length=20)
    dsubcategory = models.ForeignKey(DataDishCategory, verbose_name='类别', db_column='dsubcategory', to_field='subcategory_id', on_delete=models.CASCADE)
    dcode = models.CharField(max_length=10, unique=True)
    dname = models.CharField(max_length=255)
    dprice = models.DecimalField(max_digits=10, decimal_places=2)
    dtax = models.DecimalField(max_digits=3, decimal_places=2)
    dingredients = models.CharField(max_length=512, blank=True, null=True)
    dondelete = models.IntegerField(default=0)

    class Meta:
        managed = True
        db_table = 'data_dish'
        verbose_name = '菜品清单'

    def __str__(self):
        return '菜名：%s  价格：%s' % (self.dname, self.dprice)


class DataDeliveryMan(models.Model):
    class Meta:
        managed = True
        db_table = 'data_delivery_man'
        verbose_name = '送餐员'

    def __str__(self):
        return '编号：%s | 代码：%s | 姓名：%s' % (self.delivery_man_id, self.delivery_man_code, self.delivery_man_name)

    delivery_man_id = models.AutoField(primary_key=True, verbose_name='编号')
    delivery_man_code = models.CharField(max_length=5, verbose_name='代码')
    delivery_man_name = models.CharField(max_length=20, verbose_name='姓名')


class DataDeliveryPlatform(models.Model):
    class Meta:
        managed = True
        db_table = 'data_delivery_platform'
        verbose_name = '送餐平台'

    def __str__(self):
        return '编号：%s | 代码：%s | 平台名：%s' % (self.platform_id, self.platform_code, self.platform)

    platform_id = models.AutoField(primary_key=True, verbose_name='编号')
    platform_code = models.CharField(max_length=5, verbose_name='代码')
    platform = models.CharField(max_length=20, verbose_name='平台名')
    platform_commission = models.DecimalField(verbose_name='平台抽成', default=0, max_digits=3, decimal_places=2)


class DataTicket(models.Model):
    ticket_id = models.CharField(primary_key=True, max_length=20)
    ticket_time = models.CharField(verbose_name='订单时间', max_length=20)
    type = models.IntegerField(verbose_name='订单类型', default=0, choices=((0, '堂食'), (1, '打包'), (2, '外送')))
    table_num = models.CharField(verbose_name='订单号/桌号', max_length=20)
    person_quantity = models.IntegerField(default=1)
    client_name = models.CharField(verbose_name='客户姓名', max_length=50, null=True, blank=True)
    client_address = models.CharField(verbose_name='客户地址', max_length=250, null=True, blank=True)
    client_telephone = models.CharField(verbose_name='客户电话', max_length=20, null=True, blank=True)
    ticket_note = models.CharField(verbose_name='订单备注', max_length=255, null=True, blank=True)
    ticket_status = models.IntegerField(verbose_name='订单状态', default=1, choices=((0, '预约订单'), (1, '准备中'), (2, '已完成'), (3, '已取消')))
    payment_status = models.IntegerField(verbose_name='支付状态', default=0, choices=((0, '未付款'), (1, '付款中'), (2, '已付款')))
    ticket_price = models.DecimalField(verbose_name='整单价格', default=0, max_digits=10, decimal_places=2)
    ticket_discount = models.DecimalField(verbose_name='整单折扣', default=1.00, max_digits=3, decimal_places=2)
    pay_by_cash = models.DecimalField(verbose_name='现金支付', default=0, max_digits=10, decimal_places=2)
    pay_by_ticket = models.DecimalField(verbose_name='饭票支付', default=0, max_digits=10, decimal_places=2)
    pay_by_card = models.DecimalField(verbose_name='银行卡支付', default=0, max_digits=10, decimal_places=2)
    pay_by_check = models.DecimalField(verbose_name='支票支付', default=0, max_digits=10, decimal_places=2)
    pay_by_transfer = models.DecimalField(verbose_name='转账支付', default=0, max_digits=10, decimal_places=2)
    pay_by_wechat = models.DecimalField(verbose_name='微信支付', default=0, max_digits=10, decimal_places=2)
    pay_by_alipay = models.DecimalField(verbose_name='支付宝支付', default=0, max_digits=10, decimal_places=2)
    pay_by_another = models.DecimalField(verbose_name='其他支付', default=0, max_digits=10, decimal_places=2)
    zrapport_condition = models.IntegerField(verbose_name='日结状态', default=0, choices=((0, '未日结算'), (1, '完成日结算')))
    delivery_man = models.ForeignKey(DataDeliveryMan, on_delete=models.CASCADE, verbose_name='送餐员',
                                     db_column='f_delivery_man', default=1)
    delivery_platform = models.ForeignKey(DataDeliveryPlatform, on_delete=models.CASCADE, verbose_name='送餐平台',
                                          db_column='f_delivery_platform', default=12)
    ticket_reduction = models.DecimalField(verbose_name='整单减免', default=0, max_digits=10, decimal_places=2)
    ticket_emergency = models.IntegerField(verbose_name='加急状态', choices=((0, '普通'), (1, '优先'), (2, '最紧急')), default=0)
    finish_time = models.CharField(max_length=32, verbose_name='完成时间', null=True, blank=True)
    ticket_tax10 = models.DecimalField(verbose_name='tva10%', default=0, max_digits=10, decimal_places=2)
    ticket_tax20 = models.DecimalField(verbose_name='tva20%', default=0, max_digits=10, decimal_places=2)
    ticket_tax = models.DecimalField(verbose_name='tva总', default=0, max_digits=10, decimal_places=2)
    delivery_time = models.CharField(verbose_name='配送时间', max_length=30, null=True, blank=True)
    payment_history = models.CharField(verbose_name='付款历史', max_length=255, null=True, blank=True)
    ticket_restaurant_count = models.IntegerField(verbose_name='饭票张数', default=0)

    class Meta:
        db_table = 'data_ticket'
        verbose_name = '订单表'

    def __str__(self):
        return '订单id：%s  订单日期：%s  订单号：%s' % (self.ticket_id, self.ticket_time, self.table_num)


class DataNoteBase(models.Model):
    class Meta:
        managed = True
        db_table = 'data_note_base'
        verbose_name = '备注库'

    def __str__(self):
        return '代号：%s | 备注内容：%s' % (self.id, self.note_content)

    id = models.IntegerField(primary_key=True)
    note_category_id = models.IntegerField(verbose_name='备注类别编号')
    note_category = models.CharField(verbose_name='备注类别', max_length=20)
    note_content = models.CharField(verbose_name='备注内容', max_length=250)
    max = models.IntegerField(verbose_name='最大位数', default=0)
    # note_id = models.IntegerField(unique=True)


class DataSpecialNote(models.Model):
    class Meta:
        managed = True
        db_table = 'data_special_note'
        verbose_name = '备注'

    def __str__(self):
        return self.note

    note_id = models.IntegerField(primary_key=True)
    note = models.CharField(verbose_name='备注内容', max_length=250)
    component = models.CharField(verbose_name='编号明细', max_length=250)


class DataOrder(models.Model):
    order_id = models.CharField(verbose_name='order编号', primary_key=True, max_length=32)  # Field name made lowercase.
    order_time = models.CharField(max_length=32)
    code = models.ForeignKey(DataDish, related_name='orders', db_column='code', to_field='dcode', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    # o_note = models.ForeignKey(DataSpecialNote, db_column='o_note', verbose_name='菜品备注',on_delete=models.CASCADE, default=1)
    o_note = models.CharField(db_column='o_note', verbose_name='菜品备注', max_length=250)
    prepare_status = models.IntegerField(verbose_name='准备状态', default=1, choices=((0, '预定'), (1, '准备中'),  (2, '已备齐'), (3, '已完成')))
    discount_type = models.IntegerField(verbose_name='打折类型', choices=((0, '参与整单打折'), (1, '不参与整单打折')), default=0)
    extra_discount = models.DecimalField(verbose_name='特殊折扣', default=1.00, max_digits=3, decimal_places=2)
    emergency = models.IntegerField(verbose_name='加急状态', choices=((0, '普通'), (1, '优先'), (2, '最紧急')), default=0)
    tid = models.ForeignKey(DataTicket, db_column='tid', on_delete=models.CASCADE, verbose_name='订单id')
    person = models.IntegerField(verbose_name='客户', default=1)
    finish_time = models.CharField(max_length=32, verbose_name='完成时间', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'data_order'
        verbose_name = '订单流水'

    def __str__(self):
        return '流水id：%s  |  数量：%s  |  菜品：%s' % (self.order_id, self.quantity, self.code)


class NoteTest(models.Model):
    class Meta:
        managed = True
        db_table = 'note_test'
        verbose_name = '测试'

    def __str__(self):
        return self.note

    note_id = models.IntegerField(primary_key=True)
    note = models.CharField(verbose_name='备注内容', max_length=250)
    component = models.CharField(verbose_name='编号明细', max_length=250)


class DataPrint(models.Model):
    class Meta:
        managed = True
        db_table = 'data_print'
        verbose_name = '打印队列'

    def __str__(self):
        return self.print_content

    print_id = models.CharField(verbose_name='打印编号', primary_key=True, max_length=32)
    print_type = models.IntegerField(verbose_name='打印类型') # 0:cuisine, 1:salle, 2:yellowT
    print_content = models.TextField(verbose_name='打印内容', max_length=65535)
