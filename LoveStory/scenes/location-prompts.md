# Локациялар: референс промпттары

Мақсат: бір локация барлық кадрда **бір орын** болып көрінуі. Бөлме терезесі, вокзалдың
күмбезі, төбедегі тас әр кадрда өзгермеуі керек.

## Жұмыс тәртібі

1. **Негізгі кадр (master plate).** Бос локация, адам жоқ, бейтарап күндізгі жарық, кең
   план. 4–8 нұсқа жасап, біреуін бекітесің. Бұл кезеңде тек архитектураға, заттарға
   және композицияға қара.
2. **Жарық нұсқалары.** Бекітілген master plate-ті референс етіп, тек жарықты өзгертесің
   (cold / warm / dream / түн). Әр локацияға клипте нақты керек нұсқалар ғана жазылған.
3. **Бастапқы кадр (start frame).** Видео генерацияламас бұрын кейіпкер референсін
   (`images/characters/`) локацияның жарық нұсқасымен біріктіріп, кадрдың алғашқы
   суретін жаса. Содан кейін оны видео генераторға бер (Google Flow-да *Frames to Video*).
   Бұл ең көп жұмыс істейтін тәсіл: видео генераторға бет пен орынды бірден ойлап табуға
   мүмкіндік қалмайды.

Сақтау: `images/locations/<код>_master.png`, `<код>_cold.png`, `<код>_warm.png` т.с.с.

Барлық промпттың соңына қосылатын тұрақты бөлік:
`empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark`

**Ереже:** локация сипаттамасы `tokens.json`-дағы мәтінмен сөзбе-сөз бірдей. Біреуін
өзгертсең, екіншісін де өзгерт, әйтпесе кадр промпттары референсқа сай келмейді.

---

## Негізгі локациялар

### ROOM: Арудың пәтері · 10+ кадр (ең маңызды)

Клиптің жүрегі. Бір бұрыш бекітілуі тиіс: **терезе, терезе алды, перделер**. Кадрлардың
көбі сол жерде.

**Master:**
```
Wide shot of a small old apartment room with a tall wooden window, heavy brown velvet curtains, sheer white tulle, faded floral wallpaper and a wide wooden windowsill. The window is the center of the composition, a worn armchair to one side, an old wooden floor, a few books on a shelf. Soft neutral daylight from the window, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

**cold, таң** (s02–s04, s11, s22, s25, s27, s29, s31):
```
The same room as in the reference image, same window, same curtains, same wallpaper, same composition. Early overcast morning, cold blue-grey light through the window, sheer tulle moving slightly, dust in a pale light beam, muted melancholic mood, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

**cold, түн, шам** (s09, s10):
```
The same room as in the reference image, same window, same curtains, same wallpaper. Night, dark blue light outside the window, a single small candle burning on the windowsill next to a stack of old letters is the only warm light in the room, deep shadows, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

**warm, көктем** (s30, s39):
```
The same room as in the reference image, same window, same curtains, same wallpaper. Bright spring morning, the window wide open, a blossoming garden outside, soft golden sunlight filling the room, a vase with red carnations on the windowsill, warm hopeful mood, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

### MEADOW: Тянь-Шань етегіндегі шалғын · 7 кадр

Клип осында басталып, осында аяқталады. Бекітілетін нәрсе: **тау сызығының пішіні және
шалғынды кесіп өтетін жіңішке соқпақ.**

**Master:**
```
Wide shot of a wide meadow of tall grass and small white wildflowers in the foothills of the Tien Shan mountains, a narrow footpath winding through the grass toward the mountains, snow-capped peaks on the horizon. Soft neutral daylight, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

**cold, тұманды таң** (s01):
```
The same meadow as in the reference image, same footpath, same mountain silhouette. Dawn before sunrise, thick low mist over the grass, cold blue-grey light, the mountains barely visible, silent and empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

**warm, күн шығу** (s17–s19, s51, s54):
```
The same meadow as in the reference image, same footpath, same mountain silhouette. Sunrise, low golden sun behind the mountains, golden mist glowing over the grass, backlit wildflowers, gentle lens flare, warm romantic mood, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

**dream** (s35):
```
The same meadow as in the reference image, same footpath. Dreamlike memory, overexposed soft white-gold glow, hazy bloom, faded warm colors, soft focus edges, empty, no people, photorealistic, 35mm film grain, 16:9, no text, no watermark.
```

### STATION: ескі вокзал · 9 кадр

Айырылу мен кездесу осында. Бекітілетін нәрсе: **күмбезді темір шатыр, платформа, поезд.**
Бұл локация суық та, жылы да болып көрінеді, сондықтан master plate маңызды.

**Master:**
```
Wide shot of an old railway station platform with an arched iron roof and a long passenger train, glass panels in the roof, cast-iron columns, an old station clock hanging above the platform, a long empty platform. Soft neutral daylight, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

**cold, айырылу** (s07, s24):
```
The same station as in the reference image, same arched roof, same clock, same train. Grey overcast morning, cold blue-grey light, light steam near the train, wet platform, lonely melancholic mood, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

**warm, кездесу** (s43–s48, s50):
```
The same station as in the reference image, same arched roof, same clock, same train. Bright morning sun streaming through the glass roof in long golden beams, warm dust in the air, joyful warm mood, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

**Ескерту:** s38 (вокзал залы) әзірге токенсіз. Залды платформамен бір стильде жаса
(сол темір конструкция, сол сағат), сонда екі кеңістік бір ғимарат болып көрінеді.

### CITY: түнгі жаңбырлы көше · 3 кадр

