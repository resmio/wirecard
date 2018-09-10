from collections import OrderedDict
import hashlib
from urllib.parse import unquote
from urllib.parse import parse_qsl
import requests
from wirecard.adapters import SSLAdapter
import ssl


class QMoreError(Exception):
    pass


class QMore:
    """
    Client library for Wirecard's QMORE payment gateway interface
    http://www.wirecard.at/en/products/qmore/

    """
    def __init__(self, customerId, secret, password=None, shopId=None,
                 language='en', verify=True, jsVersion='pci3',
                 iframeCssUrl=None):
        self.customerId = customerId
        self.shopId = shopId
        self.secret = secret
        self.language = language
        self.password = password
        self.verify = verify
        self.jsVersion = jsVersion
        self.iframeCssUrl = iframeCssUrl

        # make sure we use TLS protocol for HTTPS
        self.session = requests.Session()
        self.session.mount('https://', SSLAdapter(ssl_version=ssl.PROTOCOL_TLSv1_2))

    def init_datastorage(self, orderIdent,
                         returnUrl='http://www.example.com/return'):
        """
        Init data datastorage

        """
        url = 'https://secure.wirecard-cee.com/qmore/dataStorage/init'
        data = OrderedDict((
            ('customerId', self.customerId),
            ('shopId', self.shopId),
            ('orderIdent', orderIdent),
            ('returnUrl', returnUrl),
            ('language', self.language),
            ('javascriptScriptVersion', self.jsVersion),
        ))

        # remove unused optional values (None values)
        data = OrderedDict([(a, data[a]) for a in data if data[a] is not None])

        fingerprint = self.make_request_fingerprint(
            data.values() + [self.secret])
        data.update([('requestFingerprint', fingerprint),
                     ('iframeCssUrl', self.iframeCssUrl),])
        response = self.session.post(url, data, verify=self.verify)

        result = dict(parse_qsl(response.text))

        error_count = int(result.get('errors', '0'))
        if error_count:
            errors = [(
                result['error.%d.errorCode' % i],
                result['error.%d.message' % i],
                result['error.%d.consumerMessage' % i]
                ) for i in range(error_count, error_count + 1)]
            raise QMoreError(errors)

        result['javascriptUrl'] = unquote(result['javascriptUrl'])
        return result

    def init_frontend(self, amount, currency, paymentType, language,
                      orderDescription, successUrl, cancelUrl, failureUrl,
                      serviceUrl, confirmUrl, consumerUserAgent,
                      consumerIpAddress, autoDeposit=None,
                      financialInstitution=None, noscriptInfoUrl=None,
                      windowName=None, duplicateRequestCheck=None,
                      storageId=None, orderIdent=None, customerStatement=None,
                      **kwargs):
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
            ('customerStatement', customerStatement),
            ('successUrl', successUrl),
            ('cancelUrl', cancelUrl),
            ('failureUrl', failureUrl),
            ('serviceUrl', serviceUrl),
            ('confirmUrl', confirmUrl),
            ('requestFingerprintOrder', ''),
            ('consumerUserAgent', consumerUserAgent),
            ('consumerIpAddress', consumerIpAddress),
            ('autoDeposit', autoDeposit),
            ('storageId', storageId),
            ('orderIdent', orderIdent),
            ('duplicateRequestCheck', duplicateRequestCheck),
            ('windowName', windowName),
            ('noscriptInfoUrl', noscriptInfoUrl),
        ))
        data.update(**kwargs)

        # remove unused optional values (None values)
        data = OrderedDict([(a, data[a]) for a in data if data[a] is not None])

        data['requestFingerprintOrder'] = ','.join(data.keys() + ['secret'])
        fingerprint = self.make_request_fingerprint(
            data.values() + [self.secret])
        data.update([('requestFingerprint', fingerprint)])

        response = self.session.post(url, data, verify=self.verify)
        result = dict(parse_qsl(response.text))

        error_count = int(result.get('errors', '0'))
        if error_count:
            errors = [(
                          result['error.%d.errorCode' % i],
                          result['error.%d.message' % i],
                          result['error.%d.consumerMessage' % i]
                      ) for i in range(error_count, error_count + 1)]
            raise QMoreError(errors)

        if response.status_code in range(400, 600):
            errors = [(
                response.status_code,
                parse_qsl(response.text),
                'Unfortunately, your payment could not be processed.'
            )]
            raise QMoreError(errors)

        result['redirectUrl'] = unquote(result['redirectUrl'])
        return result['redirectUrl']

    def recurring_payment(self, sourceOrderNumber, amount, orderDescription,
                          language='en', orderNumber=None,
                          customerStatement=None, autoDeposit=None,
                          orderReference=None, currency='EUR'):
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
            ('orderNumber', orderNumber),
            ('sourceOrderNumber', sourceOrderNumber),
            ('autoDeposit', autoDeposit),
            ('orderDescription', orderDescription),
            ('amount', amount),
            ('currency', currency),
            ('orderReference', orderReference),
            ('customerStatement', customerStatement),
        ))

        # remove unused optional values (None values)
        data = OrderedDict([(a, data[a]) for a in data if data[a] is not None])

        fingerprint = self.make_request_fingerprint(data.values())
        data['requestFingerprint'] = fingerprint
        del data['secret']
        response = self.session.post(url, data, verify=self.verify)
        result = dict([s.split('=') for s in response.text.split('&')])

        error_count = int(result.get('errors', '0'))
        if error_count:
            errors = [(
                result['error.%d.errorCode' % i],
                result['error.%d.message' % i],
                result['error.%d.consumerMessage' % i]
            ) for i in range(error_count, error_count + 1)]
            raise QMoreError(errors)

        return result

    def make_request_fingerprint(self, data):
        return hashlib.sha512(''.join(data).encode('utf-8')).hexdigest()

    def verify_response(self, data):
        data['secret'] = self.secret
        try:
            fingerprint = self.make_request_fingerprint(
                (data[i] for i in data['responseFingerprintOrder'].split(',')))
            return data['responseFingerprint'] == fingerprint
        except KeyError:
            return False
