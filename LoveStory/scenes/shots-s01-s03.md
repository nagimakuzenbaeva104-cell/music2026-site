# s01–s03: Кіріспе (0:00–0:14.5, фортепиано)

Бұл 14.5 секунд көрерменге клиптің тонын береді: тыныштық, суық таң, күту.
Әлі сөз жоқ, тек фортепиано. Сондықтан қозғалыс баяу, кадрда артық ештеңе жоқ.

**Әр кадр екі қадаммен жасалады:**
1. **Бастапқы кадр (сурет).** Локация мен кейіпкер референстерін тіркеп, кадрдың алғашқы суретін жасайсың.
2. **Видео.** Сол суретті *Frames to Video*-ға бересің. Видео промпты тек
   қозғалыс пен камераны сипаттайды. Сахнаны суреттің өзі көрсетеді.

**Техникалық талаптар:**
- `build.py` видеоның **1-секундынан** бастап кеседі (`clip_in = 1.0`). Сондықтан видео
  кадр ұзақтығынан кемінде 1 секундқа ұзын болуы керек: s01, s02 ≥ 6 с, s03 ≥ 5.5 с.
- Видеодағы дыбыс монтажда алынып тасталады. Генератор дыбыс қосса да, оған мән берме.
- Сақтау: `videos/s01.mp4`, `videos/s02.mp4`, `videos/s03.mp4`.

---

## s01 · 0:00–0:05 · cold · Дрон баяу алға

**Хикаядағы орны:** бос шалғын. Клиптің соңғы кадры (s54) осы шалғында, бірақ күн шыққанда
болады. Екеуі бір-біріне жауап береді, сондықтан **екі кадрдағы тау сызығы бірдей болуы керек.**

**Референс:** `images/locations/MEADOW_cold.png`

**1. Бастапқы кадр:**
```
The same meadow as in the reference image, same footpath, same mountain silhouette. High aerial view from a drone about 30 meters above the ground, looking forward toward the mountains, the footpath leading the eye to the center of the frame. Dawn before sunrise, thick low mist lying over the tall grass and white wildflowers, the snow-capped peaks barely visible through the haze. Empty, no people, no animals. Cinematic 35mm film look, muted cold blue-grey color grade, soft overcast light, melancholic mood, fine film grain, 16:9, no text, no watermark.
```

**2. Видео:**
```
Very slow, smooth aerial drone push forward over the misty meadow, gliding steadily toward the mountains. The low mist drifts gently over the grass, the wildflowers sway slightly in a light breeze. No sudden movement, no camera shake, no people. Calm, quiet, melancholic. Cinematic 35mm film look, muted cold blue-grey grade, fine film grain.
```

**Қате кетуі мүмкін жерлер:** дрон тым жылдам ұшады; тұман бірден сейіліп кетеді; кадрда
құс, жануар немесе адам пайда болады. Солардың бірі болса, қайта генерацияла.

---

## s02 · 0:05–0:10 · cold · Статика, жақын план

**Хикаядағы орны:** клиптің басты заты, хаттар, бірінші рет көрінеді. Келесі кадрда
Ару осы буманы қолына алады, сондықтан **бума терезе алдында тұрған орын s03-те де
сол жерде болуы керек.**

**Референс:** `images/locations/ROOM_cold.png` + `images/props/letters.png`

**1. Бастапқы кадр:**
```
Close-up of the bundle of old handwritten letters from the reference image, tied with a faded red satin ribbon, lying on the wide wooden windowsill of the same room as in the reference image. The tall wooden window and the sheer white tulle are softly out of focus behind the letters, heavy brown velvet curtain at the edge of the frame. Early overcast morning, cold pale light through the glass, a few dust particles in the air. Cinematic 35mm film look, shallow depth of field, muted cold blue-grey color grade, melancholic mood, fine film grain, 16:9, no readable text, no watermark.
```

**2. Видео:**
```
Static locked-off camera, no camera movement. The sheer tulle curtain behind the letters moves gently in a soft morning breeze, dust particles float slowly through a pale beam of light. The letters stay perfectly still. Quiet, melancholic, lonely. Cinematic 35mm film look, shallow depth of field, muted cold blue-grey grade, fine film grain.
```

**Қате кетуі мүмкін жерлер:** лента түсі өзгереді немесе өзі шешіліп кетеді; конверттегі
жазу оқылатын, бірақ мағынасыз әріптерге айналады. Бір сәтке ғана көрінсе де, қайта генерацияла.

---

## s03 · 0:10–0:14.5 · cold · Орта план

**Хикаядағы орны:** Ару бірінші рет кадрға кіреді. Көрермен оның бетін осы кадрдан
есте сақтайды, сондықтан **бет референске 100% сай келуі керек.**

**Референс:** `images/characters/her_B.png` + `images/locations/ROOM_cold.png` +
`images/props/letters.png`

**1. Бастапқы кадр:**
```
Medium shot in the same room as in the reference image, same window, same curtains, same wallpaper. The same woman as in the character reference, same face, same hairstyle parted in the middle, same pearl stud earrings, wearing a long dark navy belted dress and a black wool coat. She has just stepped into the room and stands two steps from the window, looking at the bundle of letters with the red ribbon lying on the windowsill. Her face is in soft three-quarter view, calm, tired, quietly longing. Early overcast morning, cold pale window light. Cinematic 35mm film look, shallow depth of field, muted cold blue-grey color grade, fine film grain, 16:9, no text, no watermark.
```

**2. Видео:**
```
Static camera, very slight slow push in. The woman walks slowly to the window, reaches out and gently picks up the bundle of letters with both hands, holds it close and looks down at it. Slow, calm, natural movement, her face stays consistent. Soft cold morning light, the tulle curtain moves gently. Cinematic 35mm film look, shallow depth of field, muted cold blue-grey grade, fine film grain.
```

**Қате кетуі мүмкін жерлер:** бет кадрдың ортасына қарай басқа адамға айналады; қолы
(саусақтары) бұрмаланады; бума қолға алынғанда «екіге бөлінеді». Бет 1-секундтан
кейін өзгерсе, ол видеоны алма: кадрдың ең маңызды бөлігі осы.

---

## Үшеуін тексеру

Үш видеоны қатар қойып, бір көрініс ретінде көр:

```bash
python3 tools/build.py render --preview --snap
```

- [ ] Үшеуінің түсі бірдей суық ма? Біреуі жылырақ болса, бірден байқалады.
- [ ] s02 мен s03-тегі терезе мен бума бір орын ба?
- [ ] Ару s03-те референстегі адам ба?
- [ ] Қозғалыс баяу ма, фортепианоның ырғағына сай ма?

Үшеуі де өтсе, процесс жұмыс істеп тұр деген сөз. Қалған 51 кадрды дәл осылай жасайсың.
