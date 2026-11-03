---@class LegacyAtlasLootInstance
---@field InstanceID? number
---@field LevelRange? number[] minimum entry level, recommended minimum and maximum

---@class LegacyAtlasLootDatabase
---@field Get fun(self: LegacyAtlasLootDatabase, module: string): table<string, LegacyAtlasLootInstance>?

---@class LegacyAtlasLootLoader
---@field LoadModule fun(self: LegacyAtlasLootLoader, module: string)

---@class LegacyAtlasLoot
---@field ItemDB LegacyAtlasLootDatabase
---@field Loader? LegacyAtlasLootLoader

---@type LegacyAtlasLoot?
AtlasLoot = nil
