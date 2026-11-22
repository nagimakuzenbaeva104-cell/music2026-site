# Тизер: 13 кадрдың өндіріс парағы

Бұл парақ тек тизерге керек кадрларды қамтиды. Кадрлар тізбектегі ретімен емес, **жасау ретімен** топталған: алдымен оңайлары, соңында екі кейіпкер бірге түсетін ең қиындары.

## 0-қадам. Төрт референс сурет

Тизерге алты емес, төрт сурет жеткілікті: Ару (A, B), Диас (A, B). C киімі финалға керек, ал финал тизерде жоқ.

1. Алдымен `her_A` суретін жаса. Беті ұнаған нұсқаны тапқанша қайталай бер, кейінгінің бәрі осы бетке сүйенеді.
2. `her_B` суретін жасағанда `her_A` суретін референс етіп жүкте де, промптқа *same person, same face* деп қос.
3. Диаспен де солай істе: алдымен `him_A`, содан кейін `him_B`.

**her_A.png**: Ару, A киімі (махаббат кезеңі)
```
Character reference sheet of a 24-year-old Kazakh woman with long straight black hair, warm brown eyes, soft oval face, natural makeup, wearing a cream midi dress with a thin light-beige knit cardigan. Four views on a plain light grey background: front close-up portrait, three-quarter view, side profile, full body standing. Soft even studio light, photorealistic, consistent face in all views, no text.
```

**her_B.png**: Ару, B киімі (күту кезеңі)
```
Character reference sheet of a 24-year-old Kazakh woman with long straight black hair, warm brown eyes, soft oval face, natural makeup, wearing a long dark navy belted dress and a black wool coat. Four views on a plain light grey background: front close-up portrait, three-quarter view, side profile, full body standing. Soft even studio light, photorealistic, consistent face in all views, no text.
```

**him_A.png**: Диас, A киімі
```
Character reference sheet of a 27-year-old Kazakh man with short black hair, light stubble, kind dark eyes, slim athletic build, wearing a light grey-blue linen shirt with rolled sleeves and beige chinos. Four views on a plain light grey background: front close-up portrait, three-quarter view, side profile, full body standing. Soft even studio light, photorealistic, consistent face in all views, no text.
```

**him_B.png**: Диас, B киімі
```
Character reference sheet of a 27-year-old Kazakh man with short black hair, light stubble, kind dark eyes, slim athletic build, wearing a dark navy wool coat over a black turtleneck. Four views on a plain light grey background: front close-up portrait, three-quarter view, side profile, full body standing. Soft even studio light, photorealistic, consistent face in all views, no text.
```

## Google Flow баптаулары

- Формат: **16:9**. Тік (Shorts) нұсқасын скрипт өзі қиып жасайды, бөлек генерациялау керек емес. Бірақ тік нұсқада кадрдың тек ортасы қалады, сондықтан кейіпкерді кадрдың ортасына қойған дұрыс. Беті шетте қалса, `moodfilm.csv`-дағы `focus` бағанымен түзетемін.
- Ұзақтығы: Flow-дың стандарты (~8 с) жеткілікті. Скрипт әр клиптің 1-секундынан бастап керек бөлігін ғана алады, себебі алғашқы кадрлар көбіне бұлдыр болып шығады.
- Әр кадрды 2-4 нұсқада жасап, **ең жақсысын ғана** сақта.
- Файл аты: кадр нөмірі, мысалы `s09.mp4`, `s10.mp4`.

**Дайын болғанда:** видеоларды Google Drive-тағы **«LoveStory - Бізді күткен таң»** папкасына сал (әнді де, `song.mp3`). Мен оларды сол жерден алып, тизерді жинаймын. Бәрін бірден жасау міндетті емес: алғашқы 4 кадрды салсаң-ақ, стилін бірге тексеріп аламыз.

## 1-топ. Кейіпкерсіз кадрлар (бірінші жаса)

Референс керек емес. Стильді тексеруге ыңғайлы: түсі мен атмосферасы ұнамаса, кейіпкерлі кадрларға өтпей тұрып осы жерде түзетеміз.

### s09 · тизерде 1-кадр · 3.6 с · cold

