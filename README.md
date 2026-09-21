# Portofolio - Samuel Kaevin Phasca

Nama : Samuel Kaevin Phasca

NPM : 2506657333

Kelas : PBP E

## Deskripsi Proyek

Website portofolio pribadi berbasis Django, dibuat sebagai bagian dari tugas mata kuliah Pemrograman Berbasis Platform (PBP). Awalnya (Tugas 1) halaman ini cuma HTML dan CSS statis. Sekarang datanya sudah disimpan di database dan sebagian bisa dikelola langsung dari website lewat form.

Halaman yang ada saat ini:

- **Profile**: data diri (nama, NPM, foto, bio, tautan sosial) dan timeline pengalaman.
- **Experience**: daftar pengalaman dari database.
- **Project**: daftar proyek yang bisa ditambah, diedit, dihapus, dan dicari berdasarkan nama.
- **Award**: daftar penghargaan yang bisa ditambah, diedit, dihapus, difilter per tingkat, dan dicari. Tampilan kartunya sengaja dibiarkan sama seperti versi awal supaya konsisten dengan halaman Experience dan Project.

### Progres Mingguan

| Minggu | Yang dikerjakan |
| --- | --- |
| Tugas 1 | Halaman profile statis dengan HTML semantik dan CSS responsif (Grid + Flexbox), deploy ke PWS. |
| Tugas 2 | Model `Experience`, `Project`, dan `Award`, halaman untuk tiap model, unit test, dan script `populate_data.py` untuk isi data awal dari CV. |
| Tutorial 3 | Template dasar `base.html`, form tambah proyek, hapus proyek, dan data proyek yang disajikan lewat JSON. |
| Tugas 3 | Refactor template, CRUD lengkap + JSON untuk bagian Award, edit proyek, JSON untuk semua data, dan beberapa perbaikan tampilan (detail di bawah). |


### Endpoint

| URL | Keterangan |
| --- | --- |
| `/award/` | Daftar award (dari JSON yang dideserialisasi), mendukung `?level=` dan `?q=` |
| `/award/add/` | Form tambah award |
| `/award/<uuid>/edit/` | Form edit award |
| `/award/<uuid>/delete/` | Hapus award (POST) |
| `/project/add/`, `/project/<uuid>/edit/`, `/project/<uuid>/delete/` | Tambah, edit, dan hapus proyek |
| `/api/awards/` | Semua award dalam JSON, mendukung `?level=` dan `?q=` |
| `/api/awards/<uuid>/` | Satu award dalam JSON |
| `/api/projects/` | Semua proyek dalam JSON, mendukung `?title=` |
| `/api/projects/<uuid>/` | Satu proyek dalam JSON |
| `/api/experiences/` | Semua experience dalam JSON |

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
5. Jalankan migrasi, isi data awal (opsional), lalu jalankan server development:
   ```
   python manage.py migrate
   python populate_data.py
   python manage.py runserver
   ```
   Kalau sebelumnya sudah pernah menjalankan proyek ini, `migrate` tetap wajib dijalankan ulang karena Tugas 3 menambah kolom baru di tabel Award.
6. Buka `http://localhost:8000/` di browser.
7. Untuk menjalankan unit test:
   ```
   python manage.py test
   ```

## Deployment

Proyek di-deploy ke PWS Fasilkom UI (Dockerfile + gunicorn, binding ke port 80 sesuai konvensi Traefik platform PWS) di `samuel-kaevin-myportofolio.pws.cs.ui.ac.id`.

## AI Disclosure

Saya memakai **Claude Code** (lewat aplikasi desktop Claude) sebagai teman diskusi dan pembimbing selama mengerjakan proyek ini. Posisinya lebih ke "asdos pribadi" yang bisa ditanya kapan saja: memberi rekomendasi, menunjukkan arah, dan membantu menyusun draf kode. Keputusan, pengecekan, dan tanggung jawab atas hasil akhirnya tetap di saya.

**Tugas 1**

- Debugging deployment: deployment ke PWS sempat gagal (404, lalu Bad Gateway). Saya minta Claude membaca source code dan menelusuri penyebabnya. Ketemu bahwa repo belum punya Dockerfile dan `ALLOWED_HOSTS` salah tulis. Claude juga merujuk dokumentasi PWS untuk memastikan port yang benar (80, bukan 8080) sebelum saya commit perbaikannya.

**Tugas 3**
1. Claude membantu saya untuk melakukan debugging, melakukan test, melakukan konsultasi, dan melakukan pembantuan jika aku mengalami eror



## Pertanyaan Reflektif

### Tugas 1

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

