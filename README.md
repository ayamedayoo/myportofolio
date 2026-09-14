# Portofolio - Samuel Kaevin Phasca

Nama : Samuel Kaevin Phasca

NPM : 2506657333

Kelas : PBP E

## Deskripsi Proyek

Website portofolio pribadi berbasis Django, dibuat sebagai bagian dari tugas mata kuliah Pemrograman Berbasis Platform (PBP). Sampai dengan Tugas 1, halaman ini masih murni HTML5 dan CSS3 (belum memakai database maupun arsitektur MVT) dan terdiri dari dua bagian:

- **Profile**: data diri (nama, NPM, foto, bio, tautan sosial).
- **Pengalaman**: daftar pengalaman organisasi/kerja dalam bentuk timeline editorial, ditata dengan CSS Grid + Flexbox lengkap dengan efek hover.

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

Sebagian pekerjaan di repo ini saya kerjakan dibantu Claude Code lewat ekstensi VS Code. Kira-kira begini pembagiannya:

- Debugging deployment: sebelum Tugas 1 ini dikerjakan, deployment ke PWS sempat gagal (404, lalu Bad Gateway). Saya minta Claude membaca source code, menelusuri kenapa error, lalu ia menemukan bahwa repo belum punya Dockerfile sama sekali dan `ALLOWED_HOSTS` salah tulis. Claude juga sempat riset dokumentasi resmi platform PWS untuk memastikan konvensi port yang benar (port 80, bukan 8080) sebelum saya commit fix-nya.

## Pertanyaan Reflektif

**1. Apakah Anda menggunakan elemen semantik HTML5 seperti `<section>`, `<article>`, atau `<aside>`? Bagaimana elemen tersebut membantu?**

Iya, saya pakai elemen semantik seperti `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, dan `<footer>`, ditambah `<dl>`/`<dt>`/`<dd>` untuk data NPM dan Program studi. Section "Profile" dan "Pengalaman" saya bungkus dengan `<section>` masing-masing punya `id` sendiri (`#profile`, `#pengalaman`) supaya bisa dituju langsung dari link navigasi (`<a href="#pengalaman">`). Untuk tiap entri pengalaman, saya pakai `<article>` karena setiap entri sebenarnya berdiri sendiri sebagai satu "unit konten" (satu pengalaman kerja lengkap dengan judul, organisasi, dan meta datanya) yang secara teori bisa dipindah atau diambil sendiri tanpa kehilangan makna, beda dengan `<div>` yang memang tidak punya makna apa-apa. Manfaat yang paling saya rasakan justru bukan ke visual (karena secara default `<section>`/`<article>` tidak beda dari `<div>`), tapi ke kejelasan struktur waktu saya nulis dan baca ulang kode saya sendiri, dan juga ke aksesibilitas: screen reader jadi bisa mengenali "landmark" halaman (header, nav, main, footer) sehingga pengguna dengan alat bantu bisa lompat antar bagian lebih mudah.

**2. Tantangan tata letak apa yang ditemukan saat membuat CSS responsif? Bagaimana evaluasi elemen mana yang diprioritaskan saat desktop ke mobile?**

Ada dua momen yang paling bikin saya mikir ulang. Di section Profile, awalnya foto saya taruh di kanan sejajar dengan identitas dan detail di kiri pakai `grid-template-areas`, enak dilihat di desktop, tapi begitu layar di-shrink ke ukuran mobile tanpa diubah apa-apa, fotonya jadi kegencet kecil di samping teks. Makanya saya ubah urutan `grid-template-areas` khusus di breakpoint mobile jadi satu kolom dengan urutan identity, photo, details, supaya foto tetap jadi "wajah" yang langsung kelihatan setelah nama, bukan malah ketutup teks panjang. Di section Pengalaman juga ada masalah serupa: tiap baris timeline saya buat grid dengan angka index di kolom kiri berlebar tetap, dan di layar sempit, judul jabatan yang panjang (contohnya "SaaS Sales Intern - B2B Lead Growth & Client Engagement") kalau digabung sama badge tipe pekerjaan ("Purnawaktu") bikin barisnya jadi sesak kalau ukurannya tidak disesuaikan. Yang saya lakukan: elemen yang paling penting dibaca duluan, yaitu nama jabatan, saya biarkan fleksibel lebarnya pakai `flex-wrap`, sementara elemen pendukung seperti tanggal dan lokasi saya tumpuk jadi satu kolom vertikal saat mobile ketimbang sejajar horizontal, jadi tidak rebutan ruang dan tetap gampang dipindai dari atas ke bawah.

