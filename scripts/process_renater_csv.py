import argparse
import csv
import json
import re
import subprocess
import sys
import time
import urllib.request

RED = "\033[91m"
RESET = "\033[0m"


def check_siret_info(siret):
    url = f"https://recherche-entreprises.api.gouv.fr/search?q={siret}"
    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                if not data.get("results"):
                    return {"status": "not_found", "name": None}

                result = data["results"][0]
                name = result.get("nom_complet") or result.get("nom_commercial")

                for etab in result.get("matching_etablissements", []):
                    if etab.get("siret") == siret:
                        enseignes = etab.get("liste_enseignes")
                        enseigne = enseignes[0] if enseignes else None

                        etab_name = etab.get("nom_commercial") or enseigne or name
                        is_open = etab.get("etat_administratif") == "A"
                        return {
                            "status": "open" if is_open else "closed",
                            "name": f"{name} :: {etab_name}",
                        }

                is_open = result.get("etat_administratif") == "A"
                return {"status": "open" if is_open else "closed", "name": name}
        except Exception as e:
            if getattr(e, "code", None) == 429 and attempt < max_retries - 1:
                time.sleep(2)
                continue
            print(f"{RED}Error checking {siret}: {e}{RESET}", file=sys.stderr)
            return {"status": "error", "name": None}
    return {"status": "error", "name": None}


def read_csv_entries(csv_path):
    entries = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entity_id = row.get("EntityID", "").strip()
            siret = row.get("SIRET", "").strip()
            nom_csv = (
                row.get("Non d'établissement", "").strip()
                or row.get("Nom d'établissement", "").strip()
            )
            domains_raw = row.get("Domaines", "")

            if not entity_id or not siret:
                continue

            domains = [d for d in re.split(r"\s+", domains_raw) if d]

            entries.append(
                {
                    "name": nom_csv,
                    "entity_id": entity_id,
                    "siret": siret,
                    "domains": domains,
                    "errors": [],
                }
            )
    return entries


