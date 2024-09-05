## <center>在Windows系统中配置Python运行环境

&emsp;&emsp;大多数Python项目依赖于特定的库或模块来正常运行。例如，一个作用于网页爬虫的项目需要依赖于`requests`库发送网络请求，而一个用于数据分析的项目则依赖于`pandas`或`numpy`等科学计算库。这些Python的第三方依赖包不会随着项目代码一起被包含在GitHub仓库中，自然，我们下载得到的项目文件中也不会包含这部分的内容。所以需要在本地的Python解释器中手动安装这个依赖环境，才能得以运行相对应的项目代码。

# 1. 使用Anaconda（推荐）

&emsp;&emsp;Anaconda 是一个流行的开源Python发行版，用于科学计算。它包含了数据科学和机器学习领域中常用的一系列工具和库。其安装的方式也非常简单。具体安装过程如下：

- **Step 1. 进入Anaconda3的官网：https://www.anaconda.com/**

&emsp;&emsp;进入后，无需登录，直接点击右上角的`Free Download`按钮进入Anaconda安装包的下载页面。注意：Anaconda为外网网站，国内网络如果打不开，可开启科学上网或稍等一会再次进行尝试。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240731163815601.png" width=60%></div>

- **Step 2. 下载Windows版本的Anaconda3**

&emsp;&emsp;同样，此页面也并不需要填写`Email Adress`等信息，直接点击`Skip registration` 跳过信息注册即可获取到接下来的下载链接。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240731163847372.png" width=60%></div>

&emsp;&emsp;Anaconda软件提供Windwos、Mac和Linux三个版本，大家可根据自己的电脑系统灵活选择。这里我们选择Windows版本的Anaconda安装包进行下载，其默认使用的Python版本为3.12版本。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240731163908685.png" width=60%></div>

&emsp;&emsp;如果网络正常，会自动弹出下载弹窗，自行选择下载路径。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240731164015309.png" width=60%></div>

- **Step 3. 安装Windows版本的Anaconda3**

&emsp;&emsp;进入安装包存放位置，直接使用鼠标双击运行安装程序，执行傻瓜式安装进程。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240731165644203.png" width=60%></div>

&emsp;&emsp;第一步会对Anaconda软件的安装情况做一下简要说明，直接点击`Next`按钮执行下一步。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240731164947801.png" width=60%></div>

&emsp;&emsp;接下来同意软件的许可协议，点击`I Agree`按钮。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240731165001053.png" width=60%></div>

&emsp;&emsp;这一步根据情况自行选择，选择哪一个都不会影响Windows当前用户的使用。其中如果选择All Users，则当前Windows系统下的所有子账户都可以使用Anaconda软件。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240731165017955.png" width=60%></div>

&emsp;&emsp;关于Anaconda3的默认安装路径强烈不建议大家进行修改，直接使用默认安装路径。如若修改，可能会导致后续的环境变量出现不可预知的问题。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240731165048667.png" width=60%></div>

&emsp;&emsp;这里强烈建议勾选`Add Anaconda3 to my_path environment variable`，这会自动设置环境变量，否则还需要后续再手动设置。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240731165213390.png" width=60%></div>

&emsp;&emsp;上述自定义配置设置好以后，耐心等待安装完成即可。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240731165239532.png" width=60%></div>

&emsp;&emsp;安装程序执行完成后，点击`Next`进入下一步骤。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240731165426233.png" width=60%></div>

&emsp;&emsp;当出现`Finish`按钮后，说明当前的电脑上已经成功安装了Anaconda环境。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240731165410115.png" width=60%></div>

- **Step 4. 启动Anaconda3进行验证**

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113013453190.png" width=60%></div>

&emsp;&emsp;根据个人情况，自行选择是否需要升级到最新版本。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113013728212.png" width=60%></div>

&emsp;&emsp;如果选择了升级的话，等待完成即可。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113013747057.png" width=60%></div>

- **Step 5. Anaconda3简要说明**

