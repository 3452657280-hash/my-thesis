<!-- 外文资料翻译 草稿 v0.1（2026-11-11）。学校要求 ≥1200 字并附原文；本稿译出摘要、第1节、第3节（约 4000 字）。原文许可 CC BY 4.0，可翻译并注明出处。定稿前作者通读润色、核对公式符号，并按学校模板排版（译文在前、原文在后）。 -->

# 外文资料翻译

**原文出处**：Lukas Bahr, Christoph Wehner, Judith Wewerka, José Bittencourt, Ute Schmid, Rüdiger Daub. Knowledge graph enhanced retrieval-augmented generation for failure mode and effects analysis[J]. Journal of Industrial Information Integration, 2025, 45: 100807. DOI: 10.1016/j.jii.2025.100807. 预印本：arXiv:2406.18114v3. 许可协议：CC BY 4.0。

**翻译范围**：摘要；第1节 引言；第3节 面向FMEA的问答（3.1–3.3）。

---

## 译文

# 知识图谱增强的检索增强生成在失效模式与影响分析中的应用

### 摘要

失效模式与影响分析（FMEA）是降低潜在失效风险的重要工具，在新产品的爬坡阶段尤其如此。然而，FMEA工具通常采用表格结构，推理能力有限，制约了FMEA的有效性。与此同时，大语言模型（LLM）为高级自然语言处理任务带来了新的可能，但在需要事实性知识的任务中仍面临困难，检索增强生成（RAG）方法正是为弥补这一不足而提出的。RAG从非参数化的数据存储中检索信息，再由语言模型生成回答。在此基础上，本文提出用知识图谱（KG）来增强非参数化数据存储。通过把知识图谱引入RAG框架，我们希望对FMEA数据同时实现分析型问答和语义型问答。本文的贡献包括：FMEA数据的集合论标准化表示及其模式（schema）、从FMEA知识图谱生成向量嵌入的算法，以及一个知识图谱增强的RAG框架。我们通过一项用户体验设计研究验证了该方法，并测量了上下文检索的精确率和召回率。

**关键词**：FMEA；风险评估；知识图谱；检索增强生成；大语言模型

### 1 引言

新产品在全球范围内几乎同时投产，给价值链纵向和横向上的多个跨学科团队带来了挑战。在投产阶段，质量保证团队尤其关注受控程度较差的工艺过程。此外，工艺过程往往十分复杂，因果关系难以识别，例如全球生产网络中存在各种运营、协调或沟通上的障碍。因此，需要采用以用户为中心的方法，把在试生产阶段获得的、关于生产系统爬坡和运行中可能出现问题的经验，传递给全球生产网络中的量产工厂。

失效模式与影响分析是在爬坡阶段避免潜在失效的工具之一。FMEA是一种风险分析工具，侧重于系统地识别失效、预防缺陷，例如在工艺链或产品设计中的缺陷。复杂产品通常涉及众多利益相关方，导致各方的FMEA做法不同且互不一致，使得不同开发单元之间难以基于FMEA分析进行推理。此外，由于各方维护的数据条目不一致，FMEA文档很快就会变得难以理清，其完整性和准确性不明确，难以评估。最后，FMEA结果通常以表格形式组织，缺乏推理能力，例如无法归纳错误模式的共性、进行总结，或为预防错误提供分析性指导。

大语言模型的最新进展使得在自定义数据集上进行微调成为可能，可以用于信息检索以及与FMEA中的事实进行交互。大语言模型通常在大量文本上训练，在语言理解、问答等任务中表现出巨大潜力，但在需要事实性知识时常常出错。如何设计适用于需要事实性知识的任务的大语言模型，仍是一个开放的研究问题。Shuster等人的研究表明，在要求事实准确的问答任务上，检索增强生成优于单纯的语言模型。RAG架构把信息保存在非参数化存储中，并利用语言模型生成答案。非参数化存储是一种灵活、无固定模式的数据库方案，用于存储和检索数据。

