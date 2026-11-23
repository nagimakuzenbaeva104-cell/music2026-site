# s04–s06: 1-шумақтың басы (0:14.5–0:28.4)

> *Таңғы самал тереземді сипайды*
> *Сенің атың жүрегімде тұрады*

Вокал басталды. Бұл үш кадрда эмоция біртіндеп жақындайды: **хатты оқиды → есімді
сипайды → хатты жүрегіне басады.** Камера да солай: орта план → макро → жақын план.
Кадр сайын Аруға жақындаймыз.

Жұмыс тәртібі `shots-s01-s03.md`-дағыдай: алдымен бастапқы кадр (сурет), содан кейін видео
(*Frames to Video*).

**Видеоның ең аз ұзақтығы** (`clip_in = 1.0` + кадр ұзақтығы):

| Кадр | Ұзақтығы | Видео кемінде |
|---|---|---|
| s04 | 6.4 с | **7.4 с** (генератордың ұзын режимін таңда) |
| s05 | 3.8 с | 4.8 с |
| s06 | 3.7 с | 4.7 с |

**s03-пен жалғастық:** Ару пальтосын әлі шешпеген. Бума шешілген, қызыл лента мен қалған
хаттар терезе алдында жатыр. Бұл детальдар үш кадрда да сақталуы керек.

---

## s04 · 0:14.5–0:20.9 · cold · Орта план, баяу жақындау

**Ән сөзі:** «Таңғы самал тереземді сипайды»

**Хикаядағы орны:** ән сөзі кадрда сөзбе-сөз көрінеді: самал терезеден кіріп, перделерді
тербейді. Кіріспедегі ең ұзақ, ең тыныш кадр. Көрермен Аруды осы жерде алғаш рет ұзақ көреді.

**Референс:** `her_B.png` + `ROOM_cold.png` + `letters.png`
(+ s03 видеосының соңғы кадры, жалғастық үшін)

**1. Бастапқы кадр:**
```
Medium shot in the same room as in the reference image, same tall wooden window, same curtains, same wallpaper. The same woman as in the character reference, same face, same hairstyle parted in the middle, same pearl stud earrings, wearing a long dark navy belted dress and a black wool coat, standing by the window in three-quarter view and reading a single handwritten letter held in both hands. The untied faded red ribbon and the rest of the bundle of letters lie on the windowsill beside her. The sheer white tulle hangs between her and the glass. Early overcast morning, cold pale window light softly lighting her face from the side, the rest of the room in soft shadow. Cinematic 35mm film look, shallow depth of field, muted cold blue-grey color grade, melancholic mood, fine film grain, 16:9, no readable text, no watermark.
```

**2. Видео:**
```
Very slow, smooth dolly in toward the woman. A gentle morning breeze comes through the window and the sheer tulle curtain billows softly around her, a strand of her hair moves slightly. She keeps reading the letter, her eyes slowly moving along the lines, a faint sad smile appears for a moment. Calm, quiet, tender. Her face stays consistent. Cinematic 35mm film look, shallow depth of field, muted cold blue-grey grade, fine film grain.
```

**Қате кетуі мүмкін жерлер:** перде оның бетін жауып қалады; хат қолында көбейіп кетеді
немесе жоғалады; дауылдағыдай тым күшті жел соғады. Кадрдың маңызы тыныштықта, ал
«самал» дегеніміз нәзік жел.

---

## s05 · 0:20.9–0:24.7 · cold · Макро

**Ән сөзі:** «Сенің атың жүрегімде тұрады» (бірінші жартысы)

**Хикаядағы орны:** «Сенің атың» деген сөз кадрда есімге айналады. Бұл клиптің ең
интимді инсерті.

**Негізгі қиындық: жазу.** AI видео генераторлары кириллица мен қолжазбаны дұрыс жаза
алмайды. Макро планда «Диас» орнына мағынасыз белгілер шығады, ал көрермен оны бірден
көреді. Екі жол бар:

