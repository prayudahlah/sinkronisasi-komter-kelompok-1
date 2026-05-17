# sinkronisasi-komter-kelompok-1

## Setup

```bash
git clone https://github.com/prayudahlah/sinkronisasi-komter-kelompok-1
cd sinkronisasi-komter-kelompok-1
uv sync
```

## Menjalankan

Server:
```bash
uv run server.py
```

Client:
```bash
uv run client.py --server prayudahlah:8000
```

## Fitur Dashboard

- Status koneksi & live node table
- Bar chart deviasi waktu tiap node dari rata-rata
- Riwayat adjustment per iterasi
- Tombol Start/Stop sinkronisasi
