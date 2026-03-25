# 第一集 Context Engineering 基本概念 (全内容对比版)

> 自动生成的带全部图片的逐字稿对应文档。如果图片有外部链接，也会一并提取。


![Slide 1](../../bilibili_video/slides_p1/slide_0001.jpg)

好,各位同学大家好啊,我们就开始来上课吧 今天呢,我们要继续来讲AI Agent 那今天的课程呢,还是比较科普性的 那我们分成三个段落 第一段呢,我们来讲AI Agent背后的核心技术

我们比较系统化的来讲Context Engineering 然后第二段呢,我们来讲AI Agent之间的互动 然后最后我们来讲AI Agent对于我们未来的工作 可能造成什么样的冲击 好,那我们就先从AI Agent的核心技术

Context Engineering开始讲起 那等一下这段课程呢,也许你听了会觉得似曾相似 因为很多呢,Context Engineering的技术 都已经在这个OpenCloud里面被试作 那今天这段课程比较不一样的地方是

会引用大量的论文 那你发现这些论文都是非常新的论文 几个月前半年前的论文 而这些技术都已经被试作在OpenCloud里面 所以上周其实很多技术我们都已经有提到

那只是今天呢,再从另外一个角度来谈Context Engineering 好,那在谈Context Engineering之前呢 这边有一个开场 我们还是跟大家复习一下为什么需要Context Engineering 那我们知道语言模型呢,就是在做文字接龙

你给它一个输入,给它一个Pump 它就接一段话出来 那人类给语言模型一个输入 语言模型给人类一个回应 那这个回应不一定是一句话


![Slide 5](../../bilibili_video/slides_p1/slide_0005.jpg)


![Slide 6](../../bilibili_video/slides_p1/slide_0006.jpg)


![Slide 7](../../bilibili_video/slides_p1/slide_0007.jpg)


![Slide 8](../../bilibili_video/slides_p1/slide_0008.jpg)


![Slide 9](../../bilibili_video/slides_p1/slide_0009.jpg)

它可能是一个使用工具的指令 那这个使用工具的指令 可能会去驱动环境里面的某一个程式 被执行 然后得到工具的输出

那当我们要把工具的输出传给语言模型 告诉它这个工具执行的结果的时候 你不能够只给它工具的输出 大家要记得语言模型是活在当下的 它只管现在的输入


![Slide 10](../../bilibili_video/slides_p1/slide_0010.jpg)


![Slide 11](../../bilibili_video/slides_p1/slide_0011.jpg)