然而，由于数值所附带的符号含义会丢失，现有RAG方法难以提取分析型数据，这限制了从FMEA的数值信息中得出结论。例如，“工序X中风险优先数最高的失效原因是什么？”这样的问题就无法从非参数化数据存储中正确推断出来。一种可能的解决办法是把非参数化存储的数据嵌入知识图谱中。知识图谱以有向、带标签的多重图来表示数据，把数据存为节点和关系，从而保存符号化的事实。知识图谱的符号结构为数据提供了上下文，使可解释的推理器能够从数据中得出新的见解。搜索引擎（谷歌、必应等）和问答服务（苹果Siri、亚马逊Alexa等）等知名工具都已认识到语义技术的优势。

本文的贡献在于把知识图谱集成到RAG框架中，实现对FMEA数据的易用且具有分析能力的问答。本文对FMEA进行了集合论意义上的标准化形式描述，使得任何FMEA都可以映射到知识图谱中，而不论其创建或存储使用何种工具。为了把这一集合论标准化表示转换为知识图谱，本文为任意FMEA提出了一个模式。随后，本文提出一种遍历FMEA知识图谱以生成向量嵌入的算法。最后，本文展示了如何把非参数化数据存储集成到知识图谱中，形成知识图谱增强的RAG（KG-RAG）框架。KG-RAG框架既能检索人类可理解的信息，又能通过知识图谱的图查询提供分析能力。一项用户体验设计研究提供了该方法有效性的信息，我们还进一步测量了上下文召回率和精确率。

### 3 面向FMEA的问答

本文提出知识图谱增强的RAG框架，用于对FMEA数据进行分析型和语义型问答。与微调大语言模型不同，KG-RAG框架允许在不重新训练的情况下动态更新数据，并支持基本的数值分析，例如找出风险优先数最高的失效模式。在3.1节中，我们用集合论形式化地描述FMEA，使其能够转换为3.2节所述的FMEA知识图谱，并给出从FMEA知识图谱计算向量嵌入的算法。在3.3节中，我们介绍KG-RAG框架，它通过向量搜索检索FMEA上下文，并以知识图谱的图查询加以增强，为用户的查询提供定制化的结果。

#### 3.1 FMEA的集合论形式化

在制造系统中，任何FMEA都可以用集合论框架加以形式化定义。一个FMEA由集合F组成，其中每个元素代表一种不同的失效模式。失效模式是指工艺、产品或系统可能无法实现其预定功能的具体方式。形式上，设F = {f₁, f₂, …, fₙ}为所有已识别失效模式的集合，每一失效模式f∈F都与以下要素相关联：

- 失效影响E(f)：该失效模式对系统造成的影响或后果；
- 失效原因C(f)：导致该失效模式的根本原因或理由；
- 失效措施M(C(f))：用于评估该失效模式的措施。

此外，存在一个映射A: F(f) → P，把失效模式F(f)映射到它在生产线中出现的位置，其中P表示在制造过程中出现的位置，例如工序或工位。

FMEA还使用其他映射，以等级R = {1, …, 5}评价严重度、发生概率和探测概率，等级越高表示该失效模式越关键。风险优先数（RPN）给出失效模式的总体风险等级。我们采用以下映射：

- 严重度S：映射S: E(f) → R，输入失效影响E(f)，返回严重度等级；
- 发生概率O：映射O: C(f) → R，输入失效原因C(f)，返回该事件的概率等级；
- 探测概率D：映射D: M(C(f)) → R，输入失效措施M(C(f))，返回探测概率等级；
- 风险优先数RPN：映射RPN: (S, O, D) → U，输入S、O和D，返回总体风险等级U = S·O·D。

以这种方式定义FMEA的核心要素和映射，可以把任何具体的FMEA纳入这一集合论形式化之中。该方法保证了一致性，便于对不同FMEA进行系统分析；同时，它还使任何FMEA都能转换为知识图谱，以便查询和向量搜索。

