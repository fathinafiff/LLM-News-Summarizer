import re
from collections import Counter

def preprocessing(teks):
    # Tokenisasi kalimat
    kalimat = re.split(r'[.!?]', teks)
    kalimat = [k.strip() for k in kalimat if k.strip()]
    return kalimat

def hitung_frekuensi(teks):
    # Tokenisasi kata dan hitung frekuensi
    kata_kata = re.findall(r'\b\w+\b', teks.lower())
    frekuensi = Counter(kata_kata)
    return frekuensi

def skor_kalimat(kalimat, frekuensi):
    # Hitung skor kalimat berdasarkan frekuensi kata
    skor = {}
    for k in kalimat:
        kata_kata = re.findall(r'\b\w+\b', k.lower())
        skor[k] = sum(frekuensi[kata] for kata in kata_kata if kata in frekuensi)
    return skor

def buat_ringkasan(teks, n_kalimat=3):
    # Proses teks
    kalimat = preprocessing(teks)
    frekuensi = hitung_frekuensi(teks)
    skor = skor_kalimat(kalimat, frekuensi)
    # Pilih kalimat terbaik
    kalimat_terpilih = sorted(skor, key=skor.get, reverse=True)[:n_kalimat]
    return ' '.join(kalimat_terpilih)

# Contoh artikel
artikel = """
Indonesia adalah negara kepulauan terbesar di dunia. Dengan lebih dari 17 ribu pulau, Indonesia kaya akan keanekaragaman budaya. Ekonomi negara ini juga terus berkembang, terutama di sektor teknologi dan pariwisata. Meski begitu, tantangan seperti infrastruktur dan pemerataan ekonomi masih harus diatasi.
"""

# Buat ringkasan
ringkasan = buat_ringkasan(artikel)
print("Ringkasan:", ringkasan)
