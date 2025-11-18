from copy import deepcopy

from database.impianto_DAO import ImpiantoDAO
from model.impianto_DTO import Impianto

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        # TODO
        risultati = []
        for impianto in self._impianti:
            somma = 0
            counter = 0
            consumi = impianto.get_consumi()   # metto i consumi in una lista
            for consumo in consumi:
                if consumo.data.month == mese:    # se il mese è quello richiesto faccio la media
                    somma += consumo.kwh
                    counter += 1
            media = somma/counter
            risultati.append((impianto.nome, media))
        return risultati

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        # TODO
        if giorno >7: # quando il giorno è più grande di 7 non ricorro più
            # se il costo ottimo non è ancora stato cambiato o se è più grande di quello già presente lo cambio e cambia la sequenza
            if self.__costo_ottimo == -1 or self.__costo_ottimo > costo_corrente:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = deepcopy(sequenza_parziale)
            return
        for impianto, consumi in consumi_settimana.items():   # itero tra chiavi e valori(lista)
            nuovo_costo = costo_corrente + consumi[giorno-1]   # aggiorno il costo totale con quella del giorno attuale
            nuova_sequenza = sequenza_parziale + [impianto]   # aggiungo l'impianto di oggi alla sequenza
            if ultimo_impianto != impianto and ultimo_impianto is not None:
                nuovo_costo +=5   # se non sono al prim giorno e se ho cambiato impianto aggiungo 5 euro
            self.__ricorsione(nuova_sequenza, giorno+1, impianto, nuovo_costo, consumi_settimana)  # chiamo la ricorsione con nuovi valori



    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        # TODO
        consumi_dict = {}
        for impianto in self._impianti:
            consumi = impianto.get_consumi()   # metto i consumi in una lista
            consumo_settimana = []  # lista per ogni impianto
            for giorno in range(1,8):
                kw_ora = 0  # variabile per azzerare ogni volta il valore
                for consumo in consumi:
                    if consumo.data.month == mese and consumo.data.day == giorno:   # se il mese è giusto e finché sono tra 1 e 7
                        kw_ora = consumo.kwh
                consumo_settimana.append(kw_ora)
            consumi_dict[impianto.id] = consumo_settimana  # dizionario con id:lista consumi settimana
        return consumi_dict