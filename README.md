# Prenotazione Automatica Unimi
Questo script serve per prenotare automaticamente le lezioni in presenza dell'
UNIMI durante il periodo di quarantena. Idealmente è uno script da utilizzare
con cron.

Installazione
============
Per installare
```
pip install prenotazione-unimi
```

Utilizzo
=======
Per vedere tutti gli utilizzi esegui `python3 main.py --help`. Puoi specificare
i parametri `--username`, `--password` e `--cf-code` utilizzando
rispettivamente le variabili d'ambiente `UNIMI_USERNAME`, `UNIMI_PASSWORD` e
`UNIMI_CF`.

Prima di poterlo usare comunque avrete bisogno di configurare il vostro profilo
sul sito per le prenotazioni, altrimenti lo script non riuscirà a prendere gli
ID delle varie lezioni.

![alt_text](https://raw.githubusercontent.com/Mroik/Prenotazione-Automatica-Unimi/master/unknown.png)
