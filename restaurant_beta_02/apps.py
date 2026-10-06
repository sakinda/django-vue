from django.apps import AppConfig


class RestaurantBeta02Config(AppConfig):
    name = 'restaurant_beta_02'

    def ready(self):
        import os
        import random
        import re
        import json
        from datetime import datetime, time
        from decimal import Decimal

        import requests
        from django.conf import settings
        from django.db import transaction
        from django.core.serializers.json import DjangoJSONEncoder

        try:
            from zoneinfo import ZoneInfo
        except Exception:
            ZoneInfo = None

        try:
            from apscheduler.schedulers.background import BackgroundScheduler
        except Exception:
            print('[WIX_SYNC] APScheduler not available; wix auto-sync disabled')
            return

        # 不再依赖本地文件锁；每个 Django 进程都启动自己的 Wix 轮询。
        # 这里只防止同一个进程内重复执行 ready() 时重复创建 scheduler。
        pid = os.getpid()
        started_pids = getattr(self.__class__, '_wix_sync_started_pids', set())
        if pid in started_pids:
            return
        started_pids.add(pid)
        self.__class__._wix_sync_started_pids = started_pids

        from .models import DataDish, DataOrder, DataTicket, DataPrint
        from . import views as v

        tz = ZoneInfo('Europe/Paris') if ZoneInfo else None
        if tz is None:
            try:
                import pytz
                tz = pytz.timezone('Europe/Paris')
            except Exception:
                tz = None

        def js_ms(dt):
            return int(dt.timestamp() * 1000)

        def js_time_str(dt):
            return (
                str(dt.year)
                + f"{dt.month:02d}"
                + str(dt.day)
                + f"{dt.hour:02d}"
                + f"{dt.minute:02d}"
                + f"{dt.second:02d}"
            )

        def extract_code(text):
            m = re.search(r'\[([^\[\]]+)\]', str(text or ''))
            return m.group(1).strip() if m else ''

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

        def parse_wix_dt(value):
            if not value:
                return None
            s = str(value)
            if s.endswith('Z'):
                s = s[:-1] + '+00:00'
            try:
                return datetime.fromisoformat(s)
            except Exception:
                return None

        def window_start(now_paris):
            if now_paris.time() < time(17, 0):
                return now_paris.replace(hour=0, minute=0, second=0, microsecond=0)
            if now_paris.time() >= time(17, 0):
                return now_paris.replace(hour=17, minute=0, second=0, microsecond=0)
            return now_paris.replace(hour=0, minute=0, second=0, microsecond=0)

        def fetch_wix_orders(limit=100):
            url = v.WIX_ECOM_ORDERS_SEARCH_URL
            api_key = getattr(settings, 'WIX_API_KEY', None) or v.WIX_API_KEY
            site_id = getattr(settings, 'WIX_SITE_ID', None) or v.WIX_SITE_ID
            headers = {
                'Authorization': api_key,
                'wix-site-id': site_id,
                'Content-Type': 'application/json'
            }
            body = {
                'sort': [{'fieldName': 'createdDate', 'order': 'DESC'}],
                'cursorPaging': {'limit': min(int(limit or 100), 100)}
            }
            r = requests.post(url, headers=headers, json={'search': body}, timeout=25)
            r.raise_for_status()
            return r.json().get('orders') or []

        def expand_items(name, quantity, modifier_labels, description_lines):
            code = extract_code(name)
            if code:
                return [{'code': code, 'quantity': quantity}]
            out = []
            for entry in (modifier_labels or []) + (description_lines or []):
                out.append({'code': extract_code(entry) or '', 'quantity': 1})
            return out

        enabled_flag_path = getattr(
            settings,
            'WIX_APSCHEDULER_FLAG_FILE',
            '/tmp/restaurant_beta_02_wix_sync.enabled'
        )

        def read_enabled():
            default_enabled = bool(getattr(settings, 'WIX_APSCHEDULER_ENABLED', True))
            try:
                if not os.path.exists(enabled_flag_path):
                    return default_enabled, 'settings'
                raw = (open(enabled_flag_path).read() or '').strip().lower()
            except Exception:
                return default_enabled, 'settings'

            if raw in ('1', 'true', 'on', 'yes'):
                return True, 'file'
            if raw in ('0', 'false', 'off', 'no'):
                return False, 'file'
            return default_enabled, 'settings'

        enabled, source = read_enabled()
        state = {'enabled': enabled, 'enabled_source': source}
        print(
            f"[WIX_SYNC] init enabled={state['enabled']} source={state['enabled_source']} "
            f"pid={pid} tz=Europe/Paris interval=60s flagFile={enabled_flag_path}"
        )

        def enqueue_print(ticket_id, order_number_str, base_print_id):
            try:
                print_id = str(base_print_id)
                try:
                    n = int(print_id)
                except Exception:
                    n = js_ms(datetime.now(tz) if tz else datetime.now())
                    print_id = str(n)

                while DataPrint.objects.filter(print_id=print_id).exists():
                    n += 1
                    print_id = str(n)

                ticket_obj = DataTicket.objects.get(ticket_id=ticket_id)
                ticket_data = v.DataTicketSerializer(ticket_obj).data
                DataPrint.objects.create(
                    print_id=print_id,
                    print_type=5,
                    print_content=json.dumps(ticket_data, ensure_ascii=False, separators=(',', ':'), cls=DjangoJSONEncoder)
                )
                print(f"[WIX_SYNC] created ticket={ticket_id} orderNumber={order_number_str} print_id={print_id}")
            except Exception as e:
                print(f"[WIX_SYNC] print enqueue failed ticket={ticket_id} orderNumber={order_number_str}: {e}")

        def sync_once():
            current_enabled, current_source = read_enabled()
            if current_enabled != state['enabled'] or current_source != state['enabled_source']:
                state['enabled'] = current_enabled
                state['enabled_source'] = current_source
                print(f"[WIX_SYNC] toggle enabled={state['enabled']} source={state['enabled_source']}")
            if not state['enabled']:
                return

            now = datetime.now(tz) if tz else datetime.now()
            start = window_start(now)
            today = now.date()

            try:
                raw_orders = fetch_wix_orders(limit=100)
            except Exception as e:
                print(f"[WIX_SYNC] fetch_wix_orders failed: {e}")
                return

            print(f"[WIX_SYNC] tick now={now.isoformat()} start={start.isoformat()} fetched={len(raw_orders)}")

            for o in raw_orders:
                try:
                    created_dt = parse_wix_dt(o.get('createdDate'))
                    if created_dt is None:
                        continue
                    if tz and created_dt.tzinfo is not None:
                        created_dt = created_dt.astimezone(tz)
                    if created_dt.date() != today:
                        continue
                    if created_dt < start:
                        continue
                except Exception as e:
                    print(f"[WIX_SYNC] order time filter failed id={o.get('id')} number={o.get('number')}: {e}")
                    continue

                line_items = o.get('lineItems') or []
                line_item_names = []
                for li in line_items:
                    pn = li.get('productName')
                    if isinstance(pn, dict):
                        n = pn.get('original') or pn.get('translated')
                    else:
                        n = pn
                    if n:
                        line_item_names.append(n)

                normalized = [str(n).strip().casefold() for n in line_item_names]
                is_reservation = any(n in ('réservation', 'reservation', '订位', '预订', '預訂') for n in normalized)
                if is_reservation:
                    continue

                order_number = o.get('number')
                if order_number is None:
                    continue
                order_number_str = str(order_number)
                if DataTicket.objects.filter(client_name__endswith=order_number_str).exists():
                    continue

                billing = (o.get('billingInfo') or {}).get('contactDetails') or {}
                customer_name = ((billing.get('firstName') or '') + ' ' + (billing.get('lastName') or '')).strip()

                payment_status = o.get('paymentStatus')
                if payment_status == 'PAID':
                    client_name = f"(已付){customer_name} - {order_number_str}"
                elif payment_status == 'NOT_PAID':
                    client_name = f"(未付！){customer_name} - {order_number_str}"
                else:
                    client_name = f"{customer_name} - {order_number_str}"

                now2 = datetime.now(tz) if tz else datetime.now()
                ms = js_ms(now2)
                ticket_id = 'T' + str(ms)
                while DataTicket.objects.filter(ticket_id=ticket_id).exists():
                    ms += 1
                    ticket_id = 'T' + str(ms)
                    now2 = datetime.fromtimestamp(ms / 1000, tz) if tz else datetime.fromtimestamp(ms / 1000)
                ticket_time = js_time_str(now2)

                with transaction.atomic():
                    if DataTicket.objects.filter(client_name__endswith=order_number_str).exists():
                        continue

                    if 'next_delivery_n' not in state:
                        state['next_delivery_n'] = DataTicket.objects.filter(type=2).count() + 1

                    table_num = f"L{state['next_delivery_n']}"
                    state['next_delivery_n'] += 1

                    ticket = DataTicket.objects.create(
                        ticket_id=ticket_id,
                        ticket_time=ticket_time,
                        ticket_pickup_time=str(ms),
                        type=2,
                        table_num=table_num,
                        client_name=client_name,
                        delivery_platform_id=7,
                        ticket_price=parse_price(((o.get('priceSummary') or {}).get('total') or {}).get('formattedAmount')),
                    )

                    for li in line_items:
                        pn = li.get('productName')
                        if isinstance(pn, dict):
                            name = pn.get('original') or pn.get('translated')
                        else:
                            name = pn
                        qty = li.get('quantity') or 1
                        try:
                            qty = int(qty)
                        except Exception:
                            qty = 1

                        modifier_labels = []
                        seen_mod = set()
                        for mg in (li.get('modifierGroups') or []):
                            for m in ((mg or {}).get('modifiers') or []):
                                label = (m or {}).get('label')
                                if isinstance(label, dict):
                                    label_name = label.get('original') or label.get('translated')
                                else:
                                    label_name = label
                                if label_name and label_name not in seen_mod:
                                    seen_mod.add(label_name)
                                    modifier_labels.append(label_name)

                        description_lines = []
                        seen_desc = set()
                        for dl in (li.get('descriptionLines') or []):
                            tv = dl.get('plainText') if isinstance(dl, dict) else dl
                            if isinstance(tv, dict):
                                text = tv.get('original') or tv.get('translated')
                            else:
                                text = tv
                            if text is not None:
                                text = str(text).strip()
                            if text and text not in seen_desc:
                                seen_desc.add(text)
                                description_lines.append(text)

                        for e in expand_items(name, qty, modifier_labels, description_lines):
                            code = e.get('code') or ''
                            if not code:
                                continue
                            if not DataDish.objects.filter(dcode=code).exists():
                                continue

                            now3 = datetime.now(tz) if tz else datetime.now()
                            ms3 = js_ms(now3)
                            order_id = 'D' + str(ms3) + str(random.randint(100, 999))
                            order_time = js_time_str(now3)

                            DataOrder.objects.create(
                                order_id=order_id,
                                order_time=order_time,
                                code_id=code,
                                quantity=e.get('quantity') or 1,
                                o_note='无备注',
                                tid=ticket,
                            )

                    base_print_id = str(ms)
                    transaction.on_commit(
                        lambda tid=ticket.ticket_id, on=order_number_str, bp=base_print_id: enqueue_print(tid, on, bp)
                    )

        try:
            sync_once()
        except Exception as e:
            print(f"[WIX_SYNC] initial sync failed: {e}")

        scheduler = BackgroundScheduler(timezone='Europe/Paris')
        scheduler.add_job(sync_once, 'interval', minutes=1, id='wix_sync', replace_existing=True, max_instances=1)
        scheduler.start()
        self._wix_sync_scheduler = scheduler