**Ән сөзі:** Үмітімнің оты әлі сөнбейді  
**Камера:** Макро  
**Көрініс:** Хаттардың жанында жанып тұрған шырақ.  
**Неге керек:** «Үмітімнің оты әлі сөнбейді» сөзіне шырақ: ашылу

```
Macro close-up of a small candle flame burning on a windowsill next to a stack of old letters, soft bokeh, the flame flickers but does not go out, cinematic 35mm film look, shallow depth of field, muted cold blue-grey color grade, soft overcast light, melancholic mood, fine film grain, 16:9, no text, no subtitles, no watermark
```

### s07 · тизерде 6-кадр · 2.5 с · cold

**Ән сөзі:** Кеше кеткен жолдар алыс көрінсе де  
**Камера:** Кең план статика  
**Көрініс:** Бос, тұманды перрон.  
**Неге керек:** «Қайта оралшы»: бос перрон. Естелік пен бүгінгі күн кезектеседі

```
Wide static shot of an empty an old railway station platform with an arched iron roof and a long passenger train on a foggy morning, no people, wet platform, cinematic 35mm film look, shallow depth of field, muted cold blue-grey color grade, soft overcast light, melancholic mood, fine film grain, 16:9, no text, no subtitles, no watermark
```

### s16 · тизерде 7-кадр · 3.0 с · warm

**Ән сөзі:** Қолыңды бер  
**Камера:** Макро  
**Көрініс:** Саусақтары айқасады, артынан күн сәулесі.  
**Неге керек:** Саусақтар айқасады

```
Macro close-up of a man's hand and a woman's hand slowly interlacing fingers, strong golden backlight, grass softly out of focus, cinematic 35mm film look, shallow depth of field, soft golden natural light, gentle lens flare, warm romantic color grade, fine film grain, 16:9, no text, no subtitles, no watermark
```

### s29 · тизерде 12-кадр · 2.5 с · cold

**Ән сөзі:** Бірге құрған арман бізді шақырған  
**Камера:** Статика уақыт өтуі  
**Көрініс:** Терезе алдында конверттер көбейеді, сыртта маусым ауысады.  
**Неге керек:** Конверттер көбейеді: уақыт өтіп жатыр

```
Static close-up on the windowsill of a small old apartment room with a tall wooden window, heavy brown velvet curtains, sheer white tulle, faded floral wallpaper and a wide wooden windowsill: envelopes pile up one by one as time passes, outside the window the tree changes from autumn leaves to snow to fresh green buds, cinematic 35mm film look, shallow depth of field, muted cold blue-grey color grade, soft overcast light, melancholic mood, fine film grain, 16:9, no text, no subtitles, no watermark
```

## 2-топ. Ару жалғыз (B киімі)

Ингредиент ретінде `her_B.png` суретін қос.

### s10 · тизерде 2-кадр · 3.6 с · cold

**Ән сөзі:** Үмітімнің оты әлі сөнбейді  
**Камера:** Жақын план  
**Көрініс:** Қыздың жүзі: көзінде жас, бірақ әлсіз үміт күлкісі.  
**Неге керек:** Көз жасы мен әлсіз күлкі: көңіл-күйді бірден береді

```
Close-up of a 24-year-old Kazakh woman with long straight black hair, warm brown eyes, soft oval face, natural makeup, wearing a long dark navy belted dress and a black wool coat by the window, a tear on her cheek but a small hopeful smile, warm candle light on one side of her face, cinematic 35mm film look, shallow depth of field, muted cold blue-grey color grade, soft overcast light, melancholic mood, fine film grain, 16:9, no text, no subtitles, no watermark
```

### s11 · тизерде 3-кадр · 4.2 с · cold

**Ән сөзі:** Көзім көкке үнсіз қарайды  
**Камера:** Төменнен орта план  
**Көрініс:** Ашық терезеден аспанға қарайды.  
**Неге керек:** «Көзім көкке үнсіз қарайды»: сөз бен кадр дәл түседі

