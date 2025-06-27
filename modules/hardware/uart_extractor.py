# UART Extractor
import serial.tools.list_ports

print("🔌 UART Extractor: Scanning available serial ports...")
ports = serial.tools.list_ports.comports()
baud_rates = [9600, 19200, 38400, 57600, 115200]

for port in ports:
    print(f"Found port: {port.device}")
    for baud in baud_rates:
        try:
            print(f"  Trying {baud} baud...")
            with serial.Serial(port.device, baud, timeout=2) as ser:
                ser.write(b'\n')  # Prompt
                output = ser.read(100).decode(errors='ignore')
                if output:
                    print(f"  >>> UART output at {baud}:
{output}")
                    with open(f"logs/uart_dump_{port.device.replace('/','_')}_{baud}.log", "w") as f:
                        f.write(output)
        except Exception as e:
            print(f"  Error on {port.device} at {baud}: {e}")
