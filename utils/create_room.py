from typing import List
from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data
import random
from typing import Tuple

def create_room(name: str, temp: float = 22.4, hum: float = 50, co2: float = 600.0) -> None:
    def generate_link_with_content(content, type) -> Tuple[float, float, float]:
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
        return type + id
    

    id_link = generate_link_with_content(create_id("R"), ScLinkContentType.STRING)
    main_idtf_link = generate_link_with_content(name, ScLinkContentType.STRING)
    co2_link = generate_link_with_content(co2, ScLinkContentType.FLOAT)
    temp_link = generate_link_with_content(temp, ScLinkContentType.FLOAT)
    hum_link = generate_link_with_content(hum, ScLinkContentType.FLOAT)

    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_room", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_room")
    )
    templ.quintuple(
        "_room", 
        sc_type.VAR_COMMON_ARC,
        main_idtf_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_room", 
        sc_type.VAR_COMMON_ARC,
        id_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        (sc_type.VAR_NODE, "_measurements"),
        sc_type.ACTUAL_TEMP_POS_ARC,
        "_room",
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("rrel_current_measurement", sc_type.CONST_NODE_ROLE)
    )
    templ.quintuple(
        "_measurements",
        sc_type.VAR_COMMON_ARC,
        temp_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_temp", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_measurements",
        sc_type.VAR_COMMON_ARC,
        hum_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_hum", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_measurements",
        sc_type.VAR_COMMON_ARC,
        co2_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_co2", sc_type.CONST_NODE_NON_ROLE)
    )
    generate_by_template(templ)
    return temp, hum, co2
    