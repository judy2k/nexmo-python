from .utils import make_params
from.errors import NexmoError


class SendMessageError(NexmoError):
    def __init__(self, error_messages):
        super(SendMessageError, self).__init__(
            "Failed to send message parts. {}".format(
                '; '.join(error_messages)
            )
        )


class SMSClient(object):
    def __init__(self, client):
        self._client = client

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
        # Override status-report-req if there is a callback:
        if callback is not None:
            status_report_req = 1

        # Convert boolean values to the required int:
        if status_report_req is not None:
            status_report_req = int(status_report_req)

        if client_ref is not None:
            if len(client_ref) > 40:
                raise ValueError("'client_ref' must be 40 characters or less")

        params = make_params({
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
            self._client.post('/sms/json', params)
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
    def _parse_send_message_response(json):
        return SendMessageResponse(json)


class SendMessageResponse(object):
    def __init__(self, data):
        self._json = data
        self.message_count = data['message-count']
        self.messages = [
            MessagePart(part) for part in data['messages']
            ]

    @property
    def successful_messages(self):
        return [part for part in self.messages if part.status == 0]

    @property
    def failed_messages(self):
        return [part for part in self.messages if part.status != 0]

    def raise_for_status(self):
        if any(self.failed_messages):
            raise SendMessageError(
                part.error_text for part in self.messages if part.status != 0)
        return self

    def __repr__(self):
        return u"<SendMessageResponse: {parts} parts, {errors} errors>".format(
            parts=self.message_count,
            errors=len(self.failed_messages),
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
