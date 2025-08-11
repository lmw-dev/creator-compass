# 新锐博主破冰脚本 V2.0

## 脚本A - 价值共鸣型（主打）

你好 {{ author }}！

刚看完你的视频「{{ title }}」，对你那句"**{{ golden_sentences[0] if golden_sentences else '（此处引用一句博主金句）' }}**"印象特别深。你提出的 **"{{ core_values[0] if core_values else '（此处引用核心价值观）' }}"** 的观点，简直说出了我们这些产品开发者的心声。

我叫[你的名字]，也是这个领域的从业者。我们正在做一款工具，就是为了帮助像你这样坚持"{{ core_values[1] if core_values|length > 1 else core_values[0] if core_values else '内容为王' }}"的创作者。

纯粹是技术和思想上的交流，希望能和你交换一些经验，方便加个联系方式吗？

---

## 脚本B - 专业认可型

你好 {{ author }}！

我是[你的名字]，长期关注你的内容。在最近的视频「{{ title }}」里，你关于"{{ pain_points[0] if pain_points else '相关问题' }}"的分析非常到位。

特别是你说的"{{ golden_sentences[1] if golden_sentences|length > 1 else golden_sentences[0] if golden_sentences else '相关观点' }}"，这个角度很独特，让我有不少启发。

我目前在做[你的产品/项目简介]，正好也涉及到这个领域。我们产品的核心价值之一就是"{{ value_propositions[0] if value_propositions else '相关价值' }}"，感觉可能对你现在的工作流有帮助。

想和你简单交流一下，看看我们是否有合作或互助的可能，不知是否方便？

---

## 脚本C - 资源互助型

嗨 {{ author }}！

看了你的{{ title }}，特别认同你"{{ core_values[0] if core_values else '相关理念' }}"的理念。你在{{ blogger_characteristics.expertise or '相关领域' }}的积累很扎实。

你提到的"{{ pain_points[1] if pain_points|length > 1 else pain_points[0] if pain_points else '相关困难' }}"确实是行业痛点，我手头正好有一些{{ value_propositions[1] if value_propositions|length > 1 else value_propositions[0] if value_propositions else '相关资源' }}，可能对你有帮助。

同时也很想听听你对{{ main_topics[0] if main_topics else '相关话题' }}的更多看法。如果有兴趣的话，我们可以建立长期的交流合作。加个微信如何？

---

*使用建议：优先使用脚本A（价值共鸣型），通过引用博主的金句和价值观建立深层连接。记得在发送前个性化调整细节。*