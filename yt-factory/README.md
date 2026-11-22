# YT Factory

Конвейер производства YouTube-видео: сценарий → сцены → раскадровка → озвучка →
субтитры → монтаж → MP4 (Shorts 9:16 и длинные 16:9). Бесплатные инструменты:
Piper (озвучка), faster-whisper (привязка субтитров), ffmpeg (монтаж), шрифт Inter (OFL).

## Каналы

| Канал | Папка | Статус |
|---|---|---|
| Future Million | `channels/future-million/` | пилот |
| Қазақша Хиттер | — | после пилота |
| Happy Little Friends TV | — | после решения по 3D-персонажам |

## Установка

```bash
pip install -r requirements.txt      # + ffmpeg и ImageMagick в системе
```
Голоса Piper скачиваются автоматически в `voices/` при первом запуске.

## Как сделать видео

1. Создать `projects/<канал>/<видео>/scenes.yaml` (пример: `projects/future-million/amazon-garage/`).
   - `text` — текст на экране, `[ключевые слова]` красятся в акцентный цвет канала
   - `say` — как читает диктор (обязательно, если в тексте есть цифры)
   - `hero` — крупное фоновое слово/цифра сцены
   - `asset` — ваш клип/фото в `assets/` (без него — фирменный градиент)
   - `source` — источник факта (для Future Million обязательно)
2. Раскадровка:  `python3 -m engine.factory storyboard projects/future-million/amazon-garage`
3. Черновик 540p + контактный лист: `python3 -m engine.factory preview ...`
4. После одобрения поставить `approved: true` и: `python3 -m engine.factory final ...`
5. Другой формат: `--format long` (16:9, 1920×1080).

Финальный рендер технически заблокирован, пока в `scenes.yaml` нет `approved: true`.

## Где что лежит

```
channels/<канал>/brand.yaml   шрифты, цвета, голос, размеры субтитров, звук, форматы
engine/                       tts · align (субтитры) · visuals · audio · subs (ASS) · factory (CLI)
fonts/                        Inter Display (OFL)
projects/<канал>/<видео>/     scenes.yaml, storyboard.md; build/, output/, assets/ — вне git
```

## Известные ограничения

- Без клипов в `assets/` фон — абстрактный градиент, это не «кинематографичные кадры».
- Музыка по умолчанию — синтезированный эмбиент-заглушка. Для публикации укажите трек
  в `audio.music` (например, из YouTube Audio Library).
- Piper звучит заметно синтетичнее платных голосов; качество нужно оценить на слух.