#### 3.2 在知识图谱中建模FMEA数据

我们提出一个两步流程，在知识图谱中存储和嵌入FMEA数据。FMEA数据通常以表格形式存放在数据库中。第一步，把表格数据结构映射到前文提出的集合论FMEA形式化表示上；这一标准化集合有助于把FMEA数据转换为按既定模式组织的知识图谱结构。第二步，对FMEA数据进行聚合和嵌入，并把嵌入挂接到知识图谱上，使图结构能够支持向量搜索。

**将FMEA数据转换为知识图谱。** 设知识图谱𝒢为一个有向图，定义为

𝒢 = (N, R, T)　　　　（1）

其中n∈N为节点集合，r∈R为图中的关系。集合T由形如(n_h, r, n_t)的事实（三元组）组成，其中n_h为头节点，r为关系，n_t为尾节点。

带有字面量l∈L的知识图谱为图增加了描述性特征。这些字面量提供关于节点及其关系的附加信息，使𝒢成为带字面量的知识图谱。在这种情况下，节点表示为元组n = (s_n, l₁, …, l_k)，其中s_n表示节点的符号（如名称），l₁, …, l_k是提供描述信息的字面量。字面量可以是描述性字符串、数值或关于该节点的任何其他信息。类似地，关系表示为r = (s_r, l₁, …, l_m)，其中s_r是标识关系r的符号，k和m分别表示节点和关系所关联的字面量个数。

知识图谱可以用模式加以组织，模式提供了特定于领域的一组类和规则，包括建立类的层次结构，以及定义关系的类型，例如关系的起点和终点类别。为了形式化FMEA模式，我们把FMEA的集合论表示映射到模式中相应的节点符号s_n和关系符号s_r上。对于f∈F，每一失效模式对应FMEA知识图谱中的一个子图。我们把节点F(f)定义为FailureMode（失效模式），E(f)定义为FailureEffect（失效影响），C(f)定义为FailureCause（失效原因），M(C(f))定义为FailureMeasure（失效措施），P定义为ProcessStep（工序）。模式通过关系isDueToFailureCause在F(f)与C(f)之间、通过isImprovedByFailureMeasure在C(f)与M(C(f))之间、通过resultsInFailureEffect在F(f)与E(f)之间建立层次关系。映射A: F(f) → P对应关系occursAtProcessStep，把失效与工序联系起来。其他映射如RPN、S、O和D，则作为数值字面量挂在知识图谱模式中各自对应的节点上。

把FMEA建模为知识图谱后，就可以使用推理、聚类、路径搜索等图算法，并借助查询语言方便地检索复杂的联合信息。尽管知识图谱中已有较成熟的推理方法，例如基于规则或基于分布式表示的推理方法，但这些方法难以随知识图谱规模扩展，或者难以检索更深层的组合信息，表述不清的查询尤其会给推理方法带来困难。为解决这一问题，我们提出把FMEA数据的信息块嵌入为向量表示，从而支持基于向量的推理。

**生成FMEA知识图谱的向量嵌入。** 为保证向量搜索能提取到有意义的信息，向量嵌入必须能代表整个FMEA图。为此，我们从知识图谱中构建能够刻画FMEA底层结构的信息块。例如，“X对Y有什么影响？”这样的询问并不明确，其含义取决于上下文X和Y，询问的上下文稍有变化，结果就可能不同。因此，必须采用一种能够涵盖FMEA数据中所有潜在信息的有效方法。为此，我们提出利用FMEA知识图谱的树状结构对其进行遍历，把层次结构转换为序列结构。对每个FailureMode节点，我们执行深度优先搜索（DFS），得到与之相连的节点；然后，把从根节点出发遍历到的节点汇编成一个字符串表示；对生成的文本块，使用任意的词向量编码器计算向量嵌入。随后，我们创建一个标签为VectorEmbedding的新节点，以字面量形式索引和存储该向量嵌入，并将其链接到相应的FailureMode节点上。具体步骤如算法1所示：