&emsp;&emsp;Anaconda Navigator 是 Anaconda 发行版中的一个图形用户界面（GUI），提供了一个直观的界面，通过这个界面，用户可以管理不同的环境、安装和更新包，以及启动各种数据科学和机器学习工具，例如 Jupyter Notebook、Spyder、RStudio 等。此外，它还提供了对 Anaconda Cloud 和其他资源的访问，使得分享工作和发现其他人的工作变得更加容易。Navigator 适合那些不习惯使用命令行界面的用户。其中比较关键的应用程序已经做了标注：

1. **Anaconda CMD.exe Prompt**：一个基于 Windows 命令行界面的工具，它预配置了 Anaconda 发行版的环境变量。使用 Anaconda Prompt，可以执行各种与 Anaconda 相关的命令，例如创建和管理 Conda 环境、安装、更新和卸载包等。这是一个非常强大的工具，特别是对于那些熟悉命令行操作的用户。

2. **Powershell Prompt**：类似于 Anaconda CMD.exe Prompt，Powershell Prompt 是另一种命令行界面，但它基于 Windows 的 PowerShell。PowerShell 是一种跨平台的任务自动化解决方案，包含命令行壳、脚本语言和配置管理框架。Anaconda 的 Powershell Prompt 也被配置为可以直接执行与 Anaconda 和 Conda 相关的操作。

3. **PyCharm**：一个流行的 Python 集成开发环境（IDE），由 JetBrains 开发。它提供了代码完成、调试、测试、版本控制等多种功能，非常适合 Python 项目的开发。

4. **Jupyter Lab**：它是 Jupyter Notebook 的下一代界面，提供了一个灵活和强大的工具集，用于交互式数据科学和科学计算。Jupyter Lab 不仅包括了 Jupyter Notebook 的所有功能，还增加了许多新特性，如更灵活的窗口布局、更好的编辑器、实时预览、终端、文件浏览器等。它支持多种类型的文档和活动，包括文本编辑器、Jupyter 笔记本、数据视图等，是一个更为综合的数据科学工作环境。

5. **Jupyter Notebook**：它是一个开源的 Web 应用程序，允许创建和共享包含实时代码、方程、可视化和叙述文本的文档。它广泛用于数据清洗和转换、数值模拟、统计建模、数据可视化、机器学习等领域。Jupyter Notebook 支持超过 40 种编程语言，包括 Python、R、Julia 和 Scala。它是一个非常流行的工具，特别是在数据科学和学术研究中。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113015601594.png" width=60%></div>

- **Step 6. 验证conda**

&emsp;&emsp;在Anaconda环境中，conda 是一个开源的包管理器和环境管理器，用于安装、运行和升级包和环境。验证方式如下：

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113015637119.png" width=60%></div>

&emsp;&emsp;点击后，会进入如下命令行终端，输入`conda --version` 查看conda版本。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113015816877.png" width=60%></div>

&emsp;&emsp;该命令会生效的原因，是因为我们在安装Anaconda3的过程中，自动添加了conda的环境变量，验证路径如下所示：

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113021653784.png" width=60%></div>

&emsp;&emsp;选择`Path`变量，进入后可查看已设置的环境变量的详细信息。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113234621097.png" width=60%></div>

&emsp;&emsp;这里显示的anaconda3的环境变量，就是在安装Anaconda程序时，由程序自动创建的配置信息。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113234644137.png" width=60%></div>

- **Step 7. 升级conda到最新版本**

&emsp;&emsp;在使用`Conda`包管理工具构建`Python`运行环境之前，强烈建议将 `Conda`包的版本升级到最新版本，这样做的原因是最新版本的 `Conda` 与其他最新的软件和库兼容性更强，比如对最新版本的Python的支持，以及与最新发布的包的兼容性，它会在解析和冲突处理方面更加精确和高效。当然，升级`Conda`包版本的方法也非常简单，只需要执行如下命令：
```bash
# 首先更新conda工具
conda update -n base -c defaults conda
# 再更新各库
conda update --all
```

&emsp;&emsp;具体操作方法如下所示：

&emsp;&emsp;首先，在Anaconda Navigator 中进入命令行终端。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113235655250.png" width=80%></div>

&emsp;&emsp;在命令行终端先更新conda工具

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113235418714.png" width==60%></div>

&emsp;&emsp;再更新各依赖包。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113235533881.png" width=60%></div>

- **Step 8. 查看Conda安装情况**

