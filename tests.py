from collections import OrderedDict
from nose.tools import assert_raises
from mock import patch
import requests
from wirecard.qmore import QMore, QMoreError

def test_qmore_init_datastorage():
    client = QMore('D200001', 'qmore', 'B8AKTPWBRMNBV455FG6M2DANE99WU2')
    order_ident = '12345'

    # build the mock response object
    mock_data_storage_init_result = '''storageId=ce161cce3ff466b616d21b05d56981be&storeId=ce161cce3ff466b616d21b05d56981be&javascriptUrl=https%3A%2F%2Fsecure.wirecard-cee.com%2Fqmore%2FdataStorage%2Fjs%2FD200001%2Fqmore%2Fce161cce3ff466b616d21b05d56981be%2FdataStorage.js'''
    mock_response = type('TestResponse', (object,), dict(text=mock_data_storage_init_result))

    request_url = 'https://secure.wirecard-cee.com/qmore/dataStorage/init'
    request_data = OrderedDict([
        ('customerId', 'D200001'),
        ('shopId', 'qmore'),
        ('orderIdent', '12345'),
        ('returnUrl', 'http://www.example.com/return'),
        ('language', 'en'),
        ('requestFingerprint', '3b4e255d631c05eb9382a113ea2475569e6b5c0f014721a60f2c19277ee8834bda3173c7533424a47b2a1d6820700d1ddb68dc751303dbab1b565a04928e47ba'),
    ])
    expected_result = {
        'javascriptUrl': 'https://secure.wirecard-cee.com/qmore/dataStorage/js/D200001/qmore/ce161cce3ff466b616d21b05d56981be/dataStorage.js',
        'storeId': 'ce161cce3ff466b616d21b05d56981be',
        'storageId': 'ce161cce3ff466b616d21b05d56981be'
    }

    with patch.object(requests, 'post', return_value=mock_response) as mock_method:
        data_storage_result = client.init_datastorage(order_ident)
    mock_method.assert_called_once_with(request_url, request_data)
    assert data_storage_result == expected_result

def test_qmore_init_frontend():
    client = QMore('D200001', 'qmore', 'B8AKTPWBRMNBV455FG6M2DANE99WU2')

    # make sure we raise QMoreError when an error occurs
    mock_init_frontend_result = 'error.1.message=PAYMENTTYPE+is+invalid.&error.1.consumerMessage=PAYMENTTYPE+ist+ung%26%23252%3Bltig.&error.1.errorCode=18051&errors=1'
    mock_response = type('TestResponse', (object,), dict(text=mock_init_frontend_result))
 
    with patch.object(requests, 'post', return_value=mock_response) as mock_method:
        with assert_raises(QMoreError):
            result = client.init_frontend('100.00', 'EUR', 'INVALIDPAYMENTTYPE', 'de', 'test order',
                'http://www.example.com/success', 'http://www.example.com/cancel', 'http://www.example.com/failure',
                    'http://www.example.com/service', 'http://www.example.com/confirm', 'chrome', '127.0.0.1')

    # should work fine
    mock_init_frontend_result = 'redirectUrl=https%3A%2F%2Fsecure.wirecard-cee.com%2Fqmore%2Ffrontend%2FD200001qmore%2Fselect.php%3FSID%3D8u8ev2jrc8cs0n94cppphv2036'
    mock_response = type('TestResponse', (object,), dict(text=mock_init_frontend_result))

    request_url = 'https://secure.wirecard-cee.com/qmore/frontend/init'
    request_data = OrderedDict([('customerId', 'D200001'), ('shopId', 'qmore'), ('amount', '100.00'), ('currency', 'EUR'), ('paymentType', 'CCARD'), ('language', 'de'), ('orderDescription', 'test order'), ('successUrl', 'http://www.example.com/success'), ('cancelUrl', 'http://www.example.com/cancel'), ('failureUrl', 'http://www.example.com/failure'), ('serviceUrl', 'http://www.example.com/service'), ('confirmUrl', 'http://www.example.com/confirm'), ('requestFingerprintOrder', 'customerId,shopId,amount,currency,paymentType,language,orderDescription,successUrl,cancelUrl,failureUrl,serviceUrl,confirmUrl,requestFingerprintOrder,consumerUserAgent,consumerIpAddress,secret'), ('consumerUserAgent', 'chrome'), ('consumerIpAddress', '127.0.0.1'), ('requestFingerprint', 'e46e6983ed4ea1732e8362abc6b6a31bf1c16342248eec64ef675fb5ede0874f8389177dd5b59c9b7efa6b4a0dcc6d6a6ff24c5fa1f97f71bbc2da1a866d96d6')])

    expected_result = 'https://secure.wirecard-cee.com/qmore/frontend/D200001qmore/select.php?SID=8u8ev2jrc8cs0n94cppphv2036'

    with patch.object(requests, 'post', return_value=mock_response) as mock_method:
        result = client.init_frontend('100.00', 'EUR', 'CCARD', 'de', 'test order',
            'http://www.example.com/success', 'http://www.example.com/cancel', 'http://www.example.com/failure',
                'http://www.example.com/service', 'http://www.example.com/confirm', 'chrome', '127.0.0.1')
    mock_method.assert_called_once_with(request_url, request_data)
    assert result == expected_result
