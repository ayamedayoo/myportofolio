/*
 * Fungsi bantu yang dipakai bersama oleh halaman-halaman AJAX (Project, Award).
 * Dimuat sekali lewat base.html supaya tidak perlu disalin ke setiap halaman.
 */

/**
 * Ubah karakter khusus HTML menjadi entity supaya tampil sebagai teks, bukan dijalankan.
 * '&' diganti paling awal agar hasil penggantian lain tidak ikut diubah lagi.
 * Tanda kutip ikut di-escape karena sebagian nilai disisipkan ke dalam atribut.
 */
function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

/** Baca nilai sebuah cookie, misalnya 'csrftoken' untuk header X-CSRFToken. */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Ubah balasan error JSON dari server menjadi satu kalimat untuk toast.
 * Mendukung format {errors: form.errors.get_json_data()} dan {message: "..."}.
 */
function collectErrorMessages(result, status) {
  if (result && result.errors) {
    return Object.values(result.errors).flat().map(error => error.message).join(' ');
  }
  return (result && result.message) || `Terjadi kesalahan (status ${status}).`;
}
