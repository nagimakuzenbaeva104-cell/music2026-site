--[[
  2_KillParts  —  ServerScriptService ішіне "Script" ретінде қойыңыз.

  Не істейді:
  - "Kill" тегі бар кез келген Part-ты басқан ойыншы өледі (лава, тікен т.б.).
  - Ойыншы өлгеннен кейін 1_Checkpoints скрипті оны соңғы чекпоинтке қайтарады.

  Тег қалай қойылады:
  - Part-ты таңдаңыз → Properties терезесінің төменгі жағы → "Tags" → "Kill" деп жазыңыз.
  - Ойын барысында қосылған жаңа бөліктер де автоматты түрде жұмыс істейді.
]]

local CollectionService = game:GetService("CollectionService")

local TAG = "Kill"

local function setupKillPart(part)
	if not part:IsA("BasePart") then return end

	part.Touched:Connect(function(hit)
		local humanoid = hit.Parent and hit.Parent:FindFirstChildOfClass("Humanoid")
		if humanoid and humanoid.Health > 0 then
			humanoid.Health = 0
		end
	end)
end

for _, part in ipairs(CollectionService:GetTagged(TAG)) do
	setupKillPart(part)
end

CollectionService:GetInstanceAddedSignal(TAG):Connect(setupKillPart)
