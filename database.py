# database.py
# Semua urusan database SQLite ada di file ini.
import sqlite3
from pathlib import Path

# File database akan dibuat otomatis di folder project
DB_FILE = Path(__file__).parent / "kampus.db"


def koneksi():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row   # hasil query bisa dipanggil pakai nama kolom
    return conn


def buat_tabel():
    with koneksi() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mahasiswa (
                nim           INTEGER PRIMARY KEY,
                nama          TEXT    NOT NULL,
                program_studi TEXT    NOT NULL,
                angkatan      INTEGER NOT NULL,
                ipk           REAL    NOT NULL
            )
        """)


# Lama studi dihitung oleh SQLite: tahun sekarang - angkatan
QUERY_DENGAN_LAMA_STUDI = """
    SELECT *, CAST(strftime('%Y', 'now', 'localtime') AS INTEGER) - angkatan AS lama_studi
    FROM mahasiswa
"""


def semua_mahasiswa():
    with koneksi() as conn:
        return conn.execute(QUERY_DENGAN_LAMA_STUDI + " ORDER BY nama").fetchall()


def cari_mahasiswa(nim):
    with koneksi() as conn:
        return conn.execute(QUERY_DENGAN_LAMA_STUDI + " WHERE nim = ?", (nim,)).fetchone()


def tambah_mahasiswa(nim, nama, prodi, angkatan, ipk):
    with koneksi() as conn:
        conn.execute(
            "INSERT INTO mahasiswa (nim, nama, program_studi, angkatan, ipk) VALUES (?, ?, ?, ?, ?)",
            (nim, nama, prodi, angkatan, ipk),
        )


def ubah_mahasiswa(nim, nama, prodi, angkatan, ipk):
    with koneksi() as conn:
        conn.execute(
            "UPDATE mahasiswa SET nama = ?, program_studi = ?, angkatan = ?, ipk = ? WHERE nim = ?",
            (nama, prodi, angkatan, ipk, nim),
        )


def hapus_mahasiswa(nim):
    with koneksi() as conn:
        conn.execute("DELETE FROM mahasiswa WHERE nim = ?", (nim,))