> 算法1　从FMEA图𝒢获取向量嵌入
> 过程 getVectorEmbeddings(𝒢)
> 　vectorEmbeddings ← 空集合
> 　对每个 node ∈ FailureMode：
> 　　connectedNodes ← DFS(node)
> 　　chunk ← 空字符串
> 　　对每个 properties ∈ connectedNodes：chunk ← add(properties)
> 　　vectorEmbeddings ← computeVectorEmbedding(chunk)
> 　返回 vectorEmbeddings

#### 3.3 KG-RAG框架

大语言模型凭借在海量数据上的大规模训练，能够理解语言的细微差别，并给出符合上下文的准确输出。我们按如下方式定义大语言模型的运算：大语言模型根据给定的上下文或指令c处理文本输入x并生成输出。h_process以x和c为输入，生成组合后的输入，再送入大语言模型计算推理结果LLM(h_process(x, c))。

设𝒢为3.2节提出的FMEA知识图谱。下面介绍用于从𝒢中检索信息的知识图谱增强RAG框架。该框架有两个检索信息的组件：（i）𝒢的图查询语言；（ii）向量搜索。

知识图谱查询语言能够检索对象已知的特定信息，或者进行基本的分析。设w表示用户的询问，例如“工序X的累计风险优先数是多少？”。大语言模型根据查询语言的定义自动生成具体的查询q：大语言模型利用图的语义和指令所提供的上下文c，用合适的图查询语言（如SPARQL）生成图查询q = LLM(h_process(w, c))，然后在𝒢上执行。该过程可以表示为𝒬: q → ℛ_query，其中ℛ_query是从𝒢中检索到的查询结果集合。

对于因语义信息未知而没有返回结果的查询，例如w中使用了错误的节点标签写法，或者自动生成查询失败，我们提供基于𝒢中向量嵌入的向量搜索。设v_w为w的向量表示，{v_i}（i = 1, …, ℐ）为数据库中的向量嵌入集合，ℐ为𝒢中嵌入的总数。我们定义相似度函数𝒮: (v_w, {v_i}) → {v_{i₁}, v_{i₂}, …, v_{i_k}}，返回与v_w最相似的k个向量，最相似向量的结果记为ℛ_vector。相似度函数采用余弦函数S: (v_w, v_i) → cos θ = (v_w·v_i) / (‖v_w‖‖v_i‖)，用于衡量v_w与v_i之间的相似度，其取值范围为−1到1，−1表示两个向量完全相反，1表示两个向量相似。

总体而言，KG-RAG框架包含两条流水线：一条根据用户询问w从FMEA知识图谱中检索信息，另一条把信息提供给用户。首先，把用户询问w输入大语言模型；大语言模型结合w和FMEA模式的图语义结构生成图查询q。如果𝒬(q)有结果，信息检索即告完成；如果𝒬(q)没有输出任何结果，则执行向量搜索𝒮(v_q, {v_i})，检索最相似的k个向量。检索过程的结果ℛ_query或ℛ_vector作为输入交给大语言模型，在上下文c中生成回应用户询问的答案，可表示为LLM(h_process(ℛ, c))。

**认知不确定性的处理。** 当大语言模型缺少相似示例的充足训练数据、面临认知不确定性时，容易产生幻觉。默认情况下，大语言模型无法表明自己的不确定性，无论置信度如何都会生成听起来合理的回答。本文提出的KG-RAG框架依靠检索到的上下文而非模型参数来生成答案，从而应对这一问题，并通过展示检索到的上下文，使用户能够自行评估不确定性。基于图查询得到的上下文可靠性很高，因为它们来自对FMEA中事实数据的符号操作；对于基于向量的搜索，KG-RAG方法在给出检索到的上下文的同时提供余弦距离，表示其与用户查询在语义上的接近程度，距离越大，表示认知不确定性越高。

