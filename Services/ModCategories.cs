using System.Collections.Generic;

namespace MODDevToolkit.Services
{
    /// <summary>分类中文名映射，未收录的分类原样显示</summary>
    public static class ModCategories
    {
        private static readonly Dictionary<string, string> Names = new()
        {
            // Modrinth 分类（键为小写 slug）
            ["technology"] = "科技",
            ["magic"] = "魔法",
            ["adventure"] = "冒险",
            ["cursed"] = "诅咒",
            ["decoration"] = "装饰",
            ["mobs"] = "生物",
            ["optimization"] = "性能优化",
            ["utility"] = "实用",
            ["storage"] = "存储",
            ["food"] = "食物",
            ["equipment"] = "装备",
            ["worldgen"] = "世界生成",
            ["social"] = "社交",
            ["transport"] = "运输",
            ["library"] = "支持库",
            // CurseForge 常见分类（键为小写分类名）
            ["api and library"] = "支持库",
            ["adventure and rpg"] = "冒险",
            ["mobs and pets"] = "生物",
            ["world gen"] = "世界生成",
            ["ores and resources"] = "矿物资源",
            ["energy"] = "能源",
            ["automation"] = "自动化",
            ["processing"] = "处理",
            ["utility & qol"] = "实用",
            ["cosmetic"] = "装饰",
            ["dimensions"] = "维度",
            ["structures"] = "结构",
            ["crops"] = "农业",
            ["biomes"] = "生物群系",
            ["map and information"] = "地图信息",
            ["client utility"] = "客户端实用",
            ["server utility"] = "服务端实用",
            ["education"] = "教育",
            ["genetics"] = "基因",
            ["applied science"] = "应用科学",
            ["tweaks"] = "调整优化"
        };

        public static string Display(string name)
            => Names.TryGetValue(name.ToLowerInvariant(), out var chinese) ? chinese : name;
    }
}
