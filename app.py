# app.py
# File utama: berisi semua route (alamat halaman) dan validasi input.
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
import database as db

app = Flask(__name__)
app.secret_key = "kunci-rahasia-uts"   # dibutuhkan oleh flash()


def cek_input(form, cek_nim=True):
    """Memeriksa isian form. Mengembalikan (data, daftar_kesalahan)."""
    salah = []
    nim = form.get("nim", "").strip()
    nama = form.get("nama", "").strip()
    prodi = form.get("program_studi", "").strip()
    angkatan = form.get("angkatan", "").strip()
    ipk = form.get("ipk", "").strip().replace(",", ".")

    if cek_nim:
        if not nim:
            salah.append("NIM tidak boleh kosong.")
        elif not nim.isdigit():
            salah.append("NIM hanya boleh berisi angka.")
    if not nama:
        salah.append("Nama tidak boleh kosong.")
    if not prodi:
        salah.append("Program studi tidak boleh kosong.")
    if not angkatan.isdigit():
        salah.append("Angkatan wajib diisi tahun, contoh 2024.")
    try:
        if not 0 <= float(ipk) <= 4:
            salah.append("IPK harus berada di antara 0.00 sampai 4.00.")
    except ValueError:
        salah.append("IPK wajib diisi angka, contoh 3.25.")

    data = {"nim": nim, "nama": nama, "program_studi": prodi,
            "angkatan": angkatan, "ipk": ipk}
    return data, salah


# READ: halaman utama, berisi form tambah + tabel daftar mahasiswa
@app.route("/")
def beranda():
    return render_template("index.html", daftar=db.semua_mahasiswa(), isian={}, salah=[])


# CREATE: menyimpan mahasiswa baru dari form di halaman utama
@app.route("/simpan", methods=["POST"])
def simpan():
    data, salah = cek_input(request.form)
    if not salah:
        try:
            db.tambah_mahasiswa(int(data["nim"]), data["nama"], data["program_studi"],
                                int(data["angkatan"]), float(data["ipk"]))
            flash(f"Data {data['nama']} berhasil disimpan.")
            return redirect(url_for("beranda"))
        except sqlite3.IntegrityError:
            # NIM adalah PRIMARY KEY, jadi database menolak NIM yang sama
            salah.append(f"NIM {data['nim']} sudah terdaftar, gunakan NIM lain.")
    return render_template("index.html", daftar=db.semua_mahasiswa(),
                           isian=data, salah=salah), 400


# READ: halaman detail satu mahasiswa
@app.route("/detail/<int:nim>")
def detail(nim):
    mhs = db.cari_mahasiswa(nim)
    if mhs is None:
        flash("Mahasiswa tidak ditemukan.")
        return redirect(url_for("beranda"))
    return render_template("detail.html", mhs=mhs)


# UPDATE: GET menampilkan form berisi data lama, POST menyimpan perubahan
@app.route("/ubah/<int:nim>", methods=["GET", "POST"])
def ubah(nim):
    mhs = db.cari_mahasiswa(nim)
    if mhs is None:
        flash("Mahasiswa tidak ditemukan.")
        return redirect(url_for("beranda"))

    if request.method == "POST":
        data, salah = cek_input(request.form, cek_nim=False)   # NIM tidak bisa diubah
        if not salah:
            db.ubah_mahasiswa(nim, data["nama"], data["program_studi"],
                              int(data["angkatan"]), float(data["ipk"]))
            flash(f"Data {data['nama']} berhasil diubah.")
            return redirect(url_for("beranda"))
        data["nim"] = nim
        return render_template("ubah.html", isian=data, salah=salah), 400

    return render_template("ubah.html", isian=mhs, salah=[])


# DELETE: menghapus mahasiswa
@app.route("/hapus/<int:nim>", methods=["POST"])
def hapus(nim):
    db.hapus_mahasiswa(nim)
    flash("Data mahasiswa berhasil dihapus.")
    return redirect(url_for("beranda"))


if __name__ == "__main__":
    db.buat_tabel()   # membuat tabel kalau belum ada
    app.run(debug=True)