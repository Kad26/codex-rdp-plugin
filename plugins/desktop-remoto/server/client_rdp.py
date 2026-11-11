import asyncio
import hashlib
import hmac

from aardwolf.commons.iosettings import RDPIOSettings
from aardwolf.commons.target import RDPTarget
from aardwolf.connection import RDPConnection
from aardwolf.protocol.x224.constants import SUPP_PROTOCOLS
from asyauth.common.constants import asyauthSecret
from asyauth.common.credentials.ntlm import NTLMCredential

from profilo import RdpError


NLA_PROTOCOLS = (SUPP_PROTOCOLS.HYBRID, SUPP_PROTOCOLS.HYBRID_EX)


class PinnedRdpClient(RDPConnection):
    """Bind credential use to the certificate on the same RDP TLS connection."""

    def __init__(self, profile, ip):
        target = RDPTarget(ip=ip, port=profile.port, hostname=profile.host, timeout=6,
                           domain=profile.domain or None, autologon=False)
        settings = RDPIOSettings()
        settings.channels = []
        settings.vchannels = {}
        settings.clipboard_use_pyperclip = False
        settings.video_width = 1280
        settings.video_height = 800
        settings.keyboard_layout = 1040
        settings.supported_protocols = SUPP_PROTOCOLS.HYBRID | SUPP_PROTOCOLS.HYBRID_EX

        # Keep the password out of the base client's legacy authentication paths.
        super().__init__(target, None, settings)
        self.pending_credentials = NTLMCredential(
            profile.password, profile.username, profile.domain or None, asyauthSecret.PASSWORD
        )
        self.fingerprint = profile.fingerprint
        self.authenticated = False

    async def credssp_auth(self):
        # These two private hooks are tied to the pinned aardwolf version in requirements.lock.
        try:
            certificate = self._RDPConnection__connection.get_peer_certificate()
        except Exception:
            certificate = None
        if self.x224_protocol not in NLA_PROTOCOLS or not certificate:
            return None, RdpError("Il server deve usare RDP con NLA e certificato TLS.")
        if not hmac.compare_digest(hashlib.sha256(certificate).hexdigest(), self.fingerprint):
            return None, RdpError("Certificato RDP diverso da quello configurato. Verifica il certificato del server.")

        self.credentials, self.pending_credentials = self.pending_credentials, None
        try:
            success, error = await super().credssp_auth()
            if error or success is not True:
                return None, RdpError("Login NLA rifiutato. Verifica account, password e autorizzazione RDP.")
            self.authenticated = True
            return True, None
        finally:
            self.credentials.secret = None

    async def _RDPConnection__establish_channels(self):
        if not self.authenticated:
            return None, RdpError("Il server deve accettare autenticazione RDP NLA (CredSSP).")
        return await super()._RDPConnection__establish_channels()

    async def send_disconnect(self):
        # Disconnect by closing TCP. The library's default sends an RDP shutdown request.
        return True, None

    async def open(self):
        try:
            success, error = await asyncio.wait_for(self.connect(), 27)
        except TimeoutError:
            raise RdpError("Connessione RDP scaduta. Verifica rete o VPN e disponibilità del server.") from None
        finally:
            self.pending_credentials = None
            self.authapi = None
        if isinstance(error, RdpError):
            raise error
        if not success or error:
            raise RdpError("Connessione RDP non riuscita. Verifica indirizzo, porta e compatibilità NLA.") from None

    async def close(self):
        transport = self._RDPConnection__connection
        if transport is not None:
            await transport.close()
        self.disconnected_evt.set()
        await asyncio.wait_for(self._RDPConnection__cleanup_failed_connect(), 2)
