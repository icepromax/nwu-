<template>
  <el-container class="layout-container-demo" style="height: 100%">
    <!-- 左侧导航栏 -->
    <el-aside width="120px" class="sidebar">
      <!-- 添加气泡容器 -->
      <div class="bubbles">
        <div v-for="n in 20" :key="n" class="bubble"
             :style="{
               '--delay': `${Math.random() * 8}s`,
               '--size': `${5 + Math.random() * 8}px`,
               '--left': `${Math.random() * 100}%`
             }">
        </div>
      </div>

      <el-scrollbar>
        <div class="top1-logo nav-logo" @click="goToLogin">
          <img src="@/assets/images/xiaohui.png"  :style="imgStyle"
               alt="校徽"/>
        </div>

        <el-menu class="transparent-menu">
          <div class="nav-menu-item"
               :class="{ 'active': currentComponent === 'ChatPage' }"
               @click="selectComponent('ChatPage')">
            <el-icon><ChatDotSquare/></el-icon>
            <span>聊天</span>
          </div>
          <div class="nav-menu-item"
               :class="{ 'active': currentComponent === 'AboutPage' }"
               @click="selectComponent('AboutPage')">
            <el-icon><Document/></el-icon>
            <span>介绍</span>
          </div>
<!--          <div class="nav-menu-item"-->
<!--               :class="{ 'active': currentComponent === 'EmptyPage2' }"-->
<!--               @click="selectComponent('EmptyPage2')">-->
<!--            <el-icon><Edit/></el-icon>-->
<!--            <span>是空</span>-->
<!--          </div>-->
<!--          <div class="nav-menu-item"-->
<!--               :class="{ 'active': currentComponent === 'EmptyPage3' }"-->
<!--               @click="selectComponent('EmptyPage3')">-->
<!--            <el-icon><User/></el-icon>-->
<!--            <span>页面</span>-->
<!--          </div>-->
        </el-menu>

        <!-- 底部图标部分保持不变 -->
        <div class="bottom-icons">
          <el-button class="icon-button" @click="handleToolsClick">
            <img src="@/assets/images/shezhi.png" class="custom-icon" />
          </el-button>
          <el-button class="icon-button" @click="handleHomeClick">
            <img src="@/assets/images/shouye.png" class="custom-icon" />
          </el-button>
        </div>
      </el-scrollbar>
    </el-aside>
    <!-- 功能页面 -->
    <el-main>
      <div>
        <component :is="showComponent"></component>
      </div>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import type { Component } from 'vue'
import { useRouter } from 'vue-router'
import ChatPage from "@/views/content/chat/ChatPage.vue";
import AboutPage from "@/views/content/About/AboutPage.vue";


// 修改这一行，明确指定 showComponent 的类型
const showComponent = ref<Component>(ChatPage)
const currentComponent = ref('ChatPage')  // 新增：跟踪当前选中的组件
const router = useRouter()

const imgStyle = {
  width: '98px',
  height: 'auto'
}
const selectComponent = (component: string) => {
  currentComponent.value = component
  switch (component) {
    case 'AboutPage':
      showComponent.value = AboutPage
      break
    case 'ChatPage':
      showComponent.value = ChatPage
      break

  }
}

const handleToolsClick = () => {
  // 处理工具图标点击事件
  console.log('工具图标被点击')
}

const handleHomeClick = () => {
  // 处理首页图标点击事件
  router.push('/login')
  console.log('首页图标被点击')
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.layout-container-demo .el-aside {
  color: var(--el-text-color-primary);
}

.sidebar {
  position: relative;
  overflow: hidden;
  background: linear-gradient(to bottom,
    #1cb5e0 0%,
    #0069e0 20%,
    #0052bc 40%,
    #003894 60%,
    #001e6c 80%,
    #000046 100%
  );
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  user-select: none;
}

.layout-container-demo .el-header {
  position: relative;
  background-color: var(--el-color-primary-light-7);
  color: var(--el-text-color-primary);
}

.layout-container-demo .el-menu {
  border-right: none;
}

.layout-container-demo .el-main {
  padding: 0;
}

.layout-container-demo .toolbar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  right: 20px;
}

