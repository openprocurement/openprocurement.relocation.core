# -*- coding: utf-8 -*-
from openprocurement.api.utils import update_logging_context
from openprocurement.api.validation import validate_json_data, validate_data
from openprocurement.relocation.core.models import Transfer


def validate_transfer_data(request):
    update_logging_context(request, {'transfer_id': '__new__'})
    data = validate_json_data(request)
    if data is None:
        return
    model = Transfer
    return validate_data(request, model, data=data)


def validate_set_or_change_ownership_data(request):
    if request.errors:
        # do not run validation if some errors are already detected
        return
    data = validate_json_data(request)
    fields_set = set(['id', 'transfer', 'tender_token'])
    request_set = set([field for field in fields_set if data.get(field)])
    if not data.get('id'):
        request.errors.add('body', 'id', 'This field is required.')

    if len(fields_set.difference(request_set)) != 1:
        request.errors.add('body', 'name', 'Request must contain either "id and transfer" or "id and tender_token".')

    if request.errors:
        request.errors.status = 422
        return
    request.validated['ownership_data'] = data


def validate_ownership_data(request):
    if request.errors:
        # do not run validation if some errors are already detected
        return
    data = validate_json_data(request)

    for field in ['id', 'transfer']:
        if not data.get(field):
            request.errors.add('body', field, 'This field is required.'.format(field))
    if request.errors:
        request.errors.status = 422
        return
    request.validated['ownership_data'] = data


def validate_accreditation_level(request, item, level_name):
    level = getattr(type(item), level_name)
    if not any([request.check_accreditation(l) for l in iter(str(level))]):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit ownership change')
        request.errors.status = 403
        return

    if item.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit ownership change')
        request.errors.status = 403
        return
