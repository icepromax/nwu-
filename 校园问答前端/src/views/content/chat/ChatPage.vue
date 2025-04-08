<template>
  <div class="ai-practice-container">
    <!-- 左侧历史对话记录 -->
    <div class="history-panel">
      <div class="new-chat-container">
        <button class="new-chat-btn" @click="newConversation">
          新建对话
          <el-icon class="plus-icon">
            <Plus/>
          </el-icon>
        </button>
      </div>
      <ul class="history-list">
        <li v-for="(item, index) in historyList" :key="index" @click="selectConversation(index)"
            :class="{ active: currentConversationIndex === index }">
          {{ item.title }}
          <el-icon class="delete-icon" @click.stop="deleteConversation(index)">
            <Delete />
          </el-icon>
        </li>
      </ul>
    </div>

    <!-- 右侧对话页面 -->
    <div class="chat-wrapper">
      <div class="chat-panel">
        <!-- 上半部分聊天界面 -->
        <div class="chat-messages" ref="chatMessagesRef">
          <div v-for="(message, index) in currentConversation.messages" :key="index" :class="['message', message.role]">
            <div class="avatar">
              <div v-if="message.role !== 'user'" class="ai-avatar">
                <img src="@/assets/images/img_2.png" alt="AI Avatar">
              </div>
              <div v-else>
                <img src="@/assets/images/img_1.png" alt="Me">
              </div>
            </div>

            <div class="content">
              <!-- 思考过程（阴影化显示） -->
              <div v-if="showThink && message.think" class="thinking-content" v-html="message.think"></div>
              <!-- 最终回答 -->
              <div class="answer-content" v-html="message.content"></div>
            </div>

          </div>
        </div>

        <!-- 输入框 -->
        <div class="input-area">
          <div class="input-wrapper">
            <el-popover placement="top" :width="150" trigger="hover" :disabled="!!userInput.trim()">
              <template #reference>
                  <el-icon class="input-icon link-icon">
                    <Link/>
                  </el-icon>
              </template>
              <span>该功能还在开发中</span>
            </el-popover>
            <input
                v-model="userInput"
                @keyup.enter="sendMessage"
                placeholder="输入消息，按回车发送..."
                type="text"
                :disabled="isInputDisabled"
            >
            <div class="button-group">


<!--              <div class="audio-wave" v-if="isRecording" @click="finishRecording">-->
<!--                <span v-for="n in 4" :key="n" :style="{ animationDelay: `${n * 0.2}s` }"></span>-->
<!--              </div>-->
<!--              <el-icon v-else class="input-icon microphone-icon" @click="toggleRecording">-->
<!--                <Microphone/>-->
<!--              </el-icon>-->


              <el-popover placement="top" :width="150" trigger="hover" :disabled="!!userInput.trim()">
                <template #reference>
                  <el-icon class="input-icon microphone-icon" @click="toggleRecording">
                    <Microphone/>
                  </el-icon>
                </template>
                <span>该功能还在开发中</span>
              </el-popover>


              <div class="separator"></div>

              <el-popover placement="top" :width="200" trigger="hover" :disabled="!!userInput.trim()">
                <template #reference>

                  <el-button class="send-button" circle @click="sendMessage" :disabled="!userInput.trim()">
                    <el-icon>
                      <Top/>
                    </el-icon>
                  </el-button>

                </template>
                <span>请文字/录音/上传语音回复</span>
              </el-popover>
            </div>
          </div>
        </div>

        <div class="disclaimer">
          「西小北」的回答可能包含AI生成内容，如有疑问请咨询学校相关部门获取权威信息~
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>
import {ref, computed, nextTick, onMounted, onUnmounted} from 'vue';
import {Link, Microphone, Plus, Delete} from '@element-plus/icons-vue';
import {ElMessage} from 'element-plus';
import {get, post} from '@/utils/request'
import {API} from '@/api/config'
import { marked } from 'marked';
import { useElementVisibility } from '@vueuse/core';


// 使用sessionId来维护上下文
const sessionIds = ref({}); // 存储每个对话的sessionId {index: sessionId}
const historyList = ref([
  {
    title: '西大智能问答系统',
    messages: [{
      role: 'assistant',
      content: [
          '您好，我是西小北，有什么可以帮助您的呢'
      ].join('\n')
    }]
  }
]);

const currentConversationIndex = ref(0);
const userInput = ref('');
const chatMessagesRef = ref(null);
const isInputDisabled = ref(false);

const currentConversation = computed(() => historyList.value[currentConversationIndex.value]);

// 获取当前对话的sessionId
const getCurrentSessionId = () => {
  if (!sessionIds.value[currentConversationIndex.value]) {
    sessionIds.value[currentConversationIndex.value] = generateSessionId();
  }
  return sessionIds.value[currentConversationIndex.value];
};

