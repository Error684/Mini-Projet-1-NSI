import random, math
from collections import Counter

#Impaire Noir (1 Pique, 3 Trefle)
#Pair Rouge (2 Coeur, 4 Carreaux)
#[Couleur, valeur]
# Treys , a utiliser

global deck
global deck_pioche

global board
global pot
global partieFini

partieFini = False

ConvertionCouleurs = {1: "Pique", 2: "Coeur", 3: "Trèfle", 4: "Carreau"}
ConvertionValeurs = {11: "Valet", 12: "Dame", 13: "Roi", 14: "As"}

ConvertionIndicePuissanceMain = {1: "Flush Royale", 2: "Straight Flush", 3: "Four of a kind", 4: "Full House", 5:"Flush", 6:"Straight", 7:"Three of a Kind", 8:"Double Pair", 9:"Pair", 10:"High Card"}
for v in range(2, 11):
    ConvertionValeurs[v] = str(v)

previous_bet = 0
pot = 0

deck = []
deck_pioche = [False for t in range(52)]
#Création du jeu de 52 cartes
for i in range(4):
    for j in range(2, 15):
        deck.append([i+1,j])

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))
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
    def __init__(self, Main, Wallet, Agression, freqBluff, hasFolded, argent_mis_dans_le_round, name):
        self.Main = Main
        self.Wallet = Wallet
        self.Agression = Agression
        self.freqBluff = freqBluff  
        self.hasFolded = hasFolded    
        self.argent_mis_dans_le_round = argent_mis_dans_le_round
        self.name = name
    
    def Miser(self):
        force_main = 0
        classement_main = self.evaluationMain()
        if isinstance(classement_main, tuple):
            force_main = classement_main[0]
        else:
            force_main = classement_main
        #Retourne 0.1 pour une high card et 1 pour une flush royale (ducoup sa nous donne une range entre 0.1 et 1)
        bettingForce = (10 - force_main + 1)
        #Retourne une mise que le bot va placer , proportionelle a la puissance de la main , l'aggresivité et l'argent actuelle du joueur
        BettingAmmount = (0.5 * bettingForce * (0.5 + self.Agression * 0.5)) * self.Wallet / 4
        # 10 pour éviter les mise minuscules
        return int(max(10, BettingAmmount))
    def __str__(self):
        return self.name
    #Détermine l'action du bot (Fold, Check/Call, Bet/Raise) et le montant de mise associé 
    def prendreUneDecision(self, ammount_to_call, minimum_raise):
        force_main = 0
        classement_main = self.evaluationMain()
        
        if isinstance(classement_main, tuple):
            force_main = classement_main[0]
        else:
            force_main = classement_main
        
        # I: Mains très fortes (Relancer ou miser fort)
        if force_main <= 4:
            bet_ammount = self.Miser()
            if ammount_to_call == 0:
                return "Bet", bet_ammount  # Personne n'a misé, on ouvre fort
            else:
                # Quelqu'un a misé, on relance très fort
                raise_amount = clamp(ammount_to_call + bet_ammount, 0, self.Wallet)
                return "Raise", int(raise_amount)
                
        # II: Mains Fortes (Miser, suivre, ou relancer légèrement)
        elif force_main <= 7:          
            bet_ammount = self.Miser() * 0.7

            if ammount_to_call == 0:
                # Personne n'a misé, on peut checker ou miser
                return random.choices([("Check", 0), ("Bet", bet_ammount)], [3, 1])[0]
            
            # Quelqu'un a misé, on décide si on suit ou on relance
            elif self.Agression >= 0.5 and ammount_to_call < self.Wallet * 0.3: # Ne relance que si la mise n'est pas trop énorme
                raise_amount = clamp(ammount_to_call + (0.10 * bet_ammount), 0, self.Wallet)
                return "Raise", int(raise_amount)
            else: 
                # On suit simplement
                return "Call", ammount_to_call
                
        # III: Mains faibles (Checker ou se coucher)
        else:

            if ammount_to_call == 0:
                # Personne n'a misé, on check. On ne bluffe que si on est agressif.
                if self.Agression >= 0.7 and self.freqBluff > 0.5:
                    return random.choices([("Check", 0), ("Bet", self.Miser() * 0.3)], [1, self.freqBluff * 10])[0]
                return "Check", 0
            else:
                # Quelqu'un a misé. Si la mise est faible, on peut la suivre. Sinon, on se couche.
                if ammount_to_call <= self.Wallet * 0.1: # Suit si c'est moins de 10% de son tapis
                    return "Call", ammount_to_call
                else:
                    return "Fold", 0
              
    def evaluationMain(self):
        """
        Retourne un tuple comme sa : (Force_main, -type_de_carte, -(kickers))
        On retourne les kickers et le type de cartes en negatif au moins dans la win condition , 
        on peut juste utilser un min() pour trouver la plus haute, un roi sera plus petit qu'un 10, donc il ressort en premier

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

        pocketCards = [deck[index] for index in self.Main]
        allCards = pocketCards + board
        #Trie AllCards du plus grand au plus faible pour trouver le kicker plus simplement 
        allCards.sort(key=lambda x: x[1], reverse=True)

        valeurs_de_allCards = [card[1] for card in allCards]
        # On utilise la fonction Counter de la lib Collection , cards'est plus simple te plus efficace
        compteur_valeurs = Counter(valeurs_de_allCards)

        for couleur, valeur in allCards:
            carteTriee.setdefault(couleur, []).append(valeur)

        #  Condition 1 : FLUSH ROYALE
        #Si VALEUR_FLUSH_ROYALE est contenu dans une des clée de carteTriee (vu que VALEUR_FLUSH_ROYALE est un set , on vérifie si il est subset), si oui : Quinte flush royale
        if any(VALEUR_FLUSH_ROYALE.issubset(set(listeDeCartes)) for listeDeCartes in carteTriee.values()): return (1,)
        
        # Condition 2 : STRAIGHT FLUSH
        for listeDeCartes in carteTriee.values():
            #On trie listeDeCartes , et on enlève les doublons
            listeDeCartes_sans_doublons = sorted(list(set(listeDeCartes)), reverse=True)

            if len(listeDeCartes) >= 5:
                
                #  Condition 2A : STRAIGHT FLUSH (5 high):
                #Cherche pour le cas spécifique : AS - 2 - 3 - 4 - 5
                if set([14, 2, 3, 4, 5]).issubset(set(listeDeCartes_sans_doublons)):
                    return (2, -5) 
                
                #  Condition 2B : STRAIGHT FLUSH GENERAL
                # Vérifie si les 5 cartes ce suivent, retourne le la plus haute cartes pour le kicker (listeDeCartes_sans_doublons[i])
                for i in range(len(listeDeCartes_sans_doublons) - 4):
                    if listeDeCartes_sans_doublons[i] - listeDeCartes_sans_doublons[i+4] == 4:
                        return (2, -listeDeCartes_sans_doublons[i])
                
        # Condition 3: 4 OF A KIND (CARRE)
        if 4 in compteur_valeurs.values():
            rang_carre = [r for r, c in compteur_valeurs.items() if c == 4][0]
            kicker = max(r for r in valeurs_de_allCards if r != rang_carre)
            return (3, -rang_carre, -kicker)  
        
        # Condition 4 : FULL HOUSE
        three_of_a_kind = 3 in compteur_valeurs.values()
        pair = 2 in compteur_valeurs.values()

        if (three_of_a_kind and pair) or (list(compteur_valeurs.values()).count(3) >= 2):
            #On prend le rang des trois cartes du brelan 
            rang_three_of_a_kind = sorted([r for r, c in compteur_valeurs.items() if c == 3], reverse=True)[0]
            #On prend le rang des deux cartes de la paire
            rang_paire = max(r for r, c in compteur_valeurs.items() if c >= 2 and r != rang_three_of_a_kind)
            return (4, -rang_three_of_a_kind, -rang_paire)

        #Condition 5 : Flush
        for listeDeCartes in carteTriee.values():
            #Si une couleurs a plus de 5 éléments , on a une Flush
            if len(listeDeCartes) >= 5:
                #On met toutes les cartes de la Flush dans un tuple pour le return 
                carte_flush = tuple(sorted(listeDeCartes, reverse=True)[:5])
                return (5, tuple(-c for c in carte_flush))
        
        #Condition 6 : Straight (5 High)   
        valeurs_sans_doublons = sorted(list(set(valeurs_de_allCards)), reverse=True)
        #Cherche pour le cas spécifique : AS - 2 - 3 - 4 - 5
        if set([14, 2, 3, 4, 5]).issubset(valeurs_sans_doublons):
            return (6, -5) 
        
        #Cherche si les cartes se suivent , retourne la carte la plus haute pour le kicker
        if len(valeurs_sans_doublons) >= 5:
            for i in range(len(valeurs_sans_doublons) - 4):
                if valeurs_sans_doublons[i] - valeurs_sans_doublons[i+4] == 4:
                    return (6, -valeurs_sans_doublons[i]) 
        
        #Condition 7 : Three of a kind (Condition déja faite dans le Full House)
        if three_of_a_kind:

            rang_three_of_a_kind = [r for r, c in compteur_valeurs.items() if c == 3][0]
            kickers = tuple(r for r in valeurs_de_allCards if r != rang_three_of_a_kind)[:2]
            return (7, -rang_three_of_a_kind, tuple(-k for k in kickers))

        #Condition 8 : Double Paire
        nb_de_paires = 0
        #On test toutes les cartes de compteur_valeurs , et on ajoute 1 a nb_de_paires si jamais on trouve une paire
        for cartes in compteur_valeurs.values():
            if cartes >= 2:
                nb_de_paires = nb_de_paires + 1
        #Si on a plus ou 2 paires , on a une double paires
        if nb_de_paires >=2 :
            rang_paire = sorted([r for r, c in compteur_valeurs.items() if c >= 2], reverse=True)
            paire_haute = rang_paire[0]
            paire_basse = rang_paire[1]
            kicker = max(r for r in valeurs_de_allCards if r not in [paire_haute, paire_basse])
            return (8, -paire_haute, -paire_basse, -kicker)

        #Condition 9 : Pair (Condition déja faite dans le Full House)
        if pair :
            rang_paire = [r for r, c in compteur_valeurs.items() if c == 2][0]
            kickers = tuple(r for r in valeurs_de_allCards if r != rang_paire)[:3]
            return (9, -rang_paire, tuple(-k for k in kickers))

        # Si aucunes des condition de sont atteintes , on a une High Card
        kickers = tuple(valeurs_de_allCards[:5])
        return (10, tuple(-k for k in kickers))
    
def choix_joueur(portefeuille_joueur, ammount_to_call):
    mise_joueur=0
    choix= int(input("\nQuelle action voulez vous prendre ? (1 : Se coucher, 2: Checker, 3: Miser, 4: All-In, 5: Suivre): "))
    action = {1:"Fold", 2:"Check", 3:"Bet", 4:"All-in", 5:"Call"}
    if choix==1:
            print("Vous vous êtes coucher")
            Joueur_Humain.hasFolded = True
    if choix==2:
            mise_joueur = mise_joueur
    if choix==3:
                mise= int(input("On mise combien ? : ")) 
                mise_joueur= mise_joueur + mise  
                portefeuille_joueur = portefeuille_joueur - mise  
    if choix==4:
            mise_joueur = mise_joueur + portefeuille_joueur
            portefeuille_joueur = 0
    if choix==5:
            mise_joueur = previous_bet
    return (action[choix],mise_joueur)

Bot1 = Joueur(DistribuerX(2), 5000, 0.5, 0.5, False, 0, "Bot 1")
Bot2 = Joueur(DistribuerX(2), 5000, 0.5, 0.5, False, 0, "Bot 2")
Joueur_Humain = Joueur(DistribuerX(2), 5000, 0, 0, False, 0, "Joueur")

def tour_de_mise(joueurs):
    global pot

    #Reinitialise l'argent mis dans le round pour chaque joueurs
    for joueur in joueurs:
        joueur.argent_mis_dans_le_round = 0


    bet_le_plus_eleve = 0
    dernier_raise = None
    actionOuverte = True

    # Players who are still in the hand
    active_players = [p for p in joueurs if not p.hasFolded]
    
    #Tant que tout les joueurs n'on pas la meme somme d'argent mise dans le round on continure (l'action est ouverte)
    while actionOuverte:
        actionOuverte = False # It will be set to True if a bet/raise occurs
    
        #On skip tout les joueurs qui on fold
        for current_player in active_players:
            if current_player.hasFolded:
                continue

            # Si l'action est revenu au dernier joueurs qui a raise , on termine le round (l'action se ferme)
            if current_player == dernier_raise:
                actionOuverte = False
                break
            
            amount_to_call = bet_le_plus_eleve - current_player.argent_mis_dans_le_round

            # On differencie le joueur humain des bots 
            if current_player.Agression == 0: 
                action, mise = choix_joueur(current_player.Wallet, amount_to_call)
            else:
                # On calcule minmum_raise pour que les bots puissent prendre une décision
                minimum_raise = bet_le_plus_eleve + 5 # Simplified
                action, mise = current_player.prendreUneDecision(amount_to_call, minimum_raise)

            if action == "Fold":
                current_player.hasFolded = True
                print(f"{current_player} a fold.")
            
            #Call = On "suis" le bet précedent, on égalise la quantité d'argent misé
            elif action in ["Check", "Call"]:
                bet_amount = amount_to_call
                current_player.Wallet -= bet_amount
                current_player.argent_mis_dans_le_round += bet_amount
                pot += bet_amount
                print(f"{current_player} {action} un montant de : {bet_amount}.")

            # Bet/Rise , on actualise bet_le_plus_eleve
            elif action in ["Bet", "Raise"]:
                
                total_bet_for_player = amount_to_call + mise
                bet_le_plus_eleve = current_player.argent_mis_dans_le_round + total_bet_for_player
                
                current_player.Wallet -= total_bet_for_player
                current_player.argent_mis_dans_le_round += total_bet_for_player
                pot += total_bet_for_player
                
                print(f"{current_player} {action} pour {bet_le_plus_eleve}.")
                
                # Vu qu'on a raise , l'action se ré-ouvre
                actionOuverte = True
                dernier_raise = current_player
        
        # Si personne na raise , et que tout le monde a la meme somme d'argent mise dans le round  = le tour est fini
        if not actionOuverte:
            break
            
        # On verifie si il ne reste qu'un joueur "actif"
        if sum(1 for p in active_players if not p.hasFolded) <= 1:
            partieFini = True
            break

    print("\n--- Round de mise terminé. ---")
    print(f"Le pot est maintenant de : {pot}\n")

def Main():
    global board
    joueurs = [Joueur_Humain, Bot1, Bot2]
    
    main_Joueur = [deck[index] for index in Joueur_Humain.Main]
    
    # Pre-Flop
    if partieFini != True:
        print("--- Tour de mise PRE-FLOP ---")
        print(f"Votre main: {[Convertion(cards[0], cards[1]) for cards in main_Joueur]}")
        tour_de_mise(joueurs) 
    else:
        calcule_victoire()
    
    # Flop
    if partieFini != True:
        board = [deck[Distribuer()] for i in range(3)]
        print("\n--- Tour de mise FLOP ---")
        print(f"FLOP: {[Convertion(cards[0], cards[1]) for cards in board]}")
        print(f"Votre main: {[Convertion(cards[0], cards[1]) for cards in main_Joueur]}")
        tour_de_mise(joueurs) 
    else:
        calcule_victoire()
    
    # Turn
    if partieFini != True:
        board.append(deck[Distribuer()])
        print("\n--- Tour de mise TURN ---")
        print(f"TURN: {[Convertion(cards[0], cards[1]) for cards in board]}")
        print(f"Votre main: {[Convertion(cards[0], cards[1]) for cards in main_Joueur]}")
        tour_de_mise(joueurs) 
    else:
        calcule_victoire()

    # River
    if partieFini != True:
        board.append(deck[Distribuer()])
        print("\n--- Tour de mise RIVER ---")
        print(f"RIVER: {[Convertion(cards[0], cards[1]) for cards in board]}")
        print(f"Votre main: {[Convertion(cards[0], cards[1]) for cards in main_Joueur]}")
        tour_de_mise(joueurs) 
    else:
        calcule_victoire()
    print("----- Partie Fini ! -----")
    calcule_victoire()

def calcule_victoire():
    eval_bot1 = Bot1.evaluationMain()
    eval_bot2 = Bot2.evaluationMain()
    eval_joueur = Joueur_Humain.evaluationMain()

    #Python peut comparer des tuples, pas besoin de les trier, on compare juste qui a la main la plus forte pour trouver le gagnant
    joueurs_et_evaluations = [
        ("Joueur", eval_joueur),
        ("Bot 1", eval_bot1),
        ("Bot 2", eval_bot2)
    ]

    # On ne compare pas les tuples directement , on prend leur deuxieme élement (l'évaluation de main + kicker) avec key=lambda item: item[1]
    # on fait min() parce que plus l'indice est faible , plus forte est la main
    meilleure_evaluation = min(joueurs_et_evaluations, key=lambda item: item[1])[1]

    #Cherche si il y a plusieurs mains avec les meme forces de main pour gerer les égalités
    gagnants = [nom for nom, evaluation in joueurs_et_evaluations if evaluation == meilleure_evaluation]


    print(f"\nLe pot est de {pot}")

    hand_name_joueur = ConvertionIndicePuissanceMain[eval_joueur[0]]
    kickers_joueur = eval_joueur[1:]
    print(f"Le Joueur avait : {hand_name_joueur}, kickers/valeurs : {kickers_joueur}")

    hand_name_1 = ConvertionIndicePuissanceMain[eval_bot1[0]]
    kickers_1 = eval_bot1[1:]
    print(f"Le Bot 1 avait : {hand_name_1}, kickers/valeurs : {kickers_1}")

    hand_name_2 = ConvertionIndicePuissanceMain[eval_bot2[0]]
    kickers_2 = eval_bot2[1:]
    print(f"Le Bot 2 avait : {hand_name_2}, kickers/valeurs : {kickers_2}")

    # Anonce le/les gagnant(s)
    if len(gagnants) > 1:
        print(f"\nÉgalité entre : {', '.join(gagnants)}! Ils se partagent le pot de {pot} !")
    else:
        print(f"\nLe gagnant est : {gagnants[0]}! Il gagne {pot} !")

Main() 
