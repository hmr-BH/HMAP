# AI 屎山信号清单（ai-slop-signals）

本文件是评估维度 4「AI 屎山痕迹」的取证清单。每条信号给出识别方法、正例（人类可维护的写法）与反例（屎山写法）、扣分指导。

**判断原则**：不是"出现过 AI 味就扣分"，而是**"这些痕迹是否已经影响人类维护"**。零星残留（一两个未使用导入）属于正常开发残留；成规模、集中污染、影响阅读和修改的才是屎山。

---

## 信号 1：幻觉注释（最严重的信号）

**识别**：注释里提到的函数/文件/参数/行为，在代码里根本不存在，或与事实矛盾。典型是 AI 生成后代码被改过而注释没跟着改，或 AI 编造了它以为存在的 API。

**反例**：
```python
# 利用缓存加速（注意：此处调用了 get_cached_data，配置见 redis_client）
data = fetch_from_db()  # get_cached_data 早已被删，redis_client 从未存在
```
注释引用了不存在的函数和配置对象，误导读者去寻找并不存在的东西。

**正例**：
```python
# 直接查库不缓存：该接口调用频率极低（日均个位数），不值得为它引入缓存层
data = fetch_from_db()
```
注释讲清了"为什么不做缓存"这个权衡，与代码完全一致。

**扣分**：出现 1 处幻觉注释即视为重大信号，该维度至少压到 70 以下；多处（≥3 处）集中出现压到 45 以下。

---

## 信号 2：复述型注释（只描述操作，不讲述原因）

**识别**：注释等于把代码翻译成自然语言，没有增加任何信息。AI 生成代码的典型特征，随处可见就是污染。

**反例**：
```python
# 循环遍历列表中的每一项
for item in items:
    # 如果 x 大于 10 则执行加法
    if x > 10:
        # 把结果加到总和中
        total += item.value
```

**正例**：
```python
for item in items:
    if x > 10:
        # 阈值取 10：低于此值的记录是噪声数据，不参与求和
        total += item.value
```

**识别技巧**：逐行注释出现频率高、且每行注释都能从代码本身秒懂，即可判定为复述型。用 Grep 统计注释密度（注释行数 / 总行数），密度异常高（>30%）且多为短注释时重点抽查。

---

## 信号 3：死代码与未使用导入

**识别**：
- 未使用的导入：`import`/`use`/`require` 声明了但全文无引用（用 Grep 对每个导入名全文检索）。
- 定义了但从未被调用的函数/类/常量（对项目内符号做引用计数）。
- 被注释掉的大段代码块（`/* ... */` 或 `# ...` 整块保留在源码里）。

**反例**：
```python
import os, sys, json, random, hashlib  # 其中 sys/random/hashlib 全文从未使用

def legacy_parse(data):
    """旧版解析逻辑，已废弃"""
    # ... 数百行从未被任何地方调用的代码
```

**正例**：无未使用导入；废弃逻辑直接删除，用 git 历史保留。

**扣分**：未使用导入零星出现（每文件 ≤2 个）属正常残留；整段死函数/死分支成规模出现（≥3 处）或注释掉的整块代码出现在交付源码中，压到 70 以下。

---

## 信号 4：过度工程（为简单问题套模式）

**识别**：问题本身用 10 行能解决，却套上工厂/抽象基类/观察者/多层接口。AI 常把"设计模式"当装饰，生成一批没有调用方、只为"显得正规"的类。

**反例**：
```python
class MessageSender(Protocol):
    def send(self, msg: str) -> None: ...

class ConsoleSender:
    def send(self, msg: str) -> None:
        print(msg)

class SenderFactory:
    @staticmethod
    def create(kind: str) -> MessageSender:
        if kind == "console":
            return ConsoleSender()
        raise ValueError(f"unknown: {kind}")

def main():
    sender = SenderFactory.create("console")
    sender.send("hello")
```
为一句 `print` 引入接口 + 工厂 + 协议，全项目只有一个调用方，且将来不会有多实现。

