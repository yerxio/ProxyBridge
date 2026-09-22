# ProxyBridge

将**带认证的 HTTP 上游代理**桥接为本地普通 HTTP 代理，供 Chrome、curl、自动化工具等使用。应用只需要连接本地监听端口，无需支持上游代理用户名和密码。

> 当前版本仅实现 HTTP 上游代理（包括 HTTPS `CONNECT` 隧道）。SOCKS5、VMess 等作为后续可插拔传输类型预留，当前不实现。

## 快速开始

### 1. 准备 Python 环境

要求 Python `3.10` 或更高版本。首次使用时，在项目根目录创建独立虚拟环境并安装项目：

```bash
cd /Users/yang/Documents/ProxyBridge
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
```

`-e .` 是 editable 安装：代码仍保留在当前目录，但虚拟环境可以正确找到
`src/proxybridge` 包。后续使用不需要重复安装；如果修改了依赖或重新克隆项目，再执行一次安装命令即可。

检查安装是否成功：

```bash
.venv/bin/python -c "import proxybridge; print(proxybridge.__file__)"
.venv/bin/python -m proxybridge --help
```

Windows PowerShell 对应命令：

```powershell
py -3 -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m proxybridge --help
```

### 2. 启动服务

```bash
.venv/bin/python -m proxybridge --upstream http://USER:PASSWORD@HOST:PORT
```

Chrome 配置：

```text
HTTP 代理：127.0.0.1:18888
HTTPS 代理：127.0.0.1:18888
```

也可以使用环境变量，避免凭据出现在 shell 历史中：

```bash
export PROXYBRIDGE_UPSTREAM='http://USER:PASSWORD@HOST:PORT'
.venv/bin/python -m proxybridge
```

## 代理切换

当前进程支持单一活动上游代理。切换时使用 `--upstream` 重新启动服务；服务设计保留了 `UpstreamTransport`、`UpstreamSelector` 抽象，后续可增加代理池、健康检查和运行时切换 API，而不改动客户端协议处理层。

```bash
.venv/bin/python -m proxybridge \
  --listen 127.0.0.1:18888 \
  --upstream http://USER:PASSWORD@NEW_HOST:2000
```

## 参数

```text
--listen HOST:PORT       本地监听地址，默认 127.0.0.1:18888
--upstream URL           上游 HTTP 代理 URL，格式 http://[USER:PASSWORD@]HOST:PORT
--upstream-file PATH     从文件读取 URL（可用环境变量覆盖密码）
--connect-timeout SEC    连接超时，默认 30
--idle-timeout SEC       隧道空闲超时，默认 120
--log-level LEVEL        DEBUG/INFO/WARNING，默认 INFO
--version                显示版本
```

## 安全约定

- 默认只监听 `127.0.0.1`，避免把本地代理暴露到局域网。
- 日志不输出用户名、密码或完整 URL 查询参数。
- 不解密 HTTPS；`CONNECT` 建立后只转发字节流。
- 生产环境建议使用环境变量或权限为 `0600` 的配置文件。

## 目录结构

```text
src/proxybridge/
  __main__.py       CLI 入口
  cli.py            参数解析、配置校验
  config.py         不含密钥的配置模型
  server.py         线程 TCP 服务生命周期
  connection.py     HTTP 请求、CONNECT、双向 relay
  upstream.py       上游代理选择与认证头
  __init__.py       包版本信息
 tests/              协议和配置测试
 config/             本地配置示例（不放真实凭据）
```

## 开发

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m proxybridge --help
```