---

## 原文

# Knowledge graph enhanced retrieval-augmented generation for failure mode and effects analysis

### Abstract

Failure mode and effects analysis (FMEA) is an essential tool for mitigating potential failures, particularly during the ramp-up phases of new products. However, its effectiveness is often limited by the reasoning capabilities of the FMEA tools, which are usually tabular structured. Meanwhile, large language models (LLMs) offer novel prospects for advanced natural language processing tasks. However, LLMs face challenges in tasks that require factual knowledge, a gap that retrieval-augmented generation (RAG) approaches aim to fill. RAG retrieves information from a non-parametric data store and uses a language model to generate responses. Building on this concept, we propose to enhance the non-parametric data store with a knowledge graph (KG). By integrating a KG into the RAG framework, we aim to leverage analytical and semantic question-answering capabilities for FMEA data. This paper contributes by presenting set-theoretic standardization and a schema for FMEA data, an algorithm for creating vector embeddings from the FMEA-KG, and a KG-enhanced RAG framework. Our approach is validated through a user experience design study, and we measure the precision and performance of the context retrieval recall.

**Keywords**: FMEA; Risk assessment; Knowledge graphs; Retrieval-augmented generation; Large language models

### 1 Introduction

A global and close-to-simultaneous start of production for a new product challenges multiple and interdisciplinary teams along the vertical and horizontal value chain. Quality assurance teams are particularly concerned during the start of production with poorly controlled processes (Colledani et al., 2018). Furthermore, processes are often complex, and cause-and-effect relationships are difficult to identify, for example, due to various operations, coordination, or communication barriers in a global production network (Possner et al., 2024; Wehner et al., 2023). For this reason, experience gained in pre-series with regard to possible problems during the ramp-up and operation of production systems must be transferred to the series plants in a global production network using user-centered approaches (Eirich et al., 2023).

Failure mode and effects analysis (FMEA) is one tool to avoid potential failures during a ramp-up phase. FMEA is a risk analysis tool that focuses on systematically identifying failures and preventing defects, for example, in the process chain or the product's design (ISO/IEC, 2019; IEC, 2018). Typically, many stakeholders are involved in complex products, leading to different and incoherent FMEA approaches that make it difficult to reason over the FMEA analysis between the different development units (Ozarin, 2013). Furthermore, FMEA documents become quickly inextricable as actors maintain inconsistent data entries, leading to documentation that is difficult to evaluate with unclear completeness and integrity (Carlson, 2012). Lastly, FMEA results are usually tabular structured and lack reasoning capabilities, such as finding generalizations in error patterns, summarizing, or analytic guidance for error prevention.

Recent advances in large language models (LLMs) enable fine-tuning of custom data sets. This can be used for information retrieval and interactions with facts of the FMEA. LLMs are commonly trained on large amounts of text and show great potential, among others, in tasks such as language comprehension or answering questions (Brown et al., 2020). However, LLMs often fail when factual knowledge is required (Pan et al., 2024). Designing LLMs for tasks that require factual knowledge remains an open research question. In Shuster et al. (2021), the authors show that retrieval-augmented generation (RAG) outperforms language models for question-answering (QA) tasks that require factual precision. The RAG architecture stores the information in a non-parametric store and utilizes a language model to generate the answer. A non-parametric store is a flexible and schema-less database solution for storing and retrieving data.

However, current RAG approaches face difficulties extracting analytical data due to the loss of symbolic meaning attached to numerical values. This limits drawing conclusions from the numerical information of the FMEA. For example, "What failure cause has the highest risk priority number for the process step X?" cannot be correctly inferred from the non-parametric data store. One possible solution is to embed the non-parametric data stored in a knowledge graph (KG). KGs store symbolic facts by representing data as nodes and relations in a directed, labeled multi-graph (Hogan et al., 2021). The symbolic structure of the KG contextualizes the data and allows interpretable reasoners to derive novel insights from the data (Schramm et al., 2023). Prominent tools such as search engines (Google, Bing, etc.) or query answering services (Apple Siri, Amazon Alexa, etc.) have recognized the benefits of semantic technologies (Noy et al., 2019; Nigam et al., 2020).

