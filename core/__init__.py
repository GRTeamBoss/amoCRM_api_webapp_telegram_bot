from typing import TypedDict, Literal

RESERVED_KEY_MAP: dict[str, str] = {
    "from_": "from",
    "class_": "class",
    "def_": "def",
    "return_": "return",
    "import_": "import",
    "with_": "with"
}

def serialize_dict_to_json(params) -> dict[str, any]:
  converted: dict = {}
  for k, v in params.items():
    if type(params[k]) == dict:
      converted[new_key:=RESERVED_KEY_MAP.get(k, k)] = serialize_dict_to_json(params[k])
    else:
      converted[new_key:=RESERVED_KEY_MAP.get(k, k)] = v
  return converted


class DateFilter(TypedDict):
  from_: None | int | str
  to_: None | int | str

class OrderFilter(TypedDict):
  complete_till: None | Literal["asc", "desc"]
  created_at: None | Literal["asc", "desc"]
  updated_at: None | Literal["asc", "desc"]
  id: None | Literal["asc", "desc"]

class TaskFilter(TypedDict):
  responsible_user_id: None | int | list
  is_completed: Literal[False, True]
  type: None | str | list
  task_type: None | int | list
  entity_type: None | int | list
  entity_id: None | int | list
  task_id: None | int | list
  updated_at: None | int | DateFilter
  id: None | str | list
  created_at: None | int | DateFilter
  created_by: None | int | list
  entity: None | str | list
  value_before: None | str | list
  value_after: None | str | list
  with_: None | str
  order: None | OrderFilter
  query: None | int | str
  pipeline_id: None | int | str
  price: None | int
  name: None | str
  statuses: None | int | list
  closed_at: None | int | DateFilter
  closest_task_at: None | int | DateFilter

