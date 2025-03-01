import nmap
import json
import whois
import pyfiglet
from colorama import Fore, Style, init
import argparse
import sys
sys.stdout.reconfigure(encoding='utf-8')  # Force UTF-8 Encoding

# Initialize colorama for Windows
init()

def print_banner():
    banner = pyfiglet.figlet_format("HawkEye", font="doom")
    print(Fore.CYAN + banner + Style.RESET_ALL)
    print(Fore.YELLOW + "🦅 Vulnerability Scanner - Developed by a nerd\n" + Style.RESET_ALL)
    print(Fore.GREEN + "Usage:\n" + Style.RESET_ALL)
    print(Fore.GREEN + "  python hawkeye.py <target> [options]\n" + Style.RESET_ALL)
    print(Fore.GREEN + "Options:\n" + Style.RESET_ALL)
    print(Fore.GREEN + "  --json       Save results as JSON file (scan_report.json)\n" + Style.RESET_ALL)
    print(Fore.GREEN + "  --ports <range>  Specify port range to scan (e.g., 1-65535)\n" + Style.RESET_ALL)
    print(Fore.GREEN + "Example:\n" + Style.RESET_ALL)
    print(Fore.GREEN + "  python hawkeye.py scanme.nmap.org\n" + Style.RESET_ALL)
    print(Fore.GREEN + "  python hawkeye.py scanme.nmap.org --json\n" + Style.RESET_ALL)
    print(Fore.GREEN + "  python hawkeye.py scanme.nmap.org --ports 20-1000\n" + Style.RESET_ALL)

def scan_ports(target, ports="1-1024"):
    scanner = nmap.PortScanner()
    scanner.scan(target, ports)
    results = {}
    for host in scanner.all_hosts():
        results[host] = {
            'hostnames': scanner[host].hostnames(),
            'state': scanner[host].state(),
            'ports': []
        }
        for proto in scanner[host].all_protocols():
            for port in scanner[host][proto]:
                service = scanner[host][proto][port]['name']
                state = scanner[host][proto][port]['state']
                results[host]['ports'].append({'port': port, 'service': service, 'state': state})
    return results

def get_whois_info(domain):
    try:
        domain_info = whois.whois(domain)
        return {
            "domain": domain_info.domain_name,
            "registrar": domain_info.registrar,
            "creation_date": str(domain_info.creation_date),
            "expiration_date": str(domain_info.expiration_date),
            "name_servers": domain_info.name_servers if isinstance(domain_info.name_servers, list) else []
        }
    except:
        return {"error": "WHOIS lookup failed"}

def print_results(scan_results, whois_results, target):
    print(Fore.CYAN + f"\n🎯 Target: {target}\n" + Style.RESET_ALL)
    
    if scan_results:
        for host, data in scan_results.items():
            print(Fore.YELLOW + f"🔍 Host: {host} - State: {data['state']}\n" + Style.RESET_ALL)
            for port_info in data['ports']:
                color = Fore.GREEN if port_info['state'] == "open" else Fore.RED
                print(color + f"  ➤ Port {port_info['port']}: {port_info['service']} ({port_info['state']})" + Style.RESET_ALL)
    
    if whois_results and "error" not in whois_results:
        print(Fore.MAGENTA + "\n🌍 WHOIS Information:" + Style.RESET_ALL)
        print(Fore.CYAN + f"  📌 Domain: {whois_results.get('domain', 'Unknown')}" + Style.RESET_ALL)
        print(Fore.CYAN + f"  🏢 Registrar: {whois_results.get('registrar', 'Unknown')}" + Style.RESET_ALL)
        print(Fore.CYAN + f"  📅 Creation Date: {whois_results.get('creation_date', 'Unknown')}" + Style.RESET_ALL)
        print(Fore.CYAN + f"  🔚 Expiration Date: {whois_results.get('expiration_date', 'Unknown')}" + Style.RESET_ALL)
        print(Fore.CYAN + f"  🌐 Name Servers: {', '.join(whois_results.get('name_servers', []))}" + Style.RESET_ALL)

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="Vulnerability Scanner - Cybersecurity Tool")
    parser.add_argument("target", nargs="?", help="IP or domain to scan")
    parser.add_argument("--json", help="Save results as JSON", action="store_true")
    parser.add_argument("--ports", help="Specify port range to scan (e.g., 1-65535)", default="1-1024")
    args = parser.parse_args()
    
    if not args.target:
        args.target = input(Fore.CYAN + "🔍 Enter the IP or domain to scan: " + Style.RESET_ALL)
    
    target = args.target
    
    print(Fore.YELLOW + f"\n[+] Scanning ports {args.ports}...\n" + Style.RESET_ALL)
    scan_results = scan_ports(target, args.ports)
    
    print(Fore.YELLOW + "[+] Fetching WHOIS data...\n" + Style.RESET_ALL)
    whois_results = get_whois_info(target)
    
    print_results(scan_results, whois_results, target)
    
    if args.json:
        report = {
            "target": target,
            "scan_results": scan_results,
            "whois_info": whois_results
        }
        with open("scan_report.json", "w") as file:
            json.dump(report, file, indent=4)
        print(Fore.GREEN + "[✔] Scan complete. Results saved in scan_report.json\n" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
