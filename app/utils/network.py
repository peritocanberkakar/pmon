import asyncio
import subprocess
import platform
from typing import Tuple


async def check_tcp(host: str, port: int, timeout: float = 3.0) -> Tuple[bool, float | None, str | None]:
    start = asyncio.get_event_loop().time()
    try:
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        latency_ms = (asyncio.get_event_loop().time() - start) * 1000.0
        return True, latency_ms, None
    except Exception as exc:
        return False, None, str(exc)


async def check_ping(host: str, timeout: float = 5.0, count: int = 3) -> Tuple[bool, float | None, str | None]:
    """
    PING kontrolü yapar
    
    Args:
        host: Ping atılacak host
        timeout: Timeout süresi (saniye)
        count: Ping sayısı
        
    Returns:
        (success, latency_ms, error_message)
    """
    start = asyncio.get_event_loop().time()
    
    try:
        # Platform'a göre ping komutu
        if platform.system().lower() == "windows":
            cmd = ["ping", "-n", str(count), "-w", str(int(timeout * 1000)), host]
        else:
            cmd = ["ping", "-c", str(count), "-W", str(int(timeout)), host]
        
        # Ping komutunu çalıştır
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout + 2)
        
        if process.returncode == 0:
            # Ping başarılı, latency hesapla
            latency_ms = (asyncio.get_event_loop().time() - start) * 1000.0
            
            # Ping çıktısından ortalama latency'yi çıkar (opsiyonel)
            try:
                output = stdout.decode('utf-8', errors='ignore')
                if platform.system().lower() == "windows":
                    # Windows ping çıktısından ortalama süreyi çıkar
                    if "Average = " in output:
                        avg_line = [line for line in output.split('\n') if "Average = " in line][0]
                        avg_ms = float(avg_line.split("Average = ")[1].split("ms")[0])
                        latency_ms = avg_ms
                else:
                    # Linux/Mac ping çıktısından ortalama süreyi çıkar
                    if "avg" in output:
                        avg_line = [line for line in output.split('\n') if "avg" in line][0]
                        avg_ms = float(avg_line.split("avg")[1].split("/")[1])
                        latency_ms = avg_ms
            except:
                pass  # Latency hesaplanamazsa varsayılan değer kullan
            
            return True, latency_ms, None
        else:
            error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "Ping failed"
            return False, None, error_msg
            
    except asyncio.TimeoutError:
        return False, None, "Ping timeout"
    except Exception as exc:
        return False, None, str(exc)


async def check_port(host: str, port: int, protocol: str, timeout: float = 3.0) -> Tuple[bool, float | None, str | None]:
    """
    Port kontrolü yapar (TCP/UDP/PING)
    
    Args:
        host: Kontrol edilecek host
        port: Port numarası (PING için kullanılmaz)
        protocol: Protokol (tcp, udp, ping)
        timeout: Timeout süresi
        
    Returns:
        (success, latency_ms, error_message)
    """
    if protocol.lower() == "tcp":
        return await check_tcp(host, port, timeout)
    elif protocol.lower() == "udp":
        return await check_udp(host, port, timeout)
    elif protocol.lower() == "ping":
        return await check_ping(host, timeout)
    else:
        return False, None, f"Unsupported protocol: {protocol}"
async def check_udp(host: str, port: int, timeout: float = 1.0) -> Tuple[bool, float | None, str | None]:
    # UDP için basit deneme: soket açıp dummy datagram gönderiyoruz.
    loop = asyncio.get_event_loop()
    start = loop.time()
    try:
        transport, protocol = await loop.create_datagram_endpoint(lambda: asyncio.DatagramProtocol(), remote_addr=(host, port))
        transport.sendto(b"ping")
        await asyncio.sleep(0)  # scheduling
        transport.close()
        latency_ms = (loop.time() - start) * 1000.0
        return True, latency_ms, None
    except Exception as exc:
        return False, None, str(exc)
