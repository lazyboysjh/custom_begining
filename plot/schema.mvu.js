import { registerMvuSchema } from 'https://testingcf.jsdelivr.net/gh/StageDog/tavern_resource/dist/util/mvu_zod.js';

const clamp100 = n => _.clamp(Number(n) || 0, 0, 100);

export const Schema = z
  .object({
    世界: z
      .object({
        相遇方式: z.string().prefault(''),
        场景: z.string().prefault(''),
        教会名: z.string().prefault('圣言堂'),
        回合: z.coerce.number().transform(v => Math.max(1, Math.floor(v))).prefault(1),
        同场角色: z.string().prefault(''),
      })
      .prefault({}),

    主角: z
      .object({
        姓名: z.string().prefault(''),
        身份: z.string().prefault('教堂牧师'),
        年龄外观: z.string().prefault(''),
        性格倾向: z.string().prefault(''),
        表面作风: z.string().prefault(''),
        私下心思: z.string().prefault(''),
        能力摘要: z.string().prefault('能感知并净化污秽；仪式需接触身体或精神'),
      })
      .prefault({}),

    初遇: z
      .object({
        姓名: z.string().prefault(''),
        作品: z.string().prefault(''),
        是否自定义: z.boolean().prefault(false),
        污秽类型: z.string().prefault(''),
        污秽度: z.coerce.number().prefault(40),
        信任: z.coerce.number().prefault(15),
        好感度: z.coerce.number().prefault(10),
        堕落值: z.coerce.number().prefault(5),
        依存度: z.coerce.number().prefault(0),
        仪式阶段: z.string().prefault('初见'),
        与user关系: z.string().prefault('陌路'),
        当前心态: z.string().prefault(''),
      })
      .prefault({})
      .transform(data => {
        data.污秽度 = clamp100(data.污秽度);
        data.信任 = clamp100(data.信任);
        data.好感度 = clamp100(data.好感度);
        data.堕落值 = clamp100(data.堕落值);
        data.依存度 = clamp100(data.依存度);
        return data;
      }),
  })
  .prefault({});

$(() => {
  registerMvuSchema(Schema);
});
