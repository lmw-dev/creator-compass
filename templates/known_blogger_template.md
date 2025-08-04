# 旧识博主激活脚本

## 脚本A - 关系唤醒型

{{ author }}，好久不见！

最近看到你在{{ main_topics[0] if main_topics else '相关领域' }}的内容，发展得很不错啊！特别是「{{ title }}」这期，你的{{ content_style }}比以前更成熟了。

想起之前我们聊过的{{ pain_points[0] if pain_points else '相关话题' }}，看来你已经有了新的思考和突破。

最近我在{{ value_propositions[0] if value_propositions else '相关项目' }}有些新的进展，感觉和你现在做的事情可能有些交集。有时间的话，我们再深入交流一下？

---

## 脚本B - 价值更新型

{{ author }}，你好！

一直有关注你的动态，你在{{ target_audience }}群体中的影响力越来越大了。最新这期关于{{ title }}的内容，角度很独特。

我们之前合作过的那个项目现在有了新的发展，在{{ value_propositions[1] if value_propositions|length > 1 else value_propositions[0] if value_propositions else '相关方面' }}上可能对你现在的工作有帮助。

同时也很好奇你对{{ main_topics[1] if main_topics|length > 1 else main_topics[0] if main_topics else '相关话题' }}的看法，想听听你的专业见解。

方便的时候聊聊？

---

## 脚本C - 共同成长型

嗨 {{ author }}！

看到你最近在{{ blogger_characteristics.expertise or '相关领域' }}的内容越来越深入，真的很佩服你的坚持和成长。

你提到的{{ pain_points[1] if pain_points|length > 1 else pain_points[0] if pain_points else '相关问题' }}，其实我们在实践中也遇到过类似的问题，现在有了一些新的解决思路。

觉得我们可以在{{ main_topics[2] if main_topics|length > 2 else main_topics[0] if main_topics else '相关方面' }}方面有更多交流，互相促进成长。

有空的话，我们约个时间详细聊聊？

---

*使用建议：这类脚本适用于有过接触但较长时间未联系的博主。重点在于唤醒之前的关系基础，同时展示你的新发展。*