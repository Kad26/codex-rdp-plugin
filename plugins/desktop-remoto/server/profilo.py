import argparse
from dataclasses import asdict, dataclass, field
import getpass
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import tempfile
from urllib.parse import urlsplit
import warnings

from cryptography import x509
from cryptography.hazmat.primitives import hashes
import win32crypt


class RdpError(Exception):
    pass


@dataclass(frozen=True)
class Profile:
    host: str
    port: int
    username: str
    domain: str
    fingerprint: str
    password: str = field(repr=False)

    @property
    def address(self):
        host = f"[{self.host}]" if ":" in self.host else self.host
        return f"{host}:{self.port}"


def parse_address(address):
    try:
        target = urlsplit(f"rdp://{address}")
        port = target.port if target.port is not None else 3389
        host = target.hostname
        if (not host or not 1 <= port <= 65535 or target.username is not None
                or target.path or target.query or target.fragment):
            raise ValueError
        if address != address.strip() or any(char.isspace() for char in address):
            raise ValueError
        if ":" in host:
            ipaddress.IPv6Address(host)
        elif not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9.-]{0,252}", host):
            raise ValueError
        if is_local_name(host):
            raise RdpError("Inserisci l'indirizzo del server remoto.")
        return host, port
    except ValueError:
        raise RdpError("Indirizzo RDP non valido. Usa nome o IP, con porta opzionale.") from None


def is_local_name(host):
    host = host.rstrip(".").lower()
    return host in {"localhost", socket.gethostname().lower()} or host.endswith(".localhost")


def address_ip(ip):
    address = ipaddress.ip_address(ip.split("%", 1)[0])
    return getattr(address, "ipv4_mapped", None) or address


def resolve_destination(profile):
    if is_local_name(profile.host):
        raise RdpError("Il profilo deve puntare a un server remoto.")
    try:
        # Use the resolved IP for the entire connection. TLS still checks the configured pin.
        destinations = socket.getaddrinfo(profile.host, profile.port, type=socket.SOCK_STREAM)
        local_ips = {
            address_ip(item[4][0])
            for item in socket.getaddrinfo(socket.gethostname(), None, type=socket.SOCK_STREAM)
        }
    except OSError:
        raise RdpError("Risoluzione del server RDP non riuscita.") from None

    for family, _, _, _, endpoint in destinations:
        ip = endpoint[0]
        address = address_ip(ip)
        if address.is_loopback or address.is_unspecified or address in local_ips:
            raise RdpError("Il profilo punta a un indirizzo del PC locale.")
        if address.is_multicast or address.is_link_local:
            raise RdpError("Usa un indirizzo unicast del server remoto sulla rete o VPN.")
    if not destinations:
        raise RdpError("Nessun indirizzo RDP disponibile.")
    # Prefer IPv4 for hosts with both address families.
    return min(destinations, key=lambda item: item[0] != socket.AF_INET)[4][0]


def fingerprint_from_input(value):
    fingerprint = re.sub(r"[\s:]", "", value).lower()
    if re.fullmatch(r"[0-9a-f]{64}", fingerprint):
        return fingerprint
    try:
        raw = Path(value.strip('"')).read_bytes()
        cert = (x509.load_pem_x509_certificate(raw) if b"-----BEGIN CERTIFICATE-----" in raw
                else x509.load_der_x509_certificate(raw))
        return cert.fingerprint(hashes.SHA256()).hex()
    except (OSError, ValueError):
        raise RdpError("Fornisci un certificato pubblico .cer/.pem o 64 cifre esadecimali SHA-256.") from None


def profile_path(state_dir):
    return state_dir / "server.dpapi"


def read_profile_blob(state_dir):
    try:
        with profile_path(state_dir).open("rb") as stream:
            blob = stream.read(16385)
        if not 0 < len(blob) <= 16384:
            raise RdpError("Profilo RDP illeggibile. Esegui Configura.ps1.")
        return blob
    except FileNotFoundError:
        raise RdpError("Nessun server configurato. Esegui Configura.ps1 sul PC.") from None
    except OSError:
        raise RdpError("Profilo RDP illeggibile. Esegui Configura.ps1.") from None


def decrypt_profile(blob):
    try:
        _, raw = win32crypt.CryptUnprotectData(blob, None, None, None, 1)
        return Profile(**json.loads(raw))
    except Exception:
        raise RdpError("Impossibile leggere il profilo Windows. Esegui Configura.ps1 con questo account.") from None


def save_profile(state_dir, profile):
    data = json.dumps(asdict(profile), ensure_ascii=False).encode("utf-8")
    encrypted = win32crypt.CryptProtectData(data, "Desktop remoto RDP", None, None, None, 1)
    with tempfile.NamedTemporaryFile(dir=state_dir, delete=False) as stream:
        tmp = Path(stream.name)
        stream.write(encrypted)
    try:
        os.replace(tmp, profile_path(state_dir))
    finally:
        tmp.unlink(missing_ok=True)


def configure_cli(state_dir):
    parser = argparse.ArgumentParser(description="Configura il profilo RDP locale.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--configura", action="store_true")
    mode.add_argument("--disattiva", action="store_true")
    args = parser.parse_args()

    if args.disattiva:
        profile_path(state_dir).unlink(missing_ok=True)
        print("Profilo rimosso. La connessione del plugin si chiude entro pochi secondi.")
        return

    try:
        print("Usa un account RDP dedicato e una sessione riservata senza Outlook.")
        host, port = parse_address(input("Indirizzo del server (nome o IP[:porta]) > ").strip())
        fingerprint = fingerprint_from_input(input("Certificato pubblico verificato (.cer) o SHA-256 > ").strip())
        login = input("Account RDP (utente oppure DOMINIO\\utente) > ").strip()
        domain, _, username = login.rpartition("\\")
        if not username or len(login) > 256 or any(ord(char) < 32 for char in login):
            raise RdpError("Account RDP non valido.")
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            password = getpass.getpass("Password RDP (digitazione nascosta) > ")
        if not password or len(password) > 256 or "\0" in password:
            raise RdpError("Password vuota o non valida.")
        profile = Profile(host, port, username, domain, fingerprint, password)
        save_profile(state_dir, profile)
        print(f"Profilo Windows salvato per {profile.address}.")
    except (EOFError, KeyboardInterrupt, getpass.GetPassWarning):
        parser.exit(1, "Configurazione interrotta. Usa un terminale PowerShell interattivo.\n")
    except RdpError as error:
        parser.exit(1, f"{error}\n")
    except Exception:
        parser.exit(1, "Impossibile salvare il profilo Windows.\n")
