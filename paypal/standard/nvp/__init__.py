# Partial implementation of the NameValuePair interface of PayPal

# currently allows:
# * change status of subscription/recurring payment

import urllib
import urllib2
import urlparse

from django.conf import settings

base_params = {
        'USER': settings.PAYPAL_API_USERNAME,
        'PWD': settings.PAYPAL_API_PASSWORD,
        'SIGNATURE': settings.PAYPAL_API_SIGNATURE,
        'VERSION': '60.0'
        }



class PayPalResponse:
    def __init__(self, raw_data):
        self.raw = raw_data
        self.parse()

    def parse(self):
        self.params = urlparse.parse_qs(self.raw)


class RecurringSubscription:
    def __init__(self, profileid):
        self.profileid = profileid

    def __unicode__(self):
        return str(self.profileid)
    
    def __str__(self):
        return self.__unicode__()

    def updateStatus(self, new_status):
        """Update the status of the recurring payment profile.

        new_status is in { Cancel, Suspend, Reactivate }."""

        if new_status not in ('Cancel', 'Suspend', 'Reactivate'):
            raise ValueError("Invalid value '%s' for new_status. Must be in Cancel, Suspend, Reactivate." % new_status)

        pars = {
                'METHOD': 'ManageRecurringPaymentsProfileStatus',
                'PROFILEID': self.profileid,
                'ACTION': new_status
                }

        ok, params = self.issue_cmd(pars)
        return ok

    def issue_cmd(self, parameters):
        parameters = dict(base_params.items() + parameters.items())
        data = urllib.urlencode(parameters)
        req = urllib2.Request(settings.PAYPAL_API_NVP_ENDPOINT, data, {})
        resp = urllib2.urlopen(req).read()
        resp_params = urlparse.parse_qs(resp)
        return all([x.lower() == 'success' for x in resp_params['ACK']]), resp_params