**幻灯片引用链接:**
- [https://arxi](https://arxi)

它不管你之前曾经给它过什么 所以当你得到工具一的输出的时候 你要把之前人类给的命令 语言模型自己呢 操控工具的指令

加上工具的输出 全部接在一起 丢给语言模型 那有的同学可能会说 这边不是输入三个东西吗

语言模型不是应该回 三个回应 你误会这个投影片的意思了 这边是这三段话被接成一段 对语言模型来说

它看到的就是一串非常长的输入 然后它再给一个回应 比如说它决定使用另外一个工具 然后它在得到工具二的输出 工具二的输出要丢给语言模型的时候

切记不能只给它工具二的输出 之前发生所有的事情 串成一串非常长的输入 再丢给语言模型 同样的步骤就反复下去

语言模型说它要使用工具三 得到工具三的输出 把一串非常长的输入传给语言模型 那这里会遇到的难点就是语言模型的输入长度是有限的 它不能够吃无限长的输入

这就是为什么我们需要AI agent AI agent就是拦截在语言模型跟人类 或者是语言模型要执行的环境之间的一个界面 它就像是语言模型的手门人 语言模型的经纪人

他决定语言模型会看到什么 所以来自外界的输入会经过AI agent 那这个AI agent不一定是OpenCloud OpenCloud只是AI agent的其中一个例子 那今天OpenCloud还非常的原始

你可以想成它是初代的AI agent 它也许再过几年以后 我们再回头看OpenCloud 就好像今天你拿着iPhone 去看过去的Nokia手机一样的感觉

我们现在看到的只是AI agent的原型 以后一定还会有更多的进展 那OpenCloud做的事情或AI agent做的事情 就是选择给语言模型看的内容 所以语言模型真正看到的是

OpenCloud AI agent筛选过的长度合适的输入 那这个输入它不能太长 因为语言模型它的输入就是有上限 但也不能够太短 如果太短语言模型就不知道

刚才发生了什么事 就没有办法正确的做接融 所以对AI agent来说 他要做的事情其实非常的复杂 他需要产生一个长度合适的输入

不能太长也不能太短 而这个AI agent帮语言模型 管理它的输入 让输入的长度是合适的这件事情 就叫做Context Engineering

刚才是概念性的介绍Context Engineering 如果我们今天要用比较程式语言的方法 来描述它的话 可能看起来像是这样子的 现在左边这段程式码

是没有做Context Engineering的状况 其实没有做Context Engineering的时候 你可以想成语言模型跟外界的互动 就是一个4回圈 那这个4回圈是从1到无限大

这个1要执行多少个step 那这个取决于你想要让语言模型运作多久 你想要让这个AI运作多久 那我们希望它永远地执行下去 执行到天荒地老

所以这边放一个无限大 然后呢 这边会有一个初始的输入 那这个可能就是你给语言模型的指令 那今天这个指令甚至可以就是一个非常high level的目标

比如说成为YouTuber 或者是跟鲁夫一样 就是成为海贼王 然后他就去做他自己该做的事情 然后这个我们把输入叫做I

第一个输入我们叫做I1 然后呢 我们用C来表示现在所有环境中发生的事情 那这个我们通常就叫做Context 然后用C来表示

那最开始的时候呢 C是空的 那在每一个4回圈里面会做的事情就是 把之前发生的所有事情CT 加上现在目前的输入叫做IT

它可能是人对语言模型说的一句话 它可能是语言模型执行某个工具后的结果 总之是某一个现在发生的事情 现在要给语言模型的输入 把IT跟CT接起来给语言模型

它给你一个回应叫做OT 然后接下来就把IT跟OT都接到当才的Context CT后面 我们更新我们的Context变成CT加1 这是没有做Context Engineering的状态 那如果有做Context Engineering呢

你其实唯一改变的只有最后这一行程式 其他部分运作的都还是一样的 语言模型吃一个输入吃一个Context 得到新的输出 但是我们现在不是直接把输入跟输出

接到语言模型的Context上 我们可能做了一个比较复杂的操作 我们把比较复杂的操作用大F来表示 那我们现在还没有仔细说明这个复杂操作是什么 你可以在这边定义各式各样

自己开发各式各样复杂的操作 把Context刚才的输入刚才的输出 转换成新的Context 叫做CT加1 然后CT加1呢

在下一个4回圈的时候 会被当作语言模型的输入 那至于这个F要做什么 那就要问你自己 这个就是Context Engineering

也就是一个AI Agent要做的事情 那AI Agent这个Context Engineering 在那个大F里面会做什么样的事情呢 接下来我们就来举几个例子 一个最需要做的事情就是压缩

因为之所以要做Context Engineering 最核心的需求就是语言模型的输入 不能够太长 所以那个大F里面 最重要的一个功能就是压缩

把本来很长的历史记录把它压短 那怎么压短呢 上周在最后课程结尾的时候 我们有讲说这个龙虾里面呢 是内建这个Compaction的功能的

那它做的事情 其实说穿了也不值钱 就把整个历史记录里面 扣掉System Pump的部分 比较久远的历史记录

通过某一个语言模型 然后把它变成摘要 所以省来很长的历史记录就变成了一段简短的摘要 然后再继续去接上新的资讯 这个是龙虾做的事情

那其实上周呢 在课程快结束的时候 我们也说 龙虾其实还有别的处理压缩的方式 比如说有一个非常简单粗暴的方式是

如果呢 某一段文字 它原来是某一个工具的输出 那有时候工具输出 它会输出非常长篇大论的东西


![Slide 12](../../bilibili_video/slides_p1/slide_0012.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2508.21433](https://arxiv.org/abs/2508.21433)


![Slide 13](../../bilibili_video/slides_p1/slide_0013.jpg)

**幻灯片引用链接:**
- [https://manus.im/blog/Context-Engineering-for-Al-Agents-Lessons-from-Building-Manus](https://manus.im/blog/Context-Engineering-for-Al-Agents-Lessons-from-Building-Manus)
- [https://](https://)


![Slide 14](../../bilibili_video/slides_p1/slide_0014.jpg)

**幻灯片引用链接:**
- [https://manus.im/blog/Context-Engineering-for-Al-Agents-Lessons-from-Building-Manus](https://manus.im/blog/Context-Engineering-for-Al-Agents-Lessons-from-Building-Manus)
- [https://arxiv.oig/ans/251](https://arxiv.oig/ans/251)


![Slide 15](../../bilibili_video/slides_p1/slide_0015.jpg)

**幻灯片引用链接:**
- [https://rickandmorty.fandom.com/wiki/Morty%27s_Mind_](https://rickandmorty.fandom.com/wiki/Morty%27s_Mind_)


![Slide 16](../../bilibili_video/slides_p1/slide_0016.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2504.19413](https://arxiv.org/abs/2504.19413)


![Slide 17](../../bilibili_video/slides_p1/slide_0017.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2504.19413](https://arxiv.org/abs/2504.19413)


![Slide 18](../../bilibili_video/slides_p1/slide_0018.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2502.12110](https://arxiv.org/abs/2502.12110)
- [https://arxiv.org/abs/2504.19413](https://arxiv.org/abs/2504.19413)
- [https://arxiv.org/abs/2506.06326](https://arxiv.org/abs/2506.06326)


![Slide 19](../../bilibili_video/slides_p1/slide_0019.jpg)

那把那一段长篇大论 改成这里曾经有个工具的输出 就结束了 那上周讲到这边的时候 我看我的同学笑了

你可能觉得 这个什么烂方法 这个方法真的会有用吗 神奇的事情是 这个方法还真的有用

那这个就是引用之一篇 去年年终的论文 有人就尝试在SWE Bench上面 比较用语言模型做压缩 还有单纯把工具的输出换成

这里曾经有个工具的输出 这两个方法 它们在表现上有什么样的差异 那这边这些实验呢 是做在SWE Bench上面

SWE啊 就是Software Engineering的缩写 就是要让语言模型 去做一些平常软体工程师在做的事情 那在SWE Bench里面

语言模型要解的问题就是 给它一个GitHub Repo 给它一个issue 然后它要去把这个GitHub Repo的这个issue呢 把它解掉

就一般软体工程师在做的事情 虽然非常有挑战性 不过今天很多语言模型 在这样有挑战的任务上面 都可以做得非常的不错

那这边就是尝试了 各式各样不同的语言模型 纵轴呢 是正确率 横轴呢

它这边的单位是用那个美金 你就想成是 我们今天在整个解问题的过程 在Fix这个issue的过程 用了多少的Token

花了多少的钱 付出了多少的成本 然后那黑色的点呢 它这边叫做Role Agent 也就是没有做任何的压缩


![Slide 20](../../bilibili_video/slides_p1/slide_0020.jpg)

反正环境里面发生什么事情 就通通跌到你的历史记录里面去 那这个时候你会发现 虽然在多数的情况下 Role Agent都表现得不错

但是相较于其他方法 它会耗费更多的Token 耗费更多的成本 才能解决问题 那这个红色的正方形代表的是


![Slide 21](../../bilibili_video/slides_p1/slide_0021.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2510.00615](https://arxiv.org/abs/2510.00615)


![Slide 22](../../bilibili_video/slides_p1/slide_0022.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2510.00615](https://arxiv.org/abs/2510.00615)


![Slide 23](../../bilibili_video/slides_p1/slide_0023.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2510.00615](https://arxiv.org/abs/2510.00615)

拿一个语言模型 对上下文进行压缩 如果今天上下文太长了 就用个语言模型进行压缩 那你得到的是红色这一个点

那你发现红色这个点 其实跟黑色这个点 多数的时候比起来是差不多的 所以用LLN做压缩 其实跟没有做压缩

表现在SWE Bench上面 差别没有非常大 代表这个压缩 其实是蛮有效的 但是一个神奇的地方

是这个三角形 这个三角形呢 这篇论文里面叫 Observation Masking 那其实就是我刚才讲的

把工具的输出换成 这边曾经有个工具的输出 那你发现三角形的表现 很多时候跟LLN summary的表现 其实是差不多的

也就是你与其去呼叫 一个语言模型做摘要 跟你直接把今天 Agent使用某个工具的输出 直接换成这里曾经

有个工具的输出 结果表现是差不多的 它并不会真的比LLN summary好 但是LLN summary 并没有在所有的case

都稳定的比Observation Masking好 然后呢多数时候啊 当然有做压缩 都是比较省钱的 但是你会发现

在这个例外上面 有做压缩 没有比较省钱 那作者其实也提供了一个解释啦 他说这是因为发生了一个叫做

轨迹延长的现象 当你做压缩以后 当然你的上下文变短了 但是因为有一些步骤就不见了 所以对一个语言模型来说

他觉得 我刚才到底执行过这个工具了吗 还没有吗 他重复做了刚才已经做过的事 所以变成他执行的步骤

变多了 虽然输入语言模型的 content变短 但他执行的步骤变多了 所以最后结一个问题

所耗费的token 其实就没有下降 好 那我们刚才讲了两个不同的压缩方式 那你可能问说

那实际上到底哪一个比较好呢 当然你可以两个同时执行 是在同篇论文里面 他最后提出来的方法就是 不同的压缩方法

只可以同时执行的 那他最后释出来呢 最好的策略就是 在前期的时候 先用这个observation masking的方法

把工具的输出换掉 把工具的输出缩短 但是这一招呢 终究会让你的context越来越长 因为就算你只是把工具的输出换成一句

这里曾经有个工具的输出 你的context最终还是会越来越长 所以长到某个地步以后 再用summarization的方式 一次把非常长的输入

直接压缩压短 那把这两个方法同时使用 可以得到最好的结果 好那做完压缩以后 这边要留一个句子

代表他曾经被压缩过 但这个句子应该要留什么呢 与其放一句话说 这边曾经有个工具的输出 换别的字眼

放别的符号 会不会更有效呢 所以在后来的论文里面 有人就说 那我们能不能够在这边

放一个连结 放一段记录 说这个工具的输出 详见log1.txt 那你就真的把这个工具的输出

存到你的硬碟里面 存成一个档案 叫log1.txt 这样算之后呢 可能多数的时候

语言模型都不会再 回来看这个log1.txt里面有什么 因为多数的时候 工具的输出可能没有那么重要 很多时候工具的输出可能是

执行read的 然后去读了一篇论文 然后把整篇论文的内容露了进来 那可能你根本不需要整篇论文的内容 你只需要论文的其中一段

只需要它的某一个摘要 所以这些内容不需要一直存留在你的上下文里面 但是如果你不做压缩的话 直接执行工具 这一些非常长篇大论的文章

或非常长的程式码 就会一直存留在你的上下文中 所以你可以把这一些内容 存到某一个档案里面 它就从你的这个语言模型的输入里面消失了

语言模型输入里面就只留下一句话 详见log1.txt 那如果语言模型有一天 它真的很需要知道 这个工具当初到底输入了什么


![Slide 24](../../bilibili_video/slides_p1/slide_0024.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2510.00615](https://arxiv.org/abs/2510.00615)


![Slide 25](../../bilibili_video/slides_p1/slide_0025.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2510.06727](https://arxiv.org/abs/2510.06727)


![Slide 26](../../bilibili_video/slides_p1/slide_0026.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2510.06727](https://arxiv.org/abs/2510.06727)


![Slide 27](../../bilibili_video/slides_p1/slide_0027.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2509.23586](https://arxiv.org/abs/2509.23586)

输出了什么 那这个时候 它可以再执行一个工具 它可以执行read这个指令 去log1.txt里面

把它需要的内容再读取出来 它就可以重拾它的记忆 这就让我想到那个rick&multi里面的其中一段 这是第三季的其中一段 就是有一天multi发现

他家有一个地下室 他爷爷rick呢 把他很多的记忆 通通都存在这个地下室里面 他的每一个记忆

就存在一个一个管子里面 那多数都是multi感到难堪的记忆 比如说他不小心害死了一个人等等 但也有一些呢 是rick本身觉得难堪的记忆

比如说他发音念出一个字 被multi纠正等等 然后multi发现 原来我的大半生人生的记忆 通通都存在个地下室的管子里面

就爆气 然后就跟他爷爷打了一架 就把他爷爷打倒 然后两个人记忆就都消失了 就是一个这样莫名其妙的故事

最近我重看了一下rick&multi 那我现在觉得 自从有了AI agent以后 很多这个科幻电影 科幻小说里面有的情节

感觉就没有那么神奇 比如说rick&multi最新一季里面 有一个电影制造机 就是你输了一个脚本 他就输出一个电影

你想想看 现在其实根本就已经有电影制造机了 不是很多现在的短电影 都是直接用AI生成的吗 所以这个技术现在看起来也没有那么遥远了

好总之呢 就是一个记忆清楚 然后再读取的故事 那对语言模型来说 其实刚才把存在上下文中的这个内容

放到hard disk里面 之后再读取出来 其实就是他的记忆 所以语言模型的记忆 其实就是他在某一些时候

他可以自主的去执行 把内容放到资料库 放到硬碟里面的指令 然后他就把资料放到硬碟里面 那在这边要怎么把资料储存在硬碟里面

那不同的文献就有非常多不同的方式 比如说有人呢 会把这一些档案建成graph的形状 然后让你之后在搜寻的时候 比较能够了解不同记忆之间的关联性

或者是有人会帮记忆标上时间 那你比较知道说 要存取什么时间段的记忆 或者是比较新的记忆 他可能就比较需要被读出来

然后接下来呢 只要在某个时间点 模型能够执行抽取记忆的指令 他就可以从你的资料库里面 把记忆抽取出来

那这边需要研究的就是 那怎么让模型在适当的时机 抽取出它原来存在quamp里面的记忆 到你的档案系统里面 那什么时候要从档案系统里面

把失去的记忆读取回来 那我这边就是列了比较多的论文 然后给大家参考 那这方面跟这个AI agent记忆有关的文献 可以说是汗牛冲动

那我就列了几个reference 放在这边给大家参考 好那讲到记忆 那我们其实需要稍微修改一下 刚才才有关context engineering的式子

我们刚才说 我们有一个东西叫做context 叫做C 然后我们会有一个大F 来更新这个C

那如果我们要把记忆的概念加进来的话 讲得更精确一点 这个C应该被分成两部分 那我们在这边用P和N这两个符号 来代表C的两部分

那这个P和N有什么不同呢 P就是会被丢进语言模型的资讯 N就是不会被丢进语言模型 存在你的硬碟中的资讯 所以context我们其实可以把它包含

有存在硬碟中的资讯 有可以放到语言模型中的资讯 那我们这边把context里面 两种不同的资讯 分别用P和N来表示它

好那左边这个演算法 跟右边这个演算法 除了C呢 我们告诉你说 它里面有两个component以外

唯一不同的地方就是 这个呼叫LLN的输入变了 从CT变成PT 就是要告诉你说 我们只需要把C里面

我们准备要给LLN看的部分 给LLN看就好 那其他部分就存在硬碟里面 那所以当我们更新CT的时候 是把CT里面的两个component

PT跟NT分别更新成P T加1 NT加1 那有时候你更新的是P的部分 就放进语言模型的部分

当你执行loadmemory 当你把记忆从那个硬碟中 读取出来的时候 那你就更新了P 那有时候呢

你是执行savememory 你是要把memory存到硬碟里面 那你就更新了end 所以这是一个context engineering 更完整的式子

那讲到这边呢 我想要对我们常常用的几个词汇 做一下clarification 就有几个词汇 其实在我上课的时候

往往是被混用的 比如说context 比如说prom 这两个词汇 在上课的时候

好像几乎差不多是同样的意思 但实际上如果细分起来的话 我认为这两个词汇 还是有所不同的 这边所谓的context

指的就是这个演算法的c 它包含了 会被输入语言模型的部分 也包含了存在硬碟中的部分 你可以想成所谓的context

它是AI agent所经历过的一切事情 那P呢 P是真正会被输进语言模型的部分 所以P是context的一部分 它是语言模型会看到的部分

这个部分才是prom 所以prom跟context 我认为它还是有差别的 context不一定会成为语言模型的输入 只有context的一部分会被作为prom

那不过在上课的时候 或者在文献上 或者在你看到别人在讨论的时候 往往prom跟context 其实现在就是混杂成一团

但我觉得这两者 其实还是可以做出区别的 那我们刚才讲到在做摘要的时候 其实你就是呼叫某一个语言模型 跟他说

把这一段记忆做摘要 那今天语言模型都有摘要的能力 所以他就会输出摘要来 但是有一篇paper呢 叫做Acon

他就发现说 语言模型在做摘要的时候 很多时候是会失败的 所谓的失败并不是说 它没办法产生摘要

而是它产生完摘要 把摘要放到pump里面以后 结果本来能够答对的问题 本来做得了的任务 做不了了

那这件事情呢 叫做context collect 就今天在做压缩的时候 损失了一些资讯 如果损失是最重要的资讯

那语言模型就非常有可能犯错 就像我们上一堂课举的最后一个例子 有一个Meta的研究人员 他让AI帮他收信 结果AI在做compact的时候

把最重要的指令删除邮件 要经过人类同意这个指令 把它压缩变不见了 所以模型就开始不听人类的话 所以今天在做压缩的时候

它不是一个普通的压缩 它不是一个普通的摘要 我们应该要想办法告诉语言模型 什么样的资讯 是最应该被留在pump里面的

那这篇论文的解法是 它呢拿另外一个语言模型出来 然后呢 它有一些训练资料 这些训练资料是

本来没有做压缩的时候 可以做得对 但是语言模型在压缩之后 就做不对的一些例子 然后它把这一些例子

给一个语言模型看 然后跟那个语言模型看说 你看压缩以后结果变差了 你能不能够说明一下 反省一下

为什么压缩会变差呢 然后这个语言模型呢 就检查了这两个trajectory 以后呢 它就会得出它的结论

把这个结论呢 写成feedback 那其实这个feedback呢 就是一段文字 它没有什么特别的

这边完全没有训练模型 这个feedback 就是一段文字 那下一次 有不一样的任务进来的时候

再把这段feedback 给负责摘要的语言模型看 希望有多这段额外的feedback 可以让语言模型做得更好 那其实在这篇论文里面

它也把它的资料集 分成训练资料跟测试资料 不过这边要注意 这边所谓的训练资料 并没有真的去改变模型的参数

这些训练资料 就是拿来得到这个feedback 然后测试资料 会拿这一个feedback 来强化模型做摘要的能力

当语言模型看到这个feedback的时候 它里面的参数是没有任何改变的 但它只是因为看到这个feedback 更知道说在做摘要的时候 什么资讯是重要的

如果漏了什么资讯 之后可能就会任务失败 所以它更能够做摘要 更能够做人类要的摘要 任务要的摘要

所以可以表现得更好 那ACON这招真的有用吗 还真的有用 它这个walk是做在appware上面 那appware就是要让语言模型

去操控一大堆的app 然后来执行一些比较复杂的事情 其实就跟今天AI agent 在做的事情是一样的 所以你就知道说

今天这些AI agent 那么能够执行各式各样的程式 把它组合起来 完成复杂的任务 其实早就有这样子的benchmark

在评量AI agent 能够执行复杂任务的能力 那这边横轴呢 是这个peak token 也就是在整个pump里面

token最多的时候 多到什么样的地步 那如果今天你是黑色的点 就代表没有做compression 那这个时候你的token量

当然是最多的 这三张图就是 比较三个不同的模型 然后纵轴呢 纵轴就是正确率

正确率当然是越高越好 那如果你只是做一般的llm prompt 在appware这个benchmark上面 做llm 只做llm压缩

有时候结果是会变差的 压缩完之后 本来解得了的任务 就解不了了 虽然做完压缩以后

你当然用的token量比较少 但是正确率是会下降的 那他发现说 当他用econ这个做法 也就是让语言模型

更能够做摘要 更能够做任务需要的摘要的时候 他得到的是紫色这一个点 不只所耗费的token变少 表现也变得更好

所以这个是econ做的事情 在econ那篇论文里面是完全没有训练模型的 当然你想要训练模型也是可以的 那也当然有论文 我就引用在这边

尝试去fine tune一个llm 这个llm是专门对context做压缩的 但你可能想说 那我们要怎么训练这样子的llm呢 我们一般训练一个模型的时候

你不只要输入 也要有正确的答案 才能够训练模型 但是今天 假设没有正确的答案

或实际上我们就是没有正确的答案 那我们要怎么训练这个模型呢 你又不知道正确的摘要 应该要长什么样 你又不知道什么样的摘要

才是对任务有帮助的 所以实际上在训练这个模型的时候 是用一个reinforcement learning的方法 它是说 好让这个模型产生摘要之后

那还不算完 还不知道这个摘要好不好 接下来再继续去解这个任务 然后直到最后 解完任务之后看有没有做对

有做对 就是positive reward 没有做对就是negative reward 用reinforcement learning的方法 来训练这个做摘要的语言模型

但其实做摘要的语言模型 跟负责做其他事情 比如说产生执行工具指令的模型 其实是同一个模型 所以实际上在训练的时候

你不只是强化了语言模型 做摘要的能力 你其实强化了解整个任务的能力 包括语言模型根据摘要 来解任务的能力

也许你今天这个训练 一定不只是让摘要写得更好 可能同时也是让模型 更能够读取摘要 更知道怎么从一个简短的摘要里面

去执行它的任务 训练一个LLM 他的目标是特化在 Agent 的这个情况下 可以做得更好

那讲到目前为止 我们都还没有讲 什么时候应该开始压缩 但直觉上 今天context太长的时候

就应该开始压缩 但是长到什么样的地步 应该开始压缩呢 如果你去看这个open cloud的话 那里面就是一条写死的规则

反正长度超过某个上限的时候 就开始压缩 为什么是用写死的规则呢 为什么不让语言模型自己决定什么时候要压缩呢 因为前人的文献已经发现


![Slide 28](../../bilibili_video/slides_p1/slide_0028.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2509.23586](https://arxiv.org/abs/2509.23586)


![Slide 29](../../bilibili_video/slides_p1/slide_0029.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2510.24699](https://arxiv.org/abs/2510.24699)

语言模型不喜欢做压缩 对他来说 压缩就是抹除记忆 他非常不喜欢这件事 就像Morty发现

自己大半身的记忆 都被藏在一个地下室的时候 他非常的生气 就殴打了他的爷爷 所以这个语言模型呢

跟Morty一样 他不喜欢他的记忆 无人无故就消失了 就算是你给他一个工具 跟他说

这边有个好用的工具 这个工具呢 会把你过去的记忆 某一些地方抹除 他听了就不高兴

听了就不想执行这个工具 那甚至呢 在这篇论文里面 他还尝试逼迫模型使用这个工具 他跟模型说呢

现在有一个工具叫做erase 那就是会抹去模型部分的记忆 然后他说 当我跟你说reflection 反省的时候

你就要执行erase这个工具哦 然后呢 这个模型呢 就开始做事情 做着做着做着

人类在这边强制输入说 reflection 然后非常重要 你只能做erase 不能做其他事

语言模型才不做 他就继续做他的事情 他不想要抹除他自己的记忆 所以语言模型 没那么喜欢被抹除记忆

所以怎么办呢 有一篇paper呢 叫做agent 4 所以你会发现说 今天这个

因为语言模型不太喜欢 被抹除记忆 所以open cloud 用的是强制执行的方法 只要context超过一个上限

他就执行一个动作 叫memory flush 这强制执行的 会让模型自己开始压缩自己的记忆 那有一篇paper呢

叫做agent 4 他做的事情是 他去训练模型 训练模型使用压缩记忆的工具 那他把这个压缩记忆的工具

叫做fold 叫做折叠 那这个fold呢 会吃两个输入 一个输入是

我们要把刚才 整个对话的第几步到第几步做压缩 那么说压缩完之后 你最好还可以留一个小纸条说 这边曾经被压缩过

那这个小纸条内容写什么 也可以让语言模型 透过这个工具自己决定 所以他就可以说 第三步到第四步

刚才是上网搜寻 收到了一大堆的资料 那也许太冗长了 我们就改成一句话 上网搜寻


![Slide 30](../../bilibili_video/slides_p1/slide_0030.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2510.24699](https://arxiv.org/abs/2510.24699)

我已经知道 我要的资讯 比如说台湾最高的山市玉山 然后呢 就执行这个fold的指令要的事情

把前面第三步骤跟第四步骤 置换成一段文字 那讲到这边 你可能会想说 刚才不是说语言模型

不喜欢压缩或抹除自己的记忆吗 这边怎么能够压缩或抹除自己的记忆 其实这篇论文 正好就是呼应了过去的研究 发现语言模型不喜欢压缩记忆

因为这篇论文的核心是 使用压缩记忆工具这件事情 必须要透过训练才能取得 所以他们是微调了模型的参数 这跟刚才前面

Acon不一样 Acon那个paper 教模型做summary的时候 是没调参数的 这边是得调参数才能够做到

你得逼迫去训练语言模型 使用这些压缩的工具 他才有办法自己做压缩 那在这篇论文里面 其实又有提到说

他们试图硬是Pump模型 努力的Pump模型 看看能不能够在不微调模型的情况下 让模型自己使用压缩工具 他们发现模型很难

透过Pump的情况下 稳定的使用压缩工具 所以压缩这个能力是需要另外训练的 那我们上周也讲到subagent的概念 那subagent呢


![Slide 31](../../bilibili_video/slides_p1/slide_0031.jpg)


![Slide 32](../../bilibili_video/slides_p1/slide_0032.jpg)


![Slide 33](../../bilibili_video/slides_p1/slide_0033.jpg)

**幻灯片引用链接:**
- [https://hithaldia](https://hithaldia)
- [https://ouci.dnth.gov.ua/en/warks/IwAegO7/](https://ouci.dnth.gov.ua/en/warks/IwAegO7/)
- [https://arxi](https://arxi)


![Slide 34](../../bilibili_video/slides_p1/slide_0034.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/pdf/2510.11967](https://arxiv.org/pdf/2510.11967)


![Slide 35](../../bilibili_video/slides_p1/slide_0035.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/pdf/2510.11967](https://arxiv.org/pdf/2510.11967)


![Slide 36](../../bilibili_video/slides_p1/slide_0036.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2508.21433](https://arxiv.org/abs/2508.21433)
- [https://arxiv.org/abs/2601.16746](https://arxiv.org/abs/2601.16746)


![Slide 37](../../bilibili_video/slides_p1/slide_0037.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/26](https://arxiv.org/abs/26)


![Slide 38](../../bilibili_video/slides_p1/slide_0038.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/26](https://arxiv.org/abs/26)


![Slide 39](../../bilibili_video/slides_p1/slide_0039.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/26](https://arxiv.org/abs/26)


![Slide 40](../../bilibili_video/slides_p1/slide_0040.jpg)

其实可以看作是一种自主的压缩行为 当模型到某一个时间 它产生一个使用工具的指令 叫做Spawn繁殖的时候 它就可以产生一个subagent

那其实subagent 它仍然是跟原来的语言模型互动 subagent 它的context里面可能有一个subtask 告诉这个subagent要做什么

这个subagent呢 就把它的任务传给语言模型 语言模型给它一个回复 叫它用指令 它可能传回指令的

那个指令的导致的工具的输出 然后这个状况就一直下去 那subagent呢 可能会有一个动作叫做 return

它可以执行一个工具叫return 那return里面呢 会告诉主agent说 现在subagent它的输出是什么 它想给主agent的资讯是什么

当subagent执行return以后 它就把return的资讯 丢给主agent 那主agent就可以继续再跟LLM互动下去 那当subagent执行return之后

它之前所做的事情 就通通从这一串context里面被抹除 那你就可以想成 这其实也是自动删除记忆的一种方式 那这一整段记忆

就被改成了return里面写的这句话 所以本来一直到subagent运作的时候 它的context都从这边一直到这边 但是当执行return以后 等于执行了一个自主压缩

这一段对话记录就通通不见了 对话记录就从这边开始 那为了让大家可以更直观地了解 subagent是怎么运作的 那我就截了这篇paper里面的一张图

那里面就非常清晰地 用个具体的例子展示 subagent对于context的长度的影响 那这边就是有一个很复杂的问题 他就说有一篇发表在2023年的论文

内容是跟什么什么主题有关的 然后这个作者有三个人 其中一个人是某个教授等等等等 我想说你都知道这么多资讯 还自己找不到这篇论文

还要agent帮你找 所以这显然是一个蛮artificial的问题 但总之这是一个特别拿来考验agent能力的问题 那看看agent解不解得了 然后agent看到这个问题之后

他就会首先开始搜寻相关的文章 那每一次agent执行一个动作的时候 这个时候他的context呢 都会逐渐地越来越长 那他这边就记录了context lab

那但是这一个语言模型呢 是有产生subagent的能力的 所以他先产生一个subagent 所以我们来搜寻相关的论文 然后找到相关论文以后

他只把找到的论文的标题 传回给主agent 所以这个时候整个context就缩短了 然后主agent呢 会再分裂一个subagent去执行另外一个任务

比如说验证作者数是对的 那这时候context又逐渐伸长 然后等找到这个作者的资讯之后 这个context又开始缩短 所以当你执行subagent的时候

对context而言 你当然是可以把subagent看作是 有一个主agent带了一堆小弟在工作 但是如果从context engineering的角度而言 所谓的subagent就是对context做自主的压缩

每次分裂一个subagent的时候 就是预示了某一段的context之后 会被压缩掉 所以每次产生一个subagent的时候 你就可以累积context

这个subagent结束的时候 那一段context就不见了 你就会看到这个context呢 有锯齿状的上升跟下降 那他另外呢

还特别说明说 假设如果没有这个subagent 所有的context都不断的累积的话 最终会累积到十万多个token 那超过了他们语言模型

可以吃的token的上限 所以对他们来说 能够产生subagent 也是蛮重要的能力 不过就像我刚才说的语言模型

其实不喜欢自主做压缩 所以subagent这个能力 通常不是天生的 它是后天取得的 它是需要经过训练取得的

但今天很多模型 它都有产生subagent的能力 当你把你的open cloud 接给cloud的时候 它有产生subagent的能力

但这可能不是一个 自然原生的能力 它是需要经过特别的训练 才能够具备这种能力 那在这篇论文里面

他们就有针对 产生subagent的能力 做了特别的训练 那怎么训练呢 他们是用reinforcement learning的方法

他们去用reinforcement learning的方法 去训练语言模型 希望语言模型 可以得到正确的答案 但他们发现

如果只用答案正确与否 来当作语言模型 学习的信号的话 它不见得能够 学会正确的产生subagent

因为假设你的目标 只是得到正确的答案 对语言模型来说 有什么理由 它一定要产生subagent吗

它就是努力得到正确的答案就好了 所以它其实是需要 加上一些额外的reward 才能够去促使 逼迫诱导语言模型

去使用subagent这个工具 比如说 它有一个reward是 如果主干的context过长 就会被惩罚

主干的context太长的话 就会有一个惩罚 所以今天语言模型 会不得不去分裂出一些subagent 让主干不会太长

然后呢 它又怕呢 subagent永远都不结束 有时候分裂出一个subagent 那subagent呢

就自己把自己当作主agent 然后把所有事情都做完了 就失去产生subagent的意义 这种事情 也是有可能发生的

所以 它也要去惩罚一下 如果subagent呢 做出超越范围的事情 它直接自己把整个问题解完了

那也是会受到惩罚的 那用这种方法呢 才能够训练语言模型 使用subagent这个工具 好

那讲到目前为止呢 我们刚才都是在提压缩 也就当我们context过长的时候 把过长的context 把它弄短

但是 那是治标 那我们能不能治本 一开始就不要让context过长呢 那怎么样不让context过长呢

那你就要分析一下说 现在到底是什么样的资讯 让context过长 那这篇呢 有两篇论文

都有做类似的分析 而且分析的结果 非常的一致 所以左边这篇论文 它说

它分析了 假设我们没有做context engineering 就记录现在在整个对话的历程中 到底模型做了什么事情 到底这些token来自于什么样的行为

到底这些token都代表了什么样的事情 它做了一个分析 它分析的结果是这样子的 这边action指的是模型去产生执行工具的指令 那这些指令通常很简短

所以只占了历史记录的6.5% reasoning指的是模型自己说出来的话 语言模型自己说出来的话 那这个也很简短 只占9.6%

那在整个context里面 什么样的token占据了多数的context呢 它发现所谓的observation 占据了几乎84%左右的context 那这些observation指的是来自外界的输入

比如说语言模型读了一个档案 打开 那里面整个档案所有的资讯 都变成context的一部分 它执行了某一个工具

那工具有非常长的输出 那些输出变成context的一部分 这些来自外界的输入 才占据了多数context的内容 那另外一篇论文

它也得到几乎一样的结论 那另外一篇论文 它是主要focus在那个software engineering上面 所以它主要是让模型呢 去改程式还有执行程式嘛

那它发现当模型 在做software engineering的时候 它只有12%的context是在执行程式嘛 只有11.8%的context是在修改程式嘛 多数的时候它都在读程式嘛

有76%的context是花在 把整个repo里面的程式码读进来 所以占了非常大量的context 所以有没有办法直接制本 一开始就不要让这么多的文字进入context呢

所以就有一些论文提出了一些想法 我们也许应该在observation 进到语言模型之前 就做一些过滤的行为 那一般我们在执行读一个档案

或读一个文件的时候 常见的做法就是 语言模型它输出一个指令 说我要读一个log file 然后呢你有一个叫做read的工具

那这read的工具就把log file找到 然后把log file的内容原封不动的 一口气的逼语言模型吞下去 那如果这个log file非常大 有时候语言模型的就会哽到

所以怎么办呢 也许我们需要一个更聪明的read的工具 我们也许可以让语言模型 它在输出指令的时候呢 它不只说我想要读log file

它还说我想要读log file里面 跟修复box有关的内容 那希望这个read的指令够聪明 它不只能够打开一个档案 它还能够从档案里面

找出真正重要的部分 那这个read的指令 显然它需要有一点intelligence在 它去读了这个log 从log里面

把跟bug fixing有关的content呢 把它读出来 语言模型只focus在 跟bug fixing有关的内容上面 那我刚才说这个read的指令

显然它需要有一点智能 那或者是你需要 做比较多的engineering 去implementread的这个函式 那在这篇论文里面呢

他们其实就是训练了一个 小的语言模型 所以这个read的本身 也是一个小的语言模型 这个小的语言模型

本来就可以吃这个指令 根据这个指令 找出合适的内容 再传给主要的agent 好那讲到这边

我们也可以回顾一下 看看之前在讲OpenCloud的时候 它是怎么处理memory的 在讲处理memory的时候 我们说它其实有两个函式

一个叫memory search 一个叫memory get 它其实有两个工具 那我们其实并没有细讲 为什么它需要memory get


![Slide 41](../../bilibili_video/slides_p1/slide_0041.jpg)

这个工具 你可能想说 为什么读memory 还需要一个特别的工具 读memory

memory又不是什么神奇的东西 它就是文字档 它不是什么神奇的东西 用一般的函式 用一般读档的函式

也可以把那个档案的内容 通通通通通通读出来 为什么在读memory的时候 OpenCloud要设计一个特别的工具去读Memory 其实就是为了做到

我刚才在前一页投影片里面讲的过滤 其实MemoryGet这个函式 它不是只给它要读的档案 它其实还会给额外的两个数字 代表说从这个档案的第几行开始读起

然后我们总共要读多少行 所以MemoryGet是从整个巨大的MemoryFile里面 只存取一部分出来 因为OpenCloud当初在设计的时候 害怕Memory里面存了非常大量的资料

把所有资料一次都读到语言模型的context里面 语言模型会哽到 所以它就只从Memory里面选一小段的内容 至于要怎么选一小段的内容 到底一整个MemoryFile要取哪里

由MemorySearch的结果来决定 根据MemorySearch的结果 还有语言模型自己的判断 去使用MemoryGet这个工具 只存取Memory这个档案的一小部分


![Slide 42](../../bilibili_video/slides_p1/slide_0042.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2506.01056](https://arxiv.org/abs/2506.01056)


![Slide 43](../../bilibili_video/slides_p1/slide_0043.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2506.01056](https://arxiv.org/abs/2506.01056)


![Slide 44](../../bilibili_video/slides_p1/slide_0044.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2506.01056](https://arxiv.org/abs/2506.01056)


![Slide 45](../../bilibili_video/slides_p1/slide_0045.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2506.01056](https://arxiv.org/abs/2506.01056)

这个其实也是过滤的概念 另外一个过滤的概念就是按需加载 有一篇Paper叫做NCP0 我们一般在让AI Agent使用工具的时候 你其实就是把使用工具的指令

有哪些工具 这些工具可以拿来干嘛 把它放在语言模型的SystemProm里面 那这个SystemProm在有了这些工具的指令之后 可能会非常的长

NCP0这篇Paper里面就特别提到说 举个例子 比如说有一个使用GitHub的工具 那这个使用GitHub的工具呢 足足有4600个Token

而且这只是使用GitHub的工具而已 如果有更多的工具 模型就会直接超过它的Context window 可以承受的上限 所以怎么办呢

工具这种东西应该是要动态加载的 那过去比较传统的方法是说 根据使用者输入的任务 再去挑选合适的工具 那其实这跟RIG的概念是非常类似的

假设这些工具的说明 都被存在一个非常巨大的资料库里面 今天有一个新的任务进来 根据这个任务去启动一个搜寻引擎 去工具的资料库里面进行搜寻

把相关的工具指令 把它抽取出来 将模型知道有哪些工具可以用 它就可以执行这些工具 来得到我们想要的结果

但这篇论文就是发现说呢 这不是一个特别好的方法 因为今天使用者的需求 往往非常的模糊 所以不容易根据使用者的需求

来判断需要使用哪些工具 比如说今天使用者的需求可能是 帮我修改这个bug 但是修改bug要用的工具不止一个 比如说模型会需要

至少先用读档的工具能读档 然后看了这个程式以后 再用一个这个edit编辑的工具 才能够修改这个程式码 所以今天虽然使用者只说了

帮我修改这个程式码 或帮我抵这个bug 但被换用的工具其实是好几个 那你很难直接从使用者问的这个问题 让搜寻引擎决定要使用哪些工具


![Slide 46](../../bilibili_video/slides_p1/slide_0046.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2506.01056](https://arxiv.org/abs/2506.01056)

所以这篇paper他提出来的核心想法就是 我们何不让语言模型用AI动态的决定 他自己需要什么工具 让语言模型输出他想要什么 所以语言模型可能在读到任务的指令之后

他想一想就输出一个任务的需求 输出一个工具的需求 用这个工具的需求去操控搜寻引擎 让搜寻引擎找出他需要的工具 然后他就可以使用他需要的工具来解

解接下来的任务 那这件事情啊 你可能觉得听起来很熟悉 这个其实就是OpenCloud里面所用的skill的概念 skill这个东西

他也是按需加载的 我们不会把所有的skill都放到context里面 我们不会把所有的skill都放到这个pump里面 只有在需要的时候才从硬碟里面 把skill读出来放到pump里面


![Slide 47](../../bilibili_video/slides_p1/slide_0047.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2506.01056](https://arxiv.org/abs/2506.01056)

这个就是按需加载的概念 好那讲到这边啊 我们就讲了一些有关context engineering的想法 但到目前为止 多数context engineering

也就这个大F要做的事情 都是人类决定的 人类边写好写死了固定的指令 这边就是一些写死的指令 然后让你的电脑

让你的程式 按照这些写死的指令 来处理context 但是有没有办法 让这个context engineering

做得更复杂 更有智慧 做得更好呢 有一个想法叫做 Agentic Context Engineering

那这个说法就是来自于一篇 叫Agentic Context Engineering的paper 然后把论文的连结也放在这边 那这边想法的核心就是 把context engineering

也交给语言模型 也不给人类设计 直接交给语言模型 让他自己想办法 帮自己做context engineering

也就本来大F是人类工程师设计的 现在直接交给语言模型工程师 看看他有没有更好的想法 这边这个Agentic Context Engineering的概念 如果要画成图的话就是这样

你现在有一个context 然后呢这个context呢会加上一个输入 语言模型给一个输出 接下来呢把context输入输出 全部串起来

直接丢给一个语言模型 然后他爱干嘛就干嘛 得到一个新的context 我们叫context t加1 然后呢前面可能接个system prompt

然后后面呢加个input 然后呢再从语言模型那边得到output t加1 然后再有一个语言模型把context t加1 input t加1 output t加1 再变成context t加2


![Slide 48](../../bilibili_video/slides_p1/slide_0048.jpg)


![Slide 49](../../bilibili_video/slides_p1/slide_0049.jpg)


![Slide 50](../../bilibili_video/slides_p1/slide_0050.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2510.04618](https://arxiv.org/abs/2510.04618)


![Slide 51](../../bilibili_video/slides_p1/slide_0051.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2510.04618](https://arxiv.org/abs/2510.04618)


![Slide 52](../../bilibili_video/slides_p1/slide_0052.jpg)

那这个步骤呢就反复继续下去 那我这边在画图的时候呢 没有把system prompt加到context里面 那你要把system prompt视为context的一部分也可以啦 不过如果你细读这些Agentic Context Engineering的paper的话

你会发现实际上他让语言模型自己处理的context 是全部context的一部分 他们通常就是留一个区块 这个区块给语言模型爱玩什么就玩什么 但是比较重要的东西

比如说system prompt 那里面是包含了这个AI agent本身的identity 整整重要的资讯的 这个是不能够随便乱动的 所以通常你就固定住它

不要动它 这一系列Agentic Context Engineering的paper 通常只改整个context里面的其中一部分而已 好 那Agentic Context Engineering

一个比较早期的paper 可能是Dynamic Cheat Sheet 它就把这个context叫做cheat sheet 叫做小超 那只是这个小超是会随时间变化的

那概念非常简单 就是呼叫一个语言模型 给它一段Prompt 跟它说我们这个context要怎么改比较好 然后他就把context t

input t over t 改成context t加1 就结束了 这边它的核心就是Prompt Engineering

把这段Prompt写好 希望语言模型读了这段Prompt 自己知道怎么做context Engineering 也就是用Prompt Engineering 来做context Engineering

这段Prompt非常的长 那仔细读下来呢 它的核心精神就是 存下未来能用的东西 就它告诉语言模型说


![Slide 53](../../bilibili_video/slides_p1/slide_0053.jpg)


![Slide 54](../../bilibili_video/slides_p1/slide_0054.jpg)


![Slide 55](../../bilibili_video/slides_p1/slide_0055.jpg)


![Slide 56](../../bilibili_video/slides_p1/slide_0056.jpg)


![Slide 57](../../bilibili_video/slides_p1/slide_0057.jpg)


![Slide 58](../../bilibili_video/slides_p1/slide_0058.jpg)


![Slide 59](../../bilibili_video/slides_p1/slide_0059.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2512.24601](https://arxiv.org/abs/2512.24601)


![Slide 60](../../bilibili_video/slides_p1/slide_0060.jpg)

**幻灯片引用链接:**
- [https://arxiv.org/abs/2512.24601](https://arxiv.org/abs/2512.24601)

你不要存一些很specific的东西 你要存的是精神概念 比如说什么有效的策略 可以把它存起来 如果你写一段程式嘛

你觉得之后用得上 也把它存起来 关键的发现也存起来 但是非常跟现在这个任务 有具体关联的东西

那可能之后都用不上了 就不要存起来 总之这边就是用Prompt Engineering 来做context Engineering 那像这样子的Paper呢

现在很多 比如像Agentic Contact Engineering 这篇Paper里面呢 他就做了更复杂的 他把他的这个context t到context t加1呢

就经过了更复杂的流程 那他把他的context呢 取了另外一个名字叫做Playbook 就是一个手则手册 那他希望语言模型呢

看着这个手册 做他应该做的事情 那这篇Paper实际上做的事情 我就不细讲 总之这个Playbook的演化呢

不是只有一个步骤 要过三个语言模型 这三个语言模型 分别做了不同的检查之后 最后产生一个修改Playbook的指令

他不是直接产生新的Playbook 因为他怕直接产生新的Playbook 搞不好一些旧的资讯就被弄坏了 所以他是去修改旧的Playbook 所以这三个模组合起来

会产生一个修改的指令 用这个修改的指令 去修改原来Playbook的内容 把Context T原来的Playbook 变成Context T加1

变成一本新的员工手则 这是Agentic Context Engineering 这篇Paper做的事情 那还有另外一篇Paper呢 叫做Recursive Language Model

它其实也是Agentic Context Engineering 的其中一个可能性 那这篇Paper呢 曾经一度非常的知名 因为它呢


![Slide 61](../../bilibili_video/slides_p1/slide_0061.jpg)

它号称说它发明了一个新的语言模型 这个语言模型呢 可以吃无穷长的输入 那其实它真正做的事情 就是Context Engineering

它做的事情是这样 它说假设现在的Context 真的可以非常非常的长 那非常非常长怎么办呢 就通通放到Hard Disk里面

我们只把这边的Context 拿非常非常小一部分 露得到Memory的Pump里面 那它这边Paper里面说 这些知识呢

叫做Meta Data 比如说它只记了 现在这个Context 到底有多长 然后Context呢

被切成几段 Context呢 被存在哪里 等等 非常简短的资讯

那如果用我们这边 Paper的符号来讲呢 这些存在Hard Disk里面的东西 就是App 这些会真的露到Memory里面

被露 这边不应该讲Memory 这边讲Memory 大家可能会觉得很困惑 那这边真的被放到Pump里面的

叫做P 那LM做的事情就是 看着这个P 然后去想去看看 它要从M里面

找寻什么样的资讯 然后发现语言模型很厉害 因为这个语言模型可以写程式 它会写程式呢 去对Hard Disk里面的内容做搜寻

因为它会自己呢 自主的知道 要做RAG 然后它自己知道说 它要去Hard Disk里面搜寻一些东西出来

把这些搜寻的东西拿出来 去修改它的Meta Data 所以PT就变成PT加1 那这边Paper里面 它有一个章节讨论了这个模型的

这些自主产生的Pattern 但是实际上到底有没有那么神奇 真的是见仁见智啦 因为如果你仔细去读它的Pump的话 因为这些做Context Engineering的LLF

背后是需要做Pump Engineering的 你仔细去读它的Pump的话 就只差没有教语言模型说 你直接做RAG了 它花了蛮多力气

不断地暗示语言模型说 你可以做RAG这件事 所以语言模型就写了一个程式做RAG 实际读它的Pump 我觉得也没那么神奇

不过它的表现呢 是非常好的 它说 你看原来的GPT-5 这个是个很好的模型

如果输入越来越长 输入越来越长 到某个长度 有些任务 它就解不了了

这边All-Long 这些Benchmark 就是测试语言模型 在Context非常长的情况下 它能不能够好好的运作

但是加上它的 这个Recursive Language Model以后 因为它这个Recursive Language Model 是一个Context Engineering的方法 所以它可以外挂在

任何现有的语言模型上 所以如果外挂在GPT-5上 就可以让本来已经很厉害的GPT-5 变得更厉害 在输入真的非常长

比如说长达1M 100万个Token的时候 仍然可以在这一些 长Context的Benchmark上面 做出不错的效果

总之呢 今天就是比较系统化的 跟大家介绍了Context Engineering 那我们这边有一个演算法 这个演算法

摘要了Context Engineering 实际上做的事情 那我们也跟大家说 其实Context分成两部分 一部分是Add

它是存在你的HotDisk里面的 一部分是P 它是真的会当做Prompt 丢给语言模型的 那有一系列比较新的研究

尝试说把Context Engineering里面 这个最关键的F 看能不能不要由 人类工程师来设计 也把它交给语言模型

那这个部分 要跟大家分享的 是Context Engineering