**正例**：
```python
def send_message(msg: str) -> None:
    print(msg)  # 当前只有控制台输出一种实现，等有第二种再抽象
```

**扣分**：一处装饰性抽象（无第二实现、无扩展预期）即视为信号；同一项目多处此类"模式套壳"（≥3 处）压到 70 以下。

---

## 信号 5：无效抽象与不必要的间接层

**识别**：函数/类只是"转一手"，把调用转发给另一个函数，中间没有任何逻辑、校验或转换，纯增阅读负担。

**反例**：
```python
def get_user_name(user_id):
    return _fetch_user(user_id).name

def _fetch_user(user_id):
    return database.query_user(user_id)
```
`get_user_name` 与 `_fetch_user` 之间没有任何额外逻辑，纯转发。

**正例**：
```python
def get_user_name(user_id):
    # 加缓存：用户信息读多写少，避免每次查库
    if user_id in _name_cache:
        return _name_cache[user_id]
    name = database.query_user(user_id).name
    _name_cache[user_id] = name
    return name
```
有实际职责（缓存）的包装才是正当的间接层。

**识别技巧**：对每个函数检查函数体——若函数体只是"调用另一个函数并把结果原样返回"且没有边界处理，即为无效转发。深链转发（A→B→C→D，每层都无逻辑）是高发区。

---

## 信号 6：无意义防御（吞异常、永假条件）

**识别**：
- `except Exception` / `catch (Exception)` 里是空块、`pass`、`print(...)`、`// do nothing`，错误被无声吞掉。
- 对不可能为空的变量做空值检查；对 `range` 步进做符号判断；`if x != None and x is not None` 式重复判断。
- 为了"怕出错"到处加 try/catch，把本该暴露的 bug 藏起来。

**反例**：
```python
try:
    result = risky_call()
except Exception:
    pass  # 不处理，出错就静默，调用方永远不知道失败了

if data is not None and data != None:  # 两个检查等价，且 data 一定非空
    ...
```

**正例**：
```python
try:
    result = risky_call()
except TimeoutError:
    # 超时是可预期的：走重试，重试仍失败则向上抛，让调用方决定
    result = retry(risky_call, times=3)
```

**扣分**：吞异常 1-2 处属常见惰性；成规模（≥3 处吞掉真实错误）或出现"空块 catch 包裹关键业务逻辑"压到 70 以下。

---

## 信号 7：拼凑感与风格突变

**识别**：同一文件（甚至同一函数）内多种风格并存——命名大小写混用、缩进方式混用、有时有注释有时没有、代码语言混合；或同一个问题在不同文件里用了完全不同的解法。这是 AI 多次生成拼接的典型痕迹。

**反例**：一个 Python 文件里同时出现 `fetch_data`、`FetchData`、`fetchData` 三种命名；某处用 `assert` 校验、另一处用 `if ... raise`、第三处直接不校验；注释有时英文有时中文。

**正例**：全文件统一命名规范、统一的错误处理套路、统一注释语言。

**识别技巧**：用 Grep 对项目内同类符号做命名风格统计；同文件中风格互斥（两种以上命名规范）即可判定。

---

## 信号 8：复制粘贴变体（DRY 破产）

**识别**：多段逻辑几乎相同、只有少量参数不同的代码，出现在不同文件或同一文件多处。比死代码更隐蔽——每份变体都在被调用，所以不报错，但改 bug 要改 N 处。

**反例**：
```python
# 文件 A
def calc_price_a(items, tax_rate):
    total = 0
    for item in items:
        total += item.price
    return total * (1 + tax_rate)

# 文件 B（逻辑相同，仅变量名不同）
def compute_price_b(list_of_goods, rate):
    sum = 0
    for goods in list_of_goods:
        sum = sum + goods.price
    return sum * (1 + rate)
```

