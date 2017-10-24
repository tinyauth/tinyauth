import fnmatch


def _get_list(dict, key):
    retval = dict.get(key, [])
    if isinstance(retval, list):
        return retval
    return [retval]


def _match_action(statement, action):
    for statement_action in _get_list(statement, 'Action'):
        if fnmatch.fnmatch(action, statement_action):
            return True

    # FIXME: Implement NotAction

    return False


def _match_resource(statement, resource):
    for statement_resource in _get_list(statement, 'Resource'):
        if fnmatch.fnmatch(resource, statement_resource):
            return True

    # FIXME: Implement NotResource

    return False


def allow(policy, action, resource):
    retval = "Default"

    for statement in _get_list(policy, 'Statement'):
        if not _match_action(statement, action):
            continue
        if not _match_resource(statement, resource):
            continue
        if statement['Effect'] == 'Deny':
            return "Deny"

        retval = "Allow"

    return retval
