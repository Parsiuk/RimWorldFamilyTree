import xml.etree.ElementTree as ET
import pawns
from graphviz import Digraph
import math

def main():
    pawns_list = []
    current_tick = 0

    tree = ET.parse('save.xml')
    root = tree.getroot()
    for element in root.findall("./meta/gameVersion"):
        print("Save game version:",element.text)

    for ticks in root.findall("./game/tickManager"):
        current_tick = int(ticks.find('ticksGame').text)
        print("Current game time:",current_tick)

    # Colonists on the map
    for thing in root.findall(".//thing[@Class='Pawn']"):
        for kind in thing.findall("./kindDef"):
            if kind.text == "Colonist":
                pawns_list.append(buildPawn(root,thing))

    # Dead colonists

    # Colonists inside buildings (for example crib, biosculpting pod, etc.)
    for thing in root.findall(".//li[@Class='Pawn']"):
        for kind in thing.findall("./kindDef"):
            if kind.text == "Colonist":
                pawns_list.append(buildPawn(root,thing))

    # Print colonists table
    print("Known colonists:")
    for colonist in pawns_list:
        print(colonist.first_name,colonist.last_name,colonist.age,colonist.gender)

    # Creating the graph
    f = Digraph(format='jpg', encoding='utf8', filename='family_tree')
    f.attr('node', shape='box')
    f.attr('graph',rankdir='BT')

    # Adding nodes and edges
    for colonist in pawns_list:
        colour_table = {"Male": "lightblue", "Female": "pink", "Unknown": "grey"}
        if len(colonist.parents) > 0:
            colonist_name = colonist.first_name + " "
            if colonist.nick_name:
                colonist_name += colonist.nick_name + " "
            colonist_name += colonist.last_name
            f.node(name=colonist.id,label= colonist_name + "\n" + str(colonist.age),fillcolor=colour_table[colonist.gender],style='filled')
            for parent in colonist.parents:
                if parent in str(vars(f)):
                    print("Skipping",parent,"when adding nodes. Node name already present.")
                else:
                    f.node(name=parent,label=getNameById(root,parent) + "\n" + "??",fillcolor=colour_table[getGenderById(root,parent)],style='filled')
                f.edge(colonist.id,parent)
    f.view()

def buildPawn(root,thing):
    new_pawn = pawns.Pawn(thing.find('./id').text)
    new_pawn.first_name = thing.find('name/first').text
    try:
        new_pawn.nick_name = thing.find('name/nick').text
    except Exception as error:
        print("[buildPawn] WARNING:",error," when trying to get pawns nickname. Pawn:",new_pawn.id, new_pawn.first_name, new_pawn.last_name)
    new_pawn.last_name = thing.find('name/last').text
    new_pawn.age = math.floor(float(thing.find('ageTracker/ageBiologicalTicks').text)/3600000)
    if thing.find('gender'):
        new_pawn.gender = thing.find('gender').text
    else:
        new_pawn.gender = getGenderById(root,thing.find('./id').text)
    if not new_pawn.gender:
        new_pawn.gender = "Unknown"
    relations = thing.find('social/directRelations')
    if relations:
        for other_pawn in relations:
            if other_pawn.find('def').text == "Parent":
                new_pawn.parents.append(other_pawn.find('otherPawn').text.replace("Thing_",""))
    return new_pawn

def getNameById(root,pawn_id):
    paths = ["./game/world/worldPawns/pawnsDead/li", "./game/world/worldPawns/pawnsMothballed/li", "./game/world/worldPawns/pawnsAlive/li", ".//thing[@Class='Pawn']"]
    for path in paths:
        for pawn in root.findall(path):
            if pawn.find('id').text == pawn_id:
                full_name = pawn.find('name/first').text + " "
                if pawn.find('name/nick'):
                    full_name += pawn.find('name/nick').text + " "
                full_name += pawn.find('name/last').text
                if "Dead" in path:
                    (full_name) += "†"
                return((full_name))
    return("Unknown")

def getAgeById(root,pawn_id):
    paths = ["./game/world/worldPawns/pawnsDead/li", "./game/world/worldPawns/pawnsMothballed/li", "./game/world/worldPawns/pawnsAlive/li", ".//thing[@Class='Pawn']"]
    for path in paths:
        for thing in root.findall(path):
                for kind in thing.findall("./def"):
                    if kind.text == "Human":
                        if thing.find('./id').text == pawn_id:
                            return math.floor(float(thing.find('ageTracker/ageBiologicalTicks').text)/3600000)

def getGenderById(root,pawn_id):
    paths = ["./game/world/worldPawns/pawnsDead/li", "./game/world/worldPawns/pawnsMothballed/li", "./game/world/worldPawns/pawnsAlive/li", ".//thing[@Class='Pawn']"]
    for path in paths:
        for thing in root.findall(path):
                for kind in thing.findall("./def"):
                    if kind.text == "Human":
                        if thing.find('./id').text == pawn_id:
                            body_type = str(thing.find('story/bodyType').text) + str(thing.find('story/headType').text)
                            if "Female" in body_type:
                                return "Female"
                            elif "Male" in body_type:
                                return "Male"
                            else:
                                pass
    return "Unknown"

if __name__ == "__main__":
    main()
