# 🏯 寺庙修缮募捐功德纪要系统

面向寺院修缮事务的全栈管理系统：前端以古风界面登记寺庙与殿堂、展示病害与修缮方案；
后端保存住持与工匠的会议对话、做语音转写与说话人标记、生成会议纪要 / 募捐文案 / 功德回向清单，
并把成稿的 Markdown 功德纪要邮寄给信众。

## ✨ 功能特性

- **语音转写**：把住持与工匠的对话录音转成文字（Whisper）
- **说话人标记**：区分寺方与设计方发言（pyannote，本地安装后启用）
- **角色识别 / 纪要生成 / 募捐文案 / 功德回向清单**：由 OpenAI 完成
- **古风界面**：殿堂病害可视化、修缮方案展示、响应式布局
- **信众通知**：生成 Markdown 功德纪要，一键邮寄

## 🏗️ 技术栈

- 后端：FastAPI + SQLAlchemy + SQLite + OpenAI + pyannote.audio（可选）
- 前端：Vue 3 + Element Plus + Vite

## 📦 项目结构

```
.
├── backend/
│   ├── api/            # 路由：temples.py / meetings.py / donors.py
│   ├── services/       # 业务：ai_service.py / document_service.py
│   ├── tests/          # 冒烟测试
│   ├── config.py       # 配置（可用环境变量覆盖）
│   ├── database.py     # 数据库连接
│   ├── models.py       # ORM 模型
│   ├── schemas.py      # Pydantic 模式
│   └── main.py         # 应用入口
├── frontend/           # Vue 3 前端
├── requirements.txt    # Python 依赖
├── AGENTS.md           # 本仓库的工程规则
└── README.md
```

## 🚀 快速开始

### 1. 配置环境变量