**3. Batasan apa yang dirasakan pada static web murni? Fungsionalitas dinamis apa yang ingin ditambahkan di iterasi berikutnya?**

Batasan yang paling kerasa: tiap kali saya mau nambah, edit, atau hapus satu pengalaman kerja, saya harus buka langsung file `index.html` dan duplikasi blok `<article>` manual, padahal tidak ada tempat terpusat buat ngelola datanya, jadi risiko salah ketik atau lupa update satu bagian (misalnya durasinya diganti tapi tanggalnya lupa disesuaikan) jadi lebih besar. Selain itu semua kontennya "nempel" di dalam kode, jadi kalau suatu saat ada teman yang mau bantu update pengalaman terbaru, dia harus paham HTML dulu. Begitu materi database dan arsitektur MVT diajarkan di tutorial berikutnya, yang paling ingin saya bikin duluan adalah model `Pengalaman` di database, supaya saya bisa CRUD (tambah/edit/hapus) pengalaman lewat form atau Django admin, dan section Pengalaman di halaman bisa render datanya secara dinamis dari database lewat template loop (`{% for %}`), bukan di-hardcode satu-satu di HTML kayak sekarang.

### Tugas 2

1. Jadi gini, waktu kita buka URL halaman portofolio, yang pertama nerima permintaan itu Django. Django bakal ngecek dulu file urls.py yang ada di level proyek, buat nyari pola URL mana yang cocok sama alamat yang kita ketik tadi. Nah, biasanya di urls.py proyek ini nggak langsung ke view-nya, tapi dia "lempar" dulu ke urls.py yang ada di aplikasi (misalnya aplikasi main), pakai fungsi include. Jadi ibaratnya urls.py proyek itu kayak resepsionis yang ngarahin kita ke ruangan yang tepat.

Sampai di urls.py aplikasi, baru deh URL-nya dicocokkan lagi sama fungsi view yang sesuai, contohnya fungsi show_project. Nah di dalam view ini kerjanya lumayan banyak: dia yang ngurusin permintaan tadi, terus dia juga yang "ngobrol" sama model buat ngambil data project dari database. Data yang udah diambil itu dimasukkan ke dalam bentuk dictionary yang biasa disebut context. Abis itu, view bakal manggil fungsi render, sambil bawa context tadi dan template yang mau dipakai.

Di dalam template inilah data dari context itu diolah jadi HTML beneran, biasanya pakai perulangan (loop) dari Django Template Language kalau datanya lebih dari satu, misalnya buat nampilin daftar project satu-satu. Terakhir, HTML yang udah jadi ini dikirim balik sama server ke browser kita, dan itu yang muncul di layar sebagai halaman web.

2. Menurutku, nyimpen data di model (yang nantinya masuk ke database) itu jauh lebih enak dibanding nulis data langsung di HTML. Alasannya sederhana aja: kalau data ditulis manual di HTML, terus suatu saat ada yang mau diubah atau ditambah, kita jadi harus buka lagi file HTML-nya, cari baris yang mau diedit, dan itu lumayan riskan. Salah dikit aja, misalnya kelupaan nutup tag atau ada typo, bisa bikin tampilan halamannya berantakan atau malah error.

Nah kalau datanya disimpan di model, kita nggak perlu ngoprek HTML sama sekali kalau cuma mau nambah atau ubah data. Ini juga ngaruh banget ke pengembangan aplikasi ke depannya. Soalnya aplikasi jadi lebih gampang dikembangin, misalnya kita bisa nambahin halaman admin buat operasi CRUD (create, read, update, delete) tanpa harus ganggu-ganggu bagian tampilan atau template utamanya. Jadi bagian "data" sama bagian "tampilan" itu jadi lebih terpisah rapi, nggak nyampur.

3. Jadi makemigrations itu tugasnya buat ngecek, ada perubahan apa aja di file models.py. Kalau ada perubahan, dia bakal bikinin file migrasi baru, isinya berupa file Python yang nyatet perubahan skema itu. Tapi penting dicatat, di tahap ini perubahannya belum beneran diterapkan ke database, baru sebatas "rencana" aja.

Nah baru di tahap migrate, file-file migrasi yang udah dibuat tadi dieksekusi ke database beneran. Jadi tabel-tabel di database bakal diperbarui biar sesuai sama skema yang ada di model kita.

Contoh gampangnya kayak gini: misalnya kita baru aja bikin model Project di models.py, dengan field kayak title sama description. Nah biar tabel Project ini beneran muncul di database SQLite kita, kita harus jalanin makemigrations dulu buat nyiapin rancangan tabelnya, terus lanjut jalanin migrate biar tabelnya beneran dibuat di database.
