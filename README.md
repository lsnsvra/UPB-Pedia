🛒 UPB-Pedia - E-Commerce App (UAS OOP)
UPB-Pedia adalah aplikasi e-commerce sederhana berbasis web yang dibangun menggunakan framework Flask dan FakeStore API. Proyek ini dibuat untuk memenuhi tugas Ujian Akhir Semester (UAS) mata kuliah Pemrograman Orientasi Objek.

✨ Fitur Saat Ini
Home & Katalog: Menampilkan semua daftar produk dari FakeStore API.

Detail Produk: Menampilkan deskripsi lengkap dan harga produk berdasarkan pilihan user.

Filter Kategori: Memisahkan produk berdasarkan kategori yang tersedia di API.

Keranjang, Checkout, dan Payment

🏛️ Implementasi Kode

app.py: Berfungsi sebagai pusat kendali aplikasi (Main Controller). Di sini terdapat rute URL (/, /product/<id>, /category/<name>) dan logika pengambilan data menggunakan library requests.

Integrasi API: Data produk ditarik secara real-time dari https://fakestoreapi.com/products.

Templating: Menggunakan Jinja2 untuk merender data dari API ke dalam HTML secara dinamis.