**Master:**
```
Wide shot of a narrow city street at night in the rain, wet asphalt reflecting warm street lamps and neon shop signs, soft bokeh, old low buildings, a small cafe with lit windows on one side. Empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no readable signs, no watermark.
```

**warm, танысу** (s13, s14): master plate өзі жарайды, жылы шам жарығы басым болсын.

**cold** (s28):
```
The same street as in the reference image, same buildings, same lamps. Heavy rain, cold blue-grey color grade, the neon signs dimmed, puddles reflecting grey light, lonely mood, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no readable signs, no watermark.
```

**Ескерту:** «no readable signs». AI неон жазуларды қате әріптермен жазады, кадрда бұл
бірден байқалады.

---

## Қосымша локациялар (жаңа токендер)

Бұлар бұрын промпт ішінде еркін мәтінмен жазылған еді, енді `tokens.json`-да тұр.

### HILLTOP: тау төбесі · 3 кадр (s21, s37, s52)

Махаббаттың ең жоғары нүктесі. Ол клиптің ортасында (күн бату) және соңында (күн шығу)
шығады. Бекітілетін нәрсе: **үлкен сұр тас және тау жоталарының қатпарлары.**

**Master:**
```
Wide shot of a grassy mountain hilltop in the Tien Shan foothills with one large weathered grey rock and a wide view over layered hazy mountain ridges. Soft neutral daylight, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

**warm, күн бату** (s21, s37 үшін dream нұсқасы):
```
The same hilltop as in the reference image, same rock, same mountain ridges. Sunset, the sun low on the horizon behind the ridges, strong golden-orange backlight, layered haze between the mountains, perfect for silhouettes, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

**warm, күн шығу** (s52):
```
The same hilltop as in the reference image, same rock, same mountain ridges. Sunrise, soft pink-golden light rising from behind the ridges, morning mist in the valleys below, fresh hopeful mood, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

### HIS_ROOM: Диастың жалдамалы бөлмесі · 2 кадр (s26, s34)

Арудың бөлмесіне қарама-қарсы болуы тиіс: бос, суық, жалғыз шам.

**Master:**
```
Medium-wide shot of a bare small rented room with a narrow wooden desk, a single brass desk lamp, a metal bed frame and one dark window. Bare walls with peeling paint, a few sheets of paper on the desk. Night, the desk lamp is the only light source, warm pool of light on the desk, cold dark blue shadows around, rain on the window, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

### ROOFTOP: қала шатыры · 2 кадр (s12, s32)

**cold, таң** (s12):
```
Wide shot of the flat concrete rooftop of an old Soviet-era apartment block with a low parapet and rusty TV antennas, overlooking a distant grey city. Dawn, pale cold sky, light haze over the city, lonely mood, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

**cold, түн, ай** (s32), таң нұсқасын референс етіп:
```
The same rooftop as in the reference image, same parapet, same antennas. Night, a large full moon in a dark blue sky, distant city lights below, cold blue-grey mood, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

### TRAIN: поезд купесі · 2 кадр (s23, s41)

Бір купе екі рет шығады: кетіп бара жатқанда (cold) және оралғанда (warm). Сондықтан
master plate бір болуы керек, тек терезе сыртындағы көрініс өзгереді.

**cold, вокзалда** (s23):
```
Interior of an old passenger train compartment with a wide window, worn dark-green seats and a small fold-down table. Outside the window a grey station platform with an arched iron roof, cold overcast light, raindrops and reflections on the glass, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

**warm, дала** (s41), алдыңғы суретті референс етіп:
```
The same train compartment as in the reference image, same seats, same table, same window. Outside the window the golden Kazakh steppe passing by at sunrise, warm golden light falling across the seats, hopeful mood, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

### CAFE: кафе · 1 кадр (s15)

Кадр жоғарыдан түсірілген, сондықтан ең маңыздысы — үстел.

```
Top-down close-up of a dark wooden table in a small cosy cafe by a large rain-streaked window, two cups of tea in white cups, a paper napkin and a pen, warm light from hanging lamps, raindrops on the glass at the edge of the frame, empty, no people, photorealistic, cinematic 35mm film look, 16:9, no text, no watermark.
```

---

## Реквизит (міндетті)

Хаттар мен салфетка хикаяны байланыстырып тұрған негізгі заттар. Олар 15-тен астам кадрда
шығады. Реквизит өзгерсе (лента түсі, қағаз), көрермен оны бірден байқайды.

**Хаттар бумасы** (`images/props/letters.png`):
```
Close-up product-style photo of a bundle of old handwritten letters in aged cream paper envelopes tied with a faded red satin ribbon in a simple bow, slightly worn edges, on a plain light grey background, soft even light, photorealistic, no readable text, no watermark.
```

**Салфеткадағы хат** (`images/props/napkin.png`): s15, s36, s41-де бір зат:
```
Close-up of a white paper cafe napkin folded in half, with a few lines of handwriting in blue ink visible on it, slightly creased, on a plain light grey background, soft even light, photorealistic, handwriting not readable, no watermark.
```

---

## Тексеру чек-листі

- [ ] Әр жарық нұсқасында архитектура master plate-пен бірдей ме (терезе пішіні, күмбез, тас)?
- [ ] Кадрда адам, жазу немесе су белгісі жоқ па?
- [ ] cold және warm нұсқаларын қатар қойғанда бір орын екені көріне ме?
- [ ] ROOM мен HIS_ROOM бір-біріне қарама-қарсы ма (жылы, тұрмысқа толы үй ↔ бос, суық бөлме)?
- [ ] Хаттағы лента барлық жерде қызыл ма?
