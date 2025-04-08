<template>
  <div class="about-container">
    <el-card class="about-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon :size="30" color="#409EFF"><School /></el-icon>
          <h1>西北大学智能助手</h1>
        </div>
      </template>

      <el-divider />

      <div class="feature-grid">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" v-for="(feature, index) in features" :key="index">
            <el-card shadow="never" class="feature-card">
              <div class="feature-content">
                <el-icon :size="36" :color="feature.color"><component :is="feature.icon" /></el-icon>
                <h3>{{ feature.title }}</h3>
                <p>{{ feature.description }}</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <el-divider>技术栈</el-divider>

      <div class="tech-stack">
        <el-tag v-for="tech in techStack" :key="tech" type="info" effect="dark" round>
          {{ tech }}
        </el-tag>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import {
  School,
  Document,
  ChatDotRound,
  Search,
  User,
  Setting,
  MagicStick
} from '@element-plus/icons-vue'

const features = [
  {
    icon: Document,
    title: '校园知识库',
    description: '快速查询培养方案、办事流程等官方文档',
    color: '#67C23A'
  },
  {
    icon: ChatDotRound,
    title: '智能问答',
    description: '7x24小时解答各类校园生活问题',
    color: '#409EFF'
  },
  {
    icon: Search,
    title: '精准检索',
    description: '从海量文档中快速定位所需信息',
    color: '#E6A23C'
  },
  {
    icon: User,
    title: '个人助手',
    description: '记录学习进度，提供个性化建议',
    color: '#F56C6C'
  },
  {
    icon: Setting,
    title: '事务办理',
    description: '常用事务在线指引与办理',
    color: '#909399'
  },
  {
    icon: MagicStick,
    title: 'AI增强',
    description: '基于DeepSeek-R1的智能分析',
    color: '#9c27b0'
  }
]

const techStack = [
  'Vue 3',
  'TypeScript',
  'Element Plus',
  'Flask',
  'DeepSeek-R1',
  'ChromaDB',
  'Ollama'
]
</script>

<style scoped>
.about-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.about-card {
  border-radius: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #f0f4f8 100%);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 15px;
}

.card-header h1 {
  margin: 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
  background: linear-gradient(to right, #409EFF, #9c27b0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.feature-grid {
  margin: 20px 0;
}

.feature-card {
  height: 100%;
  margin-bottom: 20px;
  border: none;
  background-color: rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.feature-content {
  padding: 20px;
  text-align: center;
}

.feature-content h3 {
  margin: 15px 0 10px;
  color: #303133;
  font-size: 18px;
}

.feature-content p {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  margin-top: 15px;
}

.el-divider__text {
  background: linear-gradient(135deg, #f5f7fa 0%, #f0f4f8 100%);
  font-size: 16px;
  font-weight: 500;
}
</style>
