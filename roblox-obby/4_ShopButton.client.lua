--[[
  4_ShopButton  —  "LocalScript" ретінде TextButton-ның ІШІНЕ қойыңыз.

  Дайындық:
  - StarterGui → ScreenGui қосыңыз → ішіне TextButton қосыңыз.
  - Батырманың мәтіні: "⚡ 2x Speed".
  - Осы LocalScript-ті сол TextButton-ның ішіне салыңыз.

  Не істейді:
  - Батырманы басқанда Roblox-тың сатып алу терезесі ашылады.
  - Сатып алғаннан кейін жылдамдықты 3_SpeedGamepass скрипті қосады.
]]

local Players = game:GetService("Players")
local MarketplaceService = game:GetService("MarketplaceService")

local SPEED_PASS_ID = 0 -- ← 3_SpeedGamepass-тағы ID-мен БІРДЕЙ болуы керек

local button = script.Parent

button.Activated:Connect(function()
	MarketplaceService:PromptGamePassPurchase(Players.LocalPlayer, SPEED_PASS_ID)
end)
