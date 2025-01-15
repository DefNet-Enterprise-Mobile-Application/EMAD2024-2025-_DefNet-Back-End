#import paho.mqtt.client as mqtt
import asyncio
from mqtt.web_socket import notify_websocket_clients 

# Aggiungi un evento per la sincronizzazione
websocket_event = asyncio.Event()

# Configurazione del broker MQTT
MQTT_BROKER = "localhost"  # Sostituisci con l'indirizzo del tuo broker MQTT
MQTT_PORT = 1883

# Crea il client MQTT
#mqtt_client = mqtt.Client()

# Coda per i messaggi MQTT
message_queue = asyncio.Queue()

# Lista per bufferizzare i messaggi prelevati dalla coda
message_buffer = []

# Dizionario per mantenere il messaggio più recente per utente
last_message_per_user = {}

# Funzione callback quando il client si connette al broker
def on_connect(client, userdata, flags, rc):
    print(f"Connesso al broker MQTT con codice di ritorno {rc}")
    client.subscribe("user/login/success")  # Sottoscrivi ai topic MQTT
    client.subscribe("user/login/fail")
    
# Funzione callback quando il client riceve un messaggio MQTT
def on_message(client, userdata, message):
    #topic = message.topic
    #payload = message.payload.decode()
    
    msg = f"Topic: {message.topic}, Message: {message.payload.decode()}"
    print(msg)  # Stampa il messaggio per il debug
    
    # Ottieni l'utente dal messaggio (assumendo che contenga "utente NomeUtente")
    #if "utente" in payload:
       # username = payload.split("utente")[1].split(" ")[1]  # Estrai il nome utente
    #else:
        #username = "unknown"
        
    # Salva l'ultimo messaggio ricevuto per il topic
    #last_message_per_user[username] = payload

     # Aggiungi il messaggio alla coda asyncio
    asyncio.run_coroutine_threadsafe(
        enqueue_message(msg), MAIN_EVENT_LOOP
    )
    
def connect_mqtt():
    """Connetti il client MQTT al broker."""
    try:
        #mqtt_client.on_connect = on_connect  # Imposta il callback di connessione
        #mqtt_client.on_message = on_message  # Imposta il callback dei messaggi
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()  # Avvia il loop MQTT per ricevere messaggi
        print("Connesso al broker MQTT")
    except Exception as e:
        print(f"Errore durante la connessione al broker MQTT: {e}")


def disconnect_mqtt():
    """Disconnetti il client MQTT dal broker."""
    try:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("Disconnesso dal broker MQTT")
    except Exception as e:
        print(f"Errore durante la disconnessione dal broker MQTT: {e}")

def publish_mqtt_message(topic: str, message: str):
    """Pubblica un messaggio su un topic MQTT specifico."""
    try:
        mqtt_client.publish(topic, message)
        print(f"Messaggio pubblicato su {topic}: {message}")
    except Exception as e:
        print(f"Errore durante la pubblicazione del messaggio MQTT: {e}")

def subscribe_to_topics():
    #Sottoscrivi ai topic MQTT rilevanti.
    mqtt_client.subscribe("user/login/success")
    mqtt_client.subscribe("user/login/fail")

# Configura il callback MQTT per inoltrare messaggi ai WebSocket
def mqtt_on_message(client, userdata, message):
    """Callback per i messaggi MQTT."""
    try:
        msg = f"Topic: {message.topic}, Message: {message.payload.decode()}"
        print(f"Callback {msg}")  # Per debug

        # Esegui `enqueue_message` nel loop principale
        asyncio.run_coroutine_threadsafe(
            enqueue_message(msg), MAIN_EVENT_LOOP
        )
    except Exception as e:
        print(f"Errore nel callback MQTT: {e}")

        
# Funzione per configurare il loop principale
def set_main_event_loop(loop):
    global MAIN_EVENT_LOOP
    MAIN_EVENT_LOOP = loop
            
            

# Aggiungi messaggi alla coda
async def enqueue_message(message):
    """Aggiunge un messaggio alla coda."""
    #await message_queue.put(message)
    message_queue.put_nowait(message)
    print(f"Stato attuale della coda: {list(message_queue._queue)}")  # Debug (accesso diretto alla coda)
    #print(f"Aggiunta del messaggio alla coda: {message}")  # Debug

# Funzione per ottenere un messaggio dalla coda
async def get_message():
    if not message_queue.empty():
        return await message_queue.get()
    return None

# Funzione per processare i messaggi dalla coda
async def process_message_queue():
    """Elabora i messaggi dalla coda e li inoltra ai WebSocket."""
    while True:
        try:
                print(" Sto eseguendo process")  # Debug
           
                # Preleva un messaggio dalla coda
                message = await message_queue.get()
            
                print(f"Messaggio prelevato dalla coda: {message}")  # Debug
            
                # Aggiungi il messaggio al buffer
                message_buffer.append(message)
           
                # Notifica i WebSocket
                await notify_websocket_clients(message)
                print("Metodo notify_websocket_clients chiamato")  # Debug
            
        except asyncio.TimeoutError:
            print("Timeout: nessun messaggio ricevuto nella coda entro il tempo limite.")
            # Reset dell'evento per assicurare che si sblocchi correttamente
            websocket_event.clear()
        except Exception as e:
            print(f"Errore durante l'elaborazione del messaggio nella coda: {e}")
            continue
        
        
