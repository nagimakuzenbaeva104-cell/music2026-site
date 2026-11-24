--[[
  3_SpeedGamepass  —  ServerScriptService ішіне "Script" ретінде қойыңыз.

  Не істейді:
  - "2x Speed" геймпассын сатып алған ойыншының жылдамдығын 2 есе арттырады.
  - Ойын ішінде сатып алса, жылдамдық бірден қосылады (қайта кіру қажет емес).

  Геймпасс қалай жасалады:
  1. Ойынды жариялаңыз (File → Publish to Roblox).
  2. create.roblox.com → Creations → ойыныңыз → Monetization → Passes → Create a Pass.
  3. Сурет жүктеп, атау беріңіз, бағасын қойыңыз (мысалы, 49 Robux) → "Item for Sale" қосыңыз.
  4. Пасстың ID санын көшіріп, төмендегі SPEED_PASS_ID-ге қойыңыз.
]]

local Players = game:GetService("Players")
local MarketplaceService = game:GetService("MarketplaceService")

local SPEED_PASS_ID = 0 -- ← ӨЗ ГЕЙМПАСС ID-іңізді осында жазыңыз
local NORMAL_SPEED = 16
local BOOSTED_SPEED = 32

local function ownsPass(player)
	local ok, owns = pcall(function()
		return MarketplaceService:UserOwnsGamePassAsync(player.UserId, SPEED_PASS_ID)
	end)
	return ok and owns
end

local function applySpeed(player, character)
	local humanoid = character:WaitForChild("Humanoid")
	if player:GetAttribute("HasSpeedPass") then
		humanoid.WalkSpeed = BOOSTED_SPEED
	else
		humanoid.WalkSpeed = NORMAL_SPEED
	end
end

Players.PlayerAdded:Connect(function(player)
	player:SetAttribute("HasSpeedPass", ownsPass(player))

	player.CharacterAdded:Connect(function(character)
		applySpeed(player, character)
	end)

	if player.Character then
		applySpeed(player, player.Character)
	end
end)

-- Ойын ішінде сатып алғанда
MarketplaceService.PromptGamePassPurchaseFinished:Connect(function(player, passId, purchased)
	if purchased and passId == SPEED_PASS_ID then
		player:SetAttribute("HasSpeedPass", true)
		if player.Character then
			applySpeed(player, player.Character)
		end
	end
end)
