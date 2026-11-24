--[[
  5_Music  —  StarterPlayer → StarterPlayerScripts ішіне "LocalScript" ретінде қойыңыз.

  Не істейді:
  - Сіздің треккерді кезекпен, шексіз ойнатады (плейлист).
  - Жүктелмеген тректі өткізіп жібереді, сондықтан ойын тоқтап қалмайды.

  Өз музыкаңызды қалай қосасыз:
  1. create.roblox.com → Creations → Audio → Upload (.mp3 немесе .ogg).
     Аудио модерациядан өтеді. Жүктеу лимиті аккаунтқа байланысты,
     нақты лимитті сол беттен тексеріңіз.
  2. Жүктелген аудионың ID санын көшіріңіз.
  3. Төмендегі TRACKS тізіміне "rbxassetid://ID" түрінде қосыңыз.
  4. Аудионың рұқсаттарында (Permissions) ойыныңызға қолдануға рұқсат беріңіз,
     әйтпесе ойында дыбыс шықпайды.

  Тек өз музыкаңызды немесе құқығы бар музыканы қолданыңыз.
  Бөтен әнді жүктесеңіз, аккаунтыңыз бұғатталуы мүмкін.
]]

local SoundService = game:GetService("SoundService")

local TRACKS = {
	"rbxassetid://0", -- ← 1-трек ID
	"rbxassetid://0", -- ← 2-трек ID
}
local VOLUME = 0.4
local LOAD_TIMEOUT = 10 -- секунд

local sound = Instance.new("Sound")
sound.Name = "BackgroundMusic"
sound.Volume = VOLUME
sound.Parent = SoundService

local index = 1

while true do
	sound.SoundId = TRACKS[index]

	-- Жүктелуін күтеміз, бірақ мәңгі емес
	local waited = 0
	while not sound.IsLoaded and waited < LOAD_TIMEOUT do
		waited += task.wait(0.5)
	end

	if sound.IsLoaded then
		sound:Play()
		sound.Ended:Wait()
	else
		warn("Трек жүктелмеді, өткізіп жібердік:", TRACKS[index])
	end

	index = index % #TRACKS + 1
end
