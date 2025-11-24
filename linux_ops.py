import subprocess
import re
import platform
import sys

class LinuxOps:
    @staticmethod
    def get_my_ip():
        """
        Executes 'ip addr' to find the actual machine IP.
        """
        if platform.system() == "Windows":
            return "127.0.0.1/24" # Mock for non-linux testing

        try:
            # Running standard Linux command
            result = subprocess.run(['ip', '-4', 'addr', 'show'], stdout=subprocess.PIPE, text=True)
            output = result.stdout
            
            # Find first non-loopback IP
            match = re.search(r'inet\s((?!(127\.0\.0\.1))\d+(\.\d+){3}/\d+)', output)
            if match:
                return match.group(1)
        except Exception as e:
            pass
        return None

    @staticmethod
    def ping_host(ip):
        """
        Pings a specific IP to see if it's alive.
        """
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        timeout = '-w' if platform.system().lower() == 'windows' else '-W'
        
        command = ['ping', param, '1', timeout, '1', str(ip)]
        
        try:
            # We mute the output (stdout=DEVNULL) so it doesn't clutter the terminal
            res = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return res.returncode == 0
        except:
            return False