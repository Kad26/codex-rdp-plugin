# Plugin RDP per Codex

**Desktop remoto RDP** è un plugin di **kad26** per Codex e ChatGPT Desktop su Windows. Apre in background una sessione Desktop remoto e permette alla chat di vedere lo schermo, fare click e digitare sul server.

## Installazione

1. Scarica `Desktop-Remoto-RDP-v0.1.0-kad26.zip` dalla [sezione Release](https://github.com/Kad26/codex-rdp-plugin/releases). Lo ZIP include il codice e gli script.
2. Estrai lo ZIP in una cartella stabile ed esegui `./Installa.ps1` e `./Configura.ps1` da PowerShell.
3. In una nuova chat locale, seleziona **Desktop remoto RDP** e chiedi di mostrarti uno screenshot del server configurato.

## Requisiti e permessi

L’anteprima richiede Windows x64, il comando `codex`, Python 3.13 x64 e un server raggiungibile via RDP diretto con NLA e NTLM. Durante la configurazione inserisci il certificato pubblico verificato del server o la sua impronta SHA-256 e un account dedicato.

La password si digita in locale e il profilo è protetto da Windows DPAPI. Gli input usano i diritti dell’account RDP. Gli screenshot richiesti sono visibili nella chat. Per istruzioni e limiti dettagliati, consulta il README incluso nello ZIP.
