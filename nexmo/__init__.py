"""
nexmo - Client library for the nexmo service.
"""

import os
from . import lo


__version__ = '1.4.0'


class NexmoError(Exception):
    pass


class SendMessageError(NexmoError):
    def __init__(self, error_messages):
        super(SendMessageError, self).__init__(
            "Failed to send message parts. {}".format(
                '; '.join(error_messages)
            )
        )


class Client(object):
    def __init__(
        self,
        key=None,
        secret=None,
    ):
        self.api_key = key or os.environ['NEXMO_API_KEY']
        self.api_secret = secret or os.environ['NEXMO_API_SECRET']

        self._client = lo.Client(
            key=self.api_key,
            secret=self.api_secret,
        )

    def send_message(
        self,
        from_number,
        to,
        call_type='text',
        text=None,  # text and unicode
        udh=None,  # binary
        body=None,  # binary
        title=None,  # wappush
        url=None,  # wappush
        vcard=None,  # vcard
        vcal=None,  # vcal
        status_report_req=None,
        callback=None,
        client_ref=None,
    ):
        if callback is not None:
            status_report_req = 1

        if status_report_req is not None:
            status_report_req = int(status_report_req)

        if client_ref is not None:
            if len(client_ref) > 40:
                raise ValueError("'client_ref' must be 40 characters or less")

        params = _make_params({
            'from_number': 'from',
            'to': 'to',
            'call_type': 'type',
            'text': 'text',
            'udh': 'udh',
            'body': 'body',
            'title': 'title',
            'url': 'url',
            'vcard': 'vcard',
            'vcal': 'vcal',
            'status_report_req': 'status-report-req',
            'callback': 'callback',
            'client_ref': 'client-ref',
        }, locals())

        return self._parse_send_message_response(
            self.post('/sms/json', params)
        )

    def send_text_message(
        self,
        from_number,
        to,
        text,
        status_report_req=None,
        callback=None,
        client_ref=None,
        send_unicode=False,
    ):
        if isinstance(text, unicode):
            text = text.encode('utf8')
        return self.send_message(
            from_number, to,
            call_type='text' if not send_unicode else 'unicode',
            text=text,
            status_report_req=status_report_req,
            callback=callback,
            client_ref=client_ref,
        )

    def send_binary_message(
        self,
        from_number,
        to,
        udh,
        body,
        status_report_req=None,
        callback=None,
        client_ref=None,
    ):
        return self.send_message(
            from_number,
            to,
            call_type='binary',
            udh=udh,
            body=body,
            status_report_req=status_report_req,
            callback=callback,
            client_ref=client_ref,
        )

    def send_wappush_message(
        self,
        from_number,
        to,
        title,
        url,
        status_report_req=None,
        callback=None,
        client_ref=None,
    ):
        return self.send_message(
            from_number,
            to,
            call_type='wappush',
            title=title,
            url=url,
            status_report_req=status_report_req,
            callback=callback,
            client_ref=client_ref,
        )

    def send_vcard_message(
        self,
        from_number,
        to,
        vcard,
        status_report_req=None,
        callback=None,
        client_ref=None,
    ):
        return self.send_message(
            from_number,
            to,
            call_type='vcard',
            vcard=vcard,
            status_report_req=status_report_req,
            callback=callback,
            client_ref=client_ref,
        )

    def send_vcal_message(
        self,
        from_number,
        to,
        vcal,
        status_report_req=None,
        callback=None,
        client_ref=None,
    ):
        return self.send_message(
            from_number,
            to,
            call_type='vcal',
            vcal=vcal,
            status_report_req=status_report_req,
            callback=callback,
            client_ref=client_ref,
        )

    @staticmethod
    def _parse_send_message_response(self, json):
        return SendMessageResponse(json)

    def post(self, path, params):
        return self._client.post(self._client.host, path, params)


class Application(object):
    def __init__(self, client, application_id, public_key, private_key=None):
        self._client = client
        self.application_id = application_id
        self.public_key = public_key
        self.private_key = private_key


def _make_params(mapping, _locals):
    return {
        dest: _locals[src]
        for src, dest in mapping.items() if _locals[src] is not None
    }


class SendMessageResponse(object):
    def __init__(self, data):
        self._json = data
        self.message_count = data['message-count']
        self.messages = [
            MessagePart(part) for part in data['messages']
            ]

    def successful(self):
        return [part for part in self.messages if part.status == 0]

    def failed(self):
        return [part for part in self.messages if part.status == 0]

    def raise_for_status(self):
        if any([part.status != 0 for part in self.messages]):
            raise SendMessageError(
                part.error_text for part in self.messages if part.status != 0)

    def __repr__(self):
        return u"<SendMessageResponse: {parts} parts, {errors} errors>".format(
            parts=self.message_count,
            errors=len(self.failed()),
        )


class MessagePart(object):
    def __init__(self, data):
        self.status = int(data['status'])
        self.to = data.get('to')
        self.message_id = data.get('message-id')
        self.network = data.get('network')

        self.client_ref = data.get('client-ref')
        self.remaining_balance = data.get('remaining-balance')
        self.message_price = data.get('message-price')

        self.error_text = data.get('error-text')
