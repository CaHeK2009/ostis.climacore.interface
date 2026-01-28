from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data, get_element_system_identifier


def delete_device_by_main_idtf_and_room(main_idtf: str, room_name: str) -> bool:
    construction = ScConstruction()  
    link_content1 = ScLinkContent(room_name, ScLinkContentType.STRING)
    construction.generate_link(sc_type.CONST_NODE_LINK, link_content1)
    links = search_links_by_contents(room_name)[0]
    if len(links) != 1: return False
    link = links[0]
    templ = ScTemplate()
    templ.quintuple(
        (sc_type.VAR_NODE, "_room"),
        sc_type.VAR_COMMON_ARC,
        link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.triple(
        ScKeynodes.resolve("concept_room", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        "_room"
    )
    templ.triple(
        ScKeynodes.resolve("concept_device", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_device")
    )
    templ.triple(
        (sc_type.VAR_NODE_CLASS, "_device_type"),
        sc_type.VAR_PERM_POS_ARC,
        "_device"
    )
    templ.triple(
        ScKeynodes.resolve("concept_device", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        "_device_type"
    )
    templ.quintuple(
        "_device_type",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_idtf_link"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_device",
        sc_type.VAR_PERM_POS_ARC,
        "_room",
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("rrel_located_at", sc_type.CONST_NODE_ROLE)
    )
    if len(search_by_template(templ)) == 0: return False
    for result in search_by_template(templ):
        if get_link_content_data(result.get("_idtf_link")) == main_idtf:
            room = result.get("_room")
            type = result.get("_device_type")
            templ = ScTemplate()
            templ.quintuple(
                (sc_type.VAR_NODE, "_device"),
                sc_type.VAR_PERM_POS_ARC,
                room,
                sc_type.VAR_PERM_POS_ARC,
                ScKeynodes.resolve("rrel_located_at", sc_type.CONST_NODE_ROLE)
            )
            templ.triple(
                type,
                sc_type.VAR_PERM_POS_ARC,
                "_device"
            )
            if not search_by_template(templ): return False
            device = search_by_template(templ)[0].get("_device")
            print(get_element_system_identifier(device))
            erase_elements(device)
            return True 
    return False