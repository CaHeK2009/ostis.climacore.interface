from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data
import random

def create_device(name: str, device_type: str, room_id: str, power: bool = False) -> str:
    def generate_link_with_content(content, content_type):
        construction = ScConstruction()  
        link_content = ScLinkContent(content, content_type)
        construction.create_link(sc_type.CONST_LINK, link_content)
        links = generate_elements(construction)
        return links[0] if links else None
    
    def create_id() -> str:
        # Генерируем случайный ID
        import time
        import hashlib
        unique_str = f"{name}_{device_type}_{room_id}_{time.time()}"
        device_id = hashlib.md5(unique_str.encode()).hexdigest()[:10]
        return f"D{device_id}"
    
    # Ищем комнату
    templ = ScTemplate()
    templ.quintuple(
        (sc_type.VAR_NODE, "_room"),
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_room_id_link"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.triple(
        ScKeynodes.resolve("concept_room", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        "_room"
    )
    
    search_results = search_by_template(templ)
    room_node = None
    for result in search_results:
        room_id_from_sc = get_link_content_data(result.get("_room_id_link"))
        if room_id == room_id_from_sc:
            room_node = result.get("_room")
            break
    
    if not room_node or not room_node.is_valid():
        print(f"❌ Комната с ID {room_id} не найдена")
        return ""
    
    print(f"✅ Найдена комната: {room_node}")
    
    # Создаем ID устройства
    device_id = create_id()
    
    # Проверяем, существует ли уже такой ID
    existing_links = search_links_by_contents(device_id)[0]
    if existing_links:
        print(f"⚠️ Устройство с ID {device_id} уже существует, генерируем новый...")
        device_id = create_id()  # Генерируем новый ID
    
    # Создаем устройство как экземпляр класса устройства (например concept_ac)
    # Проверяем, существует ли такой тип устройства
    device_class_node = ScKeynodes.resolve(f"concept_{device_type}", sc_type.CONST_NODE_CLASS)
    
    if not device_class_node.is_valid():
        print(f"❌ Тип устройства concept_{device_type} не найден")
        # Создаем новый тип устройства если его нет
        device_class_node = ScKeynodes.resolve(f"concept_{device_type}", sc_type.CONST_NODE_CLASS | sc_type.NODE_CONST)
        print(f"✅ Создан новый тип устройства: {device_class_node}")
    
    # Создаем узел устройства
    device_node = generate_elements(ScConstruction().create_node(sc_type.CONST_NODE))[0]
    
    # Создаем связи
    # 1. Устройство является экземпляром concept_device
    concept_device = ScKeynodes.resolve("concept_device", sc_type.CONST_NODE_CLASS)
    if concept_device.is_valid():
        generate_by_template(ScTemplate().triple(concept_device, sc_type.PERM_POS_ARC, device_node))
    
    # 2. Устройство является экземпляром конкретного типа (concept_ac и т.д.)
    generate_by_template(ScTemplate().triple(device_class_node, sc_type.PERM_POS_ARC, device_node))
    
    # 3. Создаем ссылки с данными
    device_id_link = generate_link_with_content(device_id, ScLinkContentType.STRING)
    device_name_link = generate_link_with_content(name, ScLinkContentType.STRING)
    
    # 4. Привязываем ID (используем nrel_id)
    generate_by_template(ScTemplate().quintuple(
        device_node,
        sc_type.PERM_POS_ARC,
        device_id_link,
        sc_type.PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    ))
    
    # 5. Привязываем имя (используем nrel_name как в базе знаний)
    generate_by_template(ScTemplate().quintuple(
        device_node,
        sc_type.PERM_POS_ARC,
        device_name_link,
        sc_type.PERM_POS_ARC,
        ScKeynodes.resolve("nrel_name", sc_type.CONST_NODE_NON_ROLE)
    ))
    
    # 6. Привязываем к комнате
    generate_by_template(ScTemplate().quintuple(
        device_node,
        sc_type.PERM_POS_ARC,
        room_node,
        sc_type.PERM_POS_ARC,
        ScKeynodes.resolve("rrel_located_at", sc_type.CONST_NODE_ROLE)
    ))
    
    # 7. Устанавливаем состояние (включено/выключено)
    if power:
        generate_by_template(ScTemplate().triple(
            ScKeynodes.resolve("is_on", sc_type.CONST_NODE),
            sc_type.PERM_POS_ARC,
            device_node
        ))
    else:
        generate_by_template(ScTemplate().triple(
            ScKeynodes.resolve("is_off", sc_type.CONST_NODE),
            sc_type.PERM_POS_ARC,
            device_node
        ))
    
    print(f"✅ Устройство создано: {name} (ID: {device_id}, тип: {device_type})")
    return device_id