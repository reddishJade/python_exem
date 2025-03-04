<template>
  <div class="home">
    <a-row :gutter="16">
      <a-col :span="8">
        <a-card title="待测试计划" :bordered="false">
          <template #extra><a @click="router.push('/test-plan')">更多</a></template>
          <a-list :data-source="upcomingTests" :loading="loading">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta
                  :title="item.title"
                  :description="item.test_date"
                />
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card title="最近成绩" :bordered="false">
          <template #extra><a @click="router.push('/test-result')">更多</a></template>
          <a-list :data-source="recentResults" :loading="loading">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta
                  :title="'总分: ' + item.total_score"
                  :description="item.test_date"
                />
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card title="健康建议" :bordered="false">
          <template #extra><a @click="router.push('/health-report')">更多</a></template>
          <a-list :data-source="healthTips" :loading="loading">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta
                  :title="item.title"
                  :description="item.description"
                />
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="16" style="margin-top: 16px">
      <a-col :span="24">
        <a-card title="体测成绩趋势" :bordered="false">
          <!-- 这里可以添加成绩趋势图表 -->
          <div style="height: 300px">
            <!-- 图表将在后续添加 -->
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Store, useStore } from 'vuex'
import axios from 'axios'

interface HealthReport {
  health_suggestions: string
}

interface TestPlan {
  id: number
  title: string
  date: string
}

interface TestResult {
  id: number
  score: number
  date: string
}

const router = useRouter()
const store = useStore()
const loading = ref(false)
const upcomingTests = ref<TestPlan[]>([])
const recentResults = ref<TestResult[]>([])
const healthTips = ref<Array<{ title: string; description: string }>>([])

const fetchData = async () => {
  try {
    // 获取待测试计划
    const testPlansResponse = await axios.get('http://localhost:8000/api/test-plans/', {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    upcomingTests.value = testPlansResponse.data.slice(0, 5)

    // 获取最近成绩
    const resultsResponse = await axios.get('http://localhost:8000/api/test-results/', {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    recentResults.value = resultsResponse.data.slice(0, 5)

    // 获取健康建议
    const reportsResponse = await axios.get('http://localhost:8000/api/health-reports/', {
      headers: { Authorization: `Bearer ${store.state.token}` }
    })
    healthTips.value = reportsResponse.data.slice(0, 5).map((report: HealthReport) => ({
      title: '健康建议',
      description: report.health_suggestions.slice(0, 50) + '...'
    }))

  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})

</script>

<style scoped>
.home {
  padding: 24px;
}
</style>
