import { registerMvuSchema } from 'https://testingcf.jsdelivr.net/gh/StageDog/tavern_resource/dist/util/mvu_zod.js';

const clamp100 = n => _.clamp(Number(n) || 0, 0, 100);

export const Schema = z.object({
  世界: z.preprocess(
    value => value == null ? {} : value,
    z.object({
      _开局配置: z.preprocess(
        value => value == null ? {} : value,
        z.object({
          时代背景: z.string().prefault('待生成'),
          故事类型: z.string().prefault('待生成'),
          故事氛围: z.string().prefault('待生成'),
          圣堂形态: z.string().prefault('圣言堂'),
          世界融入方式: z.string().prefault('待生成'),
        }).prefault({}),
      ),
      场景: z.string().prefault(''),
      圣堂名称: z.string().prefault('圣言堂'),
      回合: z.coerce.number().transform(v => Math.max(1, Math.floor(v))).prefault(1),
      出场角色: z.preprocess(
        value => value == null ? [] : value,
        z.array(z.string())
          .transform(names => [...new Set(names.map(name => name.trim()).filter(Boolean))])
          .prefault([]),
      ),
    }).prefault({}),
  ),
  主角: z.preprocess(
    value => value == null ? {} : value,
    z.object({
      姓名: z.string().prefault(''),
      身份: z.string().prefault('教堂牧师'),
      年龄外观: z.string().prefault('帅气的高中生'),
      性格倾向: z.string().prefault('阴暗好色'),
      表面作风: z.string().prefault('温和耐心，以救人为先'),
      私下心思: z.string().prefault('性压抑的高中男生'),
      能力摘要: z.string().prefault('能感知并净化污秽；仪式需接触身体或精神'),
    }).prefault({}),
  ),
  角色: z.preprocess(
    value => value == null ? {} : value,
    z.record(
      z.string(),
      z.object({
        污秽度: z.coerce.number().prefault(40),
        信任: z.coerce.number().prefault(0),
        好感度: z.coerce.number().prefault(0),
        堕落值: z.coerce.number().prefault(0),
        依存度: z.coerce.number().prefault(0),
        外貌: z.string().prefault(''),
        当前状态: z.string().prefault('保持戒备，正在观察周围环境'),
        心里想法: z.string().prefault('先弄清这里是什么地方，再决定下一步。'),
        与user关系: z.string().prefault('陌生'),
      }).transform(data => {
        data.污秽度 = clamp100(data.污秽度);
        data.信任 = clamp100(data.信任);
        data.好感度 = clamp100(data.好感度);
        data.堕落值 = clamp100(data.堕落值);
        data.依存度 = clamp100(data.依存度);
        return data;
      }),
    ).prefault({}),
  ),
});

$(() => {
  registerMvuSchema(Schema);
});
