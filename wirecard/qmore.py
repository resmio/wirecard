from collections import OrderedDict
import hashlib
from urllib import unquote
import requests

class QMoreError(Exception):
    pass

class QMore:
    """
    Client library for Wirecard's QMORE payment gateway interface
    http://www.wirecard.at/en/products/qmore/

    """
    def __init__(self, customerId, shopId, secret, password=None, language='en'):
        self.customerId = customerId
        self.shopId = shopId
        self.secret = secret
        self.language = language
        self.password = password

    def init_datastorage(self, orderIdent):
        """
        Init data datastorage

        """
    	url = 'https://secure.wirecard-cee.com/qmore/dataStorage/init'
    	data = OrderedDict((
    	    ('customerId', self.customerId),
            ('shopId', self.shopId),
    	    ('orderIdent', orderIdent),
    	    ('returnUrl', 'http://www.example.com/return'),
    	    ('language', self.language),
    	))
        data.update([('requestFingerprint', self.make_request_fingerprint(data.values() + [self.secret]))])
        response = requests.post(url, data)

        result = dict([s.split('=') for s in response.text.split('&')])
        result['javascriptUrl'] = unquote(result['javascriptUrl'])
        return result

    def init_frontend(self, amount, currency, paymentType, language,
        orderDescription, successUrl, cancelUrl, failureUrl, serviceUrl, confirmUrl,
            consumerUserAgent, consumerIpAddress, financialInstitution=None, noscriptInfoUrl=None,
                windowName=None, duplicateRequestCheck=False, storageId=None, orderIdent=None, **kwargs):
        """
        Init frontend

        """
        url = 'https://secure.wirecard-cee.com/qmore/frontend/init'

        data = OrderedDict((
            ('customerId', self.customerId),
            ('shopId', self.shopId),
            ('amount', str(amount)),
            ('currency', currency),
            ('paymentType', paymentType),
            ('language', language),
            ('orderDescription', orderDescription),
            ('successUrl', successUrl),
            ('cancelUrl', cancelUrl),
            ('failureUrl', failureUrl),
            ('serviceUrl', serviceUrl),
            ('confirmUrl', confirmUrl),
            ('requestFingerprintOrder', None),
            ('consumerUserAgent', consumerUserAgent),
            ('consumerIpAddress', consumerIpAddress),
        ))
        data.update(**kwargs)

        if storageId is not None:
            data['storageId'] = storageId

        if orderIdent is not None:
            data['orderIdent'] = orderIdent

        data['requestFingerprintOrder'] = ','.join(data.keys() + ['secret'])
        data.update([('requestFingerprint', self.make_request_fingerprint(data.values() + [self.secret]))])
        response = requests.post(url, data)
        result = dict([s.split('=') for s in response.text.split('&')])

        error_count = int(result.get('errors', '0'))
        if error_count:
            errors = [(
                result['error.%d.errorCode' % i], result['error.%d.message' % i], result['error.%d.consumerMessage' % i]
                ) for i in range(error_count, error_count + 1)]
            raise QMoreError(errors)

        result['redirectUrl'] = unquote(result['redirectUrl'])
        return result['redirectUrl']

    def recurring_payment(self, sourceOrderNumber, amount, orderDescription, language='en', orderNumber=None, autoDeposit='NO', currency='EUR'):
        """
        Recurring payment

        """
        url = 'https://secure.wirecard-cee.com/qmore/backend/recurPayment'

        data = OrderedDict((
            ('customerId', self.customerId),
            ('shopId', self.shopId),
            ('password', self.password),
            ('secret', self.secret),
            ('language', language),
            ('requestFingerprint', ''),
            ('orderNumber', orderNumber or ''),
            ('sourceOrderNumber', sourceOrderNumber),
            ('autoDeposit', autoDeposit),
            ('orderDescription', orderDescription),
            ('amount', "{0:.2f}".format(amount)),
            ('currency', currency),
        ))

        data['requestFingerprint'] = self.make_request_fingerprint(data.values())
        del data['secret']
        response = requests.post(url, data)
        result = dict([s.split('=') for s in response.text.split('&')])

        error_count = int(result.get('errors', '0'))
        if error_count:
            errors = [(
                result['error.%d.errorCode' % i], result['error.%d.message' % i], result['error.%d.consumerMessage' % i]
                ) for i in range(error_count, error_count + 1)]
            raise QMoreError(errors)

        return result

    def make_request_fingerprint(self, data):
    	return hashlib.sha512(''.join(data)).hexdigest()

    def verify_response(self, post):
        data = post.copy()
        data['secret'] = self.secret
        fingerprint = self.make_request_fingerprint((data[i] for i in data['responseFingerprintOrder'].split(',')))
        return data['responseFingerprint'] == fingerprint
