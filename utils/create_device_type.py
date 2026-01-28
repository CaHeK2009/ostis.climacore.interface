from typing import List
from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data
import random


def create_device_type(name: str, en_name: str, fixes_states: List[str], causes_states: List[str], depends_on_weather: bool = False) -> str:
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
        return type + id
    

    id_link = generate_link_with_content(create_id("DT"), ScLinkContentType.STRING)
    main_idtf_link = generate_link_with_content(name, ScLinkContentType.STRING)
    system_idtf_link = generate_link_with_content("concept_" + en_name, ScLinkContentType.STRING)
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_device", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_device_type")
    )
    templ.triple(
        ScKeynodes.resolve("concept_user_type_device", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        "_device_type"
    )
    templ.quintuple(
        "_device_type",
        sc_type.VAR_COMMON_ARC,
        main_idtf_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_device_type",
        sc_type.VAR_COMMON_ARC,
        system_idtf_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_system_idtf", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_device_type",
        sc_type.VAR_COMMON_ARC,
        id_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    for f_state in fixes_states:
        state = ScKeynodes.resolve(f"concept_{f_state}", sc_type.VAR_NODE_CLASS)
        templ.quintuple(
            "_device_type",
            sc_type.VAR_PERM_POS_ARC,
            state,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("rrel_fixes_state", sc_type.CONST_NODE_ROLE)
        )
    for c_state in causes_states:
        state = ScKeynodes.resolve(f"concept_{c_state}", sc_type.VAR_NODE_CLASS)
        templ.quintuple(
            "_device_type",
            sc_type.VAR_PERM_POS_ARC,
            state,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("rrel_causes_state", sc_type.CONST_NODE_ROLE)
        )
    if depends_on_weather:
        templ.triple(
            ScKeynodes.resolve("concept_weather_depended_device", sc_type.VAR_NODE_CLASS),
            sc_type.VAR_PERM_POS_ARC,
            "_device_type"
        )

    generate_by_template(templ)
    return id