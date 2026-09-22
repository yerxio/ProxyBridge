当前项目下, 如需使用python, 就是用项目下的`.venv`文件夹的python环境. 如果没有.venv文件夹, 则提醒用户创建项目级.venv的python环境.

当前项目不使用git进行仓库管理. 当前项目.venv的python环境要求安装dulwich. 如果没有安装, 则自动安装. 安装后, 在终端使用dulwich命令代替git命令, 不创建dulwich脚本, 只在终端使用dulwich命令即可. 如果需要commit或者push等操作, 仅能使用dulwich命令进行代替, 不可使用git命令.