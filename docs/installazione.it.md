# Codex RDP Plugin for Windows

**Desktop remoto RDP** is a local plugin for Codex and ChatGPT Desktop by **kad26**. It connects to an authorized Windows RDP session in the background and lets the chat request screenshots and send mouse and keyboard input to that session.

## Install and connect

1. Use Windows x64 with the `codex` command and Python 3.13 x64 with `py.exe` and `pyw.exe`. The server must support direct RDP with NLA and NTLM.
2. Extract the ZIP in a permanent folder and run `./Installa.ps1` in PowerShell.
3. Run `./Configura.ps1` and enter your RDP host, its verified public TLS certificate or SHA-256 fingerprint, and your dedicated RDP account. Type the password in the local prompt.
4. Select **Desktop remoto RDP** in a new local chat and ask it to connect and show a screenshot.

The profile uses Windows DPAPI. Screenshot requests send the remote desktop image to the chat. Mouse and keyboard actions use the permissions of the configured RDP account. Run `./Configura.ps1 -Disattiva` to remove the local profile.

## Guida in italiano

Plugin locale per ChatGPT Desktop e Codex su Windows. ChatGPT riceve le immagini della sessione RDP e invia al server click, trascinamenti, rotellina, tasti e testo. Il client RDP funziona in background e lascia libero il mouse, la tastiera e il desktop del PC.

## Cosa serve

- Windows x64 con ChatGPT Desktop o Codex, il comando `codex` e Python 3.13 x64 con i launcher `py.exe` e `pyw.exe`.
- Un server Windows raggiungibile direttamente via RDP dalla rete o VPN. Il server deve accettare login con password via NLA/CredSSP e NTLM.
- Un account con accesso RDP riservato al plugin e una sessione senza Outlook. RDP può riprendere una sessione aperta con lo stesso account e scollegare il client che la stava usando. La disponibilità di sessioni parallele dipende dal server.
- Il certificato TLS pubblico del listener RDP (`.cer` o `.pem`) oppure la sua impronta SHA-256, ottenuti da una fonte attendibile come l'amministratore del server. Il plugin verifica l'impronta prima di iniziare il login. Se il certificato viene rinnovato, esegui nuovamente la configurazione con il certificato verificato.

## Installa e collega il server

Estrai tutto lo ZIP in una cartella stabile. Apri PowerShell nella cartella estratta che contiene `Installa.ps1` ed esegui questi comandi.

```powershell
.\Installa.ps1
.\Configura.ps1
```

Il primo script scarica le dipendenze Python da PyPI con versioni e SHA-256 fissati, poi registra e installa il plugin dal catalogo locale. Il secondo richiede l'indirizzo del server, il certificato o l'impronta, l'account RDP e la password con digitazione nascosta. Usa `DOMINIO\utente` se l'account ha un dominio. La password resta nel profilo locale protetto da Windows DPAPI per l'utente che ha eseguito la configurazione.

Riapri ChatGPT Desktop, avvia una nuova chat locale e seleziona **Desktop remoto RDP** tra i plugin. Come primo controllo scrivi **Usa Desktop remoto RDP per collegarti al server configurato e mostrarmi uno screenshot.** Il collegamento parte alla richiesta in chat.

## Scollega o disattiva

- In chat, chiedi **Disconnetti Desktop remoto RDP**. Il plugin chiude la connessione e la sessione Windows rimane disponibile secondo le regole del server.
- Per revocare l'accesso dal PC, esegui `.\Configura.ps1 -Disattiva`. Viene rimosso il profilo locale e una connessione attiva si chiude entro pochi secondi.
- Il plugin chiude la connessione anche alla fine del processo o dopo 10 minuti senza screenshot o input. Una sola chat può usare il profilo contemporaneamente.

## Ambito

Questa versione supporta un profilo RDP diretto. RD Gateway, accessi che richiedono Smart Card, Kerberos obbligatorio o MFA interattivo richiedono un'altra integrazione. Il plugin scambia immagini e input. Appunti, dischi e dispositivi del PC restano fuori dalla sessione RDP. Gli screenshot richiesti vengono inviati a ChatGPT. Usa una sessione che puoi condividere con la chat. Mouse e tastiera agiscono con i diritti dell'account RDP.

Per Outlook usa il connettore autorizzato. Il client RDP riceve un'immagine della sessione intera, quindi il profilo va destinato a un account e a un desktop riservati senza Outlook.

## Componenti

- `plugins/desktop-remoto` contiene manifest, skill e server MCP locale.
- `Installa.ps1` prepara il runtime e installa dal catalogo in `.agents/plugins/marketplace.json`.
- `Configura.ps1` gestisce il profilo DPAPI in `%LOCALAPPDATA%\CodexDesktopRemoto`.

[Plugin locali in ChatGPT Desktop](https://developers.openai.com/plugins/build/plugins) · [Client RDP Aardwolf](https://github.com/skelsec/aardwolf) · [Sessione singola per account RDP](https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-admx-terminalserver#ts_single_session)
