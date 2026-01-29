from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data
import random

def create_room(name: str, temp: float = 22.4, hum: float = 50, co2: float = 600.0):
    def generate_link_with_content(content, content_type) -> ScAddr:
        construction = ScConstruction()  
        link_content = ScLinkContent(content, content_type)
        construction.create_link(sc_type.CONST_NODE_LINK, link_content)
        return generate_elements(construction)[0]
    
    def create_id(type: str) -> str:
        id = ''.join(random.choices('0123456789', k=10))
        while True:
            construction = ScConstruction()  
            link_content1 = ScLinkContent(id, ScLinkContentType.STRING)
            construction.generate_link(sc_type.CONST_NODE_LINK, link_content1)
            links = search_links_by_contents(id)[0]
            if len(links) == 0: break
        return type + id
    
    # Создаем ID комнаты
    room_id = create_id("R")
    print(f"Создаем комнату с ID: {room_id}, имя: {name}")
    
    # Создаем все необходимые линки
    id_link = generate_link_with_content(room_id, ScLinkContentType.STRING)
    main_idtf_link = generate_link_with_content(name, ScLinkContentType.STRING)
    temp_link = generate_link_with_content(float(temp), ScLinkContentType.FLOAT)
    hum_link = generate_link_with_content(float(hum), ScLinkContentType.FLOAT)
    co2_link = generate_link_with_content(float(co2), ScLinkContentType.FLOAT)
    
    # Ищем house_example
    house = ScKeynodes.resolve("house_example", sc_type.CONST_NODE)
    
    # Ищем набор комнат
    templ = ScTemplate()
    templ.quintuple(
        house,
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE, "_room_set"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_rooms", sc_type.CONST_NODE_NON_ROLE)
    )
    search_results = search_by_template(templ)
    
    if not search_results:
        print("Ошибка: Не найден house_example или набор комнат")
        return None
    
    room_set = search_results[0].get("_room_set")
    
    # Создаем комнату и все связи
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_room", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_room")
    )
    templ.triple(
        room_set,
        sc_type.VAR_PERM_POS_ARC,
        "_room"
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
    templ.triple(
        ScKeynodes.resolve("concept_measurement", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_measurements")
    )
    templ.quintuple(
        "_measurements",
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
    
    try:
        result = generate_by_template(templ)
        print(f"Комната создана успешно: {room_id}")
        return room_id
    except Exception as e:
        print(f"Ошибка при создании комнаты: {e}")
        return None