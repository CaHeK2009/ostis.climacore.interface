from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data
import random

def create_scenario(user_id: str, name: str, start_time: str, finish_time: str, room_id: str, hum: float, temp: float) -> str:
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

    room_node = ScAddr(0)
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
    if room_node == ScAddr(0): return ""

    user = ScAddr(0)

    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_user", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_user")
    )
    templ.quintuple(
        "_user",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_id"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    search_results = search_by_template(templ)
    user = ScAddr(0)
    for result in search_results:
        id = result.get("_id")
        if get_link_content_data(id) != user_id: continue
        user = result.get("_user")
        break
    if user == ScAddr(0): return ""

    scenario_id = generate_link_with_content(create_id("SC"), ScLinkContentType.STRING)
    main_idtf_link = generate_link_with_content(name, ScLinkContentType.STRING)
    start_time_link = generate_link_with_content(start_time, ScLinkContentType.STRING)
    finish_time_link = generate_link_with_content(finish_time, ScLinkContentType.STRING)
    temp_link = generate_link_with_content(temp, ScLinkContentType.FLOAT)
    hum_link = generate_link_with_content(hum, ScLinkContentType.FLOAT)
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_scenario", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_scenario")
    )
    templ.quintuple(
        user,
        sc_type.VAR_PERM_POS_ARC,
        "_scenario",
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("rrel_owner", sc_type.CONST_NODE_ROLE)
    )
    templ.quintuple(
        "_scenario",
        sc_type.VAR_COMMON_ARC,
        start_time_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_start_time", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_scenario",
        sc_type.VAR_COMMON_ARC,
        main_idtf_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_scenario",
        sc_type.VAR_COMMON_ARC,
        scenario_id,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_scenario",
        sc_type.VAR_COMMON_ARC,
        finish_time_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_finish_time", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_scenario",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE, "_instructions_set"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_instructions", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.triple(
        "_instructions_set",
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_instruction")
    )
    templ.quintuple(
        "_instruction",
        sc_type.VAR_COMMON_ARC,
        temp_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_temp", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_instruction",
        sc_type.VAR_COMMON_ARC,
        hum_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_hum", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_instruction",
        sc_type.VAR_COMMON_ARC,
        room_node,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_room", sc_type.CONST_NODE_NON_ROLE)
    )
    generate_by_template(templ)
    return id