const generateSessionId = () => {
  return Date.now().toString() + Math.random().toString(36).substr(2, 9);
};

const selectConversation = (index) => {
  currentConversationIndex.value = index;
  nextTick(() => {
    scrollToBottom();
  });
};

const newConversation = () => {
  const newSessionId = generateSessionId();
  const newIndex = historyList.value.length;

  historyList.value.unshift({
    title: '新对话',
    messages: [{
      role: 'assistant',
      content: '您好！我是西小北，请问有什么可以帮助您的呢？'
    },{
      role: 'user',
      content: '请问西北大学校训是什么'
    },{
      role: 'assistant',
      content: '公诚勤朴'
    }]
  });

  sessionIds.value[newIndex] = newSessionId;
  currentConversationIndex.value = 0;
};

const deleteConversation = (index) => {
  delete sessionIds.value[index];
  historyList.value.splice(index, 1);

  if (currentConversationIndex.value === index && historyList.value.length > 0) {
    currentConversationIndex.value = 0;
  }
  else if (historyList.value.length === 0) {
    currentConversationIndex.value = -1;
    newConversation();
  }
};

const showThink = ref(true); // 控制是否显示思考过程
const useKnowledge =ref(true);
// 在 sendMessage 函数中修改响应处理部分
const sendMessage = async () => {
  if (!userInput.value.trim()) return;

  const prompt = userInput.value.trim();
  userInput.value = '';

  // 添加用户消息
  currentConversation.value.messages.push({
    role: 'user',
    content: prompt
  });

  // 添加 AI 加载状态
  const loadingMessage = {
    role: 'assistant',
    content: '思考中...',
    think: '', // 存储思考过程
    loading: true
  };
  currentConversation.value.messages.push(loadingMessage);

  nextTick(scrollToBottom);
  isInputDisabled.value = true;

  try {
    const res = await post(API.GENERATE, {
      prompt: prompt,
      session_id: getCurrentSessionId(),
      use_knowledge: useKnowledge.value
    }, { timeout: 120000 });

    if (res.code === 100) {
      // 解析返回的内容（假设返回格式是 `<think>...</think> 最终回答`）
      const responseText = res.data;
      const thinkMatch = responseText.match(/<think>(.*?)<\/think>/s);
      const thinkContent = thinkMatch ? thinkMatch[1].trim() : '';
      const answerContent = thinkMatch ? responseText.replace(thinkMatch[0], '').trim() : responseText;

      // 使用 marked 渲染 Markdown 内容
      const renderedAnswer = marked(answerContent);
      const renderedThink = marked(thinkContent);

      // 更新消息
      loadingMessage.think = renderedThink;
      loadingMessage.content = renderedAnswer;
      loadingMessage.loading = false;

      // 如果有 session_id 更新，存储它
      if (res.session_id) {
        sessionIds.value[currentConversationIndex.value] = res.session_id;
      }
    } else {
      throw new Error(res.msg || '请求失败');
    }
  } catch (error) {
    console.error('发送消息失败:', error);
    loadingMessage.content = '获取回复失败，请稍后重试';
    loadingMessage.loading = false;
    ElMessage.error(error.message);
  } finally {
    isInputDisabled.value = false;
    nextTick(scrollToBottom);
  }
};

