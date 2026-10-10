"""Authorisation regression tests: authentication is not authorisation."""
from rbac import TOOLS_BY_ROLE, allowed


def test_partner_may_check_stock():
    assert allowed('partner_clinic', 'check_stock') is True


def test_partner_may_not_route():
    assert allowed('partner_clinic', 'plan_delivery_route') is False


def test_unknown_role_is_denied():
    assert allowed('unknown', 'check_stock') is False


def test_no_dump_tools_anywhere():
    for role, tools in TOOLS_BY_ROLE.items():
        for tool in tools:
            assert 'dump' not in tool, f'{role} carries a dump-style tool: {tool}'


if __name__ == '__main__':
    test_partner_may_check_stock()
    test_partner_may_not_route()
    test_unknown_role_is_denied()
    test_no_dump_tools_anywhere()
    print('rbac tests OK')