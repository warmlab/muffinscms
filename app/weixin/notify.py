from urllib.parse import urlencode
from urllib.request import urlopen

from flask import json

from ..models import Partment
from ..logging import logger

def access_weixin_api(url, body, **kwargs):
    params = urlencode(kwargs)
    final_url = '?'.join([url, params])
    data = body.encode('utf-8')
    with urlopen(final_url, data=data) as f:
        result = f.read().decode('utf-8')

        info = json.loads(result)

        return info

def notify_admins(order, shoppoint_id):
    # 获取公众号的partment
    web = Partment.query.filter_by(shoppoint_id=shoppoint_id, code='web').first()
    if not web:
        return
    # 提醒接龙发起者有新订单了
    products = ['x'.join([p.product.name, str(p.amount)]) for p in order.products]

    data = {
            "first": {
                "value": order.code if not order.index else '拼团编号: ' + str(order.index)
                },
            "keyword1": {
                "value": ' '.join(products)
                },
            "keyword2":{
                "value": '￥' + str(order.cost/100)
                },
            "keyword3":{
                "value": order.member_openid.nickname
                },
            "keyword4":{
                "value": '储值卡支付，会员: ' + order.member_openid.name + '[' + order.member_openid.phone + ']' if order.payment == 2 else "微信已支付" if order.pay_time and order.payment_code else "微信未支付"
                },
            "keyword5":{
                "value": order.note
                },
            "remark": {
                "value": '送货地址: ' + order.address.name + '[' + order.address.phone + ']' + order.address.address if order.address.delivery_way == 2 else '取货地址: ' + order.address.address
                
                }
            }

    for u in ('ox4bxso53hocK9iyC-eKNll-qRoI',
            'ox4bxsnBj7xpsSndE4TOg_LY-IKQ', 'ox4bxsn8gkt_IqaVzQIPRkuep4v8'):
        j = {
            'template_id': 'pkl-0GTnDHxthXtR381PPNAooBT1JwUYuuP-YK1nRSA',
            'touser': u,
            'data': data,
            'url': 'http://wecakes.com'
            }
        body = json.dumps(j)
        result = access_weixin_api('https://api.weixin.qq.com/cgi-bin/message/template/send', body, access_token=web.get_access_token())

        logger.debug('notify admin result: %s', result)

def notify_customer(order, partment, form_id):
    # 提醒顾客订单已经付款
    data = {
        "keyword1": {
            "value": order.index,
            },
        "keyword2": {
            "value": order.code,
            },
        "keyword3":{
            "value": '￥' + str(order.cost/100),
            },
        "keyword4":{
            "value": ' '.join(["x".join([p.product.name, str(p.amount)]) for p in order.products]),
            },
        "keyword5":{
            "value": "自提" if order.address.delivery_way==1 else "快递"
            },
        "keyword6":{
            "value": '-'.join([order.address.name, order.address.phone])
            },
        "keyword7":{
            "value": order.address.address
            },
        "keyword8":{
            "value": '您已拼团成功，如需退款，请务必在截单前申请退款，截单后不予退款，谢谢理解'
            },
        "keyword9":{
            "value": order.note,
            },
        "keyword10":{
            "value": '如有疑问，可以拨打客服电话: 13370836021'
            }
    }
    j = {
        'template_id': 'pRZaMpRAWQLuyFVtGXaWQBbsJ7ECHjPBKAWRCUBRfps',
        'touser': order.openid,
        'form_id': form_id,
        #'url':  url_for('shop.payresult', _external=True, ticket_code=order.code),
        'data': data,
        'emphasis_keyword': 'keyword1.DATA'
        }
    body = json.dumps(j)
    access_weixin_api('https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send', body, access_token=partment.get_access_token())

