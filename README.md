# EMAD2024-2025-_DefNet-Back-End
Questa repository verrà utilizzata per illustrare la creazione del microservizio reallizato con Python e FAST-Api

Ecco un esempio di documentazione in formato markdown per il tuo microservizio back-end in Python, con i comandi necessari per installare i pacchetti all'interno dell'environment su Windows, Linux e macOS.

## Introduzione

Questo progetto è un microservizio back-end scritto in Python. Questa documentazione fornisce le istruzioni per configurare l'ambiente e installare tutte le dipendenze necessarie su Windows, Linux e macOS.

## Prerequisiti

Assicurati di avere Python e `pip` installati sul tuo sistema. Puoi verificarlo eseguendo i seguenti comandi:

```sh
python --version
pip --version
```

Se non hai Python installato, puoi scaricarlo dal sito ufficiale [python.org](https://www.python.org/downloads/).

## Creazione e Attivazione dell'Ambiente Virtuale

Prima di installare le dipendenze, è consigliabile creare un ambiente virtuale.

### Windows

Apri il terminale e naviga nella directory del tuo progetto. Esegui i seguenti comandi:

```sh
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Linux / macOS

Apri il terminale e naviga nella directory del tuo progetto. Esegui i seguenti comandi:

```sh
python3 -m venv venv
source venv/bin/activate
```

## Installazione delle Dipendenze

Una volta attivato l'ambiente virtuale, puoi installare tutte le dipendenze elencate nel file `requirements.txt`.

### Windows

Assicurati che l'ambiente virtuale sia attivo e poi esegui:

```sh
pip install -r requirements.txt
```

### Linux / macOS

Assicurati che l'ambiente virtuale sia attivo e poi esegui:

```sh
pip3 install -r requirements.txt
```

## Automazione dei Processi

Puoi automatizzare i processi creando degli script di shell che eseguono i comandi sopra descritti. Ecco un esempio per ciascun sistema operativo:
