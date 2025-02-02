from diagrams import Diagram, Edge, Node, Cluster

with Diagram("Zustandsdiagramm für Vokabeltrainer", show=False, direction="LR"):
    start = Node("Start")
    ende = Node("ENDE")
    zustand_start = Node("ZustandStart")
    zustand_boxinfo = Node("ZustandBoxinfo")
    with Cluster("Setupzustaende"):
        zustand_veraender_lernuhr = Node("ZustandVeraenderLernuhr")
    with Cluster("Testzustände"):
        zustand_pruefen = Node("ZustandVokabelPruefen")
        zustand_lernen = Node("ZustandVokabelLernen")
        zustand_neue = Node("ZustandVokabelNeue")
    with Cluster("Listenzustände"):
        zustand_liste_komplett = Node("ZustandZeigeVokabellisteKomplett")
        zustand_liste_lernen = Node("ZustandZeigeVokabellisteLernen")
        zustand_liste_neue = Node("ZustandZeigeVokabellisteNeue")

    start >> zustand_start
    zustand_start >> zustand_boxinfo
    zustand_start >> zustand_veraender_lernuhr
    zustand_veraender_lernuhr >> zustand_start
    zustand_boxinfo >> zustand_pruefen
    zustand_boxinfo >> zustand_lernen
    zustand_boxinfo >> zustand_neue
    zustand_boxinfo >> zustand_liste_komplett
    zustand_boxinfo >> zustand_liste_lernen
    zustand_boxinfo >> zustand_liste_neue
    zustand_pruefen >> zustand_boxinfo
    zustand_lernen >> zustand_boxinfo
    zustand_neue >> zustand_boxinfo
    zustand_liste_komplett >> zustand_boxinfo
    zustand_liste_lernen >> zustand_boxinfo
    zustand_liste_neue >> zustand_boxinfo
    zustand_start >> ende
    zustand_boxinfo >> ende