EVENTS_TYPES = [
    {
        "key": "lead_added",
        "type": 1,
        "lang": "Новая сделка"
    },
    {
        "key": "lead_deleted",
        "type": 7,
        "lang": "Сделка удалена"
    },
    {
        "key": "lead_restored",
        "type": 10,
        "lang": "Сделка восстановлена"
    },
    {
        "key": "lead_status_changed",
        "type": 14,
        "lang": "Изменение этапа продажи"
    },
    {
        "key": "lead_linked",
        "type": 80,
        "lang": "Прикрепление сделки"
    },
    {
        "key": "lead_unlinked",
        "type": 84,
        "lang": "Открепление сделки"
    },
    {
        "key": "contact_added",
        "type": 2,
        "lang": "Новый контакт"
    },
    {
        "key": "contact_deleted",
        "type": 8,
        "lang": "Контакт удален"
    },
    {
        "key": "contact_restored",
        "type": 11,
        "lang": "Контакт восстановлен"
    },
    {
        "key": "contact_linked",
        "type": 81,
        "lang": "Прикрепление контакта"
    },
    {
        "key": "contact_unlinked",
        "type": 85,
        "lang": "Открепление контакта"
    },
    {
        "key": "company_added",
        "type": 3,
        "lang": "Новая компания"
    },
    {
        "key": "company_deleted",
        "type": 9,
        "lang": "Компания удалена"
    },
    {
        "key": "company_restored",
        "type": 12,
        "lang": "Компания восстановлена"
    },
    {
        "key": "company_linked",
        "type": 82,
        "lang": "Прикрепление компании"
    },
    {
        "key": "company_unlinked",
        "type": 86,
        "lang": "Открепление компании"
    },
    {
        "key": "customer_added",
        "type": 20,
        "lang": "Новый покупатель"
    },
    {
        "key": "customer_deleted",
        "type": 53,
        "lang": "Покупатель удален"
    },
    {
        "key": "customer_status_changed",
        "type": 57,
        "lang": "Изменение этапа покупателя"
    },
    {
        "key": "customer_linked",
        "type": 83,
        "lang": "Прикрепление покупателя"
    },
    {
        "key": "customer_unlinked",
        "type": 87,
        "lang": "Открепление покупателя"
    },
    {
        "key": "task_added",
        "type": 49,
        "lang": "Новая задача"
    },
    {
        "key": "task_deleted",
        "type": 51,
        "lang": "Задача удалена"
    },
    {
        "key": "task_completed",
        "type": 29,
        "lang": "Завершение задачи"
    },
    {
        "key": "task_type_changed",
        "type": 76,
        "lang": "Изменение типа задачи"
    },
    {
        "key": "task_text_changed",
        "type": 77,
        "lang": "Изменение текста задачи"
    },
    {
        "key": "task_deadline_changed",
        "type": 78,
        "lang": "Изменение даты исполнения задачи"
    },
    {
        "key": "task_result_added",
        "type": 33,
        "lang": "Результат по задаче"
    },
    {
        "key": "incoming_call",
        "type": 17,
        "lang": "Входящий звонок"
    },
    {
        "key": "outgoing_call",
        "type": 30,
        "lang": "Исходящий звонок"
    },
    {
        "key": "incoming_mail",
        "type": 16,
        "lang": "Входящее письмо"
    },
    {
        "key": "outgoing_mail",
        "type": 152,
        "lang": "Исходящее письмо"
    },
    {
        "key": "incoming_chat_message",
        "type": 89,
        "lang": "Входящее сообщение"
    },
    {
        "key": "outgoing_chat_message",
        "type": 90,
        "lang": "Исходящее сообщение"
    },
    {
        "key": "entity_direct_message",
        "type": 150,
        "lang": "Внутреннее сообщение"
    },
    {
        "key": "incoming_sms",
        "type": 41,
        "lang": "Входящее SMS"
    },
    {
        "key": "outgoing_sms",
        "type": 42,
        "lang": "Исходящее SMS"
    },
    {
        "key": "entity_tag_added",
        "type": 63,
        "lang": "Теги добавлены"
    },
    {
        "key": "entity_tag_deleted",
        "type": 64,
        "lang": "Теги убраны"
    },
    {
        "key": "entity_segment_attached",
        "type": 94,
        "lang": "Добавлен в сегмент"
    },
    {
        "key": "entity_segment_detached",
        "type": 95,
        "lang": "Удалён из сегмента"
    },
    {
        "key": "entity_linked",
        "type": 72,
        "lang": "Прикрепление"
    },
    {
        "key": "entity_unlinked",
        "type": 73,
        "lang": "Открепление"
    },
    {
        "key": "sale_field_changed",
        "type": 69,
        "lang": "Изменение поля \"Бюджет\""
    },
    {
        "key": "name_field_changed",
        "type": 70,
        "lang": "Изменение поля \"Название\""
    },
    {
        "key": "ltv_field_changed",
        "type": 88,
        "lang": "Сумма покупок"
    },
    {
        "key": "custom_field_value_changed",
        "type": 24,
        "lang": "Изменение поля"
    },
    {
        "key": "entity_responsible_changed",
        "type": 25,
        "lang": "Ответственный изменен"
    },
    {
        "key": "robot_replied",
        "type": 74,
        "lang": "Ответ робота"
    },
    {
        "key": "intent_identified",
        "type": 75,
        "lang": "Тема вопроса определена"
    },
    {
        "key": "nps_rate_added",
        "type": 91,
        "lang": "Новая оценка NPS"
    },
    {
        "key": "link_followed",
        "type": 59,
        "lang": "Переход по ссылке"
    },
    {
        "key": "transaction_added",
        "type": 26,
        "lang": "Покупка"
    },
    {
        "key": "common_note_added",
        "type": 27,
        "lang": "Новое примечание"
    },
    {
        "key": "common_note_deleted",
        "type": 79,
        "lang": "Примечание удалено"
    },
    {
        "key": "attachment_note_added",
        "type": 28,
        "lang": "Добавлен новый файл"
    },
    {
        "key": "targeting_in_note_added",
        "type": 31,
        "lang": "Добавление в ретаргетинг"
    },
    {
        "key": "targeting_out_note_added",
        "type": 32,
        "lang": "Удаление из ретаргетинга"
    },
    {
        "key": "geo_note_added",
        "type": 38,
        "lang": "Новое примечание с гео-меткой"
    },
    {
        "key": "service_note_added",
        "type": 39,
        "lang": "Новое системное примечание"
    },
    {
        "key": "site_visit_note_added",
        "type": 18,
        "lang": "Заход на сайт"
    },
    {
        "key": "message_to_cashier_note_added",
        "type": 60,
        "lang": "Сообщение кассиру"
    },
    {
        "key": "entity_merged",
        "type": 92,
        "lang": "Выполнено объединение"
    },
    {
        "key": "video_opened",
        "type": 97,
        "lang": "Видео было открыто"
    },
    {
        "key": "video_closed",
        "type": 98,
        "lang": "Видео было закрыто"
    },
    {
        "key": "picture_opened",
        "type": 99,
        "lang": "Картинка была открыта"
    },
    {
        "key": "picture_closed",
        "type": 100,
        "lang": "Картинка была закрыта"
    },
    {
        "key": "zoom_conference",
        "type": 96,
        "lang": "Zoom conference"
    },
    {
        "key": "segment_created",
        "type": 101,
        "lang": "Сегмент создан"
    },
    {
        "key": "key_action_completed",
        "type": 116,
        "lang": "Ключевое действие"
    },
    {
        "key": "ai_result",
        "type": 153,
        "lang": "amoCRM AI"
    },
    {
        "key": "talk_created",
        "type": 119,
        "lang": "Беседа создана"
    },
    {
        "key": "talk_closed",
        "type": 120,
        "lang": "Беседа закрыта"
    },
    {
        "key": "conversation_answered",
        "type": 135,
        "lang": "Не требует ответа"
    },
    {
        "key": "meta_chat_subscription_added",
        "type": 136,
        "lang": "подписан на"
    },
    {
        "key": "meta_chat_subscription_removed",
        "type": 137,
        "lang": "Unsubscribed from"
    },
    {
        "key": "talk_missed_event",
        "type": 122,
        "lang": "Превышено время на ответ"
    },
    {
        "key": "invoice_paid",
        "type": 62,
        "lang": "При оплате счета/покупки"
    },
    {
        "key": "invoice_created",
        "type": 118,
        "lang": "Счет/покупка создана"
    },
    {
        "key": "page_mention",
        "type": 151,
        "lang": "Упоминание страницы"
    },
    {
        "key": "dropbox_attachment",
        "type": 40,
        "lang": "Файл Dropbox"
    },
    {
        "key": "custom_field_188087_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Телефон\""
    },
    {
        "key": "custom_field_188089_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Email\""
    },
    {
        "key": "custom_field_188085_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Должность\""
    },
    {
        "key": "custom_field_188091_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Web\""
    },
    {
        "key": "custom_field_188093_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Адрес\""
    },
    {
        "key": "custom_field_1004229_value_changed",
        "type": 24,
        "lang": "Изменение поля \"LinkedIn\""
    },
    {
        "key": "custom_field_1010625_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Linkedin\""
    },
    {
        "key": "custom_field_1011565_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Telegram\""
    },
    {
        "key": "custom_field_914557_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Язык общения\""
    },
    {
        "key": "custom_field_1008913_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Responsible\""
    },
    {
        "key": "custom_field_1008147_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Industry\""
    },
    {
        "key": "custom_field_1008149_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Client type\""
    },
    {
        "key": "custom_field_311141_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Product\""
    },
    {
        "key": "custom_field_1001503_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Team size\""
    },
    {
        "key": "custom_field_1008169_value_changed",
        "type": 24,
        "lang": "Изменение поля \"due deligence\""
    },
    {
        "key": "custom_field_1011795_value_changed",
        "type": 24,
        "lang": "Изменение поля \"website\""
    },
    {
        "key": "custom_field_998921_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Lokatsiya (tashrif)\""
    },
    {
        "key": "custom_field_1008177_value_changed",
        "type": 24,
        "lang": "Изменение поля \"current office\""
    },
    {
        "key": "custom_field_311705_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Tashrif sanasi\""
    },
    {
        "key": "custom_field_935225_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Артикул\""
    },
    {
        "key": "custom_field_935231_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Группа\""
    },
    {
        "key": "custom_field_1001507_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Ijara boshlanish sanasi\""
    },
    {
        "key": "custom_field_935229_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Цена\""
    },
    {
        "key": "custom_field_1001509_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Ijara tugash sanasi\""
    },
    {
        "key": "custom_field_935227_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Описание\""
    },
    {
        "key": "custom_field_311937_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Причина закрытия\""
    },
    {
        "key": "custom_field_311939_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Причина закрытия\""
    },
    {
        "key": "custom_field_935233_value_changed",
        "type": 24,
        "lang": "Изменение поля \"External ID\""
    },
    {
        "key": "custom_field_188095_value_changed",
        "type": 24,
        "lang": "Изменение поля \"utm_content\""
    },
    {
        "key": "custom_field_935235_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Единица измерения\""
    },
    {
        "key": "custom_field_188097_value_changed",
        "type": 24,
        "lang": "Изменение поля \"utm_medium\""
    },
    {
        "key": "custom_field_935237_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Спец цена 1\""
    },
    {
        "key": "custom_field_188099_value_changed",
        "type": 24,
        "lang": "Изменение поля \"utm_campaign\""
    },
    {
        "key": "custom_field_935239_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Оптовая цена\""
    },
    {
        "key": "custom_field_188101_value_changed",
        "type": 24,
        "lang": "Изменение поля \"utm_source\""
    },
    {
        "key": "custom_field_935241_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Баллов за покупку\""
    },
    {
        "key": "custom_field_188103_value_changed",
        "type": 24,
        "lang": "Изменение поля \"utm_term\""
    },
    {
        "key": "custom_field_1013091_value_changed",
        "type": 24,
        "lang": "Изменение поля \"Изображение\""
    },
    {
        "key": "custom_field_188105_value_changed",
        "type": 24,
        "lang": "Изменение поля \"utm_referrer\""
    },
    {
        "key": "custom_field_188107_value_changed",
        "type": 24,
        "lang": "Изменение поля \"roistat\""
    },
    {
        "key": "custom_field_188109_value_changed",
        "type": 24,
        "lang": "Изменение поля \"referrer\""
    },
    {
        "key": "custom_field_188111_value_changed",
        "type": 24,
        "lang": "Изменение поля \"openstat_service\""
    },
    {
        "key": "custom_field_188113_value_changed",
        "type": 24,
        "lang": "Изменение поля \"openstat_campaign\""
    },
    {
        "key": "custom_field_188115_value_changed",
        "type": 24,
        "lang": "Изменение поля \"openstat_ad\""
    },
    {
        "key": "custom_field_188117_value_changed",
        "type": 24,
        "lang": "Изменение поля \"openstat_source\""
    },
    {
        "key": "custom_field_188119_value_changed",
        "type": 24,
        "lang": "Изменение поля \"from\""
    },
    {
        "key": "custom_field_188121_value_changed",
        "type": 24,
        "lang": "Изменение поля \"gclientid\""
    },
    {
        "key": "custom_field_188123_value_changed",
        "type": 24,
        "lang": "Изменение поля \"_ym_uid\""
    },
    {
        "key": "custom_field_188125_value_changed",
        "type": 24,
        "lang": "Изменение поля \"_ym_counter\""
    },
    {
        "key": "custom_field_188127_value_changed",
        "type": 24,
        "lang": "Изменение поля \"gclid\""
    },
    {
        "key": "custom_field_188129_value_changed",
        "type": 24,
        "lang": "Изменение поля \"yclid\""
    },
    {
        "key": "custom_field_188131_value_changed",
        "type": 24,
        "lang": "Изменение поля \"fbclid\""
    }
]