def check_entry_domains(entry, check_grist, check_mx, grist_domains, seen_domains):
    is_success = True
    for d in entry["domains"]:
        if check_grist:
            if d in seen_domains:
                conflicting_name = seen_domains[d]
                print(
                    f"  {RED}ERROR: Domain conflict (internal): '{d}' is also used by '{conflicting_name}'{RESET}",
                    file=sys.stderr,
                )
                is_success = False
            else:
                seen_domains[d] = entry["name"]

            if d in grist_domains:
                idp_name = grist_domains[d]
                if idp_name == "Passerelle Fédération Éducation Recherche":
                    print(
                        f"  Grist: Domain '{d}' found in '{idp_name}'", file=sys.stderr
                    )
                else:
                    print(
                        f"  {RED}ERROR: Domain conflict (external): '{d}' is already used by Grist IdP '{idp_name}'{RESET}",
                        file=sys.stderr,
                    )
                    is_success = False

        if check_mx:
            try:
                result = subprocess.run(
                    ["dig", "+short", "MX", d],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if not result.stdout.strip():
                    print(
                        f"  {RED}ERROR: No MX record found for domain '{d}'{RESET}",
                        file=sys.stderr,
                    )
                    is_success = False
            except Exception as e:
                print(
                    f"  {RED}ERROR: Failed to check MX record for domain '{d}': {e}{RESET}",
                    file=sys.stderr,
                )
                is_success = False
    return is_success


def get_grist_idps():
    grist_domains = {}
    url = "https://grist.numerique.gouv.fr/api/docs/gNkPzdjPZnv8rjdedfYhry/tables/Fournisseurs_d_identite/records"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

            for record in data.get("records", []):
                fields = record.get("fields", {})
                fqdns_raw = fields.get("Liste_des_FQDN")
                if not fqdns_raw:
                    continue

                if isinstance(fqdns_raw, list):
                    fqdns_raw = " ".join(str(x) for x in fqdns_raw)
                else:
                    fqdns_raw = str(fqdns_raw)

                fqdns = [d for d in re.split(r"[\s,]+", fqdns_raw) if d]
                idp_name = (
                    fields.get("Titre")
                    or fields.get("Nom_raccourci")
                    or fields.get("Nom")
                    or record.get("id")
                )

                for fqdn in fqdns:
                    grist_domains[fqdn] = idp_name
    except Exception as e:
        print(f"{RED}Error fetching Grist IdPs: {e}{RESET}", file=sys.stderr)
    return grist_domains


def process_entry_siret(entry, check_siret, entity_to_siret):
    is_success = True
    if check_siret:
        info = check_siret_info(entry["siret"])

        if info.get("name"):
            print(f"  SIRET API Name : {info['name']}", file=sys.stderr)
        print(
            f"  SIRET Link     : https://annuaire-entreprises.data.gouv.fr/etablissement/{entry['siret']}",
            file=sys.stderr,
        )

        if info["status"] == "open":
            print(f"  SIRET Status   : Open", file=sys.stderr)
            entity_to_siret[entry["entity_id"]] = entry["siret"]
        elif info["status"] == "closed":
            is_success = False
            print(f"  {RED}SIRET Status   : Closed{RESET}", file=sys.stderr)
        elif info["status"] == "not_found":
            is_success = False
            print(f"  {RED}SIRET Status   : Not found{RESET}", file=sys.stderr)
        else:
            is_success = False
            print(
                f"  {RED}SIRET Status   : Error fetching info{RESET}", file=sys.stderr
            )

        time.sleep(0.5)
    else:
        entity_to_siret[entry["entity_id"]] = entry["siret"]
    return is_success


def get_discovery_idps():
    url = "https://discovery.renater.fr/agentconnect/api.php"
    idp_map = {}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            for group in data:
                if isinstance(group, dict) and "children" in group:
                    for child in group["children"]:
                        if "id" in child and "text" in child:
                            idp_map[child["id"]] = child["text"]
    except Exception as e:
        print(
            f"{RED}Error fetching discovery service IdP list: {e}{RESET}",
            file=sys.stderr,
        )
    return idp_map


def main():
    parser = argparse.ArgumentParser(
        description="Check requested IdP additions from RENATER."
    )
    parser.add_argument("csv_file", help="Path to the CSV file to parse")
    parser.add_argument(
        "--check-siret",
        action="store_true",
        help="Check SIRET validity using the data.gouv.fr API",
    )
    parser.add_argument(
        "--check-grist",
        action="store_true",
        help="Check that domains are unique across the CSV and Grist IdPs",
    )
    parser.add_argument(
        "--check-mx",
        action="store_true",
        help="Check that an MX record exists for each domain",
    )
    parser.add_argument(
        "--check-discovery",
        action="store_true",
        help="Check that CSV Entity IDs are present in the discovery service",
    )
    parser.add_argument(
        "--check-all",
        action="store_true",
        help="Run all checks (--check-siret, --check-grist, --check-mx, --check-discovery)",
    )
    args = parser.parse_args()

    if args.check_all:
        args.check_siret = True
        args.check_grist = True
        args.check_mx = True
        args.check_discovery = True

    csv_path = args.csv_file

    print(f"Reading {csv_path}...", file=sys.stderr)
    entries = read_csv_entries(csv_path)

    all_csv_domains = [d for entry in entries for d in entry["domains"]]

    grist_domains = {}
    if args.check_grist:
        print("Fetching Grist IdPs...", file=sys.stderr)
        grist_domains = get_grist_idps()

    discovery_idps = {}
    if args.check_discovery:
        print("Fetching discovery IdPs...", file=sys.stderr)
        discovery_idps = get_discovery_idps()

    print("", file=sys.stderr)

    entity_to_siret = {}
    success_count = 0
    error_count = 0
    seen_domains = {}

    for entry in entries:
        is_success = True
        print(f"--- \033[1m{entry['name']}\033[0m ---", file=sys.stderr)
        print(f"  EntityID : {entry['entity_id']}", file=sys.stderr)
        print(f"  Domains  : {' '.join(entry['domains'])}", file=sys.stderr)

        if not check_entry_domains(
            entry, args.check_grist, args.check_mx, grist_domains, seen_domains
        ):
            is_success = False

        if not process_entry_siret(entry, args.check_siret, entity_to_siret):
            is_success = False

        if args.check_discovery:
            if entry["entity_id"] in discovery_idps:
                print(
                    f"  Discovery: Found -> {discovery_idps[entry['entity_id']]}",
                    file=sys.stderr,
                )
            else:
                is_success = False
                print(
                    f"  {RED}Discovery: NOT FOUND in discovery service{RESET}",
                    file=sys.stderr,
                )

        if is_success:
            success_count += 1
        else:
            error_count += 1

        print("", file=sys.stderr)

    if all_csv_domains:
        print("--- ALL CSV DOMAINS ---", file=sys.stderr)
        print(" ".join(all_csv_domains), file=sys.stderr)
        print("", file=sys.stderr)

    print("--- SIRET MAP ---", file=sys.stderr)
    print(json.dumps(entity_to_siret, indent=4))

    print("--- SUMMARY ---", file=sys.stderr)
    print(f"  Successfully checked: \033[92m{success_count}\033[0m", file=sys.stderr)
    print(f"  Entries in error:     {RED}{error_count}{RESET}", file=sys.stderr)
    print("", file=sys.stderr)


if __name__ == "__main__":
    main()
