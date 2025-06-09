import json
import hashlib
import hmac
import requests
from datetime import datetime
from typing import Dict, Any
from core.momo_config import CONFIG as settings
from db.models import MomoPayment
from sqlalchemy.orm import Session
from core.response import Response, CodeEnum


def create_momo_payment(db: Session, amount: int, order_info: str, user_id: int, cart_data: str = None) -> Dict[str, Any]:
    """
    Tạo thanh toán MoMo
    """
    # Tạo thông tin thanh toán mới
    order_id = MomoPayment.generate_order_id()
    request_id = MomoPayment.generate_request_id()
    
    # Lưu thông tin thanh toán vào database
    payment = MomoPayment(
        order_id=order_id,
        amount=amount,
        order_info=order_info,
        request_id=request_id,
        user_id=user_id,
        cart_data=cart_data
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # Chuẩn bị dữ liệu gửi đến MoMo theo API v2.0 (thêm tham số cho test)
    raw_data = {
        'partnerCode': settings['partner_code'],
        'accessKey': settings['access_key'],
        'requestId': request_id,
        'amount': str(amount),
        'orderId': order_id,
        'orderInfo': order_info,
        'redirectUrl': settings['return_url'],  # Sử dụng return_url từ config
        'ipnUrl': settings['notify_url'],
        'extraData': '',
        'requestType': 'payWithMethod',  # Thay đổi từ payWithMethod sang captureWallet để hỗ trợ returnUrl
        'returnUrl': settings['return_url']  # Sử dụng return_url từ config
    }
    
    # Tạo chuỗi raw data để ký theo đúng thứ tự mà MoMo mong đợi (KHÔNG bao gồm returnUrl)
    raw_signature = (
        f"accessKey={raw_data['accessKey']}"
        f"&amount={raw_data['amount']}"
        f"&extraData={raw_data['extraData']}"
        f"&ipnUrl={raw_data['ipnUrl']}"
        f"&orderId={raw_data['orderId']}"
        f"&orderInfo={raw_data['orderInfo']}"
        f"&partnerCode={raw_data['partnerCode']}"
        f"&redirectUrl={raw_data['redirectUrl']}"
        f"&requestId={raw_data['requestId']}"
        f"&requestType={raw_data['requestType']}"
    )
    
    # Tạo chữ ký HMAC SHA256
    signature = hmac.new(
        settings['secret_key'].encode('utf-8'),
        raw_signature.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    raw_data['signature'] = signature
    
    # In ra log để kiểm tra
    print("Data gửi đến MoMo:", json.dumps(raw_data, indent=2))
    print("Raw signature:", raw_signature)
    print("Generated signature:", signature)
    
    try:
        # Gửi yêu cầu đến MoMo
        response = requests.post(settings['test_endpoint'], json=raw_data)
        
        # In ra response để kiểm tra
        print("Response từ MoMo:", response.status_code)
        print(response.text)
        
        if response.status_code == 200:
            response_data = response.json()
            
            if response_data.get('resultCode') == 0:
                # Thành công
                return {
                    'status': 'success',
                    'code': 200,
                    'message': 'Thanh toán thành công',
                    'data': {
                        'payment_url': response_data.get('payUrl'),
                        'order_id': order_id,
                        'request_id': request_id
                    }
                }
            else:
                # Lỗi từ MoMo
                return {'status': 'error', 'code': 400, 'message': response_data.get('message', 'Có lỗi xảy ra từ MoMo'), 'data': None}
        else:
            return {'status': 'error', 'code': 500, 'message': 'Không thể kết nối đến MoMo', 'data': None}
    except Exception as e:
        print(f"Lỗi khi gửi request đến MoMo: {str(e)}")
        return {'status': 'error', 'code': 500, 'message': f'Lỗi kết nối: {str(e)}', 'data': None}


def verify_momo_response(db: Session, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Xác minh phản hồi từ MoMo
    """
    # Kiểm tra dữ liệu đầu vào
    required_fields = [
        'partnerCode', 'orderId', 'requestId', 'amount',
        'responseTime', 'message', 'resultCode', 'signature'
    ]
    
    for field in required_fields:
        if field not in data:
            return {
                'status': 'invalid',
                'message': f'Missing required field: {field}'
            }

    # Lấy dữ liệu từ request
    partner_code = data['partnerCode']
    order_id = data['orderId']
    request_id = data['requestId']
    amount = data['amount']
    response_time = data['responseTime']
    message = data['message']
    result_code = data['resultCode']
    transaction_id = data.get('transId', '')
    signature = data['signature']
    extra_data = data.get('extraData', '')
    order_type = data.get('orderType', '')
    pay_type = data.get('payType', '')

    # Tạo chuỗi raw signature theo đúng thứ tự MoMo yêu cầu
    raw_signature = (
        f"accessKey={settings['access_key']}"
        f"&amount={amount}"
        f"&extraData={extra_data}"
        f"&message={message}"
        f"&orderId={order_id}"
        f"&orderInfo={data.get('orderInfo', '')}"
        f"&orderType={order_type}"
        f"&partnerCode={partner_code}"
        f"&payType={pay_type}"
        f"&requestId={request_id}"
        f"&responseTime={response_time}"
        f"&resultCode={result_code}"
        f"&transId={transaction_id}"
    )

    # Tạo chữ ký xác thực
    verify_signature = hmac.new(
        settings['secret_key'].encode('utf-8'),
        raw_signature.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Debug log
    print("MoMo callback data:", data)
    print("Raw signature for verification:", raw_signature)
    print("Generated signature:", verify_signature)
    print("Received signature:", signature)

    # Xác thực chữ ký
    if signature != verify_signature:
        return {
            'status': 'invalid',
            'message': 'Invalid signature',
            'debug': {
                'expected': verify_signature,
                'received': signature,
                'raw_signature': raw_signature
            }
        }

    # Cập nhật database
    try:
        payment = db.query(MomoPayment).filter(
            MomoPayment.order_id == order_id,
            MomoPayment.request_id == request_id
        ).first()
        
        if not payment:
            return {
                'status': 'invalid',
                'message': 'Payment record not found'
            }
        
        payment.transaction_id = transaction_id
        payment.message = message
        payment.response_time = datetime.fromtimestamp(int(response_time)/1000)
        payment.status = 'completed' if result_code == '0' else 'failed'
        
        db.commit()
        db.refresh(payment)

        return {
            'status': 'verified',
            'payment': {
                'id': payment.id,
                'order_id': payment.order_id,
                'amount': float(payment.amount),
                'status': payment.status,
                'transaction_id': payment.transaction_id,
                'message': payment.message,
                'response_time': payment.response_time.isoformat() if payment.response_time else None,
                'user_id': payment.user_id,
                'cart_data': payment.cart_data
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }
