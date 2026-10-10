"""Application-level authorisation: which role may call which tool in logistics_mcp.py.

Deny by default: an unknown role, or a tool not listed for a role, is refused.
"""

# Role matrix: partner tools vs operations tools.
# Tool names must match the @mcp.tool functions in logistics_mcp.py.
TOOLS_BY_ROLE = {
    "partner_clinic": {"check_stock"},                         # partner tools
    "clinical_ops": {"check_stock", "plan_delivery_route"},    # operations tools
}

ALL_TOOLS = sorted({t for tools in TOOLS_BY_ROLE.values() for t in tools})


def allowed(role: str, tool: str) -> bool:
    # Unknown role -> empty set -> denied.
    return tool in TOOLS_BY_ROLE.get(role, set())


def require(role: str, tool: str) -> None:
    """Call at the top of each MCP tool in logistics_mcp.py."""
    if not allowed(role, tool):
        raise PermissionError(f"denied: role '{role}' may not call '{tool}'")


def print_matrix() -> None:
    roles = list(TOOLS_BY_ROLE) + ["unknown"]
    print("role".ljust(16) + "".join(t.ljust(22) for t in ALL_TOOLS))
    for r in roles:
        print(r.ljust(16) + "".join(("ALLOW" if allowed(r, t) else "DENY").ljust(22) for t in ALL_TOOLS))


if __name__ == "__main__":
    assert allowed("partner_clinic", "check_stock")
    assert not allowed("partner_clinic", "plan_delivery_route")
    assert allowed("clinical_ops", "plan_delivery_route")
    assert not allowed("unknown", "check_stock")
    assert not allowed("", "check_stock")
    assert not allowed("clinical_ops", "dump_all")
    print_matrix()
    print("rbac OK")