--[[
  1_Checkpoints  —  ServerScriptService ішіне "Script" ретінде қойыңыз.

  Не істейді:
  - Әр ойыншыға "Stage" (кезең) санағышын қосады (жоғарғы оң жақта көрінеді).
  - Ойыншы келесі чекпоинтті басқанда кезеңі өседі.
  - Өлсе, соңғы жеткен чекпоинтінде қайта пайда болады.
  - Кезеңді DataStore-да сақтайды: ойыннан шығып, қайта кірсе, прогресі жоғалмайды.

  Дайындық (Workspace ішінде):
  - "Checkpoints" атты Folder жасаңыз.
  - Ішіне Part-тар қойыңыз, атаулары: 1, 2, 3, 4 ... (тек сандар!)
  - Әр Part: Anchored = true.
  - 1-ші Part — бастапқы нүкте (SpawnLocation-ның қасына қойыңыз).

  МАҢЫЗДЫ: DataStore Studio-да жұмыс істеуі үшін:
  Game Settings → Security → "Enable Studio Access to API Services" = ON.
]]

local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")

local stageStore = DataStoreService:GetDataStore("ObbyStage_v1")
local checkpoints = workspace:WaitForChild("Checkpoints")

local function getStageValue(player)
	local leaderstats = player:FindFirstChild("leaderstats")
	return leaderstats and leaderstats:FindFirstChild("Stage")
end

local function teleportToCheckpoint(player, character)
	local stage = getStageValue(player)
	if not stage then return end

	local checkpoint = checkpoints:FindFirstChild(tostring(stage.Value))
	if not checkpoint then return end

	character:WaitForChild("HumanoidRootPart")
	task.wait() -- Roblox-тың өз spawn-ы аяқталсын
	character:PivotTo(checkpoint.CFrame + Vector3.new(0, 4, 0))
end

local function saveStage(player)
	local stage = getStageValue(player)
	if not stage then return end

	local ok, err = pcall(function()
		stageStore:SetAsync(player.UserId, stage.Value)
	end)
	if not ok then
		warn("Stage сақталмады:", player.Name, err)
	end
end

Players.PlayerAdded:Connect(function(player)
	local leaderstats = Instance.new("Folder")
	leaderstats.Name = "leaderstats"
	leaderstats.Parent = player

	local stage = Instance.new("IntValue")
	stage.Name = "Stage"
	stage.Value = 1
	stage.Parent = leaderstats

	-- Сақталған прогресті жүктеу
	local ok, saved = pcall(function()
		return stageStore:GetAsync(player.UserId)
	end)
	if ok and typeof(saved) == "number" then
		stage.Value = saved
	end

	player.CharacterAdded:Connect(function(character)
		teleportToCheckpoint(player, character)
	end)

	-- GetAsync уақыт алады, сол кезде кейіпкер пайда болып үлгеруі мүмкін
	if player.Character then
		teleportToCheckpoint(player, player.Character)
	end
end)

Players.PlayerRemoving:Connect(saveStage)

-- Сервер жабылғанда барлығын сақтау
game:BindToClose(function()
	for _, player in ipairs(Players:GetPlayers()) do
		saveStage(player)
	end
end)

-- Чекпоинттерді тыңдау
for _, part in ipairs(checkpoints:GetChildren()) do
	local number = tonumber(part.Name)
	if part:IsA("BasePart") and number then
		part.Touched:Connect(function(hit)
			local player = Players:GetPlayerFromCharacter(hit.Parent)
			if not player then return end

			local stage = getStageValue(player)
			-- Тек келесі кезеңге өтуге рұқсат (секіріп өтіп кетуге болмайды)
			if stage and number == stage.Value + 1 then
				stage.Value = number
			end
		end)
	end
end
