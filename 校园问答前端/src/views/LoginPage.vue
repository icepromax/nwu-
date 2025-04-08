<template>
  <div class="login-page">
    <div class="background">
      <div class="glow"></div>
    </div>
    <div class="bubbles">
      <div class="bubble" v-for="n in 15" :key="n"></div>
    </div>
    <div class="content">
      <div class="center-content">
        <h1>为什么不问问西小北呢？</h1>
        <p>- 关于西大你知道哪些 -</p>
        <button class="magic-button" @click="goToMainPage">
          <span>探索</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const goToMainPage = () => {
  router.push('/main');
};
</script>

<style scoped>
.login-page {
  position: relative;
  height: 100vh;
  overflow: hidden;
  background: url('@/assets/images/background.jpg') no-repeat center center;
  background-size: 100% 100%;
  margin: 0;  /* 清除默认外边距 */
  padding: 0; /* 清除默认内边距 */
}

.background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  background: rgba(10, 25, 47, 0.7); /* 添加半透明遮罩，使背景不那么刺眼 */
}

.glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(
    ellipse at center,
    rgba(29, 78, 216, 0.15) 0%,
    transparent 70%
  );
  filter: blur(60px);
  opacity: 0.8;
  animation: pulse 10s ease-in-out infinite alternate;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

.content {
  position: relative;
  display: flex;
  height: 100%;
  z-index: 1;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
}

.center-content {
  text-align: center;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

h1 {
  font-size: 4em;
  margin-bottom: 20px;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(65, 184, 255, 0.7);
  animation: glow 3s ease-in-out infinite alternate;
  margin-left: 0;
  margin-right: 0;
}

@keyframes glow {
  from {
    text-shadow: 0 0 10px rgba(65, 184, 255, 0.7);
  }
  to {
    text-shadow: 0 0 20px rgba(65, 184, 255, 0.9), 0 0 30px rgba(65, 184, 255, 0.7);
  }
}

p {
  font-size: 1.4em;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  text-shadow: 0 0 5px rgba(65, 184, 255, 0.5);
  margin: 0;
}

.magic-button {
  margin-top: 40px;
  padding: 15px 30px;
  font-size: 1.2em;
  color: #fff;
  background: linear-gradient(90deg, #00d2ff, #3a7bd5, #00d2ff);
  background-size: 200% 100%;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 0 15px rgba(0, 210, 255, 0.3);
}

.magic-button::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #00d2ff, #3a7bd5, #2ecc71, #00d2ff);
  background-size: 400% 400%;
  z-index: -1;
  animation: glowing 3s ease-in-out infinite;
  border-radius: 25px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.magic-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(0, 210, 255, 0.5);
}

.magic-button:hover::before {
  opacity: 1;
}

.magic-button:hover {
  background-position: 100% 0;
}

.magic-button:active {
  transform: translateY(1px);
}

@keyframes glowing {
  0% {
    background-position: 0 0;
  }
  50% {
    background-position: 400% 0;
  }
  100% {
    background-position: 0 0;
  }
}

.bubbles {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  top: 0;
  left: 0;
}

.bubble {
  position: absolute;
  bottom: -100px;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  opacity: 0.5;
  animation: rise 10s infinite ease-in;
}

.bubble:nth-child(1) {
  width: 40px;
  height: 40px;
  left: 10%;
  animation-duration: 8s;
}

.bubble:nth-child(2) {
  width: 20px;
  height: 20px;
  left: 20%;
  animation-duration: 5s;
  animation-delay: 1s;
}

.bubble:nth-child(3) {
  width: 50px;
  height: 50px;
  left: 35%;
  animation-duration: 7s;
  animation-delay: 2s;
}

.bubble:nth-child(4) {
  width: 30px;
  height: 30px;
  left: 50%;
  animation-duration: 11s;
  animation-delay: 0s;
}

.bubble:nth-child(5) {
  width: 45px;
  height: 45px;
  left: 65%;
  animation-duration: 6s;
  animation-delay: 1s;
}

.bubble:nth-child(6) {
  width: 25px;
  height: 25px;
  left: 75%;
  animation-duration: 8s;
  animation-delay: 3s;
}

.bubble:nth-child(7) {
  width: 35px;
  height: 35px;
  left: 85%;
  animation-duration: 12s;
  animation-delay: 2s;
}

.bubble:nth-child(8) {
  width: 28px;
  height: 28px;
  left: 30%;
  animation-duration: 6s;
  animation-delay: 4s;
}

.bubble:nth-child(9) {
  width: 42px;
  height: 42px;
  left: 55%;
  animation-duration: 9s;
  animation-delay: 3s;
}

.bubble:nth-child(10) {
  width: 38px;
  height: 38px;
  left: 40%;
  animation-duration: 7s;
  animation-delay: 5s;
}

.bubble:nth-child(11) {
  width: 32px;
  height: 32px;
  left: 70%;
  animation-duration: 10s;
  animation-delay: 4s;
}

.bubble:nth-child(12) {
  width: 46px;
  height: 46px;
  left: 15%;
  animation-duration: 8s;
  animation-delay: 2s;
}

.bubble:nth-child(13) {
  width: 24px;
  height: 24px;
  left: 60%;
  animation-duration: 11s;
  animation-delay: 1s;
}

.bubble:nth-child(14) {
  width: 36px;
  height: 36px;
  left: 25%;
  animation-duration: 9s;
  animation-delay: 3s;
}

.bubble:nth-child(15) {
  width: 44px;
  height: 44px;
  left: 80%;
  animation-duration: 7s;
  animation-delay: 5s;
}

@keyframes rise {
  0% {
    bottom: -100px;
    transform: translateX(0);
  }
  50% {
    transform: translate(100px, -500px);
  }
  100% {
    bottom: 1080px;
    transform: translateX(-200px);
  }
}
</style>
