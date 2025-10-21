import random
#Impaire Noir (1 Pique, 3 Trefle)
#Pair Rouge (2 Coeur, 4 Carreaux)
#[Couleur, valeur]
# Treys , a utiliser


global deck
global deck_pioche

global board
global pot

ConvertionCouleurs = {1: "Pique", 2: "Coeur", 3: "Trèfle", 4: "Carreau"}
ConvertionValeurs = {11: "Valet", 12: "Dame", 13: "Roi", 14: "As"}
for v in range(2, 11):
    ConvertionValeurs[v] = str(v)

deck = []
deck_pioche = [False for t in range(52)]
#Création du jeu de 52 cartes
for i in range(4):
    for j in range(2, 15):
        deck.append([i+1,j])

#Convertie du format [Couleur, valeur] a un format lisible plus simplement avant implementation UI
def Convertion(couleur , valeur):
    nom_couleur = ConvertionCouleurs[couleur]
    nom_valeur = ConvertionValeurs[valeur]
    return f"{nom_valeur} de {nom_couleur}"

#Fonction de Pioche 
def Distribuer():
    valide = False
    cartePioche = random.randint(0, 51)
    while valide == False :
        if deck_pioche[cartePioche] == True:
            cartePioche = random.randint(0, 51)
        else:
            deck_pioche[cartePioche] = True
            valide = True
    return cartePioche

def DistribuerX(x):
    carteDistribuee = []  
    for i in range(x):
        carteDistribuee.append(Distribuer())
    return carteDistribuee
        
board = [deck[Distribuer()] for cartes in range(5)]

