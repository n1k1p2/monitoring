import os
import subprocess
import sys

try:
    import paramiko
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
    import paramiko

print("Connecting to server 85.239.36.222...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    client.connect("85.239.36.222", username="root", password="id+Gu8E+JnvJ-V", timeout=10)
    print("Connected successfully! Starting deployment...")
    
    commands = [
        "git --version || (apt-get update -y -o DPkg::Lock::Timeout=120 && apt-get install -y -o DPkg::Lock::Timeout=120 git)",
        "cd monitoring && git fetch --all && git reset --hard origin/main && git pull && chmod +x deploy.sh && ./deploy.sh"
    ]
    
    for cmd in commands:
        print(f"\n[Remote] Running: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        
        while True:
            line = stdout.readline()
            if not line:
                break
            print(line, end='', flush=True)
            
        status = stdout.channel.recv_exit_status()
        err = stderr.read().decode()
        if err:
            print(f"Stderr: {err}")
            
        if status != 0:
            print(f"Command failed with exit code {status}")
            break
            
    print("\nDeployment sequence finished.")
except Exception as e:
    print(f"Execution failed: {e}")
finally:
    client.close()
