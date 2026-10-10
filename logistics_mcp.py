# logistics_mcp.py - the AfyaPlus logistics MCP server
import json
import logging
import math
from mcp.server.fastmcp import FastMCP
from rbac import allowed

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("logistics")

mcp = FastMCP("afyaplus-logistics")

with open("clinic.json") as f:
    CLINICS = json.load(f)["clinics"]

# Clinic allowlist = ids in clinic.json (C01..C05). Anything else is refused.
KNOWN_IDS = {c["id"] for c in CLINICS}
VALID_ITEMS = {"amoxicillin", "ors_sachets", "malaria_kits"}


def distance_km(a: dict, b: dict) -> float:
    """Rough distance between two clinics in kilometres."""
    dx = (a["lon"] - b["lon"]) * 111.32 * math.cos(math.radians((a["lat"] + b["lat"]) / 2))
    dy = (a["lat"] - b["lat"]) * 110.57
    return round(math.sqrt(dx * dx + dy * dy), 1)


def _deny(tool: str, role: str, reason: str, code: int) -> dict:
    # Log the decision, never the raw input or any secret.
    log.info("tool=%s role=%s result=denied reason=%s", tool, role, reason)
    return {"error": reason, "code": code}


@mcp.tool()
def check_stock(item: str, clinic_id: str, role: str) -> dict:
    """Stock level of one item at one clinic.
    Valid items: amoxicillin, ors_sachets, malaria_kits."""
    if not allowed(role, "check_stock"):
        return _deny("check_stock", role, "denied", 403)
    cid = (clinic_id or "").strip().upper()
    if cid not in KNOWN_IDS:
        return _deny("check_stock", role, "unknown clinic_id", 400)
    if item not in VALID_ITEMS:
        return _deny("check_stock", role, "unknown item", 400)
    clinic = next(c for c in CLINICS if c["id"] == cid)
    units = clinic["stock"][item]
    log.info("tool=check_stock role=%s clinic=%s item=%s result=ok", role, cid, item)
    return {"clinic_id": cid, "item": item, "units": units, "reorder_needed": units < 10}


@mcp.tool()
def plan_delivery_route(start_clinic_id: str, role: str) -> dict:
    """Plan a delivery route visiting every clinic, starting from one clinic.
    Uses the nearest-neighbour rule: always drive to the closest unvisited clinic next.
    This is quick decision support, not a guaranteed-shortest route."""
    if not allowed(role, "plan_delivery_route"):
        return _deny("plan_delivery_route", role, "denied", 403)
    sid = (start_clinic_id or "").strip().upper()
    if sid not in KNOWN_IDS:
        return _deny("plan_delivery_route", role, "unknown clinic_id", 400)
    start = next(c for c in CLINICS if c["id"] == sid)
    route, remaining, total = [start], [c for c in CLINICS if c["id"] != sid], 0.0
    while remaining:
        here = route[-1]
        nearest = min(remaining, key=lambda c: distance_km(here, c))
        total += distance_km(here, nearest)
        route.append(nearest)
        remaining.remove(nearest)
    log.info("tool=plan_delivery_route role=%s start=%s result=ok", role, sid)
    return {
        "route": [c["name"] for c in route],
        "total_km": round(total, 1),
        "method": "nearest-neighbour heuristic",
    }


@mcp.resource("clinics://directory")
def clinic_directory() -> str:
    """Read-only directory of AfyaPlus partner clinics (id and name only)."""
    return json.dumps([{"id": c["id"], "name": c["name"]} for c in CLINICS])


if __name__ == "__main__":
    mcp.run(transport="stdio")