This paper contributes by integrating KGs within a RAG framework for user-friendly and analytic QA on FMEA data. This paper formalizes a set-theoretic standardization of the FMEA, enabling any FMEA to be mapped into a KG, regardless of the tools used for the FMEA's creation or storage. To transpose this set-theoretic standardization into a KG, the paper proposes a schema for any FMEA. Subsequently, the paper suggests an algorithm for traversing the FMEA-KG to create vector embeddings. Finally, the paper demonstrates how to integrate the non-parametric data store into a KG, resulting in a KG-enhanced RAG (KG-RAG) framework. The KG-RAG framework enables retrieving human-understandable information while allowing analytical capabilities through the KG graph query. A user experience design study provides information on the effectiveness of the approach. We further measure the performance of context recall and precision.

### 3 QA for FMEA

In this paper, we introduce the KG-enhanced RAG (KG-RAG) framework for analytical and semantic QA on FMEA data. Unlike fine-tuning an LLM, the KG-RAG framework allows dynamic data updating without relearning and basic numerical analytics, like identifying the failure mode with the highest risk priority number. In Section 3.1, we formalize FMEA set-theoretically, enabling transposition into the FMEA knowledge graph described in Section 3.2. We also outline an algorithm for computing vector embeddings from the FMEA-KG. In Section 3.3, we introduce the KG-RAG framework, which retrieves the FMEA context through vector search, enhanced with KG graph queries, for customized user query results.

#### 3.1 Set-theoretic formalization of FMEA

In the context of manufacturing systems, any FMEA can be formally defined using a set-theoretic framework. An FMEA consists of a set F where each element represents a distinct failure mode (Automotive Quality and Process Improvement Committee, 2021). A failure mode is the specific manner in which a process, product, or system could potentially fail to perform its intended function. Formally, let F = {f₁, f₂, ..., fₙ} be the set of all identified failure modes. Each failure mode f ∈ F is associated with the following elements:

- Failure effect E(f): The effect or impact of the failure mode on the system.
- Failure cause C(f): The underlying cause or reason for the failure mode.
- Failure measure M(C(f)): The measure used to evaluate the failure mode.

Furthermore, there is a mapping A: F(f) → P from the failure mode F(f) to its appearance within the manufacturing line, where P denotes the occurrence in the manufacturing process, such as process step or station.

The FMEA employs further mappings that evaluate the severity, occurrence probability, and detection probability with a rating R = {1, …, 5}, for which a higher rating indicates a higher criticality for the failure mode (Stamatis, 2003). The risk priority number (RPN) gives the overall risk level rating of the failure mode. We follow the mappings:

- Severity S: A mapping S: E(f) → R, which takes a failure effect E(f) and returns the severity rating.
- Occurrence probability O: A mapping O: C(f) → R, which takes a failure cause C(f) and returns the probability rating of the event.
- Detection probability D: A mapping D: M(C(f)) → R, which takes a failure measure M(C(f)) and returns the detection rating probability.
- Risk priority number RPN: A mapping RPN: (S, O, D) → U, which takes S, O, and D and returns the overall risk level rating U = S·O·D (IEC, 2018; IEC, 2006).

Defining the core elements and mappings of an FMEA in this manner allows any specific FMEA to be integrated into the set-theoretic formalization. This approach ensures consistency and facilitates systematic analysis across different FMEAs. In addition, it enables the transposition of any FMEA into a KG for querying and vector search.

#### 3.2 Modeling FMEA data within a KG

We propose a two-step process to store and embed FMEA data in a KG. Typically, FMEA data are structured in a tabular format within a database. First, the tabular data structure is mapped to the previously proposed set-theoretic FMEA formalization. The standardized set helps to transpose the FMEA data into a KG structure for which a schema is defined. Second, the FMEA data must be aggregated, embedded, and attached to the KG to enable the graph structure for vector search.

