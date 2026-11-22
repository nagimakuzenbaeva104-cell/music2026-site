# Кейіпкерлер мен локациялар: видеодан бұрын жасалатын референстер

**Бұл қадамды өткізіп алма.** AI-видеода кейіпкер әр кадрда басқа адам болып шыға береді.
Сондықтан алдымен кейіпкерлердің тұрақты суреттерін жасаймыз, кейін әр видеоны
солардан бастаймыз (Google Flow: *Ingredients to Video* немесе *Frames to Video*).

Дайын суреттерді `images/characters/` ішіне сақта:
`her_A.png`, `her_B.png`, `her_C.png`, `him_A.png`, `him_B.png`, `him_C.png`.

## Кейіпкерлер

| | Ару (ол) | Диас (ол) |
|---|---|---|
| Жасы | 24 | 27 |
| Келбеті | ұзын түзу қара шаш, қоңыр көз, сопақ жүз | қысқа қара шаш, жеңіл сақал, мейірімді көз |
| **A**: танысу, махаббат | кремді көйлек, бежевый кардиган | ақшыл көгілдір зығыр жейде, бежевый шалбар |
| **B**: айырылу, күту | қою көк ұзын көйлек, қара пальто | қою көк пальто, қара водолазка |
| **C**: оралу, финал | ақ зығыр көйлек | джинсы куртка, сұр футболка, үлкен рюкзак |

Келбет сипаттамасы `tokens.json` ішінде бір жерде тұр. Өзгерткің келсе, тек сол файлды
өзгерт, сонда барлық 54 промпт бірден жаңарады.

### Кейіпкер парағының промпттары (сурет генераторына)

Ару:
```
Character reference sheet of a 24-year-old Kazakh woman with long straight black hair, warm brown eyes, soft oval face, natural makeup. Four views on a plain light grey background: front close-up portrait, three-quarter view, side profile, full body standing. Wearing a cream midi dress with a thin light-beige knit cardigan. Soft even studio light, photorealistic, consistent face in all views, no text.
```

Диас:
```
Character reference sheet of a 27-year-old Kazakh man with short black hair, light stubble, kind dark eyes, slim athletic build. Four views on a plain light grey background: front close-up portrait, three-quarter view, side profile, full body standing. Wearing a light grey-blue linen shirt with rolled sleeves and beige chinos. Soft even studio light, photorealistic, consistent face in all views, no text.
```

Беті ұнаған нұсқаны тапқан соң, **сол суретті** референс етіп, B және C киімдерімен қайта жасат.
Әр жолы "same person, same face" деп қос.

## Локациялар (5 ғана, әдейі)

Локация аз болған сайын клип біртұтас көрінеді. Сенің референстеріңдегі жағажай мен
бассейнді әдейі алып тастадым: олар хикаяға да, қазақ табиғатына да сәйкес келмейді.

| Код | Орын | Референс (сен жіберген) |
|---|---|---|
| ROOM | Ескі пәтер, биік терезе, қоңыр перде, гүлді тұсқағаз | қыз терезе алдында хат оқып тұр (1, 5, 8) |
| CITY | Түнгі жаңбырлы көше, неон, шағылыс | қолшатырлы қыз (2, 9) |
| STATION | Күмбезді ескі вокзал, поезд | рюкзакпен құшақтасу (3) |
| MEADOW | Тянь-Шань етегіндегі тұманды шалғын | тұманда қол ұстасу (4, 7, 11) |
| Төбе | Тау төбесі, күн бату/шығу | маңдай түйістіру (10) |

## Түс (grade)

- **cold**: бүгінгі күн, сағыныш (көк-сұр, күңгірт)
- **warm**: махаббат пен кездесу (алтын, жылы)
- **dream**: естелік (жарық, бұлыңғыр, slow motion)

Көрерменге «қазір» мен «естелікті» ажыратуға көмектесетін осы үш түс.

## Авторлық құқық туралы

Сен жіберген 12 сурет басқа авторлардікі (бірінде "ASFAR ALI" су белгісі бар).
Оларды тек көңіл-күй референсі ретінде қолдан: клипке қоюға да, генераторға
"осыны көшір" деп беруге де болмайды.
