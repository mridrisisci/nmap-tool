import socket, argparse, sys, json, csv, os, logging, subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path 
"""
Usage:
    python3 port_scanner.py target.example.com
    python3 port_scanner.py 127.0.0.1 --start 1 --end 65535 --workers 150 --timeout 1.0

"""


#ip, port = int 

def read_hosts():
    '''
    
    '''
    path = Path("/")

    with (p / 'hosts.txt').open('r') as file:
        content = file.read()
        print(content)
    

def is_port_open(ip,port, timeout=1):
    '''
    Scans the indivvidual port to see if it is open
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(ip,port)
        # Receive the banner and decode it to a string
        banner = s.recv(1024).decode().strip()
        print(f"Banner for {ip}:{port} -> {banner}")
    except (OSError, socket.error):
        return False
    else:
        return True
    finally:
        s.close()

def check_targets():
    with args.file as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line:
                continue
            scan_ports(line)

def scan_ports(host, start_time, end_time, workers=200, timeout=1, show_progress=True):
    '''
    Runs through the port range which is given to the program and executes 
    x-amount of threads
    '''
    open_ports = []
    checked = 0
    total_time = end_time - start_time + 1
    begin_time = time.time()

    def worker(port):
        nonlocal checked
        ok = is_port_open(host, port, timeout)
        checked += 1
        return port, ok # omitting 'port' generates error ???
    
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(worker, port): port for port in range(argparse.port) + 1}
        for f in as_completed(futures):
            port, ok = f.result()
            if ok:
                open_ports.append(port)
                print(f"[+] OPEN: {host}:{port}")
            if show_progress and checked % max(1, total_time // 50) == 0:
                elapsed = time.time() - begin_time
                sys.stdout.write(f"\rScanned {checked}/{total_time} ports {pct:.1f}% - elapsed {elapsed:.1f}s")
                sys.stdout.flush()



def main():
    '''
    Description provided here and details about the program
    '''
    parser = argparse.ArgumentParser(description="TCP Port Scanner 2.0")
    parser.add_argument("-t", "--target", help="Hostname or IP to scan")
    parser.add_argument("--hosts", type=int, help="HOST - multiple hosts separated by comma")
    parser.add_argument(
        '--hosts-file',
        type=argparse.FileType('r'),
        help="Path to file"
    )
    parser.add_argument("--out", "-o", help="Output file - choose where to save it")
    parser.add_argument('-tt', "--targets", type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument("-p", "--port", type=int, default=1, help="Start port to scan - default set to 1")
    parser.add_argument("-pp", "--ports", help="Ports to scan")
    parser.add_argument("-w", "--workers", type=int, default=200, help="number of threads")
    parser.add_argument("--timeout", type=int, default=1, help="socket timeout - default set to 1")
    args = parser.parse_args()

    '''try:
        ip = socket.gethostbyname(args.target)
    except socket.gaierror as e:
        print(f"ERROR: Could not resolve host: {e}", file=sys.stderr)
        sys.exit(1)
    '''

    hosts = []

    if args.target:
        try:
            ip = socket.gethostbyname(args.target)
            hosts = [ip]
            print(f"Resolved host: {args.target} -> {ip}" )
        except socket.gaierror as e:
            print(f"ERROR resolving host {args.target}: # {e}", file=sys.stderr)
            sys.exit(1)
    else:
        for line in args.host-file:
            host = line.strip()
            if not host or host.startswith("#"):
                continue
            try:
                ip = socket.gethostbyname(host)
                hosts.append(ip)
            except socket.gaierror as e:
                print(f"SKIPPING resolving host: {host}: # {e}", file=sys.stderr)


    #print(f"Scanning  {{ip}} with {args.workers} threads")

    try:
        open_ports = scan_ports(ip, workers=args.workers, timeout=args.timeout)
    except KeyboardInterrupt:
        print()
    except Exception as exc:
        print(f"\nERROR during scan: {exc}", file=sys.stderr)
        sys.exit(1)
    
    if open_ports:
        print(f"\n Open ports")
        for p in open_ports:
            print(f" - {p}")
    else:
        print("\n no open ports found from host")

if __name__ == '__main__':
    main()