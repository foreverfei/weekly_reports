### 周总结模板

### 1. 本周完成的工作

*   实验设计与实施：

    *   图像分类

* 数据收集与处理：

  *   300张管材，将其都转换为相同的32×32，并进行了数据预处理，归一化，将标签转换为独热编码，从图像数据中减去平均值，实现均值中心化

* 算法开发与优化：

  *   create_residual_block，create_attention_block复现了一下论文里的模型

* 文献阅读：

  * 图像分类相关论文：《Residual Attention Network for Image Classiﬁcation》

    《Evolving Deep Convolutional Neural Networks for Image Classification》

    粗略阅读：《Research on image classification model based on deep convolution neural network》

    《A survey of image classiﬁcation methods and techniques for improving classiﬁcation performance》

    《Multimodal semi-supervised learning for image classification》

*   论文撰写：

    *   已完成的章节或部分，修改了哪些内容。

### 2. 遇到的困难和问题

*   技术难点：

    *   编程、算法实现等方面遇到的问题。

*   理论疑惑：

    *   对某些理论概念的不理解或困惑。

*   实验问题：

    *   训练集的效果还可以但是测试集的准确率不高。![1732201432372](D:\桌面\1732201432372.png)
    *   

*   其他问题

### 3. 解决方案与已采取的措施

*   问题分析：

    *   可能是模型参数设置不对，数据集的数量太小
*   寻求的帮助：

    *   咨询了导师或同学，获得的建议。

### 4. 下周工作计划

*   主要目标：

    *   调整模型使得验证集准确率提高

*   具体任务：

    *   计划开展的实验、阅读的文献等。

*   时间安排：

    *   为每项任务制定具体的时间计划。

### **5. 需要的支持与资源**

*   导师建议：

    *   希望导师在哪些方面提供指导。

*   资源需求：

    *   需要的设备、软件、数据集等。

### 6. 其他备注

*   个人心得：

    *   本周主要在调研如何实现图像分类，目前把Residual Network基本复现，但是将数据集换成300张图片后，训练集效果可以但是验证集准确率不高，后面尝试在原有数据的基础上进行扩展或者调整实验参数，看看能不能提高一下分类的准确率。

