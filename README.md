# Prenotazione Automatica Unimi
Questo script serve per prenotare automaticamente le lezioni in presenza dell'UNIMI durante il periodo di quarantena.
Idealmente è uno script da utilizzare con cron.

Utilizzo
=======
Per vedere tutti gli utilizzi esegui `python3 main.py --help`. Puoi specificare i parametri `--username`, `--password` 
e `--cf-code` utilizzando rispettivamente le variabili d'ambiente `UNIMI_USERNAME`, `UNIMI_PASSWORD` e `UNIMI_CF`.
Se voleste utilizzarlo in cron la mia configurazione è
```
0 19 * * * python3 main.py -u "mroik@studenti.unimi.it" -p "$(kwallet-query -f Passwords -r unimi default)" book --cf-code "MRKMRK69R13E200C" --exclude "linguaggi formali e automi"
```

Prima di poterlo usare comunque avrete bisogno di configurare il vostro profilo sul sito per le prenotazioni, altrimenti lo script non riuscirà
a prendere gli ID delle varie lezioni.

![alt_text](https://raw.githubusercontent.com/Mroik/Prenotazione-Automatica-Unimi/master/unknown.png)
