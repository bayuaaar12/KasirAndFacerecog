# Kontrak integrasi face recognition

Laravel tidak melakukan pengenalan wajah. Program kamera/Python bertugas
menghasilkan `face_label`, `score` kemiripan antara `0` dan `1`, dan hasil
liveness check, lalu mengirimkannya ke aplikasi kasir.

## Konfigurasi

Salin nilai `AI_API_KEY` dari `.env` ke konfigurasi program Python. Jangan
menaruh key tersebut di source code atau mengirimkannya ke browser.

Nilai yang dapat diatur di `.env`:

- `FACE_MATCH_MIN_SCORE=0.60`
- `FACE_DETECTION_TTL_SECONDS=30`
- `FACE_REQUIRE_LIVENESS=true`

## Deteksi member

Kirim `POST /api/customers/detect-member` dengan header `X-API-KEY` dan JSON:

```json
{
  "face_label": "member_001",
  "score": 0.93,
  "liveness_passed": true
}
```

Server hanya mengembalikan member apabila skor memenuhi batas dan liveness
berhasil. Hasil yang berhasil disimpan sebagai audit dan berlaku 30 detik.
Kasir tetap harus menekan **Terapkan diskon member** pada transaksi yang aktif.
Satu hasil deteksi tidak dapat diterapkan dua kali.

## Pendaftaran wajah

Kirim `POST /api/customers/register-face` dengan header yang sama:

```json
{
  "name": "Nama Member",
  "phone": "08123456789",
  "face_label": "member_001",
  "discount_percent": 10,
  "face_image_base64": "data:image/jpeg;base64,...",
  "face_embedding": [0.01, -0.04],
  "consent_confirmed": true
}
```

`face_label` harus identik dengan label yang dipakai model Python saat
mendeteksi wajah. Foto wajah baru disimpan pada storage privat; admin yang
sudah login saja yang dapat membukanya melalui aplikasi.
