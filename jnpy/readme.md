
# jnpy 相关说明

* 在当前目录下建立.vntrader文件夹， 如果不建立， 会在/home/fangyang自动建立该文件夹
* psutil pip安装失败, 可以用conda install 安装
* ta-lib pip安装失败, 升级setuptools等工具
* psycopg2 做加密货币的, 不用安装

# ubuntu 18 + anaconda 3.7 venv
>
>install.sh脚本中这里在 /tmp 将下载的ta-lib-0.4.0解压放进ta-lib目录下 
function install-ta-lib()
{
    pushd /tmp
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
    tar -xf ta-lib-0.4.0-src.tar.gz
    cd ta-lib
    ./configure --prefix=$prefix
    make -j
    make install
    popd
}

但是， 没有安装成功，提示gcc什么错误, 按照以下步骤成功安装（注意要在py3.7的venv下）
>cd /tmp/ta-lib
>
>./configure --prefix=/usr
>
>make
>
>sudo make install
>
>cd ..
>
>pip install TA-Lib

之后如果不行， 重新跑一遍 install.sh 脚本。 但是ctp接口这里貌似还是无法import找到；
根据[vnpy issue](https://github.com/vnpy/vnpy/issues/2188)

*2.0中改为使用项目的setup.py文件中的配置来build，无需脚本了，请查看：*

python setup.py build
python setup.py install
当我们运行vnpy-2.0.9/example/client_server/server/run_server.py文件的时候会报上面的错误。ctp接口在没有build的状况下直接安装了vnpy所致。

解决方法，在vnpy-2.0.9目录下运行

python setup.py build

进行编译，在生成的/build/lib.linux-x86_64-3.7/vnpy/api/ctp目录下找到两个.so文件，
vnctpmd.cpython-37m-x86_64-linux-gnu.so
和vnctptd.cpython-37m-x86_64-linux-gnu.so，
把它们粘贴到/vnpy-2.0.9/vnpy/api/ctp目录下即可。

之前因为在manjaro上面对这2个.so文件做了版本控制， 所以需要将其删除， 然后重新build， 然后粘贴过来

最后记得，、要不连接交易所的时候报错
sudo locale-gen zh_CN.GB18030

## 连接CTP交易所的时候报错
```
terminate called after throwing an instance of 'std::runtime_error'
  what():  locale::facet::_S_create_c_locale name not valid
```
原因：接口库文件在接口调用时有返回GBK字段，但是由于本地机器没有安装相应的语言包支持。所以程序出错崩溃。

解决方法：安装中文语言包支持
```
$sudo dpkg-reconfigure locales

Generating locales (this might take a while)...
en_US.UTF-8... done
zh_CN.GB2312... done
zh_CN.GB18030... done
zh_CN.GBK... done
zh_CN.UTF-8... done
Generation complete.
```

## 交易服务器登录失败
```
/sys/firmware/dmi/tables/smbios_entry_point: Permission denied
/dev/mem: Permission denied
/sys/firmware/dmi/tables/smbios_entry_point: Permission denied
/dev/mem: Permission denied
交易服务器登录失败，代码：3，信息：CTP:不合法的登录
```
解决办法：

```
sudo chmod 777 /sys/firmware/dmi/tables/smbios_entry_point /dev/mem /sys/firmware/dmi/tables/DMI /dev/sda
```
如果不存在 /dev/sda 执行如下命令：
```
sudo chmod 777 /sys/firmware/dmi/tables/smbios_entry_point /dev/mem /sys/firmware/dmi/tables/DMI
```

