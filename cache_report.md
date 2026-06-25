# Redis Caching Exercise Report

## 1. Kode yang dimodifikasi

- `weather_api.py`
- `test_cache.py`

## 2. Deskripsi implementasi

Fungsi `get_weather(city)` sekarang menggunakan Redis untuk cache hasil API weather.

Alur cache:

1. Cek cache dengan key `weather:{city}` menggunakan perintah `GET`.
2. Jika ada data, kembalikan langsung hasil dari Redis.
3. Jika tidak ada data, panggil API lambat dengan `time.sleep(2)`.
4. Simpan hasil ke Redis dengan `SET` dan expired 300 detik (`EX 300`).
5. Kembalikan hasil data.

## 3. Redis commands yang digunakan

- `GET weather:<city>`
- `SET weather:<city> <json> EX 300`
- Secara implisit, `EXPIRE` digunakan ketika `SET` dipanggil dengan parameter `ex=300`.

## 4. Hasil uji

- First call: sekitar 2 detik
- Second call (cached): sekitar 0.00-0.05 detik

> Contoh output aktual bisa dilihat setelah menjalankan `python test_cache.py`.

## 5. Penjelasan

### Kenapa response time berbeda?

Response pertama berbeda karena sistem melakukan simulasi panggilan API lambat dengan `time.sleep(2)` dan kemudian menulis hasil ke Redis. Response kedua langsung diambil dari cache Redis tanpa menunggu delay, sehingga jauh lebih cepat.

### Apa keuntungan caching?

- Mengurangi latency response API.
- Mengurangi frekuensi panggilan ke sumber data lambat atau mahal.
- Mengurangi beban server backend dan sumber data eksternal.
- Meningkatkan pengalaman pengguna karena data kembali lebih cepat.

### Kapan sebaiknya tidak menggunakan cache?

- Data sangat dinamis dan berubah cepat sehingga cache bisa menghasilkan data usang.
- Data memiliki konsistensi kuat atau harus selalu real-time.
- Cache menambah kompleksitas dan overhead memori pada sistem.
- Data jarang diakses, sehingga cache tidak memberikan manfaat signifikan.

## 6. Cara menjalankan

1. Pastikan Redis berjalan di `redis://127.0.0.1:6379/0`.
2. Jalankan `python test_cache.py`.
3. Untuk demo HTTP, jalankan `python weather_server.py` dan buka:
   - http://127.0.0.1:5000/weather?city=Jakarta
4. Untuk menguji expired, tunggu 5 menit atau hapus key `weather:jakarta` dari Redis.

## 7. Catatan screenshot

Silakan ambil screenshot dari:

- Output terminal `python test_cache.py` yang menampilkan waktu panggilan pertama dan kedua.
- Hasil di browser pada URL `http://127.0.0.1:5000/weather?city=Jakarta`.

Screenshot tersebut akan menunjukkan bahwa cache bekerja dan response HTTP berhasil dikembalikan dari server lokal.