**A-жол, ұсынылады: телефонмен өзің түсір.** Ескі конвертке көк сиямен «Диас» деп жаз,
терезе алдына қой, бұлтты күні таңертең табиғи жарықта телефонмен макро түсір. Саусақ
есімді баяу сипайды, ал жеңде қара жүн мата болсын (кез келген қара свитер жарайды). Кадр
ұзақтығы 5 секунд. Содан кейін түс түзетуі `--grade` арқылы суық түске келтіріледі.
**Бұл 15 минуттық жұмыс, ал нәтиже AI-дан әлдеқайда сенімді.** Көрермен қолдың кімдікі
екенін ажырата алмайды.

**B-жол: AI.** Жазу фокустан тыс болады. Сонда есім оқылмайды, тек оның бар екені сезіледі.

**Референс:** `letters.png` + `ROOM_cold.png`

**1. Бастапқы кадр (B-жол):**
```
Extreme macro close-up of an old cream paper envelope from the reference image lying on a wooden windowsill. A woman's index finger rests on a short handwritten name written in blue ink, the cuff of a black wool coat sleeve visible at her wrist. The handwriting is softly out of focus and not readable, only the texture of ink and paper is visible. Cold pale morning window light grazing across the paper, showing its fibers. Cinematic 35mm film look, very shallow depth of field, muted cold blue-grey color grade, fine film grain, 16:9, no readable text, no watermark.
```

**2. Видео (B-жол):**
```
Static macro shot, no camera movement. The woman's fingertip slowly and gently traces along the handwritten name, as if touching it for the first time, then stops. Very slow, tender, careful movement. The handwriting stays soft and out of focus. Cinematic 35mm film look, very shallow depth of field, muted cold blue-grey grade, fine film grain.
```

**Қате кетуі мүмкін жерлер:** саусақтар артық немесе бұрмаланған; жазу фокусқа түсіп,
мағынасыз әріптер көрінеді. Біреуі болса, қайта генерацияла немесе A-жолға өт.

---

## s06 · 0:24.7–0:28.4 · cold · Жақын план

**Ән сөзі:** «Сенің атың жүрегімде тұрады» (екінші жартысы)

**Хикаядағы орны:** «жүрегімде» деген сөз іс-әрекетке айналады. Ару хатты жүрегіне басады.
Бұл 1-шумақтың эмоциялық шыңы. Камера ең жақын нүктеге жетеді.

**Референс:** `her_B.png` + `ROOM_cold.png` (+ s04-тің соңғы кадры)

**1. Бастапқы кадр:**
```
Close-up of the same woman as in the character reference, same face, same hairstyle parted in the middle, same pearl stud earrings, wearing a black wool coat over a dark navy dress, framed from the chest up, standing by the tall window of the same room as in the reference image. She holds a single handwritten letter with both hands at the level of her chest, her eyes are lowered to it. The sheer white tulle is softly out of focus behind her. Cold pale window light from the side, gentle shadow on the other side of her face. Cinematic 35mm film look, shallow depth of field, muted cold blue-grey color grade, quiet longing, fine film grain, 16:9, no readable text, no watermark.
```

**2. Видео:**
```
Static camera, very slight slow push in. The woman slowly presses the letter flat against her chest over her heart with both hands, closes her eyes and takes a slow deep breath, her shoulders relax slightly. Subtle, restrained emotion, no crying. Her face stays consistent. Cinematic 35mm film look, shallow depth of field, muted cold blue-grey grade, fine film grain.
```

**Қате кетуі мүмкін жерлер:** ол жылап жібереді, бірақ көз жасы s10-ға сақталған, мұнда
әлі ерте; хат қолынан жоғалады; көзін жұмғанда бет өзгереді. Эмоция ұстамды болуы керек:
шумақтың басында шыңға жету кейінгі кадрлардың әсерін әлсіретеді.

---

## Үшеуін тексеру

```bash
python3 tools/build.py render --preview --snap
```

- [ ] s03 → s04 → s05 → s06 бір үздіксіз сәт болып көріне ме (пальто, лента, жарық)?
- [ ] Камера кадр сайын жақындай ма (орта → макро → жақын)?
- [ ] s05-те мағынасыз әріптер көрінбей ме?
- [ ] s06-да эмоция ұстамды ма?
- [ ] Үшеуінің суық түсі бірдей ме?
