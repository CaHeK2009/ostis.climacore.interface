from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data
import random

def create_sensor(readings_type: str, room_id: str) -> bool:
    def generate_link_with_content(content, type) -> None:
        construction = ScConstruction()  
        link_content1 = ScLinkContent(content, type)
        construction.generate_link(sc_type.CONST_NODE_LINK, link_content1)
        link = generate_elements(construction)[0]
        return link
    

    def create_id(type: str) -> str:
        id = ''.join(random.choices('0123456789', k=10))
        while True:
            construction = ScConstruction()  
            link_content1 = ScLinkContent(id, ScLinkContentType.STRING)
            construction.generate_link(sc_type.CONST_NODE_LINK, link_content1)
            links = search_links_by_contents(id)[0]
            if len(links) == 0: break
        print(type + id)
        return type + id
    
    readings_link = generate_link_with_content(0.0, ScLinkContentType.FLOAT)
    sensor_type = ScKeynodes.resolve(f"concept_{readings_type}_sensor", sc_type.VAR_NODE_CLASS)
    id_link = generate_link_with_content(create_id("S"), ScLinkContentType.STRING)

    templ = ScTemplate()
    templ.quintuple(
        (sc_type.VAR_NODE, "_room"),
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_id"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.triple(
        ScKeynodes.resolve("concept_room", sc_type.VAR_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        "_room"
    )
    search_results = search_by_template(templ)
    room_node = ScAddr(0)
    for result in search_results:
        searched_id = get_link_content_data(result.get("_id"))
        if room_id == searched_id:
            room_node = result.get("_room")
            break
    if room_node == ScAddr(0): return False
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_sensor", sc_type.VAR_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_sensor")
    )
    templ.triple(
        sensor_type,
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_sensor")
    )
    templ.quintuple(
        "_sensor",
        sc_type.VAR_COMMON_ARC,
        readings_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_readings", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_sensor",
        sc_type.VAR_COMMON_ARC,
        id_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_sensor",
        sc_type.VAR_PERM_POS_ARC,
        room_node,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("rrel_located_at", sc_type.CONST_NODE_ROLE)
    )
    generate_by_template(templ)
    
    




    