class Joueur:   
    def __init__(self, Main, Wallet, Agression, freqBluff):
        self.Main = Main
        self.Wallet = Wallet
        self.Agression = Agression
        self.freqBluff = freqBluff      
    def Miser(self):
        #remplacer le placeholder par force une fois evaluation OK
        placeholder = 1
        defaultBettingAmount = (0.50 * placeholder * (0.5 + self.Agression * 0.5)) * self.Wallet/4
        return defaultBettingAmount
        pass
    def prendreUneDecision(self):
        pass

    def evaluationMain(self):
        """

        La méthode retourne ceci quand les conditions sont les bonnes :
        1 : Flush Royale
        2 : Straight Flush
        3 : Four of a kind
        4 : Full House
        5 : Flush
        6 : Straight
        7 : Three of a Kind
        8 : Double Pair
        9 : Pair
        10 : High Card

        """

        carteTriee = {} 
        compteur_valeurs = {}
        VALEUR_FLUSH_ROYALE = {10, 11, 12, 13, 14}

        pair = False
        three_of_a_kind = False

        #Liste de toute les cartes présentes sous la forme du deck [couleur, valeur]
        pocketCards = [deck[index] for index in self.Main]
        allCards = pocketCards + board
        allCards.sort()

        #Filtre les valeurs des suites , donne uniquement les valeurs des 5,6,7 cartes présentes  
        valeurs_de_allCards = [card[1] for card in allCards]
        valeurs_de_allCards.sort()

        #Fait un dictionaire ("carteTriee")qui a pour clée les valeurs des couleurs (1, 2, 3, 4), et les valeurs sous forme de liste : sa donne un truc de cette forme {1: [4, 5, 12], 2:[6, 9, 14], ...}
        for couleur, valeur in allCards:
            carteTriee.setdefault(couleur, []).append(valeur)
            compteur_valeurs[valeur] = compteur_valeurs.get(valeur, 0) + 1


        #  Condition 1 : FLUSH ROYALE
        #Si VALEUR_FLUSH_ROYALE est contenu dans une des clée de carteTriee (vu que VALEUR_FLUS_ROYALE est un set , on vérifie si il est subset), si oui : Quinte flush royale
        if any(VALEUR_FLUSH_ROYALE.issubset(set(listeDeCartes)) for listeDeCartes in carteTriee.values()):
            return 1
        
        # Condition 2 : STRAIGHT FLUSH
        for listeDeCartes in carteTriee.values():
            #On trie listeDeCartes , et on enlève les doublons
            listeDeCartes_sans_doublons = sorted(list(set(listeDeCartes)))

            #  Condition 2A : STRAIGHT FLUSH (5 high):
            #Cherche pour le cas spécifique : AS - 2 - 3 - 4 - 5
            if 14 in listeDeCartes_sans_doublons and 2 in listeDeCartes_sans_doublons and 3 in listeDeCartes_sans_doublons and 4 in listeDeCartes_sans_doublons and 5 in listeDeCartes_sans_doublons:
                return 2
            
            #  Condition 2B : STRAIGHT FLUSH GENERAL
            # Vérifie si les 4 premières cartes ce suivent , la derbières sera utiliser pour le kicker
            for i in range(len(listeDeCartes_sans_doublons) - 4):
                if (listeDeCartes_sans_doublons[i + 1] == listeDeCartes_sans_doublons[i] + 1 and
                    listeDeCartes_sans_doublons[i + 2] == listeDeCartes_sans_doublons[i] + 2 and
                    listeDeCartes_sans_doublons[i + 3] == listeDeCartes_sans_doublons[i] + 3 and
                    listeDeCartes_sans_doublons[i + 4] == listeDeCartes_sans_doublons[i] + 4):
                    return 2
                
        # Condition 3: 4 OF A KIND (CARRE)
        if 4 in compteur_valeurs.values(): return 3
        
        # Condition 4 : FULL HOUSE
        three_of_a_kind = 3 in compteur_valeurs.values()
        pair = 2 in compteur_valeurs.values()

        if (three_of_a_kind and pair) or (list(compteur_valeurs.values()).count(3) >=2): return 4

        #Condition 5 : Flush
        #Si une couleurs a plus de 5 éléments , on a une Flush
        for listeDeCartes in carteTriee.values():
            if len(listeDeCartes) >= 5: return 5
        
        #Condition 6 : Straight (5 High) 
        #On ajoute un 1 si jamais on detecte un AS dans les valeurs (preparation)
        if 14 in valeurs_de_allCards:
            valeurs_de_allCards.insert(0, 1)
            valeurs_de_allCards.sort()

        for i in range(len(valeurs_de_allCards) - 4):
            carte_de_debut = valeurs_de_allCards[i]
            # On scanne les 4 premières carte pour voir si elle se suivent ( la dernières n'est pas scanner pour calculer les kickers)
            if (valeurs_de_allCards[i+1] == carte_de_debut + 1 and
                valeurs_de_allCards[i+2] == carte_de_debut + 2 and
                valeurs_de_allCards[i+3] == carte_de_debut + 3 and
                valeurs_de_allCards[i+4] == carte_de_debut + 4 ): return 6
        
        #Condition 7 : Three of a kind (Condition déja faite dans le Full House)
        if three_of_a_kind : return 7

        #Condition 8 : Double Paire
        nb_de_paires = 0
        #On test toutes les cartes de compteur_valeurs , et on ajoute 1 a nb_de_paires si jamais on trouve une paire
        for cartes in compteur_valeurs.values():
            if cartes >= 2:
                nb_de_paires = nb_de_paires + 1
        #Si on a plus ou 2 paires , on a une double paires
        if nb_de_paires >=2 : return 8

        #Condition 9 : Pair (Condition déja faite dans le Full House)
        if pair : return 9

        # Si aucunes des condition de sont atteintes , on a une High Card
        high_card_value = max(valeurs_de_allCards)

        return [10, high_card_value] 

        
        

Joueur1 = Joueur(DistribuerX(2), 5000, 0.2, 0.6)

maintest = [deck[Joueur1.Main[0]], deck[Joueur1.Main[1]]] + board
maintest.sort()
print("\n" + "Évaluation : " + str(Joueur1.evaluationMain()))
print("Main + Board : " + str(maintest))