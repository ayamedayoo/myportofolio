# Portofolio - Samuel Kaevin Phasca

Nama : Samuel Kaevin Phasca

NPM : 2506657333

Kelas : PBP E

## Deskripsi Proyek

Website portofolio pribadi berbasis Django, dibuat sebagai bagian dari tugas mata kuliah Pemrograman Berbasis Platform (PBP). Sampai dengan Tugas 1, halaman ini masih murni HTML5 dan CSS3 (belum memakai database maupun arsitektur MVT) dan terdiri dari dua bagian:

- **Profile** — data diri (nama, NPM, foto, bio, tautan sosial).
- **Pengalaman** — daftar pengalaman organisasi/kerja dalam bentuk timeline editorial, ditata dengan CSS Grid + Flexbox lengkap dengan efek hover.

## Cara Menjalankan Proyek (Setup Lokal)

1. Clone repository dan masuk ke foldernya.
2. Buat dan aktifkan virtual environment:
   ```
   python -m venv env
   env\Scripts\activate      # Windows
   source env/bin/activate   # macOS/Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Buat file `.env` di root project berisi minimal:
   ```
   PRODUCTION=False
   ```
5. Jalankan migrasi (belum ada model kustom di Tugas 1, tapi tetap perlu untuk tabel bawaan Django) dan server development:
   ```
   python manage.py migrate
   python manage.py runserver
   ```
6. Buka `http://localhost:8000/` di browser.

## Deployment

Proyek di-deploy ke PWS Fasilkom UI (Dockerfile + gunicorn, binding ke port 80 sesuai konvensi Traefik platform PWS) di `samuel-kaevin-myportofolio.pws.cs.ui.ac.id`.

## AI Disclosure

Sebagian pekerjaan di repo ini dibantu **Claude Code (Claude Sonnet 5)** lewat ekstensi VS Code, dengan rincian sebagai berikut:

- **Debugging deployment**: sebelum Tugas 1 ini dikerjakan, deployment ke PWS sempat gagal (404, lalu Bad Gateway). Saya minta Claude membaca source code, menelusuri kenapa error, lalu ia menemukan bahwa repo belum punya Dockerfile sama sekali dan `ALLOWED_HOSTS` salah tulis. Claude juga sempat riset dokumentasi resmi platform PWS untuk memastikan konvensi port yang benar (port 80, bukan 8080) sebelum saya commit fix-nya.
- **Struktur & styling section Pengalaman**: saya kasih data pengalaman saya (screenshot LinkedIn), lalu minta Claude membuatkan markup dan CSS untuk section baru dengan syarat: tetap HTML5/CSS3 murni, rapi, responsif, dan bukan gaya UI generik ala AI (card dengan shadow/gradient/emoji). Hasilnya berupa layout timeline bernomor yang saya sesuaikan lagi warnanya supaya konsisten dengan tema warna yang sudah saya buat sendiri di Tutorial 0.
- **Bagian yang saya kerjakan/putuskan sendiri**: konten About Me (bio, foto, data diri), pemilihan 5 pengalaman yang ditampilkan beserta detail waktu/lokasinya, serta jawaban-jawaban reflektif di bawah ini murni tulisan saya sendiri berdasarkan pengalaman mengerjakan tugas ini — bukan hasil generate AI.
- **Verifikasi manual**: saya jalankan `python manage.py check` dan `python manage.py runserver` sendiri untuk memastikan tidak ada error sebelum commit, dan saya cek tampilannya di lebar layar desktop dan mobile secara manual lewat DevTools.

## Pertanyaan Reflektif

**1. Apakah Anda menggunakan elemen semantik HTML5 seperti `<section>`, `<article>`, atau `<aside>`? Bagaimana elemen tersebut membantu?**