**Transposing the FMEA data into a KG.** Consider a KG 𝒢 to be a directed graph defined by

𝒢 = (N, R, T),　　　　(1)

where n ∈ N is the set of nodes and r ∈ R are the relations of the graph (Schneider, 1973; Hogan et al., 2021). The set T consists of facts (triples) in the form T = (n_h, r, n_t), where n_h is the head node, r is the relation, and n_t is the tail node (Hogan et al., 2021).

KGs enhanced with literals l ∈ L add descriptive features to the graph. These literals provide additional information about the nodes and their relations, transforming 𝒢 into a knowledge graph with literals. In this context, a node is represented as a tuple n = (s_n, l₁, …, l_k), where s_n denotes the symbol of the node (such as its name), and l₁, …, l_k are literals providing descriptive information (Hogan et al., 2021). Literals can be descriptive strings, numeric values, or any other information about the node. Similarly, a relationship is indicated as r = (s_r, l₁, …, l_m), where s_r is the symbol that identifies the relationship r. The variables k and m denote the number of literals associated with the nodes and the relations, respectively.

KG can be structured using a schema that provides a set of classes and rules specific to the domain. This includes establishing a class hierarchy and defining the types of relations, such as their origin and target categories (Hogan et al., 2021). To formalize an FMEA schema, we map the set-theoretic formalization of an FMEA to the corresponding node s_n and relation s_r symbols of the schema. For f ∈ F, each failure mode corresponds to a subgraph of the FMEA-KG. We define the nodes F(f) as FailureMode, E(f) as FailureEffect, C(f) as FailureCause, M(C(f)) as FailureMeasure and P as ProcessStep. The schema realizes a hierarchy between F(f) and C(f) by the relationship isDueToFailureCause, C(f) and M(C(f)) by isImprovedByFailureMeasure, F(f) and E(f) by resultsInFailureEffect. The mapping A: F(f) → P corresponds to the relation occursAtProcessStep, linking the failure effect to a process step. Other mappings such as RPN, S, O, and D are numerical literals associated with their respective nodes within the KG schema.

The modeling of FMEA as KG allows the usage of graph algorithms, such as reasoning, clustering, or pathfinding, and a query language that facilitates the retrieval of complex joint information (Hogan et al., 2021). Although there are sophisticated reasoning methods within KGs, e.g., ruled-based or distributed representation-based inference methods, the methods do not scale with the KG's size or have difficulty retrieving deeper compositional information (Chen et al., 2020). Particularly poorly formulated queries pose challenges for reasoning methods. To address this issue, we propose to embed information chunks of the FMEA data as vector representations, enabling vector-based reasoning.

**Creating vector embeddings of the FMEA-KG.** To ensure meaningful information extraction from the vector search, vector embeddings must represent the entire FMEA graph. For this, we build information chunks from the KG that capture the underlying structure of the FMEA. For example, an inquiry such as "What is the consequence of X on Y?" is not explicit and depends on the context X and Y. The results could differ by a slight change with the context of the inquiry. Hence, adopting an efficient approach that encompasses all potential information within the FMEA data is essential. For this, we propose traversing the FMEA-KG by exploiting the tree-like structure of the FMEA-KG to transform the hierarchical structure into a sequential structure. For each FailureMode node, we perform a depth-first search (DFS) to obtain the connecting nodes. Next, we compile a singular string representation of the nodes traversed from the root node. With the generated text chunk, we compute the vector embeddings utilizing any word-to-vector encoder. Algorithm 1 fully details the steps for getting the vector embeddings. Subsequently, we create a new node n labeled VectorEmbedding that indexes and stores the vector embeddings as literal and links it to the corresponding FailureMode node.

