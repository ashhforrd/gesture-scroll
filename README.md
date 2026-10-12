# Gesture Scroll

Kontrol scroll layar menggunakan gerakan tangan di depan webcam. Aplikasi memakai
MediaPipe untuk mendeteksi 21 landmark tangan dan PyAutoGUI untuk mengirim perintah
scroll ke aplikasi yang sedang aktif.

## Gesture

1. Arahkan satu tangan ke webcam.
2. Rapatkan ujung jempol dan telunjuk untuk mengaktifkan mode scroll.
3. Sambil tetap pinch, gerakkan tangan ke atas atau bawah.
4. Lepaskan pinch untuk menghentikan scroll.

Gerakan tangan ke atas menghasilkan scroll ke atas; gerakan ke bawah menghasilkan
scroll ke bawah.

## Persyaratan

- Python 3.9 atau lebih baru
- Webcam
- macOS, Windows, atau Linux dengan desktop GUI

## Instalasi

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

Windows PowerShell menggunakan aktivasi berikut:

```powershell
.venv\Scripts\Activate.ps1
```

## Menjalankan

Uji deteksi dahulu tanpa mengendalikan layar:

```bash
gesture-scroll --dry-run
```

Jika deteksi sudah sesuai, jalankan mode normal:

```bash
gesture-scroll
```

Model Hand Landmarker akan diunduh otomatis ke `models/` pada pemakaian pertama.
Tekan `Q` pada jendela kamera untuk keluar.

Alternatif tanpa memasang command entry point:

```bash
PYTHONPATH=src python -m gesture_scroll --dry-run
```

## Izin sistem

### macOS

Berikan izin kepada Terminal atau aplikasi Python pada:

- **System Settings → Privacy & Security → Camera**
- **System Settings → Privacy & Security → Accessibility**

Izin Camera diperlukan untuk membaca webcam. Izin Accessibility diperlukan agar
PyAutoGUI dapat mengirim perintah scroll.

### Windows

Pastikan akses kamera untuk desktop apps aktif melalui **Settings → Privacy &
security → Camera**.

## Pengaturan sensitivitas

Contoh:

```bash
gesture-scroll --sensitivity 160 --dead-zone 0.009 --smoothing 0.4
```

Opsi penting:

| Opsi | Default | Fungsi |
|---|---:|---|
| `--camera` | `0` | Memilih indeks webcam |
| `--pinch-threshold` | `0.45` | Nilai lebih besar membuat pinch lebih mudah aktif |
| `--sensitivity` | `120` | Kekuatan scroll |
| `--dead-zone` | `0.012` | Batas gerakan kecil yang diabaikan |
| `--smoothing` | `0.35` | Perataan gerakan, rentang 0–1 |
| `--cooldown` | `0.06` | Jeda minimum antar-scroll dalam detik |
| `--max-scroll` | `6` | Batas scroll per pembaruan |
| `--dry-run` | mati | Deteksi saja tanpa mengontrol layar |

Jika scroll terlalu sensitif, turunkan `--sensitivity` atau naikkan `--dead-zone`.
Jika scroll terasa lambat, lakukan kebalikannya.

## Pengujian

```bash
pip install -e '.[dev]'
pytest
```

Pengujian mencakup aktivasi pinch, arah scroll, dead zone, dan reset ketika tangan
tidak terdeteksi.

## Pemecahan masalah

- **Kamera tidak terbuka atau frame tidak terbaca:** tutup FaceTime, Zoom, browser,
  atau aplikasi lain yang sedang memakai kamera. Setelah itu coba
  `gesture-scroll --dry-run` atau `gesture-scroll --camera 1 --dry-run`.
- **Deteksi bekerja tetapi layar tidak scroll:** aktifkan izin Accessibility dan
  pastikan kursor berada di atas aplikasi yang ingin di-scroll.
- **Scroll bergerak sendiri:** naikkan `--dead-zone`, misalnya menjadi `0.02`.
- **Pinch sulit aktif:** naikkan `--pinch-threshold`, misalnya menjadi `0.55`.
- **Jendela tersendat:** tutup aplikasi lain yang memakai webcam dan gunakan
  pencahayaan yang lebih terang.