Iya, saya pakai elemen semantik seperti `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, dan `<footer>`, ditambah `<dl>`/`<dt>`/`<dd>` untuk data NPM dan Program studi. Section "Profile" dan "Pengalaman" saya bungkus dengan `<section>` masing-masing punya `id` sendiri (`#profile`, `#pengalaman`) supaya bisa dituju langsung dari link navigasi (`<a href="#pengalaman">`). Untuk tiap entri pengalaman, saya pakai `<article>` karena setiap entri sebenarnya berdiri sendiri sebagai satu "unit konten" (satu pengalaman kerja lengkap dengan judul, organisasi, dan meta datanya) yang secara teori bisa dipindah atau diambil sendiri tanpa kehilangan makna — itu beda dengan `<div>` yang tidak punya makna apa-apa. Manfaat yang paling saya rasakan justru bukan ke visual (karena secara default `<section>`/`<article>` tidak beda dari `<div>`), tapi ke kejelasan struktur waktu saya nulis dan baca ulang kode saya sendiri, dan juga aksesibilitas — screen reader bisa mengenali "landmark" halaman (header, nav, main, footer) sehingga pengguna dengan alat bantu bisa lompat antar bagian dengan lebih mudah.

**2. Tantangan tata letak apa yang ditemukan saat membuat CSS responsif? Bagaimana evaluasi elemen mana yang diprioritaskan saat desktop ke mobile?**

Tantangan terbesar ada di dua tempat. Pertama, section Profile memakai `grid-template-areas` dengan foto ada di kanan (sejajar dengan identitas dan detail di kiri) — di desktop ini enak dilihat, tapi kalau langsung di-shrink ke mobile tanpa diubah, foto jadi kegencet kecil di samping teks. Solusinya saya ubah urutan `grid-template-areas` di breakpoint mobile jadi satu kolom dengan urutan identity → photo → details, supaya foto tetap jadi "wajah" yang langsung terlihat setelah nama, bukan malah ketutup teks panjang. Kedua, di section Pengalaman, tiap baris timeline awalnya saya buat grid dengan angka index di kolom kiri lebar tetap — di layar sempit, kombinasi judul jabatan yang panjang (misalnya "SaaS Sales Intern – B2B Lead Growth & Client Engagement") dengan badge tipe pekerjaan ("Purnawaktu") bikin baris jadi terlalu padat kalau ukurannya tidak disesuaikan. Cara saya evaluasi: elemen yang paling penting dibaca duluan (nama jabatan) saya biarkan tetap fleksibel lebarnya (pakai `flex-wrap`), sedangkan elemen pendukung (meta tanggal & lokasi) saya jadikan satu kolom vertikal saat mobile alih-alih sejajar horizontal, supaya tidak saling berebut ruang dan tetap gampang dipindai dari atas ke bawah.

**3. Batasan apa yang dirasakan pada static web murni? Fungsionalitas dinamis apa yang ingin ditambahkan di iterasi berikutnya?**

Batasan paling terasa: setiap kali saya mau menambah, mengedit, atau menghapus satu pengalaman kerja, saya harus buka langsung file `index.html` dan duplikasi blok `<article>` secara manual — tidak ada tempat terpusat untuk mengelola datanya, dan risiko salah ketik atau lupa update satu bagian (misal durasi tapi lupa update tanggal) jadi lebih besar. Selain itu, semua konten "hidup" di dalam kode, jadi kalau nanti ada orang lain yang ingin membantu mengisi (misal saya minta tolong teman update pengalaman terbaru), mereka harus paham HTML dulu. Di iterasi berikutnya, begitu materi database dan arsitektur MVT diajarkan, hal pertama yang ingin saya bangun adalah model `Pengalaman` di database sehingga saya bisa CRUD (tambah/edit/hapus) pengalaman lewat form atau Django admin, dan section Pengalaman di halaman akan me-render datanya secara dinamis dari database lewat template loop (`{% for %}`) alih-alih di-hardcode satu-satu di HTML seperti sekarang.
