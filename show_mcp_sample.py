import json
import logistics_mcp as m

cases = {
    "check_stock (partner, C01)": m.check_stock("amoxicillin", "C01", "partner_clinic"),
    "check_stock (unknown clinic *)": m.check_stock("amoxicillin", "*", "partner_clinic"),
    "check_stock (unknown role)": m.check_stock("amoxicillin", "C01", "unknown"),
    "plan_delivery_route (partner)": m.plan_delivery_route("C01", "partner_clinic"),
    "plan_delivery_route (ops)": m.plan_delivery_route("C01", "clinical_ops"),
}
for name, out in cases.items():
    print(name)
    print(json.dumps(out, indent=2))