<template>
  <div class="main">
    <el-form ref="refForm" :model="form" :rules="rules" label-width="auto" style="max-width: 600px" v-loading="loading">
      <el-form-item label="选择品种" prop="variety">
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
      <el-form-item label="方向" prop="direction">
        <el-radio-group v-model="form.direction">
          <el-radio value="1">做多</el-radio>
          <el-radio value="2">做空</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="仓位管理" prop="positionType">
        <el-radio-group v-model="form.positionType">
          <el-radio value="1">使用固定资金</el-radio>
          <el-radio value="2">使用总资金占比</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="固定资金（元）" v-if="form.positionType === '1'" prop="amount">
        <el-input v-model.number="form.amount" type="number" placeholder="请输入固定资金"></el-input>
      </el-form-item>
      <el-form-item label="总资金占比（%）" v-if="form.positionType === '2'" prop="principalProportion">
        <el-input v-model.number="form.principalProportion" type="number" placeholder="请输入总资金占比"></el-input>
      </el-form-item>
      <el-form-item label="总资金占比说明" v-if="form.positionType === '2'">
        假设你的资金有300000，填写10，就是10%，也就是30000
      </el-form-item>
      <el-form-item label="止损比例（%）" prop="stopLossProportion">
        <el-input v-model.number="form.stopLossProportion" type="number" placeholder="请输入止损比例"></el-input>
      </el-form-item>
      <el-form-item label="止损约为" v-if="form.positionType === '1'">
        {{ stopLossAmount }} （元）
      </el-form-item>
      <el-form-item label="止盈比例（%）" prop="takeProfitProportion">
        <el-input v-model.number="form.takeProfitProportion" type="number" placeholder="请输入止盈比例"></el-input>
      </el-form-item>
      <el-form-item label="止盈约为" v-if="form.positionType === '1'">
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
import { ElMessageBox, ElForm } from 'element-plus'

const inWebview = ref(false)

const form = reactive({
  variety: '', // 品种ID
  direction: '1', // 方向
  positionType: '1', // 仓位类型
  principalProportion: '10', // 总资金占比
  amount: '20000', // 固定金额 
  stopLossProportion: '5', // 止损比例
  takeProfitProportion: '10' // 止盈比例
})

const rules = {
  variety: [{ required: true, message: '请选择品种', trigger: 'change' }],
  direction: [{ required: true, message: '请选择方向', trigger: 'change' }],
  positionType: [{ required: true, message: '请选择仓位管理类型', trigger: 'change' }],
  amount: [
    { required: true, message: '请输入固定资金', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (form.positionType === '1' && !value) {
          callback(new Error('请输入固定资金'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  principalProportion: [
    { required: true, message: '请输入总资金占比', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (form.positionType === '2' && !value) {
          callback(new Error('请输入总资金占比'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  stopLossProportion: [{ required: true, message: '请输入止损比例', trigger: 'blur' }],
  takeProfitProportion: [{ required: true, message: '请输入止盈比例', trigger: 'blur' }]
}

const options = ref([])
const loading = ref(true)
const refForm = ref(null)

const stopLossAmount = computed(() => {
  return Number(form.amount) * Number(form.stopLossProportion) * 0.01
})

const stopProfitAmount = computed(() => {
  return Number(form.amount) * Number(form.takeProfitProportion) * 0.01
})

const fetchData = async (apiName, data) => {
  if (inWebview.value) {
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
    inWebview.value = window.pywebview && window.pywebview.api
    if (inWebview.value) {
      await loadData()
      const response = await fetchData('getLastCommond') 
      Object.keys(form).forEach(key => form[key] = response[key])
      loading.value = false
    } else {
      loading.value = false
    }
  }, 300)
})

const onSubmit = async () => {
  refForm.value.validate((valid) => {
    if (valid) {
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
    } else {
      console.log('表单校验失败')
    }
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
