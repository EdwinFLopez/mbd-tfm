import socket

def check_ip_port(ip, port, timeout=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((ip, port))
        if result == 0:
            print(f"✅ IP: {ip}, Port: {port} is OPEN and accessible!")
            return True
    except socket.gaierror:
        print(f"❌ Error: Hostname {ip} could not be resolved.")
    except socket.error as e:
        print(f"❌ An unexpected error occurred: {e}")
    finally:
        sock.close()
    print(f"❌ IP: {ip}, Port: {port} is CLOSED or unreachable. Error code: {result}")
    return False

if __name__ == "__main__":
    check_ip_port("mongodb-atlas", 27017)
    check_ip_port("spark-connect", 15002)
    check_ip_port("spark-cluster", 7077) # Master
    check_ip_port("spark-cluster", 7178) # Worker
