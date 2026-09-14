# 发布到 GitHub 与 Read the Docs（一次性操作清单）

本地仓库框架已经就绪，GitHub 仓库将创建在已授权账号 LLQ95 名下，名称 EasyIsolate。
若通过连接器已经建仓并推送，可跳过第一、二步，直接做 Read the Docs 导入。

## 一、本地初始化 git（需要已安装 Git for Windows；用连接器推送则可跳过）

在仓库根目录 `EasyIsolate/` 打开终端：

```bash
git init -b main
git add .
git commit -m "init EasyIsolate v0.1.0: short/long/hybrid WGS pipeline + bilingual guidebook"
```

## 二、创建 GitHub 仓库并推送

方式 A（网页）：在 https://github.com/new 建名为 EasyIsolate 的仓库，不要自动生成
README/.gitignore/LICENSE（本地已具备），然后：

```bash
git remote add origin https://github.com/LLQ95/EasyIsolate.git
git push -u origin main
```

方式 B（GitHub CLI）：

```bash
gh repo create EasyIsolate --public --source=. --remote=origin --push
```

推送后到 Settings → Pages，Source 选 GitHub Actions，`.github/workflows/docs.yml` 会
把 guidebook 构建成 GitHub Pages 镜像。

## 三、导入 Read the Docs（英文默认，可切中文）

1. 登录 https://readthedocs.org ，用 GitHub 账号授权；
2. Import a Project，选择 LLQ95/EasyIsolate；
3. 根目录 `.readthedocs.yaml` 已识别 MkDocs，文档语言由 mkdocs-static-i18n 控制，
   默认英文 /en/，中文在 /zh/，页头有语言切换器；直接 Build；
4. 构建成功得到 `https://easyisolate.readthedocs.io`（子域以项目设置为准）。

## 四、上线前检查

确认 `config/my_samples.csv` 与 `ref/`、`00_rawdata/` 不被提交（已在 .gitignore）；
投稿前在 CITATION.cff 补全共同作者与单位。

## 五、后续版本迭代

```bash
git add -A
git commit -m "模块号: 说明"
git push
```

推送即触发 Read the Docs 与 GitHub Pages 重新构建，并在 CHANGELOG.md 追加一条。
新增或修改文档页面时，英文 `name.md` 与中文 `name.zh.md` 需同步。
