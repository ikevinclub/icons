# icons

自用图标集，风格对齐 [Qure IconSet](https://github.com/Koolson/Qure) —— 单色图形、透明背景、无底板，专为 **QuantumultX 策略组图标** 设计。

## 规格

| 项目 | 值 |
| --- | --- |
| 尺寸 | 108 × 108 px |
| 格式 | PNG（RGBA，透明背景） |
| 图形区 | 72 × 72 px，居中，四边各留 18 px |
| 根目录 | 白色（`#FFFFFF`），适用于深色主题 |
| `light-theme/` | 深灰（`#222222`），适用于浅色主题 |

## 图标

| 图标 | 深色主题 | 浅色主题 | 适用场景 |
| --- | --- | --- | --- |
| <img src="Spotify.png" width="40"> | `Spotify.png` | `light-theme/Spotify.png` | 音乐 / 流媒体策略组 |
| <img src="Siri.png" width="40"> | `Siri.png` | `light-theme/Siri.png` | Siri / Apple 智能 / AI 策略组 |

## 使用

`[policy]` 段给策略组挂图标：

```ini
[policy]
static=SiriAI, 节点A, 节点B, img-url=https://raw.githubusercontent.com/ikevinclub/icons/main/Siri.png
static=Music,  节点A, 节点B, img-url=https://raw.githubusercontent.com/ikevinclub/icons/main/Spotify.png
```

国内网络可用 jsDelivr 加速：

```
https://cdn.jsdelivr.net/gh/ikevinclub/icons@main/Siri.png
```

> 具体参数名以你当前 QuantumultX 版本的配置文件为准。

## 重新生成 / 新增图标

图形由 Python 脚本程序化生成，不依赖任何在线服务：

```bash
cd src
pip install pillow
python build_icons.py
```

- `src/build_icons.py`：路径解析 + 光栅化（8× 超采样后降采样，边缘平滑）
- `src/spotify_si.svg`：Spotify 官方 logo 路径，取自 [simple-icons](https://github.com/simple-icons/simple-icons)（CC0 1.0）
- Siri 图标为原创绘制（对称圆角声波），非 Apple 官方素材

新增图标时，在 `src/build_icons.py` 里加一个渲染函数，`finish()` 会统一处理裁切、缩放、居中、留白和配色。

## 说明

- Apple、Siri、Spotify 等名称与图形为其各自权利人的商标，本仓库仅作个人配置用途。
- 单色透明图标在对比度不足的背景下会看不清 —— 深色背景用根目录版本，浅色背景用 `light-theme/` 版本。
