请按照以下步骤操作。我们将对 `configure` 和 `make` 命令都使用这种强制指定 `PATH` 的方法。

#### 第 1 步：进入源码目录

确保您当前位于 Python 的源码目录中。

````bash
cd /usr/src/Python-3.8.18
````

#### 第 2 步：使用强制 `PATH` 运行 `configure`

这是最关键的修改。我们使用 `env PATH=$PATH` 来将您当前用户（可以正常找到 `sed` 等命令）的 `PATH` 变量传递给 `sudo` 环境。

````bash
sudo env PATH=$PATH ./configure --enable-optimizations
````

> **说明**：这个命令告诉 `sudo`，在执行 `./configure` 之前，先设置一个临时的环境变量 `PATH`，其值等于您当前 shell 的 `$PATH`。

这一次，`configure` 脚本应该就能成功运行了。

#### 第 3 步：使用强制 `PATH` 运行 `make altinstall`

为了确保万无一失，我们在执行 `make` 时也使用同样的方法。

````bash
sudo env PATH=$PATH make altinstall
````

#### 第 4 步：验证安装

安装完成后，验证 Python 3.8 是否可用。

````bash
python3.8 -V
pip3.8 -V
````

这个方法应该可以最终解决您在编译过程中遇到的所有 `command not found` 问题。