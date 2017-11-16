import fnmatch
import ipaddress


def _match_condition_ipaddress(left, right):
    return ipaddress.ip_address(left) in ipaddress.ip_network(right)


def _match_condition_notipaddress(left, right):
    return not _match_condition_ipaddress(left, right)


def _get_list(dict, key):
    retval = dict.get(key, [])
    if isinstance(retval, list):
        return retval
    return [retval]


def _match_action(statement, action):
    for statement_action in _get_list(statement, 'Action'):
        if fnmatch.fnmatch(action, statement_action):
            return True

    # FIXME: Implement NotAction

    return False


def _match_resource(statement, resource):
    for statement_resource in _get_list(statement, 'Resource'):
        if fnmatch.fnmatch(resource, statement_resource):
            return True

    # FIXME: Implement NotResource

    return False


_condition_functions = {
    'IpAddress': _match_condition_ipaddress,
    'NotIpAddress': _match_condition_notipaddress,
}


def _match_condition(statement, context):
    # "Condition": {"IpAddress": {"aws:SourceIp": "203.0.113.0/24"}}
    for condition_check, conditions in statement.get('Condition', {}).items():
        fn = _condition_functions[condition_check]
        for condition, value in conditions.items():
            if not fn(context[condition], value):
                return False

    return True


def get_allowed_resources(policy, action, context=None):
    allowed = []
    denied = []

    for statement in _get_list(policy, 'Statement'):
        if not _match_action(statement, action):
            continue
        if not _match_condition(statement, context or {}):
            continue

        if statement['Effect'] == 'Deny':
            denied.extend(_get_list(statement, 'Resource'))
        else:
            allowed.extend(_get_list(statement, 'Resource'))

    return allowed, denied


def allow(policy, action, resource, context=None):
    retval = "Default"

    for statement in _get_list(policy, 'Statement'):
        if not _match_action(statement, action):
            continue
        if not _match_resource(statement, resource):
            continue
        if not _match_condition(statement, context or {}):
            continue
        if statement['Effect'] == 'Deny':
            return "Deny"

        retval = "Allow"

    return retval