**正例**：
```python
def calc_price(items, tax_rate):
    """按税率计算总价，供订单与购物车两处复用"""
    total = sum(item.price for item in items)
    return total * (1 + tax_rate)
```

**识别技巧**：对比相似代码块（函数体结构一致、仅命名/常量不同）；或同语言同目录内函数名高度相似（`getX`/`getX2`/`fetchX`）时重点抽查。

---

## 信号 9：AI 模板腔（语言层面的机器人味）

**识别**：
- 文档注释全是"该函数用于实现……""此方法负责处理……""以下是……"这类空转的模板句。
- 变量名高度模板化：`data`、`result`、`item`、`content`、`object` 泛滥。
- 大段凑字数的"辅助说明"，与实际行为无关。
- 每个函数开头都来一段万能开场白。

**反例**：
```python
def process_data(data):
    """该函数用于处理传入的数据，并返回处理后的结果。"""
    result = []
    for item in data:
        # 遍历每个数据项
        result.append(transform(item))
    return result
```

**正例**：
```python
def process_data(rows):
    """把原始行转成前端要的字段结构；返回空表时调用方直接展示空态。"""
    return [transform(item) for item in rows]
```

**识别技巧**：Grep 高频模板词（"该函数用于"、"该方法负责"、"以下代码"、"旨在"）统计密度。

---

## 信号 10：命名与功能不符

**识别**：函数名、变量名、文件名暗示的行为与实际实现不一致。比命名差更糟——它直接误导读者。

**反例**：
```python
def get_total(items):
    """实际返回平均值"""
    return sum(items) / len(items)
```
`fetch_data` 实际上会写入数据库；文件名 `utils.py` 里装的却是全部业务逻辑。

**识别**：抽查函数名后核对函数体行为；文件名与目录结构对照实际内容。

---

## 信号 11：过度拆分 / 过度合并

**识别**：
- 过度拆分：几十个只有 3-5 行的小文件/小函数，每个都起一个抽象名字，读者要在文件之间反复跳转才能拼出完整逻辑。
- 过度合并：几千行的单文件/单函数，所有逻辑堆在一起，无任何切分。

两者并存（既有碎片文件又有巨型函数）是更强的拼凑信号。

**反例**：`utils.py` 有 3000 行、同时又存在 `helper_a.py`（12 行）、`helper_b.py`（8 行）、`helper_c.py`（15 行）这样为了"模块化"而碎的碎片。

**识别**：统计文件行数分布，找出超大文件与超小文件；统计函数行数，找出超长函数。

---

## 信号 12：文档与代码脱节（README 撒谎）

**识别**：README 声称的功能/架构/目录结构，与代码实际不符；README 明显是模板生成（含"TODO 待完善"、"此处替换为你的项目名"等占位）；文档描述的 API 与代码签名不一致。

**反例**：README 说"支持用户注册与登录"，代码里根本没有认证相关代码；README 目录说明指向不存在的目录。

**扣分**：README 是模板占位或与代码严重脱节时，同时扣"注释文档"维度（维度 2）与本维度。

---

## 综合判定指导

| 信号密度 | 维度 4 参考分 | 对应总档位影响 |
|---------|--------------|---------------|
| 几乎无信号（≤1 处零星） | 85-95 | 总分落在 80+ 档 |
| 个别信号（2-4 处，不集中） | 70-80 | 总分落在 70-80 档 |
| 成规模（≥5 处，或一处集中污染） | 45-60 | 总分明显下压 |
| 泛滥（每抽样文件都命中 ≥2 类信号） | ≤40 | 总分很可能落到 50 以下 |

**注意**：以上分数是"该维度独立参考"，总分还要综合其余四个维度。一处集中污染（如单个 200 行函数里同时命中 复述注释 + 死代码 + 吞异常 + 命名不符）比四处分散信号更说明问题，扣分更狠。

**取证模板**：报告里每条屎山发现按此格式写——
`文件:行号 —— 信号 X（<信号名>）：<具体描述>`
