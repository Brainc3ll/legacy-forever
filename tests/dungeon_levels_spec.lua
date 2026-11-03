local ns = { L = setmetatable({}, {
	__index = function(_, key)
		return key
	end,
}) }
assert(loadfile("Integrations/AtlasLoot.lua"))("LegacyForever", ns)
local combat, database, loads = false, nil, 0
InCombatLockdown = function()
	return combat
end
local low, high, hint = ns.DungeonLevelRange(189)
assert(low == nil and high == nil and hint:find("Install AtlasLoot", 1, true))
AtlasLoot = {
	ItemDB = {
		Get = function(_, module)
			assert(module == "AtlasLootClassic_DungeonsAndRaids")
			return database
		end,
	},
	Loader = {
		LoadModule = function()
			loads = loads + 1
			database = {
				wing1 = { InstanceID = 189, LevelRange = { 20, 26, 36 } },
				wing2 = { InstanceID = 189, LevelRange = { 20, 35, 45 } },
				other = { InstanceID = 33, LevelRange = { 10, 18, 26 } },
				invalid = { InstanceID = 189, LevelRange = { 1, 1, math.huge } },
			}
		end,
	},
}
combat = true
assert(ns.DungeonLevelRange(189) == nil and loads == 0, "never load a companion during combat")
combat = false
low, high = ns.DungeonLevelRange(189)
assert(low == 26 and high == 45 and loads == 1, "combine only the matching instance's recommended ranges")
assert(ns.DungeonLevelRange(999) == nil, "unknown entrances have no invented range")
database = nil
assert(ns.DungeonLevelRange(189) == nil and loads == 1, "an unavailable module is not loaded on every hover")
print("dungeon_levels_spec: passed")