const scrollToBottom = () => {
  const chatMessages = chatMessagesRef.value;
  if (chatMessages) {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
};

onMounted(() => {
  // 初始化默认对话的sessionId
  sessionIds.value[0] = generateSessionId();
});
</script>


<style scoped>

.answer-content, .thinking-content {
  /* Markdown 通用样式 */
  line-height: 1.6;
}

.answer-content p, .thinking-content p {
  margin: 0.5em 0;
}

.answer-content pre, .thinking-content pre {
  background: #f5f5f5;
  padding: 1em;
  border-radius: 4px;
  overflow-x: auto;
}

.answer-content code, .thinking-content code {
  font-family: monospace;
  background: #f5f5f5;
  padding: 0.2em 0.4em;
  border-radius: 3px;
}


/* 思考过程样式（灰色、斜体、半透明） */
.thinking-content {
  color: #666;
  font-style: italic;
  opacity: 0.7;
  background-color: #f5f5f5;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 8px;
  border-left: 3px solid #ddd;
}

/* 最终回答样式（正常显示） */
.answer-content {
  line-height: 1.6;
}

/* 样式保持不变 */
.ai-practice-container {
  display: flex;
  height: 100vh;
  font-family: Arial, sans-serif;
}

.history-panel {
  width: 280px;
  background: linear-gradient(135deg, rgba(230, 240, 255, 0.01), rgba(240, 230, 255, 0.01));
  background-color: #ffffff;
  padding: 20px;
  overflow-y: auto;
}

.new-chat-container {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 13px; /* 略微增加内边距 */
  margin-top: 10px;
  margin-bottom: 5px;
  background: linear-gradient(to right, #0069e0, #0052bc); /* 改用更深的蓝色渐变 */
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: opacity 0.3s;
  font-size: 14px; /* 加大字号 */
  font-weight: bold; /* 加粗字体 */
}

.new-chat-btn:hover {
  opacity: 0.9;
}

.history-list {
  list-style-type: none;
  padding: 0;
}

.history-list li {
  padding: 10px;
  margin-bottom: 10px;
  background-color: #ffffff;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.history-list li:hover,
.history-list li.active {
  background-color: rgba(0, 105, 224, 0.15);
  color: #0052bc;
}

.chat-wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg,
  rgba(0, 105, 224, 0.08),
  rgba(0, 56, 148, 0.08)
  );
}

.chat-panel {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: transparent;
  box-shadow: none;
  padding-top: 12px; /* 添加顶部内边距 */
  /* padding-left: 10%;
  padding-right: 10%; */
}

.visitor-info {
  background-color: transparent; /* 背透明 */
  padding: 15px 20px; /* 增加内边距 */
  margin-bottom: 20px; /* 增加与第一条对话的距离 */
  font-weight: bold;
  color: #333;
  text-align: left;
  font-size: 18px; /* 增大字体大小 */
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding-top: 20px;
  padding-left: 10%;
  padding-right: 10%;
  background-color: transparent;
  /* 修改滚动条颜色 */
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 105, 224, 0.3) transparent;
}

/* 为 Webkit 浏览器（如 Chrome、Safari）自定义滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background-color: rgba(0, 105, 224, 0.3);
  border-radius: 3px;
}

.message {
  display: flex;
  margin-bottom: 20px;
}

.message .avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  overflow: hidden;
}

.message .avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ffffff;
}

.message .content {
  background-color: rgba(255, 255, 255, 1);
  padding: 12px 18px; /* 增加内边距 */
  border-radius: 10px;
  max-width: 80%;
  font-size: 16px; /* 增加字体大小 */
  line-height: 1.8; /* 增加行高 */
}

.message.user {
  flex-direction: row-reverse;
}

.message.user .avatar {
  margin-right: 0;
  margin-left: 10px;
}

.message.user .content {
  background-color: rgba(0, 105, 224, 0.12);
  color: black;
}

.input-area {
  padding: 20px 10% 0 10%;
  border-top: 0px solid #e0e0e0;
  background-color: transparent;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

input {
  width: 100%;
  padding: 12px 110px 12px 50px; /* 调整右侧padding以适应新的按钮组 */
  border: 1px solid rgba(204, 204, 204, 0.5);
  border-radius: 25px;
  font-size: 16px;
  background-color: rgba(255, 255, 255, 0.7);
  transition: border-color 0.3s;
  height: 55px;
}

input:focus {
  outline: none;
  border-color: #0069e0;
}

input::placeholder {
  color: #969696;
}

.button-group {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
}

.input-icon {
  color: #0069e0;
  font-size: 24px;
  cursor: pointer;
}

.link-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
}

.microphone-icon {
  margin-right: 0; /* 将右侧边距改为0 */
}

.separator {
  width: 1px;
  height: 25px;
  background-color: rgba(204, 204, 204, 0.5);
  margin: 0 10px;
}

.send-button {
  width: 40px;
  height: 40px;
  background: linear-gradient(to right, #0069e0, #0052bc); /* 保持一致的蓝色渐变 */
  border: none;
  color: white;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.send-button:disabled {
  background: rgba(0, 105, 224, 0.1);
  color: rgba(0, 82, 188, 0.3);
  cursor: default;
}

.send-button :deep(.el-icon) {
  font-size: 24px;
}

.send-button:not(:disabled):hover {
  opacity: 0.9;
}

/* 新增的免责声明样式 */
.disclaimer {
  font-size: 10px;
  color: #999;
  text-align: center;
  margin-top: 12px;
  margin-bottom: 12px;
}

.audio-wave {
  display: flex;
  align-items: center;
  height: 24px;
  width: 24px;
}

.audio-wave span {
  display: inline-block;
  width: 3px;
  height: 100%;
  margin-right: 1px;
  background: #0069e0;
  animation: audio-wave 0.8s infinite ease-in-out;
}

@keyframes audio-wave {
  0%, 100% {
    transform: scaleY(0.3);
  }
  50% {
    transform: scaleY(1);
  }
}

.message .content audio {
  margin-top: 10px;
  width: 100%;
}
</style>
