# Oggetto Notifica ( Utilizzo futuro nel DB )
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from database.database import Base

class Notifica(Base):
    __tablename__ = 'notification_alert'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(50), nullable=False)  # InfoSystem, AlertSystem, WarningSystem
    descrizione = Column(String(255), nullable=False)
    timestamp_creazione = Column(DateTime, default=datetime.utcnow)
    stato = Column(Boolean, default=False)  # False = non letta, True = letta

    def __repr__(self):
        return f"<Notifica(tipo={self.tipo}, descrizione={self.descrizione}, stato={'letta' if self.stato else 'non letta'})>"
    
    @classmethod
    def salva_notifica(cls, session, tipo, descrizione):
        nuova_notifica = cls(tipo=tipo, descrizione=descrizione)
        session.add(nuova_notifica)
        session.commit()
        return nuova_notifica

    @classmethod
    def aggiorna_stato(cls, session, notifica_id, stato):
        notifica = session.query(cls).filter(cls.id == notifica_id).first()
        if notifica:
            notifica.stato = stato
            session.commit()
            print(f"notifica aggiornata: {notifica}")
            return notifica
        return None

