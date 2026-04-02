#!/usr/bin/env python3
"""
extract_cert_sdn.py
Estrae il Subject DN da tutti i certificati elencati in cert-list.json,
arricchendo ogni record con SDN e metadati estratti dal file fisico.
"""

import argparse
import json
import os
import sys

from cryptography import x509
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend

# ═══════════════════════════════════════════════════════════
#  LOADERS PER FORMATO
# ═══════════════════════════════════════════════════════════

def load_cert_pem(data, **_):
    return x509.load_pem_x509_certificate(data, default_backend())

def load_cert_der(data, **_):
    return x509.load_der_x509_certificate(data, default_backend())

def load_cert_crt(data, **_):
    try:
        return load_cert_pem(data)
    except Exception:
        return load_cert_der(data)

def load_cert_pkcs12(data, password=None, **_):
    pwd_bytes = password.encode("utf-8") if password else None
    _, certificate, _ = pkcs12.load_key_and_certificates(
        data, pwd_bytes, default_backend()
    )
    if certificate is None:
        raise ValueError("Nessun certificato trovato nel file PKCS#12.")
    return certificate

def load_cert_jks(data, password=None, alias=None, **_):
    try:
        import jks
    except ImportError:
        print("[ERROR] Libreria 'pyjks' non installata. Eseguire: pip install pyjks")
        sys.exit(1)

    keystore = jks.KeyStore.loads(data, password or "")

    all_entries = {**keystore.certs, **keystore.private_keys}
    if not all_entries:
        raise ValueError("Nessun certificato trovato nel keystore JKS.")

    selected_alias = alias if alias and alias in all_entries else list(all_entries.keys())[0]
    entry = all_entries[selected_alias]

    if hasattr(entry, "cert"):
        cert_bytes = entry.cert
    elif hasattr(entry, "cert_chain") and entry.cert_chain:
        cert_bytes = entry.cert_chain[0][1]
    else:
        raise ValueError(f"Impossibile estrarre il certificato dall'alias '{selected_alias}'.")

    return x509.load_der_x509_certificate(cert_bytes, default_backend())

LOADERS = {
    "PEM": load_cert_pem,
    "DER": load_cert_der,
    "CRT": load_cert_crt,
    "P12": load_cert_pkcs12,
    "PFX": load_cert_pkcs12,
    "JKS": load_cert_jks,
}

# ═══════════════════════════════════════════════════════════
#  ESTRAZIONE SDN E METADATI
# ═══════════════════════════════════════════════════════════

def extract_sdn(cert):
    return cert.subject.rfc4514_string()

def extract_metadata(cert):
    return {
        "issuer": cert.issuer.rfc4514_string(),
        "serialNumber": str(cert.serial_number),
        "notValidBefore": cert.not_valid_before_utc.isoformat(),
        "notValidAfter": cert.not_valid_after_utc.isoformat(),
    }

# ═══════════════════════════════════════════════════════════
#  PROCESSAMENTO BATCH
# ═══════════════════════════════════════════════════════════

def process_cert_record(record, full_metadata=False):
    """Processa un singolo record del cert-list.json."""
    cert_path = record.get("certFilePath", "")
    cert_format = record.get("certFormat", "").upper()
    cert_password = record.get("certPassword", "") or None
    cert_alias = record.get("certAlias", "") or None
    app_name = record.get("appName", "unknown")

    # ── Verifica esistenza file ──
    if not os.path.isfile(cert_path):
        print(f"[ERROR] [{app_name}] File non trovato: {cert_path}")
        record["_error"] = f"File non trovato: {cert_path}"
        return record

    # ── Verifica formato supportato ──
    loader = LOADERS.get(cert_format)
    if not loader:
        print(f"[ERROR] [{app_name}] Formato '{cert_format}' non supportato.")
        record["_error"] = f"Formato non supportato: {cert_format}"
        return record

    # ── Caricamento certificato ──
    try:
        with open(cert_path, "rb") as f:
            data = f.read()
        cert = loader(data, password=cert_password, alias=cert_alias)
    except Exception as e:
        print(f"[ERROR] [{app_name}] Errore nel caricamento ({cert_format}): {e}")
        record["_error"] = str(e)
        return record

    # ── Estrazione SDN ──
    sdn = extract_sdn(cert)
    record["certSubjectDN"] = sdn
    print(f"[OK] [{app_name}] SDN estratto: {sdn}")

    # ── Metadati opzionali ──
    if full_metadata:
        meta = extract_metadata(cert)
        record.update(meta)
        print(f"     Issuer : {meta['issuer']}")
        print(f"     Validità: {meta['notValidBefore']} → {meta['notValidAfter']}")

    return record

def main():
    parser = argparse.ArgumentParser(
        description="Estrae il Subject DN da tutti i certificati in cert-list.json"
    )
    parser.add_argument("--cert-list", required=True,
                        help="File JSON con i record dei certificati (output di read_input_excel.py)")
    parser.add_argument("--output", required=True,
                        help="File JSON arricchito con SDN e metadati")
    parser.add_argument("--full-metadata", action="store_true",
                        help="Include issuer, serial number e date di validità")
    args = parser.parse_args()

    # ── Caricamento lista certificati ──
    if not os.path.isfile(args.cert_list):
        print(f"[ERROR] File non trovato: {args.cert_list}")
        sys.exit(1)

    with open(args.cert_list) as f:
        certs = json.load(f)

    if not certs:
        print("[WARN] Nessun certificato da processare.")
        with open(args.output, "w") as f:
            json.dump([], f, indent=2)
        return

    # ── Processamento di ogni record ──
    print(f"[INFO] Processamento di {len(certs)} certificato/i...")
    enriched = []
    errors = 0

    for i, record in enumerate(certs, 1):
        print(f"\n── Certificato {i}/{len(certs)} ──")
        result = process_cert_record(record, args.full_metadata)
        enriched.append(result)
        if "_error" in result:
            errors += 1

    # ── Salvataggio output ──
    with open(args.output, "w") as f:
        json.dump(enriched, f, indent=2)

    print(f"\n{'='*50}")
    print(f"[OK] Completato: {len(enriched) - errors} successi, {errors} errori")
    print(f"[OK] Output salvato in {args.output}")

    if errors > 0:
        print(f"[WARN] {errors} certificato/i con errori. Verificare i record con campo '_error'.")
        sys.exit(1)

if __name__ == "__main__":
    main()