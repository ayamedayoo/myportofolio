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

/**
 * Ubah balasan error dari API DRF menjadi satu kalimat untuk toast.
 * Mendukung error serializer ({"title": ["..."]}) dan error umum ({"detail": "..."}).
 */
function apiErrorMessage(data, status) {
  const messages = Object.values(data || {}).flat().filter(value => typeof value === 'string');
  return messages.join(' ') || `Permintaan gagal (HTTP ${status}).`;
}

/**
 * Kirim permintaan yang mengubah data ke API: body JSON, header X-CSRFToken, dan
 * pengecekan status dilakukan di satu tempat. Melempar ApiError kalau status bukan 2xx.
 */
class ApiError extends Error {
  constructor(data, status) {
    super(apiErrorMessage(data, status));
    this.data = data;
    this.status = status;
  }
}

async function apiWrite(url, method, payload) {
  const response = await fetch(url, {
    method,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: payload === undefined ? undefined : JSON.stringify(payload),
  });
  if (response.status === 204) return null; // DELETE berhasil, body kosong
  // Respons yang bukan JSON (mis. halaman error) dianggap objek kosong
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new ApiError(data, response.status);
  return data;
}
