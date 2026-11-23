# Ару мен Диас: референс промпттары

Мақсат: 54 кадрдың бәрінде кейіпкердің беті бірдей болуы. Сондықтан бет, тұлға және
киім бөлек кезеңдерде бекітіледі. Әр кезең алдыңғы кезеңде таңдалған суретті референс
ретінде пайдаланады.

**Тұрақты белгілер** (`tokens.json`-да бар, барлық кадрда қайталанады):
- Ару: шашы ортадан фарқпен, белге дейін; бадам пішінді қоңыр көз; түзу қою қас; кішкентай інжу сырға.
- Диас: шашы үстіңгі жағында сәл ұзынырақ; ұқыпты қысқа сақал; сол қолында қарапайым болат сағат.

Мұндағы аксессуарлар (сырға, сағат) барлық киім кезеңінде бірдей қалады. Олар
генераторға «бұл сол адам» деген қосымша белгі береді.

---

## 1-кезең. Бет (identity): ең маңызды қадам

Әр промптпен **4–8 нұсқа** жаса. Біреуін таңда. Таңдағанда тек бетке қара, киім мен
фон маңызды емес. Беті ерекше, есте қалатын нұсқаны ал. «Сұлу, бірақ жалпы» бет AI-да
келесі кадрда басқа адамға оңай айналады.

**Ару:**
```
Photorealistic close-up portrait of a 24-year-old Kazakh woman with long straight black hair parted in the middle reaching mid-back, almond-shaped warm brown eyes, straight dark eyebrows, soft oval face, natural makeup, small pearl stud earrings. Calm, slightly melancholic expression, looking directly at the camera. Plain light grey background, soft even studio light from the front, natural skin texture with visible pores, no retouching, 85mm lens, shoulders visible, wearing a simple plain cream top. No text, no watermark.
```

**Диас:**
```
Photorealistic close-up portrait of a 27-year-old Kazakh man with short black hair slightly longer on top, neatly trimmed light stubble, kind dark eyes, slim athletic build. Calm, warm, slightly tired expression, looking directly at the camera. Plain light grey background, soft even studio light from the front, natural skin texture with visible pores, no retouching, 85mm lens, shoulders visible, wearing a simple plain grey t-shirt. No text, no watermark.
```

Сақта: `images/characters/her_face.png`, `images/characters/him_face.png`

---

## 2-кезең. Кейіпкер парағы (turnaround)

1-кезеңде таңдалған бет суретін **референс ретінде** тірке.

**Ару:**
```
Character reference sheet of the same woman as in the reference image, same face, same person. Four views side by side on a plain light grey background: front close-up portrait, three-quarter view, side profile, full body standing. Long straight black hair parted in the middle reaching mid-back, small pearl stud earrings, height about 165 cm. Wearing a simple plain cream top and light trousers. Soft even studio light, photorealistic, identical face and hairstyle in all four views, 16:9, no text, no labels, no watermark.
```

**Диас:**
```
Character reference sheet of the same man as in the reference image, same face, same person. Four views side by side on a plain light grey background: front close-up portrait, three-quarter view, side profile, full body standing. Short black hair slightly longer on top, neatly trimmed light stubble, slim athletic build, height about 182 cm, a simple steel wristwatch on his left wrist. Wearing a simple plain grey t-shirt and dark trousers. Soft even studio light, photorealistic, identical face and hairstyle in all four views, 16:9, no text, no labels, no watermark.
```

Сақта: `her_sheet.png`, `him_sheet.png`

---

## 3-кезең. Киім кезеңдері A / B / C

Референс: **бет суреті + кейіпкер парағы**. Әр киімге екі нұсқа жаса: толық бойы және
белге дейін. Видео генераторға екеуі де керек.

| Кезең | Хикаядағы орны | Түсі |
|---|---|---|
| A | танысу, махаббат | warm |
| B | айырылу, күту | cold |
| C | оралу, финал | warm / dream |

### Ару

**A:**
```
Full body and waist-up photos of the same woman as in the reference images, same face, same hairstyle, same pearl stud earrings. Wearing a cream midi dress with a thin light-beige knit cardigan and simple beige flat shoes. Standing naturally, relaxed posture, gentle smile. Plain light grey background, soft even studio light, photorealistic, 16:9, no text, no watermark.
```

**B:**
```
Full body and waist-up photos of the same woman as in the reference images, same face, same hairstyle, same pearl stud earrings. Wearing a long dark navy belted dress and a black wool coat, black ankle boots. Standing still, arms close to the body, quiet sad expression. Plain light grey background, soft even studio light, photorealistic, 16:9, no text, no watermark.
```

**C:**
```
Full body and waist-up photos of the same woman as in the reference images, same face, same hairstyle, same pearl stud earrings. Wearing a flowing white linen dress, barefoot or simple light sandals. Standing in an open relaxed pose, soft hopeful smile. Plain light grey background, soft even studio light, photorealistic, 16:9, no text, no watermark.
```

### Диас

**A:**
```
Full body and waist-up photos of the same man as in the reference images, same face, same hairstyle, same stubble, same steel wristwatch on his left wrist. Wearing a light grey-blue linen shirt with rolled sleeves and beige chinos, brown leather shoes. Standing naturally, relaxed posture, warm smile. Plain light grey background, soft even studio light, photorealistic, 16:9, no text, no watermark.
```

**B:**
```
Full body and waist-up photos of the same man as in the reference images, same face, same hairstyle, same stubble, same steel wristwatch on his left wrist. Wearing a dark navy wool coat over a black turtleneck, dark trousers, black boots. Standing still, hands in coat pockets, serious distant expression. Plain light grey background, soft even studio light, photorealistic, 16:9, no text, no watermark.
```

**C:**
```
Full body and waist-up photos of the same man as in the reference images, same face, same hairstyle, same stubble, same steel wristwatch on his left wrist. Wearing a faded denim jacket over a grey t-shirt, dark jeans, worn boots, carrying a large dark hiking backpack on both shoulders. Standing, slightly tired but relieved expression. Plain light grey background, soft even studio light, photorealistic, 16:9, no text, no watermark.
```

Сақта: `her_A.png`, `her_B.png`, `her_C.png`, `him_A.png`, `him_B.png`, `him_C.png`

---

## 4-кезең. Жұп тексерісі (міндетті)

Екеуі бір кадрда бөлек жасалғандағыдай көріне ме, бойларының айырмасы сақтала ма,
соны тексеру керек. 54 кадрдың жартысына жуығында екеуі бірге.
Референс: `her_A.png` + `him_A.png`.

```
Full body photo of the two people from the reference images standing side by side, same faces, same outfits. The woman stands on the left, the man on the right, he is about a head taller than her. They look at each other with a shy smile. Plain light grey background, soft even studio light, photorealistic, 16:9, no text, no watermark.
```

Сақта: `couple_A.png`. Беттердің бірі өзгерсе, видеоға өтпе. Оның орнына 1-кезеңге
қайтып, айқынырақ бетті таңда.

---

## Таңдау чек-листі

- [ ] 4 ракурстың бәрінде бет бірдей ме (көз пішіні, қас, иек)?
- [ ] Шаш бірдей ме (Ару: ортадан фарқ; Диас: үсті ұзынырақ)?
- [ ] Сырға / сағат көрінеді ме?
- [ ] Қол саусақтары, құлақ, тістер дұрыс па (AI жиі қателесетін жерлер)?
- [ ] Бет «стоктық фото» сияқты емес, нақты адамға ұқсай ма?
- [ ] Жұп кадрда Диас Арудан бір бас биік пе?

Бәрі «иә» болса ғана `storyboard.md`-ға өт.
