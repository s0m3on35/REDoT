import matplotlib.pyplot as plt
import numpy as np

def generate_waterfall(sub_file, sample_rate=2048000, segment_duration=0.1):
    with open(sub_file, "rb") as f:
        raw = np.frombuffer(f.read(), dtype=np.uint8)
    raw = raw.astype(np.float32) - 127.5

    segment_len = int(sample_rate * segment_duration)
    num_segments = len(raw) // segment_len
    waterfall = []

    for i in range(num_segments):
        segment = raw[i * segment_len:(i + 1) * segment_len]
        spectrum_segment = np.abs(np.fft.fftshift(np.fft.fft(segment)))
        waterfall.append(10 * np.log10(spectrum_segment + 1e-12))

    waterfall = np.array(waterfall)
    plt.imshow(
        waterfall.T,
        aspect='auto',
        origin='lower',
        extent=[0, num_segments * segment_duration, -sample_rate / 2, sample_rate / 2],
        cmap='inferno'
    )
    plt.title("RF Waterfall Spectrum")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.colorbar(label="Power (dB)")
    plt.tight_layout()
    plt.savefig("rf_captures/waterfall.png")
    print("[+] Waterfall image saved to rf_captures/waterfall.png")
