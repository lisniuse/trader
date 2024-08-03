<template>
  <div class="main">
    <el-form :model="form" label-width="auto" style="max-width: 600px" v-loading="loading">
      <el-form-item label="选择品种">
        <el-select
          v-model="form.variety"
          placeholder="请选择品种"
          filterable
          remote
          :remote-method="loadData"
        >
          <el-option
            v-for="item in options"
            :key="item.id"
            :label="item.cnName"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <!-- 其余表单项保持不变 -->
      <el-form-item label="方向">
        <el-radio-group v-model="form.direction">
          <el-radio value="1">做多</el-radio>
          <el-radio value="2">做空</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="仓位管理">
        <el-radio-group v-model="form.positionType">
          <el-radio value="1">使用固定资金</el-radio>
          <el-radio value="2">使用总资金占比</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="固定资金（元）" v-if="form.positionType === '1'">
        <el-input v-model.number="form.amount" type="number" placeholder="请输入固定资金"></el-input>
      </el-form-item>
      <el-form-item label="总资金占比（%）" v-if="form.positionType === '2'">
        <el-input v-model.number="form.principalProportion" type="number" placeholder="请输入总资金占比"></el-input>
      </el-form-item>
      <el-form-item label="总资金占比说明" v-if="form.positionType === '2'">
        假设你的资金有300000，填写10，就是10%，也就是30000
      </el-form-item>
      <el-form-item label="止损比例（%）">
        <el-input v-model.number="form.stopLossProportion" type="number" placeholder="请输入止损比例"></el-input>
      </el-form-item>
      <el-form-item label="止损约为" v-if="form.positionType === '1'">
        {{ stopLossAmount }} （元）
      </el-form-item>
      <el-form-item label="止盈比例（%）">
        <el-input v-model.number="form.takeProfitProportion" type="number" placeholder="请输入止盈比例"></el-input>
      </el-form-item>
      <el-form-item label="止赢约为" v-if="form.positionType === '1'">
        {{ stopProfitAmount }} （元）
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit">立即下单</el-button>
        <el-button @click="onReset">清空</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { ElMessageBox, selectKey } from 'element-plus'

const form = reactive({
  variety: '', // 品种ID
  direction: '1', // 方向
  positionType: '1', // 仓位类型
  principalProportion: '10', // 总资金占比
  amount: '20000', // 固定金额 
  stopLossProportion: '5', // 止损比例
  takeProfitProportion: '10' // 止盈比例
})

const options = ref([])
const loading = ref(true)

const stopLossAmount = computed(() => {
  return Number(form.amount) * Number(form.stopLossProportion) * 0.01
})

const stopProfitAmount = computed(() => {
  return Number(form.amount) * Number(form.takeProfitProportion) * 0.01
})

const fetchData = async (apiName, data) => {
  if (window.pywebview && window.pywebview.api && window.pywebview.api[apiName]) {
    if (data) {
      return window.pywebview.api[apiName](data)
    } else {
      return window.pywebview.api[apiName]()
    }
  } else {
    return undefined
  }
}

const loadData = async (query) => {
  const response = await fetchData('getConfig')
  if (response && response.symbols) {
    if (query) {
      options.value = response.symbols.filter(item => item.cnName.includes(query))
    } else {
      options.value = response.symbols
    }
  }
}

onMounted(async () => {
  // 可以在这里获取初始数据，如果有需要的话
  setTimeout(async () => {
    await loadData()
    const response = await fetchData('getLastCommond') 
    Object.keys(form).forEach(key => form[key] = response[key])
    loading.value = false
  }, 300)
})

const onSubmit = async () => {
  ElMessageBox.confirm(
    '下单指令发出之后系统会立刻下单且无法撤销，是否要继续？',
    '请确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
  .then(() => {
    fetchData('sendCommand', form)
  })
}

const onReset = () => {
  Object.keys(form).forEach(key => form[key] = '')
}
</script>

<style lang="less" scoped>
.main {
  width: 600px;
  padding: 22px;
  background-color: #fff;
  margin: 0 auto;
}
</style>