.transparent-menu {
  background-color: transparent;
}

.nav-menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: transparent !important;
  height: auto;
  padding: 28px 10px; /* 调整水平内边距以适应更宽的导航栏 */
  color: #ffffff;
  transition: all 0.3s ease;
  user-select: none; /* 添加这一行 */
  position: relative; /* 添加相对定位 */
  overflow: hidden; /* 隐藏溢出部分 */
  cursor: pointer; /* 关键属性：鼠标悬停变成手型 */
}

.nav-menu-item .el-icon {
  font-size: 24px; /* 增加图标大小 */
  margin-bottom: 5px; /* 在图标和文字之间添加一些间距 */
  transition: transform 0.3s ease; /* 添加过渡效果 */
}

.nav-menu-item span {
  font-size: 12px;
  font-weight: bold; /* 添加这行来使文字加粗 */
}

.nav-menu-item::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.3s ease, height 0.3s ease;
}

.nav-menu-item.active::before {
  width: 80px; /* 从90px减小到80px */
  height: 80px; /* 从90px减小到80px */
}

.nav-menu-item.active {
  color: #ffffff;
  font-weight: bold;
}

.nav-menu-item:hover .el-icon {
  transform: scale(1.2); /* 鼠标悬停时放大图标 */
}

.nav-menu-item:hover {
  transform: none; /* 移除之前的悬停效果 */
}

.bottom-icons {
  position: absolute;
  bottom: 30px;  /* 从20px改为30px，增加底部间距 */
  left: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0;
}

.icon-button {
  background: transparent;
  border: none;
  padding: 8px 0;  /* 从10px减小到8px */
  margin: 4px 0;   /* 从5px减小到4px */
  width: 100%;
  height: 35px;    /* 从40px减小到35px */
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;  /* 从25px减小到22px */
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.icon-button + .icon-button {
  margin-top: 25px;  /* 从20px增加到25px，让两个图标之间的间距更大 */
}

.icon-button:hover {
  color: #f0f9ff;
  transform: scale(1.1);
}

.nav-logo {
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}

.nav-logo img {
  width: 50px;
  height: auto;
  margin: 30px 0;
  transition: transform 0.3s ease;
}

.nav-logo img:hover {
  transform: scale(1.1);
}

/* 为顶部图标添加特定样式 */
.top1-logo img {
  width: 50px;
  height: auto;
  margin: 30px 0;
}
/* 为顶部图标添加特定样式 */
.top2-logo img {
  margin-bottom: 10px;
}

.custom-icon {
  width: 28px;  /* 从30px减小到25px */
  height: 28px;
  filter: brightness(0) invert(1);
}

.icon-button:hover .custom-icon {
  transform: scale(1.1);  /* 保持悬停效果 */
}

/* 修改气泡样式 */
.bubble {
  position: absolute;
  left: var(--left);
  bottom: -10px;
  width: var(--size);
  height: var(--size);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  animation: rise 12s infinite ease-in;
  animation-delay: var(--delay);
}

@keyframes rise {
  0% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  20% {
    opacity: 0.5;
  }
  40% {
    transform: translateY(-30vh) translateX(5px);
  }
  60% {
    opacity: 0.7;
  }
  80% {
    transform: translateY(-60vh) translateX(-5px);
  }
  100% {
    transform: translateY(-100vh) translateX(3px);
    opacity: 0;
  }
}

/* 添加一个更自然的摆动动画 */
@keyframes sway {
  0%, 100% {
    transform: translateX(-1px);
  }
  50% {
    transform: translateX(1px);
  }
}

.bubbles {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
  pointer-events: none;
  opacity: 0.7;
}

/* 确保其他内容在气泡上层 */
.el-scrollbar {
  position: relative;
  z-index: 1;
}
</style>