```
Low angle medium shot: a 24-year-old Kazakh woman with long straight black hair, warm brown eyes, soft oval face, natural makeup, wearing a long dark navy belted dress and a black wool coat leans on the open window of a small old apartment room with a tall wooden window, heavy brown velvet curtains, sheer white tulle, faded floral wallpaper and a wide wooden windowsill and silently looks up at the pale morning sky, wind in her hair, cinematic 35mm film look, shallow depth of field, muted cold blue-grey color grade, soft overcast light, melancholic mood, fine film grain, 16:9, no text, no subtitles, no watermark
```

### s06 · тизерде 10-кадр · 3.0 с · cold

**Ән сөзі:** Сенің атың жүрегімде тұрады  
**Камера:** Жақын план  
**Көрініс:** Хатты кеудесіне басып, көзін жұмады.  
**Неге керек:** Хатты кеудесіне басады

```
Close-up of a 24-year-old Kazakh woman with long straight black hair, warm brown eyes, soft oval face, natural makeup, wearing a long dark navy belted dress and a black wool coat pressing a handwritten letter to her chest with her eyes closed, window light, quiet longing, cinematic 35mm film look, shallow depth of field, muted cold blue-grey color grade, soft overcast light, melancholic mood, fine film grain, 16:9, no text, no subtitles, no watermark
```

### s24 · тизерде 8-кадр · 3.0 с · cold

**Ән сөзі:** (скрипка)  
**Камера:** Кең план статика  
**Көрініс:** Поезд кетеді. Бос перронда қыз жалғыз қалады.  
**Неге керек:** Поезд кетеді

```
Wide static shot: the train pulls away from an old railway station platform with an arched iron roof and a long passenger train and a 24-year-old Kazakh woman with long straight black hair, warm brown eyes, soft oval face, natural makeup, wearing a long dark navy belted dress and a black wool coat is left standing alone on the empty platform, autumn leaves blowing past, fog, cinematic 35mm film look, shallow depth of field, muted cold blue-grey color grade, soft overcast light, melancholic mood, fine film grain, 16:9, no text, no subtitles, no watermark
```

## 3-топ. Диас жалғыз (B киімі)

Ингредиент ретінде `him_B.png` суретін қос.

### s12 · тизерде 4-кадр · 4.5 с · cold

**Ән сөзі:** Жүрек саған жолын табады  
**Камера:** Кең план  
**Көрініс:** Алыстағы қалада жігіт шатырда тұрып, сол аспанға қарайды.  
**Неге керек:** Жігіт сол аспанға қарайды: екеуі алыста екені түсінікті

```
Wide shot: a 27-year-old Kazakh man with short black hair, light stubble, kind dark eyes, slim athletic build, wearing a dark navy wool coat over a black turtleneck stands alone on a rooftop of a distant grey city at dawn and looks up at the same pale sky, cinematic 35mm film look, shallow depth of field, muted cold blue-grey color grade, soft overcast light, melancholic mood, fine film grain, 16:9, no text, no subtitles, no watermark
```

## 4-топ. Естеліктер (A киімі)

Ингредиент ретінде `her_A.png` суретін, екеуі бірге болса `him_A.png` суретін де қос.

### s13 · тизерде 5-кадр · 3.4 с · warm

**Ән сөзі:** Қайта оралшы жаным  
**Камера:** Жақын план slow motion  
**Көрініс:** Естелік: түнгі жаңбыр, мөлдір қолшатыр астында көздері алғаш түйіседі.  
**Неге керек:** Қайырма басталады: алғашқы көзқарас. Түс жылыға ауысады

```
Slow motion close-up two-shot under a transparent umbrella at night in a narrow city street at night in the rain, wet asphalt reflecting warm street lamps and neon shop signs, soft bokeh, a 24-year-old Kazakh woman with long straight black hair, warm brown eyes, soft oval face, natural makeup, wearing a cream midi dress with a thin light-beige knit cardigan with a black wool coat over her dress and a 27-year-old Kazakh man with short black hair, light stubble, kind dark eyes, slim athletic build, wearing a light grey-blue linen shirt with rolled sleeves and beige chinos soaked by the rain look into each other's eyes for the first time, rain drops sparkling in warm street light, cinematic 35mm film look, shallow depth of field, soft golden natural light, gentle lens flare, warm romantic color grade, fine film grain, 16:9, no text, no subtitles, no watermark
```

### s19 · тизерде 11-кадр · 3.0 с · warm

