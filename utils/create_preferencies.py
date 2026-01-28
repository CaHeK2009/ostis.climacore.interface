from typing import List
from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data



def create_preferencies(user_id: str, temp_prefs=[], hum_prefs=[]) -> bool:
    def generate_link_with_content(content, type) -> None:
        construction = ScConstruction()  
        link_content1 = ScLinkContent(content, type)
        construction.generate_link(sc_type.CONST_NODE_LINK, link_content1)
        link = generate_elements(construction)[0]
        return link

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
    if user == ScAddr(0): return False
    min_temp_link = max_temp_link = min_hum_link = max_hum_link = ScAddr(0)
    if len(temp_prefs) == 1:
        min_temp_link = generate_link_with_content(temp_prefs[0] - 0.5, ScLinkContentType.FLOAT)
        max_temp_link = generate_link_with_content(temp_prefs[0] + 0.5, ScLinkContentType.FLOAT)

    elif len(temp_prefs) == 2:
        min_temp_link = generate_link_with_content(temp_prefs[0], ScLinkContentType.FLOAT)
        max_temp_link = generate_link_with_content(temp_prefs[1], ScLinkContentType.FLOAT)

    if len(hum_prefs) == 1:
        min_hum_link = generate_link_with_content(hum_prefs[0] - 0.5, ScLinkContentType.FLOAT)
        max_hum_link = generate_link_with_content(hum_prefs[0] + 0.5, ScLinkContentType.FLOAT)

    elif len(hum_prefs) == 2:
        min_hum_link = generate_link_with_content(hum_prefs[0], ScLinkContentType.FLOAT)
        max_hum_link = generate_link_with_content(hum_prefs[1], ScLinkContentType.FLOAT)


    if min_temp_link == min_hum_link == ScAddr(0): return False

    templ = ScTemplate()
    templ.quintuple(
        user,
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE, "_prefs"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_prefs", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_prefs",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE, "_temp_range"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_temp_range", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_prefs",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE, "_hum_range"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_hum_range", sc_type.CONST_NODE_NON_ROLE)
    )
    if min_temp_link != ScAddr(0):
        templ.quintuple(
            "_temp_range",
            sc_type.VAR_COMMON_ARC,
            (sc_type.VAR_NODE_LINK, "_temp_min_link"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_min", sc_type.CONST_NODE_NON_ROLE)
        )
        templ.quintuple(
            "_temp_range",
            sc_type.VAR_COMMON_ARC,
            (sc_type.VAR_NODE_LINK, "_temp_max_link"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_max", sc_type.CONST_NODE_NON_ROLE)
        )
    if min_hum_link != ScAddr(0):
        templ.quintuple(
            "_hum_range",
            sc_type.VAR_COMMON_ARC,
            (sc_type.VAR_NODE_LINK, "_hum_min_link"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_min", sc_type.CONST_NODE_NON_ROLE)
        )
        templ.quintuple(
            "_hum_range",
            sc_type.VAR_COMMON_ARC,
            (sc_type.VAR_NODE_LINK, "_hum_max_link"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_max", sc_type.CONST_NODE_NON_ROLE)
        )

    search_results = search_by_template(templ)
    if not search_results: return False
    temp_range = search_results[0].get("_temp_range")
    hum_range = search_results[0].get("_hum_range")
    if min_temp_link != ScAddr(0):
        erase_elements(
            search_results[0].get("_temp_min_link"),
            search_results[0].get("_temp_max_link")
        )
        templ = ScTemplate()
        templ.quintuple(
            temp_range,
            sc_type.VAR_COMMON_ARC,
            min_temp_link,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_min", sc_type.CONST_NODE_NON_ROLE)
        )
        templ.quintuple(
            temp_range,
            sc_type.VAR_COMMON_ARC,
            max_temp_link,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_max", sc_type.CONST_NODE_NON_ROLE)
        )
        generate_by_template(templ)
    if min_hum_link != ScAddr(0):
        erase_elements(
            search_results[0].get("_hum_min_link"),
            search_results[0].get("_hum_max_link")
        )
        templ = ScTemplate()
        templ.quintuple(
            hum_range,
            sc_type.VAR_COMMON_ARC,
            min_hum_link,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_min", sc_type.CONST_NODE_NON_ROLE)
        )
        templ.quintuple(
            hum_range,
            sc_type.VAR_COMMON_ARC,
            max_hum_link,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_max", sc_type.CONST_NODE_NON_ROLE)
        )
        generate_by_template(templ)
    return True

    

    

     

