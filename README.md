# MAC-Flooding-20211150
# Ataque MAC Flooding — Matrícula 20211150
**Autor:** Alvaro Smilk Baez Tavera
**Matrícula:** 20211150
**Fecha:** 5 Junio 2026

---

## Descripción
Script que desborda la tabla CAM del switch enviando 
tramas Ethernet con MACs fuente aleatorias a máxima 
velocidad, forzando al switch a actuar como HUB y 
reenviar tráfico a todos los puertos.

---

## Objetivo
Demostrar el desbordamiento de la tabla CAM de un 
switch Cisco mediante inundación de MACs aleatorias, 
permitiendo capturar tráfico ajeno y aplicando las 
contramedidas necesarias.

---

## Topología
Router-20211150 (20.21.11.1)
|
SW1-20211150 (20.21.11.2)
/        
Kali Linux    PC1/PC2/PC3
(20.21.11.50) (Víctimas)
ATACANTE

## Direccionamiento
| Dispositivo | IP          | Interfaz | Rol      |
|-------------|-------------|----------|----------|
| Router      | 20.21.11.1  | gi0/0    | Gateway  |
| SW1         | 20.21.11.2  | gi0/0    | Switch   |
| Kali Linux  | 20.21.11.50 | gi3/3    | Atacante |
| PC1         | DHCP        | gi0/1    | Víctima  |
| PC2         | DHCP        | gi0/2    | Víctima  |
| PC3         | DHCP        | gi0/3    | Víctima  |

---

## Requisitos
- Python 3
- Scapy instalado
- Privilegios root
- Port Security desactivado en el switch

### Instalación
```bash
pip3 install scapy --break-system-packages
```

---

## Parámetros del script
| Parámetro   | Valor | Descripción                    |
|-------------|-------|--------------------------------|
| INTERFAZ    | eth0  | Interfaz del atacante          |
| DELAY       | 0.0   | 0 = máxima velocidad           |
| LOTE        | 200   | Tramas por envío               |
| MAX_PKTS    | 0     | 0 = infinito                   |
| PAYLOAD_TAM | 64    | Bytes de payload por trama     |

---

## Uso
```bash
# Básico:
sudo python3 05_mac_flooding.py

# Especificar interfaz:
sudo python3 05_mac_flooding.py eth0
```

---

## Funcionamiento
1. Genera lotes de 200 tramas Ethernet
2. Cada trama tiene MAC fuente y destino aleatorias
3. Envía los lotes a máxima velocidad
4. Muestra velocidad en pkt/s en tiempo real
5. La tabla CAM del switch se llena completamente
6. El switch actúa como HUB (fail open)
7. El atacante puede capturar tráfico de otros hosts

---

## Verificación del ataque
```bash
# En SW1 — tabla CAM llenándose:
show mac address-table count
# Total Mac Addresses: 8000+

# Ver tabla completa:
show mac address-table

# En Kali — capturar tráfico ajeno:
sudo tcpdump -i eth0 -n
sudo tcpdump -i eth0 -w captura.pcap
```

---

## Capturas
### Antes — tabla CAM normal
![Antes](capturas/05_antes.png)

### Script corriendo en Kali
![Script](capturas/05_script.png)

### Tabla CAM llena
![CAM llena](capturas/05_cam_llena.png)

### Tráfico capturado
![Tráfico](capturas/05_trafico.png)

---

## Contramedida
```bash
SW1(config)# interface gi3/3
SW1(config-if)# switchport port-security
SW1(config-if)# switchport port-security maximum 5
SW1(config-if)# switchport port-security violation restrict
SW1(config-if)# switchport port-security mac-address sticky
SW1(config-if)# exit
SW1(config)# end
SW1# write memory

# Verificar:
SW1# show port-security
SW1# show port-security interface gi3/3
```

### Verificación contramedida
![Contramedida](capturas/05_contramedida.png)

---

## Video
[Ver demostración en YouTube](URL_DEL_VIDEO)

---

## Referencias
- Switch CAM Table Overflow Attack
- Cisco Port Security Configuration Guide
- Herramienta: Python 3 + Scapy