> Algorithm 1 Get vector embeddings from FMEA graph 𝒢
> procedure getVectorEmbeddings(𝒢)
> 　vectorEmbeddings: set of vector embeddings
> 　for node ∈ FailureMode do
> 　　connectedNodes ← DFS(node)
> 　　chunk: string holding properties of connectedNodes
> 　　for properties ∈ connectedNodes do chunk ← add(properties)
> 　　vectorEmbeddings ← computeVectorEmbedding(chunk)
> 　return vectorEmbeddings

#### 3.3 KG-RAG framework

The LLM leverages its extensive training on vast amounts of data to comprehend language nuances and provide contextually accurate output. We define the operation of the LLM in the following way. LLMs process text input x based on a given context or instruction c to generate an output. h_process takes x and c as input and generates a combined input. This combined input is fed into the LLM, which computes the inference by LLM(h_process(x, c)).

Let 𝒢 denote the FMEA-KG proposed in Section 3.2. Subsequently, we introduce the KG-enhanced RAG framework for information retrieval from 𝒢. The framework has two components for the retrieval of information: (i) the graph query language of 𝒢 and (ii) vector search.

The KG query language enables retrieving specific information for which the object is known or for basic analytics. Let w denote a user inquiry. For example, "What is the cumulative risk priority number for the process step X?" An LLM automatically generates a specific query q adhering to the querying language definition. For this, the LLM generates the graph query using the appropriate graph query language, such as SPARQL, by leveraging the context c provided by the graph's semantics and instruction. The graph query q = LLM(h_process(w, c)) is then executed on 𝒢. The process can be expressed by 𝒬: q → ℛ_query, where ℛ_query is the set of retrieved query results from 𝒢.

For queries that do not return results due to unknown semantic information, such as wrong node label conventions in w or failures in the automatic query generation, we provide a vector search based on vector embeddings in 𝒢. Let v_w denote the vector representation of w, and {v_i} (i = 1, …, ℐ) be the set of vector embeddings in the database, where ℐ is the total number of embeddings in 𝒢. We define a similarity function 𝒮: (v_w, {v_i}) → {v_{i₁}, v_{i₂}, …, v_{i_k}}, which returns the vectors k most similar to v_w. The results of the most similar vectors are given by ℛ_vector. The similarity function is given by the cosine function S: (v_w, v_i) → cos(θ) = (v_w · v_i)/(‖v_w‖‖v_i‖), which measures the similarity between v_w and v_i (Camacho-Collados and Pilehvar, 2018). It ranges from −1 to 1, with −1 indicating completely opposite vectors and 1 indicating similar vectors.

The general KG-RAG framework operates with two pipelines: one for retrieving information from the FMEA-KG given the user inquiry w and another for serving the information to the user. Initially, the user inquiry w is fed into an LLM. The LLM generates a graph query q, considering w and the graph's semantic structure of the FMEA schema. If 𝒬(q) yields a result, the information retrieval is complete. If 𝒬(q) does not output any results, we perform a vector search 𝒮(v_q, {v_i}) to retrieve the k most similar vectors. The results from the retrieval process, either ℛ_query or ℛ_vector, are input to the LLM to generate a response addressing the user's inquiry embedded in the context c. This can be expressed by LLM(h_process(ℛ, c)).

**Handling of epistemic uncertainty.** LLMs are prone to hallucination when faced with epistemic uncertainty when they lack sufficient training data for similar examples (Hüllermeier and Waegeman, 2021). By default, LLMs cannot indicate uncertainty and generate plausible-sounding responses regardless of confidence. The proposed KG-RAG framework approach addresses this by relying on retrieved context rather than model parameters for answer generation. It enables users to assess uncertainty by displaying retrieved contexts. Graph query-based contexts are highly reliable, as they derive from symbolic manipulation and factual data in the FMEA. For vector-based search, the KG-RAG approach provides the cosine distance alongside the retrieved context, signaling semantic proximity to the user query. Greater distances indicate higher epistemic uncertainty.