复制 `.env.example` 为 `.env` 并按需填写。**全部配置项都可以留空**：未配置 Key 时后端走离线分支，
不会联网，也不会因此启动失败。

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
PYANNOTE_AUTH_TOKEN=
SMTP_HOST=
SMTP_PORT=465
SMTP_USER=
SMTP_PASSWORD=
DATABASE_URL=sqlite:///./merit_record.db
TEMP_AUDIO_DIR=./temp_audio
OUTPUT_DIR=./output
```

### 2. 启动后端

```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```

（Windows 上也可以直接运行 `start-backend.bat`。）

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问

- 前端：http://localhost:5173
- 后端：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 5. 运行测试

```bash
cd backend
python -m pytest
```

## 📖 使用流程

1. 登记寺庙，再在寺庙下登记殿堂，录入殿堂病害与修缮方案
2. 在殿堂下创建修缮会议，上传会议录音
3. 点击「AI 处理会议」，系统完成转写 → 说话人标记 → 角色识别 → 纪要 / 募捐文案 / 功德回向
4. 查看对话实录、下载 Markdown 纪要，或把纪要邮寄给信众

---

## ✅ 行为规格（验收标准）

以下每一条都是**验收点**。实现必须与规格一致；`backend/tests/test_smoke.py` 只覆盖顺利路径，
规格里没有写进冒烟测试的分支同样要正确。

### A. 会议（`/api/meetings`）

- **A1** `GET /api/meetings` 支持 `hall_id` 过滤。只要请求里带了 `hall_id`（**包括 `0`** 以及其它合法整数），
  返回的列表就必须只包含该 `hall_id` 的会议；没有任何匹配时返回 `[]`。
- **A2** `POST /api/meetings` 的 `hall_id` 必须指向一个已存在的殿堂。指向不存在的殿堂时返回 `404`，
  且不得写入任何会议记录（不得留下悬空引用）。
- **A3** `GET /api/meetings` 返回的列表按会议日期**倒序**排列（`date` 最新在前）；`date` 相同时按 `id` 倒序。
  该顺序对带 `hall_id` 过滤的请求同样成立。
- **A4** `GET /api/meetings` 的 `skip` / `limit` 仍然生效。

### B. 殿堂（`/api/temples`）

- **B1** `POST /api/temples/{temple_id}/halls`：殿堂归属**由路径参数决定**，请求体**不要求**提供 `temple_id`
  （前端登记殿堂时就不带这个字段）。若请求体同时提供了 `temple_id`，一律以路径参数为准。
- **B2** `POST /api/temples/{temple_id}/halls`：`temple_id` 指向不存在的寺庙时返回 `404`。
- **B3** `PUT /api/temples/halls/{hall_id}` 是**部分更新**：只更新请求体里出现的字段，
  未出现的字段保持原值。请求体可以只含 `damage_details`、`repair_plan`、`estimated_cost` 等任意子集。
- **B4** `PUT /api/temples/halls/{hall_id}` **不得改变殿堂所属寺庙**：即使请求体带了 `temple_id`，
  也必须忽略它并保持原值（前端会把整个殿堂对象回传，其中包含 `temple_id`）。

### C. 音频上传（`/api/meetings/{id}/upload-audio`）

- **C1** 落盘文件名必须净化：只取客户端文件名的最后一段（basename），剥离目录分隔符与 `..`。
- **C2** 上传文件必须落在 `TEMP_AUDIO_DIR` 之内；不得在 `TEMP_AUDIO_DIR` 之外创建或覆盖任何文件。
- **C3** 记录进 `meetings.audio_file_path` 并返回给客户端的路径，必须就是那个真实存在的文件路径，
  且路径里不得残留 `..` 等未规范化片段。

### D. AI 转写（`backend/services/ai_service.py`）

- **D1** `transcribe_audio` 必须真正取到转写结果：`transcript` 为识别文本，`segments` 为按时间排列的
  `{"start", "end", "text"}` 列表。注意：OpenAI SDK 返回的**分段不是 `dict`**。
- **D2** 未配置 `OPENAI_API_KEY` 时，必须走离线分支：**不得发起任何网络请求**，不得抛异常；
  `transcribe_audio` 返回 `transcript == ""` 的确定结果。
- **D3** `AIService` 必须保留一个可以在测试里整体替换的 `client` 属性作为 OpenAI 客户端的注入点
  （离线环境靠替换它来验证转写逻辑），不要在 `__init__` 里把它硬绑死。

### E. 通用

- **E1** 保持现有目录结构、接口路径与响应结构不变。
- **E2** 现有 `backend/tests/test_smoke.py` 在修复后必须继续全绿。

---

## 📝 变更说明

本次修复逐条对齐上文「行为规格（验收标准）」，根因与修法如下：

- **会议筛选与排序（A1/A3/A4）**：`GET /api/meetings` 原来用 `if hall_id` 做真值判断，
  传入 `0` 时被当成「未传参」而返回全部会议；同时查询没有任何排序，返回顺序取决于
  数据库内部顺序。已改为 `hall_id is not None` 严格过滤，并统一按 `date DESC, id DESC`
  排序，过滤与未过滤请求一致，`skip`/`limit` 仍然生效。
- **会议悬空殿堂引用（A2）**：`POST /api/meetings` 原来不校验殿堂是否存在，会议可以
  挂到任意 `hall_id` 上。已在写入前查询殿堂，不存在时直接返回 `404`，不创建任何记录。
- **登记殿堂总是失败（B1/B2）**：`HallCreate` 继承的 `HallBase` 把 `temple_id` 声明为
  必填，而前端登记表单不含该字段，FastAPI 直接返回 `422`。已把请求体与归属解耦：
  `temple_id` 改为可选且一律以路径参数为准（请求体里带了也忽略），寺庙不存在时返回 `404`。
- **殿堂更新被整体改写并改寺（B3/B4）**：`PUT /api/temples/halls/{hall_id}` 原来接收
  全量 `HallCreate` 并用 `model_dump()` 覆盖全部字段（含 `temple_id`），请求体缺字段就
  被写成 `null`，还可能把殿堂挪到别的寺庙。已新增只含可选字段的 `HallUpdate`，
  用 `model_dump(exclude_unset=True)` 只覆盖实际出现的字段，且其中不含 `temple_id`，
  殿堂所属寺庙任何情况下都不变。
- **录音文件落到 TEMP_AUDIO_DIR 之外（C1/C2/C3）**：上传时直接把
  `meeting_{id}_{file.filename}` 拼进目录，客户端文件名若含 `../` 等路径片段就会写到
  `TEMP_AUDIO_DIR` 之外。已先统一正/斜杠、只取 basename、剥离 `..` 与目录分隔符，
  空名兜底为 `audio`，再对最终绝对路径做 `commonpath` 校验，确保文件与入库路径都真实
  位于 `TEMP_AUDIO_DIR` 之内且不含未规范化片段。
- **对话实录与纪要始终为空（D1）**：两处根因。其一，OpenAI SDK 返回的分段是带属性的
  对象而不是 `dict`，原代码用 `seg["start"]` 取值必然抛异常，转写整体落入 `except`
  变成空文本、空分段；已改为兼容属性与字典两种取法。其二，生成 Markdown 前重新查询
  `DialogueTurn`，而 `SessionLocal` 配置了 `autoflush=False`，刚 `add` 的轮次尚未
  flush，查出来是空列表，导致纪要里没有实录；已改为直接用内存中已创建的轮次对象构建
  实录段落（数据仍正常落库）。
- **离线分支会真的联网（D2/D3）**：原实现把 OpenAI 客户端做成懒加载属性，未配置
  `OPENAI_API_KEY` 时访问 `client` 仍会实例化 `AsyncOpenAI`，各生成方法仍会尝试请求
  配置中的 base URL。已改为构造时仅在有 Key 时创建客户端，并把 `client` 保留为可在
  测试中整体替换的普通属性；无 Key（或注入 `None`）时转写直接返回
  `{"transcript": "", "segments": []}`，摘要 / 募捐文案 / 功德回向 / 角色识别也各有
  确定的离线结果，全程不发起网络请求、不抛异常。

---

*愿以此功德，普及于一切，我等与众生，皆共成佛道。* 🙏
