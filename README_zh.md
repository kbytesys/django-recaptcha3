# Django reCaptcha v3 [![Build Status](https://travis-ci.org/kbytesys/django-recaptcha3.svg?branch=master)](https://travis-ci.org/kbytesys/django-recaptcha2)
----

这个集成应用在Django上为 <a href="https://developers.google.com/recaptcha/intro">Google reCaptcha v3</a> 实现了一个 recaptcha 字段。 

**警告：** 此软件包与 django-recaptcha2 **不兼容**

----

## 如何安装

通过 pip 安装所需的软件包 （或下载源码自行安装）：

```bash
pip install django-recaptcha3
```

然后将 django-recaptcha3 添加到你 Django 项目配置文件的 installed apps 中：

```python
INSTALLED_APPS = (
    ...
    'snowpenguin.django.recaptcha3',
    ...
)
```

并将您的 reCaptcha 私钥和公钥添加到你 Django 项目的 settings.py 中并设置 RECAPTCHA_DEFAULT_ACTION （recaptcha默认操作名）和 RECAPTCHA_SCORE_THRESHOLD （recaptcha分数阈值）：

```python
RECAPTCHA_PRIVATE_KEY = 'your private key'
RECAPTCHA_PUBLIC_KEY = 'your public key'
RECAPTCHA_DEFAULT_ACTION = 'generic'
RECAPTCHA_SCORE_THRESHOLD = 0.5
# 如果您需要从其它地方加载 reCaptcha，而不是 https://google.com
# （比如：绕过防火墙限制）， 你可以指定要使用的代理。
# RECAPTCHA_FRONTEND_PROXY_HOST = 'https://recaptcha.net'

```

如果你需要为你的 django 项目所用到的的域名创建 apikey ，则可以访问此<a href="https://www.google.com/recaptcha/admin">网站</a>。

## 用法 
### 表单和控件
您可以使用此应用程序提供的字段便捷地创建一个包含 reCaptcha 的表单：

```python
from snowpenguin.django.recaptcha3.fields import ReCaptchaField

class ExampleForm(forms.Form):
    [...]
    captcha = ReCaptchaField()
    [...]
```

如果你不想用 settings.py 中设置的私钥，可以在字段中添加 "private_key" 参数来指定私钥。

### 使用模板
您可以使用一些模板标签来简化 reCaptcha 的使用：
 
* recaptcha_init: ：为 reCaptcha api 添加 script 标签，您必须将此标签放在 "head" 元素中的某个位置
* recaptcha_ready: ：api script 加载完毕时执行函数
* recaptcha_execute: 启动 reCaptcha 检查，并从 django forms 中的 api 设置 token 。 token 有效时间为120秒，此时间过后会自动重新生成。 
* recaptcha_key: 如果要在模板中手动使用 reCaptcha 而不通过 forms ，则需要 sitekey（又名 public api key）。此标签将返回带有配置公钥的字符串。
  
您可以照常使用该表单。

### 示例
#### Simple

只需使用 reCaptcha 字段创建一个表单，然后遵循以下模板示例：

```django
{% load recaptcha3 %}
<html>
  <head>
      {% recaptcha_init %}
      {% recaptcha_ready action_name='homepage' %}
  </head>
  <body>
    <form action="?" method="POST">
      {% csrf_token %}
      {{ form }}
      <input type="submit" value="Submit">
    </form>
  </body>
</html>
```

#### Custom callback

The callback 可用于允许通过 ajax calls 或其他方式使用从 api 获得的 token 

```django
{% load recaptcha3 %}
<html>
  <head>
      <script>
          function alertToken(token) {
              alert(token);
          }
      </script>
      {% recaptcha_init %}
      {% recaptcha_ready action_name='homepage' custom_callback='alertToken' %}
  </head>
  <body>
    <form action="?" method="POST">
      {% csrf_token %}
      {{ form }} // 表单中的 reCaptcha 字段
      <input type="submit" value="Submit">
    </form>
  </body>
</html>
```

#### Multiple render example

不需要额外的设置您便可以渲染多个 reCaptcha ：

```django
{% load recaptcha3 %}
<html>
  <head>
      {% recaptcha_init %}
      {% recaptcha_ready action_name='homepage' %}
  </head>
  <body>
    <form action="?" method="POST">
      {% csrf_token %}
      {{ form1 }} // 表单1中的 reCaptcha 字段
      <input type="submit" value="Submit">
    </form>
    <form action="?" method="POST">
      {% csrf_token %}
      {{ form2 }} // 表单2中的 reCaptcha 字段
      <input type="submit" value="Submit">
    </form>
  </body>
</html>
```

#### Bare metal!

您可以直接使用 javascript ，只需记得为表单中的隐藏字段设置正确的值

```django
<html>
  <head>
      <script src="https://www.google.com/recaptcha/api.js?render=reCAPTCHA_site_key"></script>
      <script>
        grecaptcha.ready(function() {
          var grecaptcha_execute = function(){
            grecaptcha.execute('reCAPTCHA_site_key', {action: 'homepage'}).then(function(token) {
              document.querySelectorAll('input.django-recaptcha-hidden-field').forEach(function (value) {
                  value.value = token;
              });
              return token;
            })
          };
          grecaptcha_execute()
          setInterval(grecaptcha_execute, 120000);
        });
      </script>
  </head>
  <body>
    <form action="?" method="POST">
      {% csrf_token %}
      {{ form }}
      <input type="submit" value="Submit">
    </form>
  </body>
</html>
```


## 设置

如果要设置 recaptcha 的 score ，则需要调整 bot score 阈值。

django-recaptcha3 可以按照下方示例调整 bot score 阈值。阈值的取值区间为 0~1，默认值为 0。

1 表示有极大可能是人类，0 则表示很可能是机器人，当用户访问时被评分的值小于您设置的值时用户将被拦截，谷歌建议设置 0.5。

```python
from snowpenguin.django.recaptcha3.fields import ReCaptchaField

class ExampleForm(forms.Form):
    [...]
    captcha = ReCaptchaField(score_threshold=0.5)
    [...]
```

## 测试
### Test unit support
您无法在测试中模拟 api 调用，但是可以禁用 recaptcha 字段来进行测试工作。

只需在测试中设置 RECAPTCHA_DISABLE env 变量即可：

```python
os.environ['RECAPTCHA_DISABLE'] = 'True'
```

警告：您可以使用任何单词代替 "True" ，clean 函数将仅检查变量是否存在。

### Test unit with recaptcha3 disabled
```python
import os
import unittest

from yourpackage.forms import MyForm

class TestCase(unittest.TestCase):
    def setUp(self):
        os.environ['RECAPTCHA_DISABLE'] = 'True'

    def test_myform(self):
        form = MyForm({
            'field1': 'field1_value'
        })
        self.assertTrue(form.is_valid())

    def tearDown(self):
        del os.environ['RECAPTCHA_DISABLE']
```
