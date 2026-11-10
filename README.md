# Codex RDP Plugin for Windows

**Desktop remoto RDP** is a plugin by **kad26** for Codex and ChatGPT Desktop. It connects to a Windows Remote Desktop (RDP) session in the background so the chat can request screenshots and send mouse or keyboard input to that session.

## Download and install

1. Download `Desktop-Remoto-RDP-v0.1.0-kad26.zip` from [Releases](https://github.com/Kad26/codex-rdp-plugin/releases). The ZIP includes the plugin source, setup scripts, and instructions in English and Italian.
2. Extract the ZIP to a permanent folder. Run `.\Installa.ps1` and then `.\Configura.ps1` from PowerShell.
3. In a new local chat, select **Desktop remoto RDP** and ask it to connect and show a screenshot.

## Requirements

The preview requires Windows x64, the Codex CLI, Python 3.13 x64, and a Windows server reachable over direct RDP with NLA and NTLM. Configure a dedicated RDP account and provide the server’s verified public TLS certificate or SHA-256 fingerprint.

Enter the password in the local setup prompt. Windows DPAPI protects the saved profile. Screenshots requested by the plugin are sent to the chat, and remote input runs with the permissions of the configured RDP account.