### Tugas 3

1. Kalau bikin form HTML manual, kita harus nulis sendiri tiap `<input>`, nyamain `name`-nya dengan field di model, terus di view ngambil `request.POST["title"]` satu-satu, ngecek kosong atau tidak, ngecek tipe datanya bener atau tidak, baru disimpan. Capek, dan gampang ada yang kelewat. Dengan `ModelForm`, Django baca langsung definisi model kita: field apa saja yang ada, tipenya apa, wajib atau opsional, panjang maksimalnya berapa. Dari situ dia otomatis bikin input yang sesuai (misalnya field dengan `choices` jadi dropdown, `BooleanField` jadi checkbox), sekaligus validasinya. Di view tinggal `form.is_valid()` lalu `form.save()`. Buat form update juga enak banget, cukup kasih `instance=award` dan semua field langsung terisi data lama. Jadi model tetap jadi satu-satunya sumber kebenaran. Kalau nanti saya nambah field di model Award, form-nya ikut menyesuaikan tanpa harus ngoprek HTML lagi.

   Soal `{% csrf_token %}`: ini untuk melindungi dari serangan CSRF (Cross-Site Request Forgery). Bayangin saya lagi login di website portofolio saya, terus di tab lain saya buka situs iseng yang diam-diam punya form tersembunyi yang nge-POST ke `/award/<id>/delete/`. Browser bakal ikut ngirim cookie login saya, jadi dari sisi server request itu kelihatan sah, seolah-olah saya sendiri yang klik hapus. Token CSRF mencegah ini: Django menyisipkan token acak di tiap form yang dia render, dan setiap POST yang masuk harus membawa token yang cocok. Situs lain tidak bisa tahu token itu, jadi request palsunya ditolak (403). Makanya token ini wajib ada di semua form yang mengubah data, termasuk form kecil di balik tombol hapus.

2. Menurut saya alasan utamanya karena JSON itu "bahasa asli"-nya JavaScript, sedangkan hampir semua frontend web modern ditulis pakai JavaScript. Data JSON bisa langsung dipakai dengan `response.json()` dan jadi objek biasa, tanpa parser khusus seperti XML yang harus ditelusuri node-nya satu-satu. JSON juga jauh lebih ringkas. Di XML, setiap data dibungkus tag pembuka dan penutup (`<title>...</title>`), jadi ukurannya lebih besar dan lebih capek dibaca. Selain itu JSON punya tipe data dasar seperti angka, boolean, `null`, array, dan objek, sedangkan di XML semuanya pada dasarnya teks. Contohnya `is_featured` di data award saya: di JSON muncul sebagai `true` beneran, bukan teks `"True"` yang harus dikonversi dulu. XML sebenarnya masih punya tempat, misalnya untuk dokumen yang butuh skema ketat atau sistem lama seperti SOAP dan RSS. Tapi untuk API web yang dipakai frontend dan aplikasi mobile, JSON jauh lebih praktis.

3. Contohnya waktu saya buka `/api/awards/?level=national`. Request masuk ke `urls.py` dan dicocokkan ke fungsi `get_awards_json`. Di dalam view, saya mulai dari `Award.objects.all()`, lalu kalau ada parameter `level` atau `q` saya tambahkan `.filter(...)`. Sampai sini datanya masih berupa QuerySet, yaitu kumpulan objek Python yang cuma dimengerti oleh Django. QuerySet itu lalu dimasukkan ke `serializers.serialize("json", awards)`, yang mengubah setiap objek jadi teks JSON berisi `model`, `pk`, dan `fields`. Teks itu dibungkus `HttpResponse` dengan `content_type="application/json"` supaya penerimanya tahu isinya JSON, bukan HTML. Di halaman `/award/`, saya justru memanggil view JSON ini dulu, lalu hasilnya dideserialisasi balik jadi objek `Award` dengan `serializers.deserialize`, baru dikirim ke template.

   Kenapa harus diserialisasi? Karena objek model Django itu hidup di memori Python. Isinya bukan cuma data, tapi juga method, hubungan ke database, dan tipe-tipe khusus seperti `UUID`, `date`, dan `datetime`. Semua itu tidak bisa dikirim begitu saja lewat HTTP, karena HTTP cuma bisa mengirim teks atau byte. Kalau dicoba `json.dumps(award)` langsung, Python akan error karena tidak tahu cara mengubah objek `Award` jadi JSON. Serialisasi adalah proses menerjemahkan objek itu ke format netral yang bisa dibaca siapa saja, entah JavaScript di browser, aplikasi Flutter, atau sistem lain yang sama sekali tidak kenal Django.