**Ән сөзі:** Қайта оралшы жүрегімнің жарығы  
**Камера:** Жігіттің көзімен (POV)  
**Көрініс:** Қыз артына бұрылып, камераға күледі.  
**Неге керек:** POV: қыз артына бұрылып күледі

```
POV shot: a 24-year-old Kazakh woman with long straight black hair, warm brown eyes, soft oval face, natural makeup, wearing a cream midi dress with a thin light-beige knit cardigan turns back toward the camera while walking through a wide meadow of tall grass and small white wildflowers in the foothills of the Tien Shan mountains, laughing, her hair blowing in the wind, golden sun behind her, cinematic 35mm film look, shallow depth of field, soft golden natural light, gentle lens flare, warm romantic color grade, fine film grain, 16:9, no text, no subtitles, no watermark
```

### s18 · тизерде 9-кадр · 3.5 с · warm

**Ән сөзі:** Махаббатым ешқашан сөнбейді  
**Камера:** Орта план slow motion  
**Көрініс:** Жігіт қызды айналдырады, көйлегі желпінеді.  
**Неге керек:** Шалғында айналу: ең жарық сәт

```
Slow motion: a 27-year-old Kazakh man with short black hair, light stubble, kind dark eyes, slim athletic build, wearing a light grey-blue linen shirt with rolled sleeves and beige chinos spins a 24-year-old Kazakh woman with long straight black hair, warm brown eyes, soft oval face, natural makeup, wearing a cream midi dress with a thin light-beige knit cardigan around in a wide meadow of tall grass and small white wildflowers in the foothills of the Tien Shan mountains, her dress and hair flowing, both laughing, sun flare behind them, cinematic 35mm film look, shallow depth of field, soft golden natural light, gentle lens flare, warm romantic color grade, fine film grain, 16:9, no text, no subtitles, no watermark
```

### s21 · тизерде 13-кадр · 3.5 с · warm

**Ән сөзі:** Бізді күткен таң әлі де атады  
**Камера:** Жақын план силуэт  
**Көрініс:** Төбеде күн батарда маңдайлары түйіседі.  
**Неге керек:** «Бізді күткен таң»: маңдай түйісуі

```
Close-up near silhouette on a mountain hilltop at sunset: a 24-year-old Kazakh woman with long straight black hair, warm brown eyes, soft oval face, natural makeup, wearing a cream midi dress with a thin light-beige knit cardigan and a 27-year-old Kazakh man with short black hair, light stubble, kind dark eyes, slim athletic build, wearing a light grey-blue linen shirt with rolled sleeves and beige chinos touch foreheads with eyes closed, his hands on her face, hazy hills behind, cinematic 35mm film look, shallow depth of field, soft golden natural light, gentle lens flare, warm romantic color grade, fine film grain, 16:9, no text, no subtitles, no watermark
```

## Тексеру парағы

- [ ] `s09.mp4`: Хаттардың жанында жанып тұрған шырақ.
- [ ] `s10.mp4`: Қыздың жүзі: көзінде жас, бірақ әлсіз үміт күлкісі.
- [ ] `s11.mp4`: Ашық терезеден аспанға қарайды.
- [ ] `s12.mp4`: Алыстағы қалада жігіт шатырда тұрып, сол аспанға қарайды.
- [ ] `s13.mp4`: Естелік: түнгі жаңбыр, мөлдір қолшатыр астында көздері алғаш түйіседі.
- [ ] `s07.mp4`: Бос, тұманды перрон.
- [ ] `s16.mp4`: Саусақтары айқасады, артынан күн сәулесі.
- [ ] `s24.mp4`: Поезд кетеді. Бос перронда қыз жалғыз қалады.
- [ ] `s18.mp4`: Жігіт қызды айналдырады, көйлегі желпінеді.
- [ ] `s06.mp4`: Хатты кеудесіне басып, көзін жұмады.
- [ ] `s19.mp4`: Қыз артына бұрылып, камераға күледі.
- [ ] `s29.mp4`: Терезе алдында конверттер көбейеді, сыртта маусым ауысады.
- [ ] `s21.mp4`: Төбеде күн батарда маңдайлары түйіседі.
- [ ] `song.mp3`
