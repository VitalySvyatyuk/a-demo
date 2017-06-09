# -*- coding: utf-8 -*-

import time


def easy_amo_client(conn, manager_amo_id, name, address=None,
                    tags=[],
                    phones=[], emails=[], sites=[], lead=True):
    obj = dict()
    obj['name'] = name
    obj['responsible_user_id'] = manager_amo_id
    obj['custom_fields'] = list()
    obj['tags'] = u', '.join(tags)

    if address:
        obj['custom_fields'].append({
            "id": conn.contact_field_id('ADDRESS'),
            "values": [{
                "value": address,
            }],
        })

    # phones
    obj['custom_fields'].append({
        "id": conn.contact_field_id('PHONE'),
        "values": [{"value": i, "enum": "OTHER"} for i in phones],
    })

    # emails
    obj['custom_fields'].append({
        "id": conn.contact_field_id('EMAIL'),
        "values": [{"value": i, "enum": "OTHER"} for i in emails],
    })

    # web
    obj['custom_fields'].append({
        "id": conn.contact_field_id('WEB'),
        "values": [{"value": i} for i in sites],
    })

    # setup flag in crm "It is lead"
    if lead:
        obj['custom_fields'].append({
            "id": 534748,
            "values": [{"value": "1"}],
        })
    return obj


def easy_amo_task(conn, contact_id, assignee_id, text, deadline, type="CALL"):
    obj = dict()
    obj['element_id'] = contact_id
    obj['element_type'] = 1  # contact
    obj['task_type'] = type
    obj['text'] = text
    obj['responsible_user_id'] = assignee_id
    obj['complete_till'] = time.mktime(deadline.timetuple())
    return obj


def easy_amo_note(conn, contact_id, text):
    obj = dict()
    obj['element_id'] = contact_id
    obj['element_type'] = 1  # contact
    obj['note_type'] = 4  # just note
    obj['text'] = text
    obj['responsible_user_id'] = 109672  # Marwin!
    return obj


def contact_is_lead(contact):
    for cf in contact['custom_fields']:
        if str(cf['id']) == '534748':
            if cf['values'] and cf['values'][0] and str(cf['values'][0].get('value', None)) == "1":
                return True


def contact_url(contact_id):
    return "https://grandcapital.amocrm.ru/private/contacts/edit.php?ID=%s" % (contact_id,)