&emsp;&emsp;直接输入命令`conda --version`查看当前安装的`Conda`版本，如果安装正常，将返回确定的版本。而如果安装异常，则会出现`Commanad not found`等情况，此时则需要检查自己的前述安装步骤是否有遗漏或其他问题。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240801103634039.png" width=60%></div>

&emsp;&emsp;至此，在Windows电脑上安装配置Anaconda环境的步骤就全部完成了，接下来就可以正常使用`Conda`包管理工具来创建和执行Python的虚拟运行环境了。

# 2. 使用特定的Python版本

&emsp;&emsp;如果不想要使用Anaconda3来管理虚拟环境，可以直接在Windows系统上安装指定版本的Python包，然后再使用该版本的Python来创建虚拟环境。操作过程如下：

- **Step 1. 进入Python官网下载指定版本的Python包：https://www.python.org/**

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113020224570.png" width=60%></div>

&emsp;&emsp;自行选择Python版本，运行大模型环境，需要Python 3.10版本及以上。我这里选择Python 3.10.9 的 Windows 64位版本作为示例进行安装。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113020445451.png" width=60%></div>

&emsp;&emsp;如果网络正常，会自动弹出下载弹窗，自行选择安装程序的存储路径。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240801104308977.png" width=60%></div>

- **Step 2. 下载完成后，执行傻瓜式安装**

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240801104420737.png" width=60%></div>

&emsp;&emsp;注意：这里勾选`Add python.exe to PATH`,这会在安装过程中将Python环境设置好环境变量，否则还需要手动设置。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113020739092.png" width=60%></div>

&emsp;&emsp;等待安装完成后，点击下图所示的按钮，取消路径长度限制。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113020914499.png" width=60%></div>

&emsp;&emsp;如若安装过程一切正常，则会出现如下所示`Set up was successful`.

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113020950424.png" width=60%></div>

- **Step 3. 安装完成后，验证是否安装成功**

&emsp;&emsp;能正确输出安装的Python版本，说明安装正常。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240114112942932.png" width=60%></div>

- **Step 4. 升级pip到最新版本**

&emsp;&emsp;pip 是 Python 的官方包管理工具，用于安装和管理 Python 包。它允许用户从 Python 包索引（PyPI）中安装、升级和删除包。在创建新的虚拟环境前建议升级 pip ，新版本的 pip 会提供更好的安装性能，更准确的依赖项解析。升级命令如下：
```bash
pip install --upgrade pip

```

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240114113651456.png" width=60%></div>

&emsp;&emsp;至此，在Windows电脑上单独配置Python特定版本的操作就全部完成了，接下来就可以正常使用`pip`包管理工具来创建和执行Python的虚拟运行环境了。

# 3. 如何管理多个不同版本的Python环境

&emsp;&emsp;对于直接使用Python直接创建虚拟环境的这种方式（`2. 使用特定的Python版本`），如果需要切换python版本，则只能重新下载不同版本的Python的包，重复执行上述操作。比如我们上述安装的是Python 3.10.9，如果另外一个项目需要使用Python3.12版本，则需要重新进入https://www.python.org/ 官网中下载。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113022233131.png" width=60%></div>

&emsp;&emsp;下载安装包，并按照`2. 使用特定的python版本`中介绍的操作步骤安装到本地的电脑后，需要找到Python程序的安装位置。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240114191152285.png" width=80%></div>

&emsp;&emsp;所有Python版本的环境变量都在这里定义。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113023916132.png" width=80%></div>

&emsp;&emsp;如果想通过不同的指令，启动不同版本的Python，可以在系统的环境变量中找到指定版本的Python存放位置。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113022634261.png" width=80%></div>

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113022851310.png" width=80%></div>

&emsp;&emsp;默认所有版本的python执行文件都是python.exe，可以进入指定文件夹中看到。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113023139809.png" width=80%></div>

&emsp;&emsp;如果想区分不同版本Python，并在终端可以使用，可以通过如下方式添加版本编号。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113023459818.png" width=80%></div>

&emsp;&emsp;启动验证。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20240113024151625.png" width=80%></div>

&emsp;&emsp;通过这种方式来灵活的管理一台机器上的多个Python环境。
