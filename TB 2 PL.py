import mysql.connector
from mysql.connector import Error
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HttpException(Exception):
    pass


class Buku:
    def __init__(self, judul, penulis, penerbit=None, tahun_terbit=None, konten=None, ikhtisar=None):
        self.judul = judul
        self.penulis = penulis
        self.penerbit = penerbit
        self.tahun_terbit = tahun_terbit
        self.konten = konten if konten else []
        self.ikhtisar = ikhtisar

    def read(self, halaman):
        if halaman < 1 or halaman > len(self.konten):
            raise HttpException(f"Halaman {halaman} tidak tersedia untuk buku ini.")
        else:
            return self.konten[halaman - 1]

    def __str__(self):
        return f"{self.judul} by {self.penulis}"

    def post(self):
        try:
            conn = mysql.connector.connect(
                host='localhost',
                database='perpustakaan',
                user='root',
                password='@Aulia231'
            )

            if conn.is_connected():
                cursor = conn.cursor()

                query = '''
                    INSERT INTO buku (judul, penulis, penerbit, tahun_terbit, konten, ikhtisar)
                    VALUES (%s, %s, %s, %s, %s, %s)
                '''
                values = (self.judul, self.penulis, self.penerbit, self.tahun_terbit, '\n'.join(self.konten), self.ikhtisar)

                cursor.execute(query, values)
                conn.commit()

                logger.info(f"Buku '{self.judul}' berhasil disimpan.")

        except Error as e:
            logger.error(f"Error saat menyimpan buku: {e}")
            raise HttpException("Terjadi kesalahan saat menyimpan buku.")

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
                logger.info("Koneksi ke MySQL ditutup.")


# Fungsi untuk membuat tabel buku jika belum ada
def create_table_buku():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='perpustakaan',
            user='root',
            password='@Aulia231'
        )

        if conn.is_connected():
            cursor = conn.cursor()

            create_table_query = '''
                CREATE TABLE IF NOT EXISTS buku (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    judul VARCHAR(255) NOT NULL,
                    penulis VARCHAR(255) NOT NULL,
                    penerbit VARCHAR(255),
                    tahun_terbit YEAR,
                    konten TEXT,
                    ikhtisar TEXT
                )
            '''

            cursor.execute(create_table_query)
            logger.info("Tabel 'buku' berhasil dibuat atau sudah ada sebelumnya.")

    except Error as e:
        logger.error(f"Error saat membuat tabel buku: {e}")
        raise HttpException("Terjadi kesalahan saat membuat tabel buku.")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            logger.info("Koneksi ke MySQL ditutup.")


# Fungsi untuk mengambil data buku dari basis data
def get_buku():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='perpustakaan',
            user='root',
            password='@Aulia231'
        )

        if conn.is_connected():
            cursor = conn.cursor()

            query = "SELECT * FROM buku"
            cursor.execute(query)

            bukus = []
            for (id, judul, penulis, penerbit, tahun_terbit, konten, ikhtisar) in cursor:
                buku = Buku(judul, penulis, penerbit, tahun_terbit, konten.split('\n'), ikhtisar)
                bukus.append(buku)

            return bukus

    except Error as e:
        logger.error(f"Error saat mengambil data buku: {e}")
        raise HttpException("Terjadi kesalahan saat mengambil data buku.")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            logger.info("Koneksi ke MySQL ditutup.")


# Contoh penggunaan
if __name__ == "__main__":
    # Membuat tabel buku jika belum ada
    create_table_buku()

    # Menyimpan buku ke basis data
    buku_baru = Buku("Keseharian Bersama Aul", "Aulia Thalita Salsabhila", "atas izin penulis", 2024,
                     ["Siapa itu aul?", "Kegiatan apa saja yang biasa dilakukan",
                      "Makanan Kesukaan Aul", "Tempat favorit aul",
                      "QnA"], "Buku ini memberitahu bagaimana keseharian aul")
    buku_baru.post()

    # Mengambil data buku dari basis data
    try:
        bukus = get_buku()
        for buku in bukus:
            print(f"Judul: {buku.judul}")
            print(f"Penulis: {buku.penulis}")
            print(f"Penerbit: {buku.penerbit}")
            print(f"Tahun Terbit: {buku.tahun_terbit}")
            print("Konten:")
            for i, halaman in enumerate(buku.konten, start=1):
                print(f"Halaman {i}: {halaman}")
            print(f"Ikhtisar: {buku.ikhtisar}")
            print()

    except HttpException as e:
        logger.error(f"HttpException: {e}")
