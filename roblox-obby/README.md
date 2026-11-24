# Музыкалы Obby — бастапқы жинақ

Roblox Studio-да қарапайым obby (кедергілерден өту ойыны) жасауға арналған 5 скрипт.

| Файл | Studio-да түрі | Қайда қойылады |
|---|---|---|
| `1_Checkpoints.server.lua` | Script | ServerScriptService |
| `2_KillParts.server.lua` | Script | ServerScriptService |
| `3_SpeedGamepass.server.lua` | Script | ServerScriptService |
| `4_ShopButton.client.lua` | LocalScript | StarterGui → ScreenGui → TextButton ішіне |
| `5_Music.client.lua` | LocalScript | StarterPlayer → StarterPlayerScripts |

Файлдағы `.server` / `.client` жұрнақтары тек түрін көрсету үшін қойылған. Studio-да скриптті жасап, кодты көшіріп қойсаңыз жеткілікті.

## Іске қосу ретімен

1. **Карта:** Workspace ішінде `Checkpoints` папкасын (Folder) жасаңыз. Ішіне `1`, `2`, `3`... деп аталатын Part-тар қойып, әрқайсысын `Anchored = true` етіңіз. Чекпоинттердің арасына секіретін платформалар орналастырыңыз.
2. **Қауіпті бөліктер:** лава немесе тікен рөліндегі Part-тарға `Kill` тегін қойыңыз (Properties → Tags).
3. **Тексеру:** Play батырмасын басыңыз. Чекпоинттен өткенде Stage өсуі керек, ал лаваны басқанда соңғы чекпоинтте қайта пайда болуыңыз керек.
4. **Сақтау:** Game Settings → Security → *Enable Studio Access to API Services* параметрін қосыңыз.
5. **Жариялау:** File → Publish to Roblox.
6. **Геймпасс:** геймпасс жасап, оның ID-ін `3_` және `4_` файлдарына жазыңыз.
7. **Музыка:** өз тректеріңізді жүктеп, олардың ID-ін `5_` файлына жазыңыз.

## Ескерту
Бұл скрипттер Roblox Studio-да тексерілмеген, себебі менің ортамда Studio жоқ. Қате шықса, Output терезесіндегі қызыл мәтінді көшіріп жіберіңіз, түзетіп беремін.
