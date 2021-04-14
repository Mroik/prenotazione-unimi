# Prenotazione Automatica Unimi
Questo script serve per prenotare automaticamente le lezioni in presenza dell'UNIMI durante il periodo di quarantena.
Idealmente è uno script da utilizzare con cron.

Utilizzo
=======
```
./prenotaLezioni.py <e-mail d'ateneo> <password> <codice fiscale> [lezione da escludere 1] [lezione da escludere 2] ... [lezione da escludere N]
```
Se voleste utilizzarlo in cron la mia configurazione è
```
0 19 * * * prenotaLezioni "mroik@studenti.unimi.it" "$(kwallet-query -f Passwords -r unimi default)" "MRKMRK69R13E200C" "Architettura degli elaboratori II - teoria ed. 2" "Logica matematica - lab. turno B"
```

Prima di poterlo usare comunque avrete bisogno di configurare il vostro profilo sul sito per le prenotazioni, altrimenti lo script non riuscirà
a prendere gli ID delle varie lezioni.

![alt_text](https://raw.githubusercontent.com/Mroik/Prenotazione-Automatica-Unimi/master/unknown